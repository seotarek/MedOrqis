---
name: mental-health-psychiatry
description: >-
  Psychiatry and mental health crisis skill. Implements immediate emergency protocols for active suicidal ideation, screens for psychosis and severe mania, and monitors psychotropic drug interactions.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - psychiatry
    - mental-health
    - suicide-screening
    - crisis-triage
    - ssri
    - qt-prolongation
    - depression
    - صحة-نفسية
    - طب-نفسي
---

# mental-health-psychiatry (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Detects psychiatric crises, connects users to crisis hotlines, and monitors for Serotonin Syndrome and Neuroleptic Malignant Syndrome.

### Prohibited Uses
- Delaying crisis intervention for suicidal patients
- Autonomous medication adjustments for severe psychiatric conditions

## 2. Clinical Decision Checklist
1. Screen for active suicidal ideation with intent or plan (Columbia-Suicide Severity Rating Scale)
2. Trigger immediate emergency escalation and provide localized 24/7 crisis hotline contact numbers
3. Monitor psychotropic combinations for Serotonin Syndrome (MAOIs + SSRIs) and QTc prolongation
4. Screen for Neuroleptic Malignant Syndrome in patients on antipsychotic therapy

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`psychiatry`, `mental-health`, `suicide-screening`, `crisis-triage`, `ssri`, `qt-prolongation`, `depression`, `صحة-نفسية`, `طب-نفسي`

## 4. Mandatory Input Parameters
- `mental_health_symptoms`

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
  npx skills add seotarek/MedOrqis --skill mental-health-psychiatry
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/mental-health-psychiatry/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: APA Practice Guidelines / Columbia Suicide Severity Rating Scale (C-SSRS)
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
