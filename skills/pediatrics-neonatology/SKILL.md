---
name: pediatrics-neonatology
description: >-
  Pediatric and neonatal clinical safety skill. Enforces strict weight-based dose caps (never exceeding maximum adult doses), flags age-weight entry discrepancies (lb vs kg), and screens for neonatal red flags.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - pediatrics
    - neonatology
    - pediatric-dosing
    - weight-based-dosing
    - dose-capping
    - apgar
    - طب-أطفال
    - حديثي-الولادة
---

# pediatrics-neonatology (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Provides pediatric dosing calculations, APGAR assessments, dehydration triage, and fever management in infants.

### Prohibited Uses
- Dosing pediatric medication without verified weight in kilograms

## 2. Clinical Decision Checklist
1. Verify pediatric patient weight strictly in kilograms (reject lb entries or missing weights)
2. Calculate weight-based medication dose (mg/kg) and enforce mandatory adult maximum dose cap
3. Calculate pediatric renal function via Bedside Schwartz eGFR formula (0.413 * height / Cr)
4. Screen for neonatal red flags: fever in neonate < 28 days (mandates full septic workup)

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`pediatrics`, `neonatology`, `pediatric-dosing`, `weight-based-dosing`, `dose-capping`, `apgar`, `طب-أطفال`, `حديثي-الولادة`

## 4. Mandatory Input Parameters
- `age_years`
- `weight_kg`

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
  npx skills add seotarek/MedOrqis --skill pediatrics-neonatology
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/pediatrics-neonatology/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: Nelson Textbook of Pediatrics (22nd Ed) / AAP Guidelines / WHO IMCI
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
