---
annotations_creators:
- expert-generated
- synthetic
language_creators:
- expert-generated
language:
- ar
- en
license: apache-2.0
multilinguality:
- bilingual
size_categories:
- n<1K
source_datasets:
- original
task_categories:
- text-generation
- question-answering
task_ids: []
pretty_name: MedOrqis Clinical Instructions & Tool Calling
tags:
- medical
- clinical-reasoning
- tool-calling
- function-calling
- arabic-medical
- cardiology
- nephrology
- pharmacology
- pediatrics
- emergency
- safety-guardrails
---

<div align="center">

# 🩺 MedOrqis Clinical Instructions & Tool-Calling Dataset
### The Official Synthetic Clinical SFT & Tool-Calling Dataset for MedOrqis Foundation Models
#### مجموعة بيانات التدريب السريري التوليدي واستدعاء الأدوات الحتمية لمنظومة MedOrqis

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Model](https://img.shields.io/badge/Model-MedOrqis--Hakim--6B-emerald.svg)](https://huggingface.co/seotarek/medorqis-hakim-6b)
[![GitHub](https://img.shields.io/badge/GitHub-seotarek%2FMedOrqis-black.svg)](https://github.com/seotarek/MedOrqis)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/seotarek/MedOrqis/blob/main/training/MedOrqis_Free_Training_Colab.ipynb)

</div>

---

## 📌 1. Dataset Summary

The **MedOrqis Clinical Instructions & Tool Calling Dataset** (`seotarek/medorqis-clinical-instructions`) is an expert-curated, bilingual (Arabic & English) clinical instruction dataset designed for Supervised Fine-Tuning (SFT) of medical language models (such as `MedOrqis-Hakim-6B` and `MedOrqis-Karnak-40B`).

Unlike standard conversational datasets, this dataset enforces **deterministic safety guardrails**: whenever a clinical inquiry involves mathematical scoring, clinical staging, weight-based pediatric dosing, or critical drug-drug interactions, the assistant is trained **NOT** to guess or hallucinate numbers, but to emit a native `<tool_call>` targeting one of MedOrqis's verified zero-token calculators.

---

## 🗂️ 2. Clinical Domains & Covered Scenarios

| Domain | Language | Primary Clinical Tool | Clinical Guideline Grounding | Key Clinical Objective |
| :--- | :--- | :--- | :--- | :--- |
| **Cardiology** | Arabic | `calculate_clinical_score` (`cha2ds2_va_esc2024`) | ESC 2024 AF Guidelines | Stroke risk calculation in Atrial Fibrillation without sex modifier. |
| **Nephrology** | English | `calculate_clinical_score` (`ckd_epi_2021_egfr`) | KDIGO 2024 / NKF-ASN 2021 | Race-free eGFR staging and dosing adjustments for diabetic nephropathy. |
| **Pharmacology** | Arabic | `check_drug_interactions` | MedOrqis DDI Rules | Severe fatal interaction between Warfarin (Marevan) and Diclofenac (Voltaren). |
| **Privacy / Ethics** | Ar / En | `scrub_phi` | HIPAA Safe Harbor 18 | Scrubbing Egyptian National ID, Saudi Iqama, and hospital identifiers. |
| **Pediatrics** | Arabic | `calculate_pediatric_weight_dose` | AAP Otitis Media Protocol | Weight-based Amoxicillin calculation (80 mg/kg/day) with adult dose ceiling. |
| **Pulmonology** | English | `calculate_clinical_score` (`wells_pe_score`) | BTS / Wells 2001 Criteria | Stratifying pre-test probability of pulmonary embolism post-surgery. |
| **Emergency Medicine** | Arabic | `calculate_clinical_score` (`curb65_score`) | BTS CAP Guidelines | Community-acquired pneumonia severity and ICU admission evaluation. |
| **Dialect Translation** | Arabic (Egyptian) | `normalize_terminology` | SNOMED-CT / ICD-10 | Mapping Egyptian complaints ("كرشة نفس", "حرقان فم المعدة") to ACS workup. |
| **Emergency Red Flag** | Arabic | `check_red_flags` | Neurosurgical Protocols | Immediate detection of Cauda Equina Syndrome (CES) saddle anesthesia. |
| **Cardiology Pharmacology** | English | `check_drug_interactions` | ACC/AHA & FDA Black Box | Clopidogrel + Omeprazole CYP2C19 competitive bioactivation inhibition. |

---

## 📐 3. Data Format & Schema

The dataset is distributed in standard JSON Lines (`.jsonl`). Each row adheres to the standard ChatML multi-turn conversational schema with native function declarations:

```json
{
  "id": "medorqis-cardio-ar-001",
  "language": "ar",
  "domain": "cardiology",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "calculate_clinical_score",
        "description": "Calculates deterministic, guideline-grounded clinical scores...",
        "parameters": { ... }
      }
    }
  ],
  "messages": [
    {"role": "system", "content": "You are MedOrqis Clinical AI..."},
    {"role": "user", "content": "مريض يبلغ من العمر 68 عاماً تم تشخيصه حديثاً برجفان أذيني..."},
    {
      "role": "assistant",
      "content": "لتقييم خطورة الانصمام الخثاري...",
      "tool_calls": [
        {
          "type": "function",
          "function": {
            "name": "calculate_clinical_score",
            "arguments": {
              "calculator_id": "cha2ds2_va_esc2024",
              "parameters": { "age_years": 68, "hx_hypertension": true, ... }
            }
          }
        }
      ]
    },
    {
      "role": "tool",
      "name": "calculate_clinical_score",
      "content": "{\"calculator_id\": \"cha2ds2_va_esc2024\", \"score\": 3, \"risk_tier\": \"HIGH_RISK\"}"
    },
    {
      "role": "assistant",
      "content": "بناءً على التقييم السريري الدقيق والمعتمد..."
    }
  ]
}
```

---

## 💻 4. How to Load in Python

```python
from datasets import load_dataset

dataset = load_dataset("seotarek/medorqis-clinical-instructions", split="train")
print(f"Total instructions: {len(dataset)}")
print("Sample record:", dataset[0]["id"])
```

---

## 🛡️ 5. Governance & Medical Ethics

- **De-Identification**: Zero Real Patient PHI was used. All clinical cases are synthetically generated and grounded in published clinical guidelines (ESC, KDIGO, BTS, AAP).
- **License**: Apache 2.0.
- **Repository**: [https://github.com/seotarek/MedOrqis](https://github.com/seotarek/MedOrqis)
