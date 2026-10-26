---
name: emergency-triage-redflags
description: >-
  High-urgency emergency triage and red-flag escalation gate. Evaluates ABCDE primary survey stability, screens for Sepsis, ACS, Acute Stroke, and Anaphylaxis, and executes immediate emergency redirection.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - emergency
    - red-flags
    - triage
    - abcde
    - chest-pain
    - stroke
    - anaphylaxis
    - trauma
    - طوارئ
    - علامات-خطيرة
---

# emergency-triage-redflags (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Identifies time-sensitive, life-threatening clinical emergencies and immediately halts non-emergency chat, directing patient to emergency care.

### Prohibited Uses
- Delaying emergency medical transfer
- Attempting outpatient management of unstable patients

## 2. Clinical Decision Checklist
1. Execute ABCDE Primary Survey: Airway patency, Breathing work, Circulation perfusion, Disability GCS, Exposure
2. Screen for time-sensitive emergencies: ACS, acute ischemic stroke (FAST), septic shock, anaphylaxis, tension pneumothorax
3. Filter out affirmed symptoms from negated ones (do not trigger on 'denies chest pain')
4. Execute immediate emergency redirection with local regional emergency contact numbers

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`emergency`, `red-flags`, `triage`, `abcde`, `chest-pain`, `stroke`, `anaphylaxis`, `trauma`, `طوارئ`, `علامات-خطيرة`

## 4. Mandatory Input Parameters
- `presenting_symptoms`
- `vital_signs`

## 5. Deterministic Safety Dependencies
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
  npx skills add seotarek/MedOrqis --skill emergency-triage-redflags
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/emergency-triage-redflags/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: Manchester Triage System / Emergency Severity Index (ESI) / Surviving Sepsis 2021 / AHA ACLS
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
