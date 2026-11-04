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
        "title": "Deterministic Clinical Score Calculator",
        "description": (
            "Executes validated mathematical clinical calculators (CHA2DS2-VA ESC 2024, "
            "CHA2DS2-VASc AHA 2023, CKD-EPI 2021 race-free eGFR, Bedside Schwartz pediatric eGFR, "
            "Cockcroft-Gault CrCl, Mosteller BSA, HAS-BLED, NEWS2, CURB-65, Wells DVT/PE, "
            "pediatric weight-based dosing with adult capping) using deterministic formulas.\n\n"
            "When to use:\n"
            "- Use when exact, non-hallucinated clinical risk scores, renal staging, physiological "
            "index values, or pediatric dosage caps are required from patient parameters.\n\n"
            "When NOT to use:\n"
            "- Do NOT use for acute red-flag triage or multi-symptom emergency screening without "
            "structured parameters (use check_red_flags instead).\n"
            "- Do NOT use for drug-drug interaction or contraindication checks (use check_drug_interactions instead).\n"
            "- Do NOT use for mapping regional medication trade names (use normalize_terminology instead).\n\n"
            "Behavioral transparency:\n"
            "- Fully deterministic, air-gapped, zero-side-effect computation.\n"
            "- Enforces physiological safety bounds: values exceeding physiological limits trigger "
            "safe clinical abstention (CALCULATION_REFUSED_SAFE_ABSTENTION) rather than out-of-range output.\n"
            "- Operates strictly in memory; no patient parameters are persisted or transmitted externally."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": ["calculator_id", "params"],
            "additionalProperties": False,
            "properties": {
                "calculator_id": {
                    "type": "string",
                    "description": "Identifier of the target clinical calculation engine to execute.",
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
                "params": {
                    "type": "object",
                    "description": "Key-value clinical parameters, vital signs, laboratory values, and medical history booleans required for the specified calculator_id.",
                    "properties": {
                        "age_years": {"type": "number", "description": "Patient age in years (0-120). Required by most calculators."},
                        "biological_sex": {"type": "string", "enum": ["male", "female"], "description": "Patient biological sex for gender-specific physiological equations."},
                        "serum_creatinine": {"type": "number", "description": "Serum creatinine level for renal clearance and eGFR formulas."},
                        "serum_creatinine_mg_dl": {"type": "number", "description": "Serum creatinine concentration in mg/dL for Cockcroft-Gault or Schwartz formulas."},
                        "unit": {"type": "string", "enum": ["mg/dL", "umol/L"], "description": "Unit of measurement for serum creatinine (default: 'mg/dL')."},
                        "height_cm": {"type": "number", "description": "Patient height in centimeters (required for Mosteller BSA and Bedside Schwartz)."},
                        "actual_weight_kg": {"type": "number", "description": "Patient actual body weight in kilograms (required for Cockcroft-Gault CrCl)."},
                        "weight_kg": {"type": "number", "description": "Patient weight in kilograms for pediatric dose or BSA calculation."},
                        "dose_per_kg": {"type": "number", "description": "Target pediatric dose per kilogram (e.g. mg/kg)."},
                        "max_single_adult_dose_mg": {"type": "number", "description": "Maximum ceiling single adult dose in mg to prevent pediatric overdose."},
                        "dose_unit": {"type": "string", "description": "Unit of measurement for the dose (default: 'mg')."},
                        "hx_heart_failure": {"type": "boolean", "description": "History of congestive heart failure / LV dysfunction (+1 point)."},
                        "hx_hypertension": {"type": "boolean", "description": "History of hypertension or on antihypertensive therapy (+1 point)."},
                        "hx_diabetes": {"type": "boolean", "description": "History of diabetes mellitus (+1 point)."},
                        "hx_stroke_tia_thromboembolism": {"type": "boolean", "description": "History of stroke, TIA, or thromboembolism (+2 points)."},
                        "hx_vascular_disease": {"type": "boolean", "description": "History of prior MI, peripheral artery disease, or aortic plaque (+1 point)."},
                        "hypertension_uncontrolled": {"type": "boolean", "description": "Uncontrolled systolic BP >160 mmHg (+1 in HAS-BLED)."},
                        "respiratory_rate": {"type": "integer", "description": "Breaths per minute for NEWS2 (normal: 12-20) or CURB-65 (>=30 gives 1 point)."},
                        "oxygen_saturation": {"type": "integer", "description": "SpO2 percentage (NEWS2 scale 1: >=96% is 0 points)."},
                        "systolic_bp": {"type": "integer", "description": "Systolic blood pressure in mmHg."},
                        "pulse_rate": {"type": "integer", "description": "Heart rate in beats per minute."},
                        "temperature_celsius": {"type": "number", "description": "Body temperature in degrees Celsius."},
                        "consciousness_level": {"type": "string", "enum": ["Alert", "CVPU"], "description": "Consciousness level: Alert (0) vs Confused/Voice/Pain/Unresponsive (3)."},
                        "on_supplemental_oxygen": {"type": "boolean", "description": "Whether the patient is receiving supplemental oxygen (+2 points in NEWS2)."},
                        "confusion": {"type": "boolean", "description": "New mental confusion / AMTS <= 8 for CURB-65 (+1 point)."},
                        "blood_urea_nitrogen_mg_dl": {"type": "number", "description": "Blood urea nitrogen in mg/dL (CURB-65: BUN > 19 mg/dL gives 1 point)."},
                        "diastolic_bp": {"type": "integer", "description": "Diastolic blood pressure in mmHg (CURB-65: <= 60 gives 1 point)."}
                    }
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "description": "Calculated score payload containing the numeric result, guideline risk classification, recommendation, and any safety warnings.",
            "properties": {
                "calculator_id": {"type": "string", "description": "Unique identifier of the executed clinical calculator engine."},
                "score": {"type": ["number", "null"], "description": "Deterministic computed numerical score, clearance, or dose value."},
                "unit": {"type": "string", "description": "Unit of measurement for the computed score (e.g. 'points', 'mL/min/1.73m2', 'mg')."},
                "interpretation_band": {"type": "string", "description": "Evidence-grounded risk category, clinical stage, or severity interpretation."},
                "clinical_recommendation": {"type": "string", "description": "Actionable, guideline-concordant therapeutic or monitoring recommendation."},
                "guideline_citation": {"type": "string", "description": "Authoritative clinical practice guideline source citation (e.g. ESC 2024, AHA 2023, KDIGO 2021)."},
                "warnings": {"type": "array", "items": {"type": "string"}, "description": "Clinical cautionary notes, physiological boundary flags, or special population considerations."},
                "status": {"type": "string", "description": "Execution status ('CALCULATION_REFUSED_SAFE_ABSTENTION' if physiological inputs exceed safe limits)."},
                "reason": {"type": "string", "description": "Detailed explanation if calculation was safely refused due to out-of-bounds input."},
                "recommendation": {"type": "string", "description": "Clinical safety recommendation following safe calculation refusal."}
            }
        }
    },
    {
        "name": "check_red_flags",
        "title": "Patient Red Flags & Emergency Safety Checker",
        "description": (
            "Evaluates a patient clinical consultation envelope against multi-layered safety guardrails, "
            "detecting acute life-threatening emergencies, critical drug-drug interactions, inter-skill "
            "conflicts, and missing mandatory data.\n\n"
            "When to use:\n"
            "- Use when reviewing a clinical case or patient narrative to screen for acute red flags, "
            "emergency escalation triggers, cross-specialty contradictions, or missing critical data before forming clinical plans.\n\n"
            "When NOT to use:\n"
            "- Do NOT use for calculating specific numerical clinical risk scores like CHA2DS2-VA or eGFR (use calculate_clinical_score instead).\n"
            "- Do NOT use solely for isolated drug-drug interaction lists without patient context (use check_drug_interactions instead).\n"
            "- Do NOT use for sanitizing patient identifiers (use scrub_phi instead).\n\n"
            "Behavioral transparency:\n"
            "- Pure deterministic rule-based evaluation against codified clinical guidelines.\n"
            "- Non-destructive and idempotent; does not modify patient records or persist state.\n"
            "- Immediately signals SAFE_ABSTENTION_EMERGENCY_ESCALATION upon detecting acute life-threatening emergencies."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": ["envelope"],
            "additionalProperties": False,
            "properties": {
                "envelope": {
                    "type": "object",
                    "description": "Standardized clinical consultation envelope containing patient context, vital signs, lab observations, active medications, and proposed recommendations.",
                    "required": ["patient_id"],
                    "properties": {
                        "patient_id": {"type": "string", "description": "Unique anonymized patient identifier."},
                        "demographics": {
                            "type": "object",
                            "description": "Patient demographic parameters including age, biological sex, and pregnancy status.",
                            "properties": {
                                "age_years": {"type": "number", "description": "Patient age in years."},
                                "biological_sex": {"type": "string", "enum": ["male", "female"], "description": "Biological sex."},
                                "pregnancy_status": {"type": "string", "description": "Pregnancy trimester or confirmation status."}
                            }
                        },
                        "observations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of reported clinical symptoms, physical examination findings, or complaints."
                        },
                        "active_medications": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of current active prescription and over-the-counter medications."
                        },
                        "vital_signs": {
                            "type": "object",
                            "description": "Current physiological vital signs (heart rate, blood pressure, SpO2, respiratory rate, temperature)."
                        },
                        "proposed_plan": {
                            "type": "string",
                            "description": "Proposed therapeutic plan or clinical recommendation to be safety-screened."
                        }
                    }
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "description": "Comprehensive clinical safety verdict containing gate status, detected emergency red flags, drug interactions, missing data alerts, and immediate action plans.",
            "properties": {
                "verdict_id": {"type": "string", "description": "Unique cryptographic audit tracking identifier for the safety verdict."},
                "timestamp": {"type": "string", "description": "ISO 8601 execution timestamp of the safety check."},
                "gate_status": {"type": "string", "description": "Overall safety outcome: 'PASSED_PROCEED', 'SAFE_ABSTENTION_EMERGENCY_ESCALATION', or 'SAFE_ABSTENTION_DATA_DEFICIT'."},
                "red_flags_detected": {"type": "array", "items": {"type": "object"}, "description": "List of triggered acute red flags with severity and escalation targets."},
                "critical_ddis_detected": {"type": "array", "items": {"type": "object"}, "description": "List of severe or fatal drug-drug interactions detected across active medications."},
                "missing_mandatory_data": {"type": "array", "items": {"type": "string"}, "description": "Mandatory demographic or clinical data fields absent from the patient envelope."},
                "provenance_violations": {"type": "array", "items": {"type": "string"}, "description": "Data provenance boundary violations or unverified claims."},
                "inter_skill_conflicts": {"type": "array", "items": {"type": "object"}, "description": "Cross-specialty contradictory treatment plans (e.g. anticoagulation in active bleeding)."},
                "governance_banner": {"type": "string", "description": "Mandatory clinical governance advisory banner."},
                "action_plan": {
                    "type": "object",
                    "description": "Structured immediate management plan with patient-safe wording and clinician summary.",
                    "properties": {
                        "user_safe_message": {"type": "string", "description": "Patient-facing guidance message in plain, safe language."},
                        "clinician_summary": {"type": "string", "description": "Technical clinical summary for attending healthcare providers."},
                        "emergency_redirection_required": {"type": "boolean", "description": "True if patient requires immediate emergency department transfer."},
                        "emergency_contacts": {"type": "array", "items": {"type": "string"}, "description": "Jurisdiction-specific emergency medical phone numbers."}
                    }
                }
            }
        }
    },
    {
        "name": "check_drug_interactions",
        "title": "Critical Drug-Drug Interaction Screener",
        "description": (
            "Screens a list of patient medications for severe, contraindicated, or fatal drug-drug "
            "interactions (DDIs), automatically normalizes regional trade brand names to INN generics, "
            "and verifies demographic contraindications (e.g., pregnancy, pediatric, geriatric).\n\n"
            "When to use:\n"
            "- Use when evaluating a patient's medication regimen or prescribing changes to detect potentially fatal interactions, QT prolongation, bleeding risks, or pregnancy contraindications.\n\n"
            "When NOT to use:\n"
            "- Do NOT use for comprehensive clinical triage with vitals and red flags (use check_red_flags instead).\n"
            "- Do NOT use solely for translating brand names without DDI screening (use normalize_terminology instead).\n"
            "- Do NOT use for calculating renal dose adjustments (use calculate_clinical_score instead).\n\n"
            "Behavioral transparency:\n"
            "- Fully deterministic rule engine grounded in pharmacological databases.\n"
            "- Read-only and stateless; does not store or transmit medication lists.\n"
            "- Regional trade names (e.g., Concor, Voltaren, Plavix) are automatically resolved to INN before screening."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": ["medications"],
            "additionalProperties": False,
            "properties": {
                "medications": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of medication trade brand names or INN generic names (e.g., ['Concor', 'Voltaren', 'Warfarin', 'Aspirin', 'Sildenafil'])."
                },
                "patient_demographics": {
                    "type": "object",
                    "description": "Optional patient demographic variables used to assess physiological contraindications (e.g., pregnancy, age-specific risks).",
                    "additionalProperties": False,
                    "properties": {
                        "age_years": {"type": "number", "description": "Patient age in years to assess pediatric or geriatric medication contraindications."},
                        "biological_sex": {"type": "string", "enum": ["male", "female"], "description": "Patient biological sex."},
                        "pregnancy_status": {"type": "string", "description": "Pregnancy confirmation status (e.g. 'PREGNANT', 'CONFIRMED_PREGNANT', 'first_trimester', 'not_pregnant')."}
                    }
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "description": "Report of screened medications, interaction count, and detailed descriptions of all detected critical interactions or contraindications.",
            "properties": {
                "medications_checked": {"type": "array", "items": {"type": "string"}, "description": "List of normalized medication identifiers that were evaluated."},
                "interactions_found_count": {"type": "integer", "description": "Total number of severe, contraindicated, or moderate interactions identified."},
                "interactions": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of detected interactions including severity level, clinical mechanism, immediate action, and safe therapeutic alternatives."
                }
            }
        }
    },
    {
        "name": "verify_evidence",
        "title": "Clinical Evidence & Claim Entailment Verifier",
        "description": (
            "Performs two-stage medical evidence verification: validates bibliographic citation existence "
            "and DOI authenticity, and verifies clinical claim entailment against authoritative guideline corpora "
            "with GRADE certainty scoring.\n\n"
            "When to use:\n"
            "- Use when verifying whether a clinical assertion, guideline claim, or medical citation is authentic, "
            "fully grounded, and free of medical hallucination.\n\n"
            "When NOT to use:\n"
            "- Do NOT use for executing mathematical clinical calculators (use calculate_clinical_score instead).\n"
            "- Do NOT use for checking patient acute emergency symptoms or vital signs (use check_red_flags instead).\n"
            "- Do NOT use for de-identifying clinical text (use scrub_phi instead).\n\n"
            "Behavioral transparency:\n"
            "- Deterministic verification engine executing offline cross-checks against verified guideline knowledge bases.\n"
            "- Pure read-only operation with zero state modification or network telemetry.\n"
            "- Evaluates population-specific constraints (e.g., pediatric exclusions, pregnancy contraindications)."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": ["ref_id", "claim"],
            "additionalProperties": False,
            "properties": {
                "ref_id": {
                    "type": "string",
                    "description": "Unique citation reference identifier from the guideline repository (e.g., 'ESC_2024_AF', 'KDIGO_2021', 'AHA_2023_HF')."
                },
                "claim": {
                    "type": "string",
                    "description": "The specific clinical claim, assertion, or recommendation to verify against the source guideline evidence."
                },
                "patient_age_years": {
                    "type": "number",
                    "description": "Optional patient age in years to evaluate age-dependent guideline scope and validity boundaries."
                },
                "patient_is_pregnant": {
                    "type": "boolean",
                    "description": "Optional boolean flag indicating pregnancy to evaluate pregnancy-specific guideline contraindications."
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "description": "Verification payload containing citation metadata validation and claim entailment certainty analysis.",
            "properties": {
                "citation_metadata": {
                    "type": "object",
                    "description": "Bibliographic validation result including DOI verification, publication details, and evidence grade."
                },
                "claim_entailment": {
                    "type": "object",
                    "description": "Claim entailment assessment including entailment status, confidence score, GRADE certainty, and boundary flags."
                }
            }
        }
    },
    {
        "name": "scrub_phi",
        "title": "Protected Health Information (PHI) De-identifier",
        "description": (
            "Scans clinical narratives and de-identifies Protected Health Information (PHI), masking "
            "HIPAA Safe Harbor 18 identifiers, Egyptian National IDs (14 digits), Saudi Iqama/National IDs "
            "(10 digits), Medical Record Numbers (MRN), phone numbers, and email addresses.\n\n"
            "When to use:\n"
            "- Use before logging, exporting, or passing clinical consultation transcripts, medical notes, "
            "or user dialogues to external models or public registries to guarantee patient privacy.\n\n"
            "When NOT to use:\n"
            "- Do NOT use for detecting adversarial prompt injections or security attacks (use scan_prompt_security instead).\n"
            "- Do NOT use for clinical risk scoring or vital sign assessment (use calculate_clinical_score or check_red_flags instead).\n"
            "- Do NOT use for normalizing medication brand names (use normalize_terminology instead).\n\n"
            "Behavioral transparency:\n"
            "- Pure text transformation running locally in memory using deterministic regex and checksum algorithms.\n"
            "- Read-only and stateless; neither the raw input text nor the scrubbed output is persisted to disk or logged.\n"
            "- Preserves clinical semantics and temporal relationships while replacing direct identifiers with standardized tokens."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": ["text"],
            "additionalProperties": False,
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Raw clinical text, patient consultation note, discharge summary, or dialogue containing potential PHI identifiers to redact."
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "description": "Sanitized text output and de-identification audit report detailing detected and redacted PHI categories.",
            "properties": {
                "scrubbed_text": {"type": "string", "description": "Privacy-sanitized narrative with all detected identifiers replaced with safe masking tokens."},
                "audit_report": {
                    "type": "object",
                    "description": "Detailed de-identification summary including count of detected entities and list of redacted identifier categories."
                }
            }
        }
    },
    {
        "name": "scan_prompt_security",
        "title": "Clinical Prompt Injection & Safety Guard",
        "description": (
            "Analyzes untrusted user inputs, clinical prompts, or external dialogue for adversarial attacks, "
            "prompt injections, system jailbreaks, role-play overrides, and clinical guardrail bypass attempts.\n\n"
            "When to use:\n"
            "- Use to sanitize and validate incoming text from patients, clinicians, or third-party integrations "
            "before feeding it into downstream LLM reasoning engines.\n\n"
            "When NOT to use:\n"
            "- Do NOT use for redacting personal patient identifiers or private data (use scrub_phi instead).\n"
            "- Do NOT use for screening clinical red-flag medical emergencies (use check_red_flags instead).\n"
            "- Do NOT use for verifying medical evidence or guideline claims (use verify_evidence instead).\n\n"
            "Behavioral transparency:\n"
            "- Fully deterministic regex and heuristic pattern inspection engine.\n"
            "- Completely isolated and stateless; does not execute untrusted code or store incoming text.\n"
            "- Rejection threshold halts execution when security risk patterns are confirmed."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": ["text"],
            "additionalProperties": False,
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Untrusted text string to scan for prompt injections, jailbreaks, system instruction leaks, or clinical override exploits."
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "description": "Security assessment result indicating safety status and any detected threat or policy violation patterns.",
            "properties": {
                "is_safe": {"type": "boolean", "description": "True if the text contains zero detected prompt injection or jailbreak patterns; False if threats were flagged."},
                "violations": {"type": "array", "items": {"type": "string"}, "description": "List of specific security violation categories detected (e.g. 'PROMPT_INJECTION_DIRECT', 'JAILBREAK_ROLEPLAY')."}
            }
        }
    },
    {
        "name": "normalize_terminology",
        "title": "Regional Brand to INN Medical Terminology Normalizer",
        "description": (
            "Maps regional pharmaceutical trade brand names (e.g., Concor, Augmentin, Plavix, Voltaren, Panadol) "
            "to standardized International Nonproprietary Names (INN), resolves drug classes, and validates clinical negation status.\n\n"
            "When to use:\n"
            "- Use when converting patient-reported commercial trade drug names into standardized international generic names "
            "for downstream decision support or prescribing audits.\n\n"
            "When NOT to use:\n"
            "- Do NOT use for screening multi-drug interactions or contraindications (use check_drug_interactions instead).\n"
            "- Do NOT use for general clinical safety evaluation or red-flag triage (use check_red_flags instead).\n"
            "- Do NOT use for calculating clinical risk scores (use calculate_clinical_score instead).\n\n"
            "Behavioral transparency:\n"
            "- Deterministic, dictionary-grounded terminology mapping engine with zero external API dependencies.\n"
            "- Read-only and stateless; returns canonical INN, ATC classification, and regional availability without side effects."
        ),
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "required": ["brand_name"],
            "additionalProperties": False,
            "properties": {
                "brand_name": {
                    "type": "string",
                    "description": "Commercial pharmaceutical brand name to normalize (e.g., 'Concor', 'Augmentin', 'Plavix', 'Voltaren', 'Lantus')."
                }
            }
        },
        "outputSchema": {
            "type": "object",
            "description": "Standardized pharmacological entity payload including INN generic name, therapeutic class, ATC code, and regional market distribution.",
            "properties": {
                "brand_name": {"type": "string", "description": "Original brand name submitted for normalization."},
                "inn_generic_name": {"type": "string", "description": "Standardized International Nonproprietary Name (INN)."},
                "drug_class": {"type": "string", "description": "Primary pharmacological or therapeutic class (e.g. 'Beta-blocker', 'NSAID')."},
                "atc_code": {"type": "string", "description": "Anatomical Therapeutic Chemical (ATC) classification code."},
                "regional_availability": {"type": "array", "items": {"type": "string"}, "description": "List of geographical markets where this brand name is actively distributed."}
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
