---
name: pharmacology-dosing-interactions
description: >-
  High-risk pharmacology, dosing, and drug interaction engine. Enforces strict renal and hepatic dose adjustments, verifies Narrow Therapeutic Index (NTI) drug levels, and blocks lethal drug-drug interactions.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - pharmacology
    - drug-interactions
    - renal-dosing
    - cockcroft-gault
    - hepatic-adjustment
    - crcl
    - ddi
    - صيدلة-إكلينيكية
    - جرعات-دوائية
---

# pharmacology-dosing-interactions (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Calculates precise drug dosages based on weight and renal function (eGFR/CrCl), and intercepts contraindicated drug combinations.

### Prohibited Uses
- Calculating chemotherapy or NTI dosing without serum drug levels and renal/hepatic markers

## 2. Clinical Decision Checklist
1. Normalize all medication brand names to international nonproprietary names (INN)
2. Evaluate full medication list against critical DDI rules (e.g. sildenafil + nitrates, warfarin + NSAIDs)
3. Calculate Cockcroft-Gault CrCl with Ideal/Adjusted Body Weight adjustments in obesity
4. Adjust dosages and dosing intervals for renally cleared medications according to CrCl

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`pharmacology`, `drug-interactions`, `renal-dosing`, `cockcroft-gault`, `hepatic-adjustment`, `crcl`, `ddi`, `صيدلة-إكلينيكية`, `جرعات-دوائية`

## 4. Mandatory Input Parameters
- `drug_inn`
- `patient_demographics`
- `renal_function`

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
  npx skills add seotarek/MedOrqis --skill pharmacology-dosing-interactions
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/pharmacology-dosing-interactions/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: FDA Drug Labeling / BNF / Stockley's Drug Interactions (2024)
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
