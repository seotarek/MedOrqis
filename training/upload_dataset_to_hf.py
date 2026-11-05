#!/usr/bin/env python3
"""
MedOrqis Foundation Model — Hugging Face Dataset Publisher
Uploads the curated bilingual clinical instruction dataset to:
https://huggingface.co/datasets/seotarek/medorqis-clinical-instructions

Zero local model download footprint.
"""

import os
import sys
from huggingface_hub import HfApi, create_repo

def _load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k not in os.environ:
                        os.environ[k] = v

_load_env_file()
HF_TOKEN = os.getenv("HF_TOKEN", "")
if not HF_TOKEN:
    print("[ERROR] HF_TOKEN is not set. Please add it to your environment or .env file.")
    sys.exit(1)

REPO_ID = "seotarek/medorqis-clinical-instructions"
LOCAL_DATASET_FILE = "training/medorqis_clinical_instructions.jsonl"

DATASET_README_CARD = """---
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
"""

def upload_dataset():
    print("=" * 65)
    print(f"MEDORQIS DATASET PUBLISHER -> HUGGING FACE HUB")
    print(f"Target Dataset Repo: {REPO_ID}")
    print("=" * 65)
    
    if not os.path.exists(LOCAL_DATASET_FILE):
        print(f"[ERROR] Dataset file not found at: {LOCAL_DATASET_FILE}")
        sys.exit(1)
        
    api = HfApi(token=HF_TOKEN)
    
    # 1. Create dataset repository if it doesn't exist
    try:
        print("[1/3] Ensuring repository exists...")
        create_repo(
            repo_id=REPO_ID,
            repo_type="dataset",
            private=False,
            token=HF_TOKEN,
            exist_ok=True
        )
        print(f"[SUCCESS] Repository confirmed: https://huggingface.co/datasets/{REPO_ID}")
    except Exception as e:
        print(f"[NOTE] create_repo notice: {e}")

    # 2. Upload JSONL dataset
    print(f"[2/3] Uploading {LOCAL_DATASET_FILE}...")
    api.upload_file(
        path_or_fileobj=LOCAL_DATASET_FILE,
        path_in_repo="train.jsonl",
        repo_id=REPO_ID,
        repo_type="dataset",
        token=HF_TOKEN
    )
    print("[SUCCESS] train.jsonl uploaded successfully.")

    # 3. Upload Dataset Card (README.md)
    print("[3/3] Uploading Dataset Card (README.md)...")
    readme_path = "training/DATASET_README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(DATASET_README_CARD)
        
    api.upload_file(
        path_or_fileobj=readme_path,
        path_in_repo="README.md",
        repo_id=REPO_ID,
        repo_type="dataset",
        token=HF_TOKEN
    )
    print("[SUCCESS] Dataset Card (README.md) uploaded successfully.")
    print("=" * 65)
    print(f"🎉 Dataset is LIVE at: https://huggingface.co/datasets/{REPO_ID}")
    print("=" * 65)

if __name__ == "__main__":
    upload_dataset()
