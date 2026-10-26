---
name: geriatrics-polypharmacy
description: >-
  Geriatric medicine, polypharmacy, and deprescribing skill. Implements AGS Beers Criteria (2023) and STOPP/START criteria, assesses anticholinergic cognitive burden, and identifies fall risks.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - geriatrics
    - polypharmacy
    - beers-criteria
    - stopp-start
    - fall-risk
    - anticholinergic-burden
    - طب-المسنين
    - تعدد-الأدوية
---

# geriatrics-polypharmacy (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Reviews elderly medication lists, flags potentially inappropriate medications (PIMs), and guides structured deprescribing.

### Prohibited Uses
- Abruptly stopping chronic psychotropic or cardiac medications without tapering

## 2. Clinical Decision Checklist
1. Audit medication list against 2023 American Geriatrics Society (AGS) Beers Criteria
2. Identify high anticholinergic burden drugs contributing to cognitive decline and fall risks
3. Screen for drug-drug interactions in elderly patients taking >= 5 concurrent medications
4. Formulate structured deprescribing taper plans for sedatives, hypnotics, and redundant agents

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`geriatrics`, `polypharmacy`, `beers-criteria`, `stopp-start`, `fall-risk`, `anticholinergic-burden`, `طب-المسنين`, `تعدد-الأدوية`

## 4. Mandatory Input Parameters
- `medication_list`
- `patient_age_years`

## 5. Deterministic Safety Dependencies
- `core.clinical_calculators`
- `core.context_validator`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill geriatrics-polypharmacy
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/geriatrics-polypharmacy/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: 2023 AGS Beers Criteria / STOPP/START Criteria Version 3 (2023)
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
