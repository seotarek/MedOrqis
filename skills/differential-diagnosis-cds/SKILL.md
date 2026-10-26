---
name: differential-diagnosis-cds
description: >-
  Diagnostic decision support skill. Constructs structured VINDICATE differential diagnoses, highlights must-not-miss life-threatening conditions, and proposes prioritized diagnostic workups.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - differential-diagnosis
    - vindicate
    - clinical-decision-support
    - cds
    - symptom-checker
    - workup
    - تشخيص-تفريقي
---

# differential-diagnosis-cds (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Aids clinicians in expanding diagnostic breadth, preventing premature cognitive closure, and prioritizing testing.

### Prohibited Uses
- Autonomous definitive diagnosis
- Excluding emergency etiologies without objective testing

## 2. Clinical Decision Checklist
1. Categorize potential etiologies using the VINDICATE mnemonic
2. Highlight high-morbidity 'Must-Not-Miss' diagnoses at the top of differential
3. Order prioritized diagnostic tests by diagnostic yield and invasiveness
4. Check for cognitive biases (anchoring, premature closure, availability heuristic)

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`differential-diagnosis`, `vindicate`, `clinical-decision-support`, `cds`, `symptom-checker`, `workup`, `تشخيص-تفريقي`

## 4. Mandatory Input Parameters
- `presenting_symptoms`
- `patient_demographics`

## 5. Deterministic Safety Dependencies
- `core.context_validator`
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
  npx skills add seotarek/MedOrqis --skill differential-diagnosis-cds
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/differential-diagnosis-cds/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: Society to Improve Diagnosis in Medicine (SIDM) / BMJ Best Practice
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
