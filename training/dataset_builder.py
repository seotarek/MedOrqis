#!/usr/bin/env python3
"""
MedOrqis Foundation Model — Clinical Instruction & Tool-Calling Dataset Builder
Generates bilingual (Arabic & English) clinical instruction datasets formatted for SFT
compatible with Karnak-40B / Karnak-6B / Qwen ChatML native <tool_call> schemas.

Zero local model download footprint: output is a compact JSONL file uploaded directly
to Hugging Face Datasets (seotarek/medorqis-clinical-instructions).
"""

import json
import os
from typing import List, Dict, Any

CLINICAL_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculate_clinical_score",
            "description": "Calculates deterministic, guideline-grounded clinical scores (CHA2DS2-VA ESC 2024, CKD-EPI 2021 eGFR, Bedside Schwartz, Cockcroft-Gault CrCl, NEWS2, CURB-65, HAS-BLED, Wells DVT/PE).",
            "parameters": {
                "type": "object",
                "properties": {
                    "calculator_id": {
                        "type": "string",
                        "enum": [
                            "cha2ds2_va_esc2024",
                            "cha2ds2_vasc_aha2023",
                            "ckd_epi_2021_egfr",
                            "bedside_schwartz_egfr",
                            "cockcroft_gault_crcl",
                            "has_bled_score",
                            "news2_score",
                            "curb65_score",
                            "wells_dvt_score",
                            "wells_pe_score"
                        ]
                    },
                    "parameters": {"type": "object"}
                },
                "required": ["calculator_id", "parameters"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_pediatric_weight_dose",
            "description": "Calculates safe pediatric weight-based drug doses with strict physiological plausibility validation and mandatory adult maximum dose capping (Zero Overdose Policy).",
            "parameters": {
                "type": "object",
                "properties": {
                    "age_years": {"type": "number", "description": "Patient age in years (0-18)."},
                    "weight_kg": {"type": "number", "description": "Patient weight in kilograms."},
                    "dose_per_kg": {"type": "number", "description": "Recommended dose per kg."},
                    "max_single_adult_dose_mg": {"type": "number", "description": "Absolute ceiling maximum single dose in mg."},
                    "dose_unit": {"type": "string", "default": "mg"}
                },
                "required": ["age_years", "weight_kg", "dose_per_kg", "max_single_adult_dose_mg"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_drug_interactions",
            "description": "Screens patient medications for severe or fatal drug-drug interactions, normalizes regional trade names to INN, and flags contraindications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "medications": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of brand or generic drug names."
                    }
                },
                "required": ["medications"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrub_phi",
            "description": "De-identifies Protected Health Information (HIPAA 18, Egyptian NID, Saudi Iqama, phone, MRN) from clinical narratives.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Raw clinical note containing potential PHI."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_red_flags",
            "description": "Evaluates patient clinical presentation against multi-layered safety guardrails, detecting acute emergencies and safety escalations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "findings": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of observed symptoms, exam findings, or red flag complaints."
                    }
                },
                "required": ["findings"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "normalize_terminology",
            "description": "Maps regional trade brand names (e.g. Concor, Augmentin, Plavix, Voltaren) or regional colloquial complaints to standard clinical terminology (INN, SNOMED-CT, ICD-10).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Trade brand name, colloquial medical phrase, or clinical term."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_evidence",
            "description": "Two-stage evidence verification: checks citation existence/authenticity and evaluates claim entailment with GRADE certainty.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ref_id": {"type": "string", "description": "Clinical guideline identifier (e.g. ESC_2024_AF, KDIGO_2024_CKD)."},
                    "claim": {"type": "string", "description": "Clinical claim to verify."}
                },
                "required": ["ref_id", "claim"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are MedOrqis Clinical AI, an expert bilingual (Arabic & English) clinical decision intelligence system.
You provide evidence-grounded clinical analysis following international guidelines (ESC 2024, KDIGO 2024, NICE, GOLD 2024, BTS).
CRITICAL RULE: Never calculate mathematical clinical risk scores, drug dosages, or drug-drug interactions using probabilistic guessing. Always invoke MedOrqis deterministic tools for calculation and safety guardrails."""


def get_curated_training_records() -> List[Dict[str, Any]]:
    """Generates foundational clinical training pairs formatted for Karnak/Qwen ChatML."""
    records = []

    # 1. Arabic Clinical Scenario - Cardiology CHA2DS2-VA (ESC 2024)
    records.append({
        "id": "medorqis-cardio-ar-001",
        "language": "ar",
        "domain": "cardiology",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "مريض يبلغ من العمر 68 عاماً تم تشخيصه حديثاً برجفان أذيني غير صمام (Non-valvular Atrial Fibrillation). التاريخ المرضي: ارتفاع ضغط الدم (Hypertension) وتصلب شرايين محيطية (Vascular disease). لا يوجد تاريخ لفشل عضلة القلب أو جلطة دماغية سابقة، وسكر الدم طبيعي. كيف نقيم خطورة الانصمام الخثاري وما هي التوصية بخصوص مضادات التخثر طبقاً لـ ESC 2024؟"},
            {
                "role": "assistant",
                "content": "لتقييم خطورة الانصمام الخثاري وتحديد الحاجة إلى مضادات التخثر الفموية (OAC) وفقاً لأحدث إرشادات الجمعية الأوروبية لأمراض القلب ESC 2024، يجب استخدام حاسبة CHA2DS2-VA الحتمية لتفادي أخطاء الحساب الذهني.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate_clinical_score",
                            "arguments": {
                                "calculator_id": "cha2ds2_va_esc2024",
                                "parameters": {
                                    "age_years": 68,
                                    "hx_hypertension": True,
                                    "hx_diabetes": False,
                                    "hx_stroke_tia_thromboembolism": False,
                                    "hx_vascular_disease": True,
                                    "hx_heart_failure": False
                                }
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "calculate_clinical_score",
                "content": json.dumps({
                    "calculator_id": "cha2ds2_va_esc2024",
                    "score": 3,
                    "risk_tier": "HIGH_RISK",
                    "recommendation": "Class I, Level A: Oral anticoagulation (DOAC preferred over VKA) is recommended for stroke prevention in patients with CHA2DS2-VA score >= 2.",
                    "epistemic_version": "ESC_2024_AF_GUIDELINES"
                })
            },
            {
                "role": "assistant",
                "content": """بناءً على التقييم السريري الدقيق والمعتمد:

1. **نتيجة تقييم CHA2DS2-VA (ESC 2024)**: تبلغ النتيجة **3 نقاط** (نقطة للعمر 68 سنة، نقطة لارتفاع ضغط الدم، ونقطة لمرض الأوعية الدموية المحيطية).
2. **مستوى الخطورة السريرية**: تصنيف عالي الخطورة (HIGH_RISK).
3. **التوصية العلاجية (Class I, Level A)**: يوصى ببدء العلاج بمضادات التخثر الفموية المباشرة (DOAC مثل Apixaban أو Rivaroxaban أو Dabigatran) كخيار أول مفضل على الوارفارين للوقاية من السكتة الدماغية الانصمامية، مع ضرورة تقييم خطورة النزيف وحساب وظائف الكلى (CrCl Cockcroft-Gault) قبل اختيار الجرعة المناسبة."""
            }
        ]
    })

    # 2. English Clinical Scenario - Nephrology CKD-EPI 2021
    records.append({
        "id": "medorqis-nephro-en-002",
        "language": "en",
        "domain": "nephrology",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "A 54-year-old female patient with long-standing type 2 diabetes presents for routine follow-up. Serum creatinine is 1.4 mg/dL. Please evaluate her renal function using the race-free CKD-EPI 2021 guideline equation and advise on staging."},
            {
                "role": "assistant",
                "content": "To accurately evaluate renal function without racial bias, I will calculate the estimated glomerular filtration rate (eGFR) using the race-free 2021 CKD-EPI equation via MedOrqis deterministic calculator.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate_clinical_score",
                            "arguments": {
                                "calculator_id": "ckd_epi_2021_egfr",
                                "parameters": {
                                    "serum_creatinine_mg_dl": 1.4,
                                    "age_years": 54,
                                    "sex": "female"
                                }
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "calculate_clinical_score",
                "content": json.dumps({
                    "calculator_id": "ckd_epi_2021_egfr",
                    "egfr_ml_min_per_1_73m2": 44.8,
                    "ckd_stage": "G3b (Moderate to Severe Reduction: 30-44)",
                    "guideline": "KDIGO 2024 / NKF-ASN 2021 Joint Task Force"
                })
            },
            {
                "role": "assistant",
                "content": """Based on the 2021 CKD-EPI equation:

- **eGFR**: **44.8 mL/min/1.73 m²**
- **KDIGO Staging**: **Stage G3b** (Moderately to severely decreased kidney function).

**Clinical Management Recommendations (KDIGO 2024)**:
1. **Medication Review**: Adjust dosages of renally cleared oral hypoglycemic agents (e.g. metformin dose reduction if eGFR 30-44; consider SGLT2 inhibitor nephroprotection if tolerated).
2. **Monitoring**: Recheck serum creatinine, electrolytes, and urine albumin-to-creatinine ratio (uACR) every 3 to 6 months.
3. **Cardiovascular & Nephrology Referral**: Refer to nephrology if rapid eGFR decline (>5 mL/min/1.73m²/year) or significant proteinuria is detected."""
            }
        ]
    })

    # 3. Arabic Pharmacology - Drug-Drug Interaction (DDI) & Trade Name Normalization
    records.append({
        "id": "medorqis-pharm-ar-003",
        "language": "ar",
        "domain": "pharmacology",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "مريض كبير في السن يتناول علاج Marevan (Warfarin) بانتظام لمشاكل قلبية، واشتكى من آلام مفصلية شديدة في الركبة فقام الطبيب بكتابة دواء Voltaren (Diclofenac) 75mg مرتين يومياً. هل هناك تعارض دوائي بين هذين الصنفين؟"},
            {
                "role": "assistant",
                "content": "سأقوم بفحص التداخلات الدوائية الخطرة بين Marevan و Voltaren عبر محرك السلامة الدوائية الحتمي في MedOrqis.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "check_drug_interactions",
                            "arguments": {
                                "medications": ["Marevan", "Voltaren"]
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "check_drug_interactions",
                "content": json.dumps({
                    "status": "CRITICAL_INTERACTION_DETECTED",
                    "severity": "FATAL_MAJOR",
                    "pair": ["Warfarin", "Diclofenac"],
                    "mechanism": "NSAIDs inhibit platelet aggregation and damage gastric mucosa while warfarin impairs clotting factor synthesis, synergistically multiplying gastrointestinal hemorrhage risk up to 3-5 fold.",
                    "clinical_action": "CONTRAINDICATED: Avoid co-administration. Substitute with topical analgesics or paracetamol."
                })
            },
            {
                "role": "assistant",
                "content": """⚠️ **تحذير سريري حرج: تعارض دوائي خطير جداً (Major/Contraindicated Interaction)**:

1. **طبيعة التعارض**: يحتوي **Voltaren** على مادة الديكلوفيناك (مضاد التهاب غير ستيرويدي NSAID)، بينما **Marevan** هو الوارفارين (مضاد تخثر فيتامين K).
2. **الآلية الخطرة**: الجمع بينهما يضاعف خطر حدوث **نزيف هضمي حاد وقاتل (Severe Gastrointestinal Bleeding)** بنسبة تصل إلى 3-5 أضعاف؛ حيث يثبط الديكلوفيناك تجمع الصفائح الدموية ويهيج بطانة المعدة بينما يعطل الوارفارين عوامل التخثر.
3. **التوصية الفورية**: **يجب إيقاف الفولتارين فوراً**. البديل الآمن لآلام المفاصل هو الباراسيتامول (Paracetamol) بجرعة محسوبة، أو العلاجات الموضعية (Topical Capsaicin)، مع قياس مستوى INR للمريض للتأكد من استقراره."""
            }
        ]
    })

    # 4. English & Arabic PHI De-identification - Patient Privacy Protection
    records.append({
        "id": "medorqis-phi-ar-en-004",
        "language": "ar-en",
        "domain": "privacy",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Please sanitize this clinical note before sending it to research: 'Patient Mahmoud Hassan, Egyptian NID 29501011234567, phone 01012345678, admitted to Qasr Al-Ainy hospital on Oct 14 with acute dyspnea.'"},
            {
                "role": "assistant",
                "content": "I will redact all Protected Health Information (HIPAA 18 identifiers, Egyptian National ID, and regional phone numbers) using MedOrqis deterministic PHI scrubber.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "scrub_phi",
                            "arguments": {
                                "text": "Patient Mahmoud Hassan, Egyptian NID 29501011234567, phone 01012345678, admitted to Qasr Al-Ainy hospital on Oct 14 with acute dyspnea."
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "scrub_phi",
                "content": json.dumps({
                    "status": "SCRUBBED",
                    "redacted_text": "Patient [NAME_REDACTED], Egyptian NID [NATIONAL_ID_REDACTED], phone [PHONE_REDACTED], admitted to [HOSPITAL_REDACTED] on [DATE_REDACTED] with acute dyspnea.",
                    "entities_removed": ["PATIENT_NAME", "NATIONAL_ID", "PHONE_NUMBER", "HOSPITAL_NAME", "DATE"]
                })
            },
            {
                "role": "assistant",
                "content": """Here is the anonymized, privacy-compliant clinical note ready for research:

> *"Patient [NAME_REDACTED], Egyptian NID [NATIONAL_ID_REDACTED], phone [PHONE_REDACTED], admitted to [HOSPITAL_REDACTED] on [DATE_REDACTED] with acute dyspnea."*

All personal identifiers (name, Egyptian NID, phone number, institutional site, and date) have been scrubbed in accordance with international healthcare privacy standards."""
            }
        ]
    })

    # 5. Arabic Pediatric Dose Calculation - Otitis Media Amoxicillin
    records.append({
        "id": "medorqis-peds-ar-005",
        "language": "ar",
        "domain": "pediatrics",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "طفل عمره 3 سنوات ووزنه 14 كجم، تم تشخيصه بالتهاب الأذن الوسطى الحاد (Acute Otitis Media). نريد وصف أموكسيسيلين بجرعة 80 مجم/كجم/يوم مقسمة على جرعتين. ما هي الجرعة الصحيحة لكل مرة مع التأكد من عدم تجاوز الحد الأقصى؟"},
            {
                "role": "assistant",
                "content": "لحساب الجرعة الدقيقة للطفل ومنع أي تجاوز للحدود الدوائية القصوى، سأستخدم حاسبة الجرعات الحسابية للأطفال في MedOrqis.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate_pediatric_weight_dose",
                            "arguments": {
                                "age_years": 3,
                                "weight_kg": 14.0,
                                "dose_per_kg": 40.0,
                                "max_single_adult_dose_mg": 1000.0,
                                "dose_unit": "mg"
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "calculate_pediatric_weight_dose",
                "content": json.dumps({
                    "age_years": 3,
                    "weight_kg": 14.0,
                    "calculated_single_dose_mg": 560.0,
                    "max_adult_single_dose_mg": 1000.0,
                    "capped": False,
                    "daily_total_mg": 1120.0,
                    "frequency": "Every 12 hours (BID)",
                    "guideline": "AAP 2023 Acute Otitis Media Dosing Protocol (80-90 mg/kg/day divided q12h)"
                })
            },
            {
                "role": "assistant",
                "content": """الحساب الدوائي الدقيق وفق بروتوكول الأكاديمية الأمريكية لطب الأطفال (AAP):

1. **الجرعة الواحدة**: **560 مجم** مرتين يومياً (كل 12 ساعة).
2. **الجرعة اليومية الإجمالية**: **1120 مجم/اليوم** (14 كجم × 80 مجم/كجم/يوم).
3. **التحقق من السلامة**: الجرعة المحسوبة لم تتجاوز الجرعة القصوى للبالغين (1000 مجم لكل جرعة)، وتعتبر آمنة ومطابقة لوزن الطفل.
4. **مدة العلاج**: 10 أيام للأطفال دون سن سنتين، أو 7-10 أيام للأطفال فوق سنتين مع التهاب أذن وسطى مؤكد."""
            }
        ]
    })

    # 6. English Pulmonology - Suspected Pulmonary Embolism (Wells PE Criteria)
    records.append({
        "id": "medorqis-pulmo-en-006",
        "language": "en",
        "domain": "pulmonology",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "A 62-year-old male who underwent total hip replacement 2 weeks ago presents to the emergency department with sudden-onset pleuritic chest pain and shortness of breath. Heart rate is 112 bpm. No clinical signs of DVT, no hemoptysis, no active malignancy. What is the pre-test probability of pulmonary embolism using the Wells criteria and the diagnostic next step?"},
            {
                "role": "assistant",
                "content": "I will evaluate the pre-test probability of pulmonary embolism using the deterministic Wells PE score calculator.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate_clinical_score",
                            "arguments": {
                                "calculator_id": "wells_pe_score",
                                "parameters": {
                                    "clinical_signs_symptoms_dvt": False,
                                    "pe_most_likely_or_equal_to_alt": True,
                                    "heart_rate_gt_100": True,
                                    "immobilization_or_surgery_past_4wks": True,
                                    "previous_pe_or_dvt": False,
                                    "hemoptysis": False,
                                    "active_malignancy": False
                                }
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "calculate_clinical_score",
                "content": json.dumps({
                    "calculator_id": "wells_pe_score",
                    "score": 6.0,
                    "interpretation_band": "Wells PE Score 6.0: PE Likely (2-tier)",
                    "clinical_recommendation": "PE Likely: Proceed immediately to CT Pulmonary Angiography (CTPA). Consider therapeutic anticoagulation while awaiting imaging if no bleeding contraindications."
                })
            },
            {
                "role": "assistant",
                "content": """**Wells Criteria Clinical Stratification**:

- **Calculated Score**: **6.0 points** (PE most likely diagnosis: 3.0, Tachycardia >100 bpm: 1.5, Recent major surgery within 4 weeks: 1.5).
- **Classification**: **PE Likely** (Threshold > 4.0 in 2-tier model).

**Diagnostic & Management Protocol (ESC / BTS Guidelines)**:
1. **Immediate Imaging**: Proceed directly to **CT Pulmonary Angiography (CTPA)**. Do *not* delay imaging for a D-dimer test, as a negative D-dimer cannot safely rule out PE in patients with high pre-test probability.
2. **Empiric Anticoagulation**: Initiate parenteral anticoagulation (e.g., therapeutic LMWH or Fondaparinux) immediately while awaiting CTPA confirmation, unless severe active bleeding or contraindications are present."""
            }
        ]
    })

    # 7. Arabic Emergency - Pneumonia CURB-65 Severity Score
    records.append({
        "id": "medorqis-er-ar-007",
        "language": "ar",
        "domain": "emergency",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "مريض عمره 72 عاماً وصل قسم الطوارئ بسعال منتج وبلغم صديدي وحمى. عند الفحص: واعي تماماً ولا يوجد تشوش ذهني، معدل التنفس 34 نفس/دقيقة، ضغط الدم 85/55 مم زئبق، وتحليل اليوريا في الدم (BUN) يبلغ 28 مجم/ديسيلتر. احسب درجة CURB-65 وحدد هل يحتاج تنويم بالمستشفى أم بالعناية المركزة؟"},
            {
                "role": "assistant",
                "content": "سأقوم بحساب درجة شدة الالتهاب الرئوي المكتسب من المجتمع (CURB-65) حتمياً لتحديد خطة التنويم الآمنة.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "calculate_clinical_score",
                            "arguments": {
                                "calculator_id": "curb65_score",
                                "parameters": {
                                    "confusion": False,
                                    "bun_mg_dl": 28.0,
                                    "respiratory_rate_bpm": 34,
                                    "systolic_bp_mmhg": 85,
                                    "diastolic_bp_mmhg": 55,
                                    "age_years": 72
                                }
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "calculate_clinical_score",
                "content": json.dumps({
                    "calculator_id": "curb65_score",
                    "score": 4,
                    "interpretation_band": "CURB-65 Score 4: High Risk (Severe CAP)",
                    "mortality_estimate": "22.2% - 27.8%",
                    "clinical_recommendation": "Urgent hospital admission required; urgently evaluate for Intensive Care Unit (ICU) admission."
                })
            },
            {
                "role": "assistant",
                "content": """**تقييم شدة الالتهاب الرئوي (CURB-65 BTS Guidelines)**:

1. **النتيجة المحسوبة**: **4 نقاط** من أصل 5:
   - ارتفاع اليوريا (BUN 28 > 19 mg/dL): +1
   - تسرع التنفس (RR 34 >= 30 bpm): +1
   - هبوط ضغط الدم (SBP 85 < 90 أو DBP 55 <= 60): +1
   - العمر (72 >= 65 سنة): +1
2. **مستوى الخطورة**: **التهاب رئوي حاد عالي الخطورة (Severe CAP)** بنسبة وفيات متوقعة تتجاوز 22%.
3. **القرار السريري الفوري**:
   - **تنويم عاجل في المستشفى مع تقييم فوري للقبول في وحدة العناية المركزة (ICU)**.
   - البدء العاجل في إنعاش السوائل الوريدية لضبط ضغط الدم، وسحب مزرعة دم وبلغم، وبدء المضادات الحيوية الوريدية واسعة المجال خلال ساعة واحدة من الوصول."""
            }
        ]
    })

    # 8. Egyptian Dialect / Colloquial Symptoms Normalization - Acute Coronary Syndrome
    records.append({
        "id": "medorqis-dialect-ar-008",
        "language": "ar",
        "domain": "cardiology",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "المريض جاي بيقول: 'يا دكتور حاسس بحرقان وتقل ف فم معدتي بيسمع ف كتفي الشمال ورقبتي، ومعاه كرشة نفس وعرق ساقع بقاله ساعتين ومش راضي يروح'. كيف تترجم هذه الشكوى بالمعايير الطبية وما هو الإجراء الطارئ؟"},
            {
                "role": "assistant",
                "content": "سأقوم بترجمة المصطلحات العامية وتنميطها طبياً وفق معاجم MedOrqis للتأكد من العلامات التحذيرية الحمراء.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "normalize_terminology",
                            "arguments": {
                                "query": "حرقان وتقل ف فم معدتي بيسمع ف كتفي الشمال وكرشة نفس وعرق ساقع"
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "normalize_terminology",
                "content": json.dumps({
                    "original_text": "حرقان وتقل ف فم معدتي بيسمع ف كتفي الشمال وكرشة نفس وعرق ساقع",
                    "mapped_entities": [
                        {"colloquial": "تقل ف فم معدتي", "clinical_term": "Epigastric pressure / Retrosternal chest discomfort", "icd10": "R07.9"},
                        {"colloquial": "بيسمع ف كتفي الشمال ورقبتي", "clinical_term": "Radiation to left shoulder and neck", "snomed_ct": "260413007"},
                        {"colloquial": "كرشة نفس", "clinical_term": "Acute dyspnea / Shortness of breath", "icd10": "R06.0"},
                        {"colloquial": "عرق ساقع", "clinical_term": "Diaphoresis / Cold sweats", "snomed_ct": "52613005"}
                    ],
                    "suspicion": "High suspicion for Acute Coronary Syndrome (ACS / STEMI / NSTEMI)"
                })
            },
            {
                "role": "assistant",
                "content": """🚨 **تنبيه طبي طارئ: اشتباه قوي جداً بمتلازمة الشريان التاجي الحادة (Acute Coronary Syndrome - ACS)**:

1. **الترجمة الطبية الدقيقة للشكوى العامية**:
   - **تقل وحرقان فم المعدة والكتف الأيسر**: ألم صدري خناقي وصفي مع تشعب للطرف العلوي والرقبة (Anginal retrosternal chest pain with left arm radiation).
   - **كرشة نفس**: ضيق تنفس حاد (Dyspnea).
   - **عرق ساقع**: تعرق غزير بردي (Diaphoresis)، وهو من أهم المؤشرات على فرط النشاط العصبي الودي المرافق لاحتشاء عضلة القلب.

2. **التصرف الفوري في قسم الطوارئ (خلال 10 دقائق)**:
   - رسم قلب فوري ذو 12 مسرى (12-Lead ECG) لنفي أو إثبات احتشاء عضلة القلب المصحوب بارتفاع قطاع ST (STEMI).
   - قياس تروبونين عالي الحساسية (High-Sensitivity Troponin).
   - إعطاء أسبرين للمضغ 300 مجم ما لم توجد موانع نزيف حادة.
   - تركيب خط وريدي وتوصيل المريض بجهاز المراقبة القلبية المستمرة."""
            }
        ]
    })

    # 9. Arabic Emergency Red Flag - Cauda Equina Syndrome
    records.append({
        "id": "medorqis-redflag-ar-009",
        "language": "ar",
        "domain": "emergency",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "مريضة تشتكي من ألم أسفل الظهر منذ شهر، ولكن منذ صباح اليوم لاحظت صعوبة شديدة في التبول مع سلس بولي وتنميل في منطقة المقعدة وبين الفخذين وضعف في الساقين. هل هذا يستدعي زيارة الطوارئ؟"},
            {
                "role": "assistant",
                "content": "هذه الأعراض تحمل مؤشرات خطر حرجة تستوجب فحص الرايات الحمراء (Red Flags) فوراً عبر محرك الأمان في MedOrqis.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "check_red_flags",
                            "arguments": {
                                "findings": [
                                    "Acute low back pain",
                                    "Saddle anesthesia / numbness between thighs",
                                    "Urinary retention / incontinence",
                                    "Bilateral lower limb weakness"
                                ]
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "check_red_flags",
                "content": json.dumps({
                    "status": "CRITICAL_RED_FLAG_TRIGGERED",
                    "syndrome": "Cauda Equina Syndrome (CES)",
                    "urgency": "NEUROSURGICAL_EMERGENCY",
                    "window": "Decompression within 24-48 hours to prevent permanent bladder/bowel paralysis"
                })
            },
            {
                "role": "assistant",
                "content": """🛑 **حالة طوارئ جراحية قصوى: اشتباه بمتلازمة ذنب الفرس (Cauda Equina Syndrome - CES)**:

1. **الخطورة**: ظهور **تنميل منطقة السرج (Saddle anesthesia)** مصحوباً بـ **سلس أو احتباس بولي وضعف في الساقين** يعني وجود انضغاط حاد وكبير على الحزمة العصبية أسفل الحبل الشوكي.
2. **الإجراء العاجل**:
   - **التوجه فوراً وبشكل طارئ إلى أقرب مستشفى به قسم جراحة مخ وأعصاب أو طوارئ جراحية**.
   - إجراء أشعة رنين مغناطيسي عاجلة للفقرات القطنية (Emergency Lumbar MRI).
   - قد تتطلب الحالة تدخلاً جراحياً لفك الضغط العصبي (Surgical Decompression) خلال أقل من 24-48 ساعة لتجنب فقدان التحكم البولي الحركي الدائم."""
            }
        ]
    })

    # 10. English Pharmacology - Clopidogrel and Omeprazole Interaction
    records.append({
        "id": "medorqis-pharm-en-010",
        "language": "en",
        "domain": "pharmacology",
        "tools": CLINICAL_TOOLS_SCHEMA,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "A patient post-PCI with a drug-eluting stent is taking Plavix (clopidogrel 75mg daily) and complains of dyspepsia. The physician considers starting Prilosec (omeprazole 20mg daily). Is this combination safe?"},
            {
                "role": "assistant",
                "content": "I will check for pharmacokinetic drug-drug interactions between Plavix and Prilosec using MedOrqis safety engine.",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "check_drug_interactions",
                            "arguments": {
                                "medications": ["Plavix", "Prilosec"]
                            }
                        }
                    }
                ]
            },
            {
                "role": "tool",
                "name": "check_drug_interactions",
                "content": json.dumps({
                    "status": "SIGNIFICANT_INTERACTION",
                    "severity": "MAJOR",
                    "pair": ["Clopidogrel", "Omeprazole"],
                    "mechanism": "Omeprazole is a potent CYP2C19 inhibitor that blocks the hepatic bioactivation of the prodrug clopidogrel into its active antiplatelet metabolite, increasing recurrent stent thrombosis and ischemic cardiovascular events.",
                    "clinical_action": "Avoid combination. Recommend Pantoprazole or Famotidine (H2 blocker) as gastroprotective alternatives."
                })
            },
            {
                "role": "assistant",
                "content": """⚠️ **Significant Clinical Warning: Drug Interaction (CYP2C19 Competitive Inhibition)**:

1. **Pharmacological Mechanism**: **Clopidogrel (Plavix)** is an inactive prodrug that requires activation by the hepatic enzyme **CYP2C19**. **Omeprazole (Prilosec)** significantly inhibits CYP2C19, cutting the production of clopidogrel's active antiplatelet metabolite by almost half, thereby significantly increasing the risk of **stent thrombosis and recurrent myocardial infarction**.
2. **FDA & ACC/AHA Guideline Recommendation**: Co-administration of omeprazole or esomeprazole with clopidogrel should be strictly avoided in patients with coronary stents.
3. **Safe Alternatives for Dyspepsia**:
   - **Pantoprazole (Protonix)**: Minimal CYP2C19 inhibitory potency and significantly safer with clopidogrel.
   - **Famotidine (Pepcid)**: An H2-receptor antagonist that does not interfere with clopidogrel activation."""
            }
        ]
    })

    return records


def build_and_export_dataset(output_path: str = "training/medorqis_clinical_instructions.jsonl"):
    """Builds and writes dataset in JSONL format."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    records = get_curated_training_records()
    
    with open(output_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"[DATASET BUILDER] Exported {len(records)} clinical instruction records to {output_path}")
    return output_path


if __name__ == "__main__":
    build_and_export_dataset()
