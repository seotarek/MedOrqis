---
name: nursing-clinical-care
description: >-
  Inpatient nursing and bedside clinical care skill. Computes NEWS2 early warning scores, monitors pressure injury risks (Braden Scale), and formulates patient care plans.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - nursing
    - news2
    - braden-scale
    - vital-signs
    - wound-care
    - patient-safety
    - care-plan
    - تمريض
    - رعاية-سريرية
---

# nursing-clinical-care (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Supports bedside nursing assessments, vital sign trend tracking, and escalation protocols for deteriorating patients.

### Prohibited Uses
- Discontinuing nursing vital checks in high-risk patients

## 2. Clinical Decision Checklist
1. Compute National Early Warning Score 2 (NEWS2) from 6 physiological parameters
2. Trigger rapid response team escalation for NEWS2 score >= 5 or single parameter score of 3
3. Assess Braden Scale for pressure ulcer risk and mandate repositioning schedules
4. Verify fall risk precautions and maintain bedside safety barriers

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`nursing`, `news2`, `braden-scale`, `vital-signs`, `wound-care`, `patient-safety`, `care-plan`, `تمريض`, `رعاية-سريرية`

## 4. Mandatory Input Parameters
- `vital_signs`
- `mental_status`

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
  npx skills add seotarek/MedOrqis --skill nursing-clinical-care
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/nursing-clinical-care/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: Royal College of Physicians NEWS2 Guidelines / NPUAP Braden Scale
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
