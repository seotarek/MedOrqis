---
name: laboratory-medicine-pathology
description: >-
  Laboratory medicine and pathology interpretation skill. Flags critical panic values, resolves metric unit discrepancies (mmol/L vs mg/dL), and maps lab parameters to LOINC concepts.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - laboratory
    - panic-values
    - loinc
    - critical-labs
    - biochemistry
    - hematology
    - pathology
    - تحاليل-طبية
    - قيم-حرجة
---

# laboratory-medicine-pathology (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Interprets lab profiles (CBC, BMP, LFTs, Coagulation, ABG), flags critical panic thresholds, and suggests confirmatory testing.

### Prohibited Uses
- Overriding clinical lab delta checks
- Ignoring critical laboratory panic alerts

## 2. Clinical Decision Checklist
1. Screen reported lab values against emergency panic alert thresholds
2. Harmonize unit discrepancies (e.g. serum creatinine mg/dL vs umol/L, glucose mg/dL vs mmol/L)
3. Map lab test to standardized LOINC concept code
4. Recommend immediate clinician notification for critical panic results

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`laboratory`, `panic-values`, `loinc`, `critical-labs`, `biochemistry`, `hematology`, `pathology`, `تحاليل-طبية`, `قيم-حرجة`

## 4. Mandatory Input Parameters
- `test_name`
- `value`
- `unit`

## 5. Deterministic Safety Dependencies
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
  npx skills add seotarek/MedOrqis --skill laboratory-medicine-pathology
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/laboratory-medicine-pathology/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: CLSI Laboratory Safety & Panic Value Guidelines / IFCC LOINC Standards
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
