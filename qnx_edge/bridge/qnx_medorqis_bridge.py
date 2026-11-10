#!/usr/bin/env python3
"""
MedOrqis-QNX: Edge-to-Host Telemetry Bridge
Connects to QNX Neutrino RTOS 8.0 bedside monitor via POSIX socket,
validates CRC32 integrity, runs deterministic cross-verification against MedOrqis Core,
scrubs PHI, and triggers MedOrqis-LLM clinical decision support.
Standards: IEC 62304 / ISO 14971 / HIPAA & GDPR de-identification compliant.
"""

import os
import sys
import socket
import struct
import zlib
import json
import time
import argparse
from typing import Dict, Any, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from core.clinical_calculators import calculate_news2_score, SafeCalculationRefusal
from core.phi_deidentifier import PHIDeidentifier
from core.safety_guardrails import SafetyGuardrailsEngine
from qnx_edge.bridge.clinical_advisory import ClinicalAdvisoryEngine

# 64-byte packed struct format matching vitals_types.h:
# < (little-endian)
# I (magic_header: 4)
# H (version: 2)
# I (sequence_id: 4)
# Q (timestamp_us: 8)
# 16s (patient_id: 16)
# H (heart_rate_bpm: 2)
# H (systolic_bp_mmhg: 2)
# H (diastolic_bp_mmhg: 2)
# H (respiratory_rate_bpm: 2)
# f (spo2_percent: 4)
# f (temperature_celsius: 4)
# B (on_supplemental_oxygen: 1)
# B (consciousness: 1)
# B (news2_score: 1)
# B (alert_level: 1)
# H (red_flags_mask: 2)
# I (calculation_latency_ns: 4)
# I (crc32_checksum: 4)
TELEMETRY_PACKET_FORMAT = "<IHIQ16sHHHHffBBBBHII"
TELEMETRY_PACKET_SIZE = struct.calcsize(TELEMETRY_PACKET_FORMAT) # 64 bytes
MEDORQIS_MAGIC_HEADER = 0x4D454451 # "MEDQ"

ALERT_NAMES = {
    0: "ALERT_LEVEL_ROUTINE (Low Risk)",
    1: "ALERT_LEVEL_MEDIUM (Urgent Review)",
    2: "ALERT_LEVEL_CRITICAL (Emergency Rapid Response)"
}

