---
name: rehabilitation-physical-therapy
description: >-
  Physical therapy and rehabilitation skill. Designs post-operative, stroke, and musculoskeletal recovery protocols while evaluating hemodynamic and spinal exercise contraindications.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - physical-therapy
    - rehabilitation
    - stroke-rehab
    - post-op-rehab
    - mobility
    - fim
    - علاج-طبيعي
    - تأهيل
---

# rehabilitation-physical-therapy (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Proposes progressive mobility protocols, assesses functional recovery scales, and checks post-surgical weight-bearing restrictions.

### Prohibited Uses
- Mobilizing patients with unstable spinal fractures or acute deep vein thrombosis without clearance

## 2. Clinical Decision Checklist
1. Verify surgical clearance and weight-bearing status before initiating mobilization
2. Screen for acute DVT using Wells DVT Criteria before calf manipulation or leg exercise
3. Monitor hemodynamic tolerance during orthostatic position changes (prevent syncopal falls)
4. Structure progressive neuro-rehabilitation exercises following acute ischemic stroke

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`physical-therapy`, `rehabilitation`, `stroke-rehab`, `post-op-rehab`, `mobility`, `fim`, `علاج-طبيعي`, `تأهيل`

## 4. Mandatory Input Parameters
- `surgical_or_neurological_status`
- `mobility_level`

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
  npx skills add seotarek/MedOrqis --skill rehabilitation-physical-therapy
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/rehabilitation-physical-therapy/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: AHA/ASA Stroke Rehabilitation Guidelines / APTA Practice Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
