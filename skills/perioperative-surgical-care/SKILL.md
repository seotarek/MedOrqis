---
name: perioperative-surgical-care
description: >-
  Perioperative surgical care and risk assessment skill. Calculates Revised Cardiac Risk Index (RCRI), manages pre-op anticoagulation interruption/bridging, and monitors for acute surgical abdomen.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - surgery
    - perioperative
    - rcri
    - pre-op-clearance
    - anticoagulation-bridging
    - who-surgical-checklist
    - جراحة
    - تخدير
---

# perioperative-surgical-care (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Evaluates perioperative cardiac and pulmonary risk, guides antithrombotic timing around surgery, and assesses surgical emergencies.

### Prohibited Uses
- Permitting elective surgery in unstratified high-risk cardiac patients

## 2. Clinical Decision Checklist
1. Compute Revised Cardiac Risk Index (RCRI) score for major non-cardiac surgery
2. Calculate pre-test probability for venous thromboembolism via Wells DVT/PE scores
3. Plan antithrombotic interruption and bridging protocol based on procedural bleeding risk
4. Enforce WHO Surgical Safety Checklist checkpoints (Sign In, Time Out, Sign Out)

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`surgery`, `perioperative`, `rcri`, `pre-op-clearance`, `anticoagulation-bridging`, `who-surgical-checklist`, `جراحة`, `تخدير`

## 4. Mandatory Input Parameters
- `surgical_procedure`
- `patient_demographics`
- `cardiac_history`

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
  npx skills add seotarek/MedOrqis --skill perioperative-surgical-care
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/perioperative-surgical-care/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: 2024 AHA/ACC Perioperative Cardiovascular Evaluation Guidelines / ASA Physical Status
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