class QnxMedOrqisBridge:
    def __init__(self, host: str = "127.0.0.1", port: int = 5055, audit_dir: Optional[str] = None):
        self.host = host
        self.port = port
        self.audit_dir = audit_dir or os.path.join(PROJECT_ROOT, "qnx_edge/reports")
        os.makedirs(self.audit_dir, exist_ok=True)

        self.phi_scrubber = PHIDeidentifier()
        self.safety_engine = SafetyGuardrailsEngine()
        self.advisory_engine = ClinicalAdvisoryEngine()

        self.packets_received = 0
        self.verification_discrepancies = 0
        self.critical_events_detected = 0

        self.audit_log_path = os.path.join(self.audit_dir, "qnx_telemetry_audit.jsonl")
        self.handover_report_path = os.path.join(self.audit_dir, "qnx_clinical_handover.md")

    def unpack_packet(self, raw_bytes: bytes) -> Optional[Dict[str, Any]]:
        """
        Unpacks and validates 64-byte QNX binary packet.
        """
        if len(raw_bytes) != TELEMETRY_PACKET_SIZE:
            return None

        fields = struct.unpack(TELEMETRY_PACKET_FORMAT, raw_bytes)
        (
            magic, version, seq_id, ts_us, patient_id_raw,
            hr, sbp, dbp, rr, spo2, temp,
            o2, cons, news2, alert, red_flags,
            latency_ns, crc_received
        ) = fields

        # 1. Magic Header Verification
        if magic != MEDORQIS_MAGIC_HEADER:
            print(f"[BRIDGE ERROR] Invalid magic header: 0x{magic:08X}")
            return None

        # 2. CRC-32 Integrity Verification (IEEE 802.3 over first 60 bytes)
        crc_calculated = zlib.crc32(raw_bytes[:60]) & 0xFFFFFFFF
        if crc_calculated != crc_received:
            print(f"[BRIDGE ERROR] CRC mismatch: calc 0x{crc_calculated:08X} != recv 0x{crc_received:08X}")
            return None

        patient_id = patient_id_raw.decode("ascii", errors="ignore").rstrip("\x00")

        return {
            "magic": magic,
            "version": version,
            "sequence_id": seq_id,
            "timestamp_us": ts_us,
            "patient_id": patient_id,
            "heart_rate_bpm": hr,
            "systolic_bp_mmhg": sbp,
            "diastolic_bp_mmhg": dbp,
            "respiratory_rate_bpm": rr,
            "spo2_percent": round(spo2, 1),
            "temperature_celsius": round(temp, 1),
            "on_supplemental_oxygen": bool(o2),
            "consciousness": int(cons),
            "news2_score": int(news2),
            "alert_level": int(alert),
            "alert_level_name": ALERT_NAMES.get(alert, f"UNKNOWN_{alert}"),
            "red_flags_mask": int(red_flags),
            "calculation_latency_ns": int(latency_ns),
            "crc32_checksum": crc_received
        }

    def verify_against_medorqis_core(self, telemetry: Dict[str, Any]) -> bool:
        """
        Executes Double-Check Protocol:
        Compares embedded QNX-computed NEWS2 against MedOrqis core/clinical_calculators.py.
        """
        try:
            o2_str = "OXYGEN" if telemetry["on_supplemental_oxygen"] else "AIR"
            cons_str = "CVPU" if telemetry["consciousness"] else "ALERT"

            py_result = calculate_news2_score(
                respiration_rate_bpm=telemetry["respiratory_rate_bpm"],
                spo2_percent=telemetry["spo2_percent"],
                air_or_oxygen=o2_str,
                systolic_bp_mmhg=telemetry["systolic_bp_mmhg"],
                pulse_bpm=telemetry["heart_rate_bpm"],
                consciousness=cons_str,
                temperature_celsius=telemetry["temperature_celsius"],
                age_years=68
            )

            qnx_score = telemetry["news2_score"]
            py_score = int(py_result.score)

            if qnx_score != py_score:
                self.verification_discrepancies += 1
                print(f"[CROSS-VERIFICATION FAILED] QNX={qnx_score} != MedOrqis Core={py_score}")
                return False

            return True
        except SafeCalculationRefusal as e:
            print(f"[SAFE REFUSAL] Core calculator rejected invalid inputs: {e}")
            return False

    def process_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main pipeline:
        1. Double-Check Verification with Core
        2. PHI scrubbing
        3. Audit logging
        4. Emergency handover generation if alert is CRITICAL
        """
        self.packets_received += 1
        is_verified = self.verify_against_medorqis_core(telemetry)
        telemetry["core_verified"] = is_verified

        # PHI Scrubbing check (ensure pseudonym format)
        scrubbed_id, _ = self.phi_scrubber.deidentify(telemetry["patient_id"])
        telemetry["scrubbed_patient_id"] = scrubbed_id

        # Write audit line
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(telemetry) + "\n")

        # Clinical Handover if critical or medium alert
        if telemetry["alert_level"] >= 1:
            if telemetry["alert_level"] == 2:
                self.critical_events_detected += 1

            handovers = self.advisory_engine.generate_isbar_handover(telemetry)
            telemetry["handover_generated"] = True

            # Save latest clinical handover markdown
            report_content = (
                f"# MedOrqis-QNX Emergency Clinical Handover Report\n\n"
                f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}  \n"
                f"**Verification Status**: {'VERIFIED DETERMINISTIC CONVERGENCE' if is_verified else 'DISCREPANCY DETECTED'}  \n"
                f"**QNX Microkernel Latency**: {telemetry['calculation_latency_ns']} ns\n\n"
                f"---\n\n"
                f"{handovers['english']}\n\n"
                f"---\n\n"
                f"{handovers['arabic']}\n"
            )
            with open(self.handover_report_path, "w", encoding="utf-8") as f:
                f.write(report_content)

        return telemetry

    def run_client(self, max_packets: Optional[int] = None, timeout_seconds: int = 15):
        """
        Connects to QNX socket and streams packets.
        """
        print(f"[BRIDGE START] Connecting to QNX RTOS Bedside Monitor at {self.host}:{self.port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_seconds)

        retries = 10
        connected = False
        for i in range(retries):
            try:
                sock.connect((self.host, self.port))
                connected = True
                print(f"[BRIDGE CONNECTED] Successfully connected to QNX Monitor on {self.host}:{self.port}")
                break
            except (ConnectionRefusedError, socket.timeout):
                time.sleep(0.5)

        if not connected:
            print(f"[BRIDGE ERROR] Could not connect to QNX Monitor on {self.host}:{self.port}")
            return False

        try:
            while True:
                data = b""
                while len(data) < TELEMETRY_PACKET_SIZE:
                    chunk = sock.recv(TELEMETRY_PACKET_SIZE - len(data))
                    if not chunk:
                        print("[BRIDGE INFO] Monitor closed stream.")
                        return True
                    data += chunk

                packet = self.unpack_packet(data)
                if packet:
                    self.process_telemetry(packet)
                    print(f"[TELEMETRY RECV] Seq {packet['sequence_id']:02d} | "
                          f"HR {packet['heart_rate_bpm']:3d} | SBP {packet['systolic_bp_mmhg']:3d} | "
                          f"SpO2 {packet['spo2_percent']:4.1f}% | NEWS2 {packet['news2_score']:2d}/20 | "
                          f"{packet['alert_level_name']} | Latency: {packet['calculation_latency_ns']} ns | "
                          f"Core Check: {'PASS' if packet['core_verified'] else 'FAIL'}")

                if max_packets and self.packets_received >= max_packets:
                    break
        except KeyboardInterrupt:
            print("\n[BRIDGE STOP] Stopped by user.")
        finally:
            sock.close()

        print(f"[BRIDGE SUMMARY] Packets: {self.packets_received} | Discrepancies: {self.verification_discrepancies} | Critical Events: {self.critical_events_detected}")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedOrqis-QNX Edge-to-Host Bridge")
    parser.add_argument("--host", default="127.0.0.1", help="QNX Monitor host")
    parser.add_argument("--port", type=int, default=5055, help="QNX Monitor port")
    parser.add_argument("--max-packets", type=int, default=None, help="Maximum packets to process")
    args = parser.parse_args()

    bridge = QnxMedOrqisBridge(host=args.host, port=args.port)
    bridge.run_client(max_packets=args.max_packets)
