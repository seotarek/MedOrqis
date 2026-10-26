#!/usr/bin/env python3
"""
Specialized deterministic execution script for emergency-triage-redflags (v2.1.0).
Wired to domain calculator: emergency_triage_evaluation.
"""

import sys
import json
import os

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from core.context_validator import validate_treatment_readiness, ProvenanceViolationError
from core.safety_guardrails import SafetyGuardrailsEngine
from core.clinical_calculators import (
    calculate_cha2ds2_va_esc2024,
    calculate_ckd_epi_2021_egfr,
    calculate_bedside_schwartz_egfr,
    calculate_cockcroft_gault_crcl,
    calculate_pediatric_weight_dose,
    calculate_news2_score,
    calculate_has_bled_score,
    calculate_curb65_score,
    calculate_wells_dvt_score,
    SafeCalculationRefusal
)


def run_skill(payload_dict):
    guardrails = SafetyGuardrailsEngine()
    verdict = guardrails.evaluate_safety(payload_dict)

    result = {
        "skill_name": "emergency-triage-redflags",
        "version": "2.1.0",
        "safety_class": "Class C",
        "tier": "Tier 3",
        "gate_status": verdict["gate_status"],
        "red_flags": verdict["red_flags_detected"],
        "critical_ddis": verdict.get("critical_ddis_detected", []),
        "governance_banner": verdict.get("governance_banner", ""),
        "action_plan": verdict["action_plan"]
    }

    # Domain specific computation: ABCDE Primary Survey & Emergency Triage Level
    vitals = payload_dict.get("vital_signs", {})
    demographics = payload_dict.get("patient_demographics", {})
    age = demographics.get("age_years")
    sex = demographics.get("biological_sex", "MALE")

    try:
        # 1. ABCDE Primary Survey Analysis
        abcde_status = {
            "airway": "PATENT",
            "breathing": "NORMAL",
            "circulation": "STABLE",
            "disability": "ALERT",
            "exposure": "NORMAL"
        }
        
        # Airway check
        patient_symptoms = [str(p.get("value", "")).lower() for p in payload_dict.get("provenance_items", [])]
        patient_symptoms += [str(s).lower() for s in payload_dict.get("presenting_symptoms", [])]
        
        if any("stridor" in s or "airway_swelling" in s or "airway" in s for s in patient_symptoms):
            abcde_status["airway"] = "COMPROMISED_CRITICAL"
            
        # Breathing vitals
        rr = vitals.get("respiratory_rate_bpm")
        spo2 = vitals.get("spo2_percent")
        if (rr is not None and (rr > 30 or rr < 8)) or (spo2 is not None and spo2 < 90):
            abcde_status["breathing"] = "SEVERE_DISTRESS"
        elif (rr is not None and rr > 24) or (spo2 is not None and spo2 < 94):
            abcde_status["breathing"] = "MODERATE_DISTRESS"

        # Circulation vitals
        sbp = vitals.get("systolic_bp_mmhg")
        hr = vitals.get("heart_rate_bpm") or vitals.get("pulse_bpm")
        if (sbp is not None and sbp < 90) or (hr is not None and (hr > 130 or hr < 40)):
            abcde_status["circulation"] = "HEMODYNAMICALLY_UNSTABLE"
        elif (sbp is not None and sbp < 100) or (hr is not None and hr > 100):
            abcde_status["circulation"] = "BORDERLINE_TACHYCARDIA"

        # Disability
        gcs = vitals.get("gcs_score")
        if gcs is not None and gcs < 13:
            abcde_status["disability"] = "ALTERED_MENTAL_STATUS"

        # Determine Emergency Triage Acuity (Manchester / ESI equivalent)
        if verdict["gate_status"] == "SAFE_ABSTENTION_EMERGENCY_ESCALATION" or any(v.startswith("COMPROMISED") or v == "SEVERE_DISTRESS" or v == "HEMODYNAMICALLY_UNSTABLE" for v in abcde_status.values()):
            triage_acuity = "LEVEL_1_RESUSCITATION_IMMEDIATE"
            recommended_disposition = "Immediate trauma/resuscitation bay transfer with EMS alert."
        elif len(verdict["red_flags_detected"]) > 0 or any(v in ["MODERATE_DISTRESS", "BORDERLINE_TACHYCARDIA", "ALTERED_MENTAL_STATUS"] for v in abcde_status.values()):
            triage_acuity = "LEVEL_2_EMERGENT_VERY_URGENT"
            recommended_disposition = "Emergency department bed placement within 10-15 minutes."
        else:
            triage_acuity = "LEVEL_3_URGENT_OR_ROUTINE"
            recommended_disposition = "Standard outpatient or urgent care evaluation."

        result["domain_assessment"] = {
            "triage_scale": "Emergency Severity Index (ESI) / Manchester Triage System Compatible",
            "triage_acuity": triage_acuity,
            "abcde_primary_survey": abcde_status,
            "clinical_disposition": recommended_disposition,
            "red_flags_count": len(verdict["red_flags_detected"]),
            "emergency_escalation_required": verdict["action_plan"]["emergency_redirection_required"]
        }
    except Exception as e:
        result["domain_assessment"] = {"status": "ERROR_DURING_ASSESSMENT", "message": str(e)}


    return result


if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = {
            "envelope_id": "CLI-TEST-V2.1",
            "timestamp": "2026-10-26T12:00:00Z",
            "patient_demographics": {"age_years": 40, "biological_sex": "MALE", "weight_kg": 75},
            "provenance_items": [
                {"concept_key": "diagnosis", "value": "Essential Hypertension", "provenance_type": "DOCUMENTED_CLINICAL_RECORD"}
            ],
            "active_allergies": [],
            "current_medications": ["concor", "panadol"],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }

    res = run_skill(payload)
    print(json.dumps(res, indent=2))
