---
name: obstetrics-gynecology
description: >-
  Obstetrics, gynecology, and maternal-fetal safety skill. Screens for pre-eclampsia/eclampsia, ectopic pregnancy, postpartum hemorrhage, and verifies medication safety in pregnancy and lactation.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - obgyn
    - pregnancy
    - lactation
    - teratogenic
    - pre-eclampsia
    - gestational-diabetes
    - postpartum
    - نساء-وتوليد
    - حمل-ورضاعة
---

# obstetrics-gynecology (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Identifies acute maternal red flags, calculates gestational age, and checks Briggs Drugs in Pregnancy and Lactation safety.

### Prohibited Uses
- Prescribing Category X or known teratogenic drugs (ACEi, ARBs, isotretinoin, methotrexate) in pregnancy

## 2. Clinical Decision Checklist
1. Screen for acute obstetric emergencies: severe pre-eclampsia (BP >= 160/110 + symptoms), ectopic pregnancy
2. Cross-check all prescribed medications against FDA/Briggs pregnancy teratogenicity registries
3. Halt administration of contraindicated teratogens (isotretinoin, valproate, ACE inhibitors, methotrexate)
4. Confirm lactation safety before authorizing maternal medication intake

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`obgyn`, `pregnancy`, `lactation`, `teratogenic`, `pre-eclampsia`, `gestational-diabetes`, `postpartum`, `نساء-وتوليد`, `حمل-ورضاعة`

## 4. Mandatory Input Parameters
- `pregnancy_status`
- `gestational_age_weeks`

## 5. Deterministic Safety Dependencies
- `core.clinical_calculators`
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
  npx skills add seotarek/MedOrqis --skill obstetrics-gynecology
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/obstetrics-gynecology/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: ACOG Practice Bulletins / RCOG Green-top Guidelines / Briggs Drugs in Pregnancy
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
