---
name: oncology-palliative-care
description: >-
  Oncology emergencies and palliative symptom management skill. Screens for febrile neutropenia, spinal cord compression, tumor lysis syndrome, and guides opioid titration and breakthrough pain control.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - oncology
    - palliative-care
    - febrile-neutropenia
    - pain-management
    - opioid-conversion
    - tumor-lysis
    - أورام
    - رعاية-تلطيفية
---

# oncology-palliative-care (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Identifies oncologic emergencies requiring immediate hospital admission and provides structured palliative symptom algorithms.

### Prohibited Uses
- Delaying broad-spectrum antibiotics in suspected neutropenic fever
- Calculating cytotoxic chemotherapy doses without oncologist sign-off

## 2. Clinical Decision Checklist
1. Screen for Febrile Neutropenia (fever >= 38.3°C with ANC < 500/uL): mandates empiric IV antipseudomonal within 1 hour
2. Detect acute spinal cord compression in metastatic cancer patients (urgent MRI + high-dose dexamethasone)
3. Calculate equianalgesic opioid conversions (morphine milligram equivalents) to prevent accidental overdose
4. Screen for acute Tumor Lysis Syndrome following cytotoxic chemotherapy initiation

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`oncology`, `palliative-care`, `febrile-neutropenia`, `pain-management`, `opioid-conversion`, `tumor-lysis`, `أورام`, `رعاية-تلطيفية`

## 4. Mandatory Input Parameters
- `cancer_type`
- `current_treatment`
- `symptoms`

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
  npx skills add seotarek/MedOrqis --skill oncology-palliative-care
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/oncology-palliative-care/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: ASCO / NCCN Clinical Practice Guidelines / ESMO Palliative Care Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
