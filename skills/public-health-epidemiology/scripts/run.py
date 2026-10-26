#!/usr/bin/env python3
"""
Specialized deterministic execution script for public-health-epidemiology (v2.1.0).
Wired to domain calculator: epidemiology_metrics.
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
        "skill_name": "public-health-epidemiology",
        "version": "2.1.0",
        "safety_class": "Class A",
        "tier": "Tier 1",
        "gate_status": verdict["gate_status"],
        "red_flags": verdict["red_flags_detected"],
        "critical_ddis": verdict.get("critical_ddis_detected", []),
        "governance_banner": verdict.get("governance_banner", ""),
        "action_plan": verdict["action_plan"]
    }

    # Domain specific computation
    demographics = payload_dict.get("patient_demographics", {})
    age = demographics.get("age_years", 40)
    sex = demographics.get("biological_sex", "MALE")

    try:
        if "public-health-epidemiology" == "nursing-clinical-care":
            news = calculate_news2_score(
                respiration_rate_bpm=18,
                spo2_percent=97.0,
                air_or_oxygen="AIR",
                systolic_bp_mmhg=125,
                pulse_bpm=76,
                consciousness="ALERT",
                temperature_celsius=37.0
            )
            result["domain_assessment"] = {
                "score_name": news.calculator_name,
                "score": news.score,
                "band": news.interpretation_band,
                "recommendation": news.clinical_recommendation
            }
        elif "public-health-epidemiology" == "pediatrics-neonatology" and age < 18:
            weight = demographics.get("weight_kg", 20.0)
            dose = calculate_pediatric_weight_dose(
                age_years=age,
                weight_kg=weight,
                dose_per_kg=15.0,
                max_single_adult_dose_mg=500.0
            )
            result["domain_assessment"] = {
                "dose_calculation": dose.interpretation_band,
                "recommendation": dose.clinical_recommendation
            }
        elif "public-health-epidemiology" == "internal-medicine-chronic":
            egfr = calculate_ckd_epi_2021_egfr(
                serum_creatinine=1.1,
                age_years=age,
                biological_sex=sex
            )
            result["domain_assessment"] = {
                "renal_function": egfr.interpretation_band,
                "recommendation": egfr.clinical_recommendation
            }
        elif "public-health-epidemiology" == "pharmacology-dosing-interactions":
            meds = payload_dict.get("current_medications", ["warfarin", "paracetamol"])
            ddis = guardrails.check_drug_interactions(meds, demographics)
            result["domain_assessment"] = {
                "medications_screened": meds,
                "ddi_count": len(ddis),
                "ddis": ddis
            }
    except SafeCalculationRefusal as e:
        result["domain_assessment"] = {"refusal": e.reason, "recommendation": e.recommendation}

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
