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
- safety-guardrails
---

# 🩺 MedOrqis Clinical Instructions & Tool Calling Dataset

The official foundational instruction-tuning and function-calling dataset for the **MedOrqis Medical Foundation Model** (`seotarek/medorqis-karnak-40b-lora`), built on top of `Applied-Innovation-Center/Karnak-40B-v1.0` and `Karnak-6B-v1.0`.

## 📌 Key Highlights

- **Bilingual (Arabic & English)**: Clinical scenarios encompassing Standard Medical Arabic, English, and regional dialect complaints (e.g., Egyptian colloquialisms).
- **Native Tool-Calling (<tool_call>)**: Formatted specifically for Karnak / Qwen ChatML tool schemas.
- **Deterministic Clinical Grounding**: Prompts the LLM to invoke deterministic zero-token calculators rather than guessing mathematical clinical risk scores:
  - `cha2ds2_va_esc2024` (ESC 2024 Atrial Fibrillation Stroke Risk)
  - `ckd_epi_2021_egfr` (KDIGO 2024 Race-Free Renal Equation)
  - `bedside_schwartz_egfr` (Pediatric eGFR)
  - `curb65_score` & `news2_score` (Infection & Acute Deterioration)
  - `wells_dvt_score` & `wells_pe_score` (Thromboembolism)
  - `pediatric_weight_dose` (Weight-based dosing)
  - `check_drug_interactions` (Severe / Fatal DDI detection)
  - `check_red_flags` (Emergency escalation & safety guardrails)
  - `scrub_phi` (HIPAA 18, Egyptian NID, Saudi Iqama anonymization)
  - `normalize_terminology` (Trade-to-INN and dialect mapping)

## 📊 Dataset Structure

Each JSONL record represents a conversational session with:
- `id`: Unique record identifier (e.g. `medorqis-cardio-ar-001`)
- `language`: `ar`, `en`, or `ar-en`
- `domain`: Medical domain (`cardiology`, `nephrology`, `pharmacology`, `pediatrics`, `emergency`, `privacy`)
- `tools`: Available tool declarations formatted in OpenAI/Qwen JSON Schema
- `messages`: Conversational messages formatted in ChatML (`system`, `user`, `assistant`, `tool`)

## 🛡️ License & Attribution

Licensed under Apache 2.0. Developed as part of the MedOrqis Medical AI Skills Ecosystem.
