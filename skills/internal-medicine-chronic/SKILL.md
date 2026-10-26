---
name: internal-medicine-chronic
description: >-
  Internal medicine and chronic disease management skill. Evaluates multi-morbidity interactions across cardiology, endocrinology, nephrology, and pulmonology.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - internal-medicine
    - chronic-disease
    - diabetes
    - hypertension
    - ckd
    - copd
    - heart-failure
    - kdigo
    - باطنة
    - أمراض-مزمنة
---

# internal-medicine-chronic (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Provides guideline-concordant chronic care plans for diabetes, hypertension, heart failure, and CKD.

### Prohibited Uses
- Autonomous dose titration of insulin without patient SMBG log review

## 2. Clinical Decision Checklist
1. Calculate CHA2DS2-VA (ESC 2024) stroke risk for patients with atrial fibrillation
2. Calculate race-free CKD-EPI 2021 eGFR and assign KDIGO G/A staging
3. Reconcile multi-drug regimens for drug-disease contraindications (e.g. NSAIDs in CKD/HF)
4. Set individualized HbA1c and blood pressure targets according to patient frailty and life expectancy

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`internal-medicine`, `chronic-disease`, `diabetes`, `hypertension`, `ckd`, `copd`, `heart-failure`, `kdigo`, `باطنة`, `أمراض-مزمنة`

## 4. Mandatory Input Parameters
- `chronic_conditions`
- `current_medications`

## 5. Deterministic Safety Dependencies
- `core.clinical_calculators`
- `core.safety_guardrails`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill internal-medicine-chronic
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/internal-medicine-chronic/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: ADA Standards of Care in Diabetes 2024 / KDIGO CKD Guidelines / ESC Heart Failure Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
