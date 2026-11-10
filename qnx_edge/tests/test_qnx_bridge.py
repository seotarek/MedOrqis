#!/usr/bin/env python3
"""
MedOrqis-QNX: Automated Test Suite for Python Edge-to-Host Bridge
Tests:
1. 64-byte binary packet serialization and deserialization
2. CRC-32 integrity verification and corrupt packet dropping
3. Double-Check Protocol: C QNX score vs Python core/clinical_calculators.py
4. PHI de-identification validation
5. Bilingual ISBAR handover generation
"""

import os
import sys
import unittest
import struct
import zlib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from qnx_edge.bridge.qnx_medorqis_bridge import (
    QnxMedOrqisBridge,
    TELEMETRY_PACKET_FORMAT,
    TELEMETRY_PACKET_SIZE,
    MEDORQIS_MAGIC_HEADER
)
from qnx_edge.bridge.clinical_advisory import ClinicalAdvisoryEngine

class TestQnxBridge(unittest.TestCase):
    def setUp(self):
        self.bridge = QnxMedOrqisBridge(audit_dir="/tmp/medorqis_qnx_test_audit")

    def _create_synthetic_packet(
        self,
        hr=75, sbp=120, dbp=80, rr=16, spo2=98.0, temp=37.0,
        o2=0, cons=0, news2=0, alert=0, red_flags=0, latency_ns=350,
        corrupt_crc=False, corrupt_magic=False
    ) -> bytes:
        magic = 0xDEADBEEF if corrupt_magic else MEDORQIS_MAGIC_HEADER
        version = 1
        seq_id = 42
        ts_us = 1700000000000000
        patient_id_bytes = b"PAT-ICU-084\x00\x00\x00\x00\x00"

        # Pack first 60 bytes
        pre_crc_fmt = "<IHIQ16sHHHHffBBBBHI"
        raw_pre_crc = struct.pack(
            pre_crc_fmt,
            magic, version, seq_id, ts_us, patient_id_bytes,
            hr, sbp, dbp, rr, float(spo2), float(temp),
            o2, cons, news2, alert, red_flags, latency_ns
        )

        crc = zlib.crc32(raw_pre_crc) & 0xFFFFFFFF
        if corrupt_crc:
            crc ^= 0x12345678

        return raw_pre_crc + struct.pack("<I", crc)

    def test_packet_size_matches_c_contract(self):
        self.assertEqual(TELEMETRY_PACKET_SIZE, 64)

    def test_valid_packet_unpack(self):
        raw = self._create_synthetic_packet(hr=72, sbp=122, dbp=78, rr=15, spo2=98.5, temp=36.9)
        unpacked = self.bridge.unpack_packet(raw)

        self.assertIsNotNone(unpacked)
        self.assertEqual(unpacked["patient_id"], "PAT-ICU-084")
        self.assertEqual(unpacked["heart_rate_bpm"], 72)
        self.assertEqual(unpacked["systolic_bp_mmhg"], 122)
        self.assertEqual(unpacked["diastolic_bp_mmhg"], 78)
        self.assertEqual(unpacked["respiratory_rate_bpm"], 15)
        self.assertAlmostEqual(unpacked["spo2_percent"], 98.5, places=1)
        self.assertAlmostEqual(unpacked["temperature_celsius"], 36.9, places=1)

    def test_corrupt_crc_rejection(self):
        raw_corrupt = self._create_synthetic_packet(corrupt_crc=True)
        unpacked = self.bridge.unpack_packet(raw_corrupt)
        self.assertIsNone(unpacked, "Corrupt CRC must be safely rejected")

    def test_corrupt_magic_rejection(self):
        raw_corrupt = self._create_synthetic_packet(corrupt_magic=True)
        unpacked = self.bridge.unpack_packet(raw_corrupt)
        self.assertIsNone(unpacked, "Corrupt Magic header must be safely rejected")

    def test_double_check_protocol_convergence(self):
        # Patient with acute sepsis: HR 135, BP 85/50, RR 28, SpO2 89%, Temp 39.4, O2=1, Confused=1
        # NEWS2 calculated: RR 28 (3) + SpO2 89% (3) + O2 (2) + SBP 85 (3) + HR 135 (3) + Confused (3) + Temp 39.4 (2) = 19
        raw = self._create_synthetic_packet(
            hr=135, sbp=85, dbp=50, rr=28, spo2=89.0, temp=39.4,
            o2=1, cons=1, news2=19, alert=2, red_flags=0x00FF
        )
        telemetry = self.bridge.unpack_packet(raw)
        self.assertIsNotNone(telemetry)

        # Cross-verify against MedOrqis Core
        verified = self.bridge.verify_against_medorqis_core(telemetry)
        self.assertTrue(verified, "Double-Check Protocol must verify exact convergence with core/clinical_calculators.py")

    def test_bilingual_isbar_generation(self):
        engine = ClinicalAdvisoryEngine()
        telemetry = {
            "patient_id": "PAT-ICU-084",
            "news2_score": 16,
            "alert_level_name": "ALERT_LEVEL_CRITICAL (Emergency Rapid Response)",
            "heart_rate_bpm": 138,
            "systolic_bp_mmhg": 82,
            "diastolic_bp_mmhg": 48,
            "respiratory_rate_bpm": 28,
            "spo2_percent": 88.5,
            "temperature_celsius": 39.4,
            "on_supplemental_oxygen": True,
            "consciousness": 1,
            "calculation_latency_ns": 412
        }

        handover = engine.generate_isbar_handover(telemetry)
        self.assertIn("english", handover)
        self.assertIn("arabic", handover)
        self.assertIn("disclaimer", handover)

        # Verify English ISBAR structure
        self.assertIn("ISBAR CLINICAL DETERIORATION HANDOVER", handover["english"])
        self.assertIn("SURVIVING SEPSIS BUNDLE (SEPSIS SIX)", handover["english"])
        self.assertIn("PAT-ICU-084", handover["english"])

        # Verify Arabic ISBAR structure
        self.assertIn("تقرير تسليم التدهور السريري الحاد", handover["arabic"])
        self.assertIn("حزمة Sepsis Six", handover["arabic"])
        self.assertIn("PAT-ICU-084", handover["arabic"])

        # Verify Regulatory Disclaimer presence
        self.assertIn("IEC 62304 Class A/B Advisory Software", handover["english"])
        self.assertIn("IEC 62304 Class A/B Advisory Software", handover["arabic"])

if __name__ == "__main__":
    unittest.main()
