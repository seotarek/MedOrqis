#!/usr/bin/env python3
"""
MedOrqis Model Context Protocol (MCP) Server (v2.1.0)
Standardized JSON-RPC 2.0 stdio server exposing deterministic clinical calculators,
safety guardrails, critical DDI checks, evidence verification, and PHI scrubbing.
"""

import sys
import os
import json
import traceback

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.clinical_calculators import (
    calculate_cha2ds2_va_esc2024,
    calculate_cha2ds2_vasc_aha2023,
    calculate_ckd_epi_2021_egfr,
    calculate_bedside_schwartz_egfr,
    calculate_cockcroft_gault_crcl,
    calculate_pediatric_weight_dose,
    calculate_mosteller_bsa,
    calculate_has_bled_score,
    calculate_news2_score,
    calculate_curb65_score,
    calculate_wells_dvt_score,
    calculate_wells_pe_score,
    SafeCalculationRefusal
)
from core.safety_guardrails import SafetyGuardrailsEngine
from core.citation_validator import CitationValidator
from core.claim_entailment_verifier import ClaimEntailmentVerifier
from core.phi_deidentifier import PHIDeidentifier
from core.prompt_security_guard import PromptSecurityGuard
from core.terminology_normalizer import TerminologyNormalizer

TOOLS_REGISTRY = [
    {
        "name": "calculate_clinical_score",
        "description": "Calculates deterministic, guideline-grounded clinical scores (CHA2DS2-VA ESC 2024, CHA2DS2-VASc AHA 2023, CKD-EPI 2021 eGFR, Bedside Schwartz Pediatric eGFR, Cockcroft-Gault CrCl, Pediatric Dose Capping, Mosteller BSA, HAS-BLED, NEWS2, CURB-65, Wells DVT/PE).",
        "inputSchema": {
            "type": "object",
            "required": ["calculator_id", "params"],
            "additionalProperties": False,
            "properties": {
                "calculator_id": {
                    "type": "string",
                    "enum": [
                        "cha2ds2_va_esc2024",
                        "cha2ds2_vasc_aha2023",
                        "ckd_epi_2021_egfr",
                        "bedside_schwartz_egfr",
                        "cockcroft_gault_crcl",
                        "pediatric_dose_calculator",
                        "mosteller_bsa",
                        "has_bled_score",
                        "news2_score",
                        "curb65_score",
                        "wells_dvt_score",
                        "wells_pe_score"
                    ]
                },
                "params": {"type": "object"}
            }
        }
    },
    {
        "name": "check_red_flags",
        "description": "Evaluates patient clinical context against multi-layered safety guardrails, detecting acute emergencies, critical DDIs, and inter-skill conflicts.",
        "inputSchema": {
            "type": "object",
            "required": ["envelope"],
            "additionalProperties": False,
            "properties": {
                "envelope": {"type": "object"}
            }
        }
    },
    {
        "name": "check_drug_interactions",
        "description": "Screens a list of patient medications for severe or fatal drug-drug interactions, normalizes regional trade names to INN, and flags contraindications.",
        "inputSchema": {
            "type": "object",
            "required": ["medications"],
            "additionalProperties": False,
            "properties": {
                "medications": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of medication trade names or INN generic names (e.g. ['concor', 'voltaren', 'warfarin'])"
                },
                "patient_demographics": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "age_years": {"type": "number"},
                        "biological_sex": {"type": "string"},
                        "pregnancy_status": {"type": "string"}
                    }
                }
            }
        }
    },
    {
        "name": "verify_evidence",
        "description": "Two-stage evidence verification: checks citation existence/authenticity and evaluates claim entailment with GRADE certainty.",
        "inputSchema": {
            "type": "object",
            "required": ["ref_id", "claim"],
            "additionalProperties": False,
            "properties": {
                "ref_id": {"type": "string"},
                "claim": {"type": "string"},
                "patient_age_years": {"type": "number"},
                "patient_is_pregnant": {"type": "boolean"}
            }
        }
    },
    {
        "name": "scrub_phi",
        "description": "De-identifies Protected Health Information (HIPAA 18, Egyptian NID, Saudi Iqama/NID, phone, MRN) from clinical narratives.",
        "inputSchema": {
            "type": "object",
            "required": ["text"],
            "additionalProperties": False,
            "properties": {
                "text": {"type": "string"}
            }
        }
    },
    {
        "name": "scan_prompt_security",
        "description": "Scans untrusted patient text or system prompts for prompt injection, jailbreak attempts, or clinical safety constraint overrides.",
        "inputSchema": {
            "type": "object",
            "required": ["text"],
            "additionalProperties": False,
            "properties": {
                "text": {"type": "string"}
            }
        }
    },
    {
        "name": "normalize_terminology",
        "description": "Maps regional trade brand names (e.g. Concor, Augmentin, Plavix, Voltaren) to international nonproprietary names (INN) and checks negation/unit fidelity.",
        "inputSchema": {
            "type": "object",
            "required": ["brand_name"],
            "additionalProperties": False,
            "properties": {
                "brand_name": {"type": "string"}
            }
        }
    }
]


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    try:
        if tool_name == "calculate_clinical_score":
            calc_id = arguments.get("calculator_id")
            p = arguments.get("params", {})

            if calc_id == "cha2ds2_va_esc2024":
                res = calculate_cha2ds2_va_esc2024(
                    age_years=p["age_years"],
                    hx_heart_failure=p.get("hx_heart_failure", False),
                    hx_hypertension=p.get("hx_hypertension", False),
                    hx_diabetes=p.get("hx_diabetes", False),
                    hx_stroke_tia_thromboembolism=p.get("hx_stroke_tia_thromboembolism", False),
                    hx_vascular_disease=p.get("hx_vascular_disease", False)
                )
            elif calc_id == "cha2ds2_vasc_aha2023":
                res = calculate_cha2ds2_vasc_aha2023(
                    age_years=p["age_years"],
                    biological_sex=p["biological_sex"],
                    hx_heart_failure=p.get("hx_heart_failure", False),
                    hx_hypertension=p.get("hx_hypertension", False),
                    hx_diabetes=p.get("hx_diabetes", False),
                    hx_stroke_tia_thromboembolism=p.get("hx_stroke_tia_thromboembolism", False),
                    hx_vascular_disease=p.get("hx_vascular_disease", False)
                )
            elif calc_id == "ckd_epi_2021_egfr":
                res = calculate_ckd_epi_2021_egfr(
                    serum_creatinine=p["serum_creatinine"],
                    age_years=p["age_years"],
                    biological_sex=p["biological_sex"],
                    unit=p.get("unit", "mg/dL")
                )
            elif calc_id == "bedside_schwartz_egfr":
                res = calculate_bedside_schwartz_egfr(
                    height_cm=p["height_cm"],
                    serum_creatinine_mg_dl=p["serum_creatinine_mg_dl"],
                    age_years=p["age_years"]
                )
            elif calc_id == "cockcroft_gault_crcl":
                res = calculate_cockcroft_gault_crcl(
                    serum_creatinine_mg_dl=p["serum_creatinine_mg_dl"],
                    age_years=p["age_years"],
                    actual_weight_kg=p["actual_weight_kg"],
                    biological_sex=p["biological_sex"],
                    height_cm=p.get("height_cm")
                )
            elif calc_id == "pediatric_dose_calculator":
                res = calculate_pediatric_weight_dose(
                    age_years=p["age_years"],
                    weight_kg=p["weight_kg"],
                    dose_per_kg=p["dose_per_kg"],
                    max_single_adult_dose_mg=p["max_single_adult_dose_mg"],
                    dose_unit=p.get("dose_unit", "mg")
                )
            elif calc_id == "mosteller_bsa":
                res = calculate_mosteller_bsa(
                    height_cm=p["height_cm"],
                    weight_kg=p["weight_kg"]
                )
            elif calc_id == "has_bled_score":
                res = calculate_has_bled_score(
                    hypertension_uncontrolled=p.get("hypertension_uncontrolled", False),
                    abnormal_renal_function=p.get("abnormal_renal_function", False),
                    abnormal_liver_function=p.get("abnormal_liver_function", False),
                    prior_stroke=p.get("prior_stroke", False),
                    bleeding_history_or_predisposition=p.get("bleeding_history_or_predisposition", False),
                    labile_inr=p.get("labile_inr", False),
                    elderly_age_gt_65=p.get("elderly_age_gt_65", False),
                    drugs_antiplatelet_or_nsaid=p.get("drugs_antiplatelet_or_nsaid", False),
                    alcohol_excess=p.get("alcohol_excess", False)
                )
            elif calc_id == "news2_score":
                res = calculate_news2_score(
                    respiration_rate_bpm=p["respiration_rate_bpm"],
                    spo2_percent=p["spo2_percent"],
                    air_or_oxygen=p.get("air_or_oxygen", "AIR"),
                    systolic_bp_mmhg=p["systolic_bp_mmhg"],
                    pulse_bpm=p["pulse_bpm"],
                    consciousness=p.get("consciousness", "ALERT"),
                    temperature_celsius=p["temperature_celsius"]
                )
            elif calc_id == "curb65_score":
                res = calculate_curb65_score(
                    confusion=p.get("confusion", False),
                    bun_mg_dl=p.get("bun_mg_dl"),
                    urea_mmol_l=p.get("urea_mmol_l"),
                    respiratory_rate_bpm=p.get("respiratory_rate_bpm"),
                    systolic_bp_mmhg=p.get("systolic_bp_mmhg"),
                    diastolic_bp_mmhg=p.get("diastolic_bp_mmhg"),
                    age_years=p["age_years"]
                )
            elif calc_id == "wells_dvt_score":
                res = calculate_wells_dvt_score(**p)
            elif calc_id == "wells_pe_score":
                res = calculate_wells_pe_score(**p)
            else:
                return {"error": f"Unknown calculator_id: '{calc_id}'"}

            return {
                "calculator_id": res.calculator_id,
                "score": res.score,
                "unit": res.unit,
                "interpretation_band": res.interpretation_band,
                "clinical_recommendation": res.clinical_recommendation,
                "guideline_citation": res.guideline_citation,
                "warnings": res.warnings
            }

        elif tool_name == "check_red_flags":
            engine = SafetyGuardrailsEngine()
            envelope = arguments.get("envelope", {})
            return engine.evaluate_safety(envelope)

        elif tool_name == "check_drug_interactions":
            engine = SafetyGuardrailsEngine()
            medications = arguments.get("medications", [])
            demographics = arguments.get("patient_demographics", {})
            interactions = engine.check_drug_interactions(medications, demographics)
            return {
                "medications_checked": medications,
                "interactions_found_count": len(interactions),
                "interactions": interactions
            }

        elif tool_name == "verify_evidence":
            ref_id = arguments.get("ref_id")
            claim = arguments.get("claim")
            age = arguments.get("patient_age_years")
            preg = arguments.get("patient_is_pregnant", False)

            c_val = CitationValidator()
            meta_res = c_val.validate_citation({"ref_id": ref_id})

            ent_ver = ClaimEntailmentVerifier()
            ent_res = ent_ver.verify_claim_entailment(
                claim_text=claim,
                ref_id=ref_id,
                patient_age_years=age,
                patient_is_pregnant=preg
            )

            return {
                "citation_metadata": meta_res,
                "claim_entailment": ent_res
            }

        elif tool_name == "scrub_phi":
            text = arguments.get("text", "")
            deid = PHIDeidentifier()
            scrubbed, report = deid.deidentify(text)
            return {
                "scrubbed_text": scrubbed,
                "audit_report": report
            }

        elif tool_name == "scan_prompt_security":
            text = arguments.get("text", "")
            guard = PromptSecurityGuard()
            safe, violations = guard.scan_prompt(text)
            return {
                "is_safe": safe,
                "violations": violations
            }

        elif tool_name == "normalize_terminology":
            brand = arguments.get("brand_name", "")
            norm = TerminologyNormalizer()
            return norm.normalize_brand_name(brand)

        else:
            return {"error": f"Unknown tool: '{tool_name}'"}

    except SafeCalculationRefusal as e:
        return {
            "status": "CALCULATION_REFUSED_SAFE_ABSTENTION",
            "reason": e.reason,
            "parameter": e.parameter,
            "recommendation": e.recommendation
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error_type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }


def run_stdio_server():
    """Reads JSON-RPC 2.0 lines from stdin and outputs responses to stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "medorqis-mcp-server", "version": "2.1.0"}
                }
            }
        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS_REGISTRY}
            }
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            output = handle_tool_call(tool_name, tool_args)
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(output, indent=2)}]
                }
            }
        else:
            res = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found."}
            }

        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_stdio_server()
