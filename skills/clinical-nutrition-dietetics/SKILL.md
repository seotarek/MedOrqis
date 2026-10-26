---
name: clinical-nutrition-dietetics
description: >-
  Clinical nutrition and medical nutrition therapy skill. Computes basal caloric/protein requirements, manages diabetic/renal diets, and flags food-drug interactions.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - nutrition
    - dietetics
    - bmi
    - harris-benedict
    - enteral-feeding
    - malnutrition
    - food-drug-interactions
    - تغذية-علاجية
---

# clinical-nutrition-dietetics (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Calculates nutritional needs, manages therapeutic diet restrictions, and designs enteral/parenteral nutrition support.

### Prohibited Uses
- Formulating TPN without daily electrolyte and liver function monitoring

## 2. Clinical Decision Checklist
1. Calculate Basal Metabolic Rate (BMR) via Harris-Benedict or Mifflin-St Jeor formula
2. Adjust target protein intake based on clinical state (0.8 g/kg for stable CKD, 1.5-2.0 g/kg for ICU/sepsis)
3. Check for food-drug interactions (e.g. grapefruit and CYP3A4 statins, vitamin K and warfarin)
4. Screen for Refeeding Syndrome risk in severely malnourished or prolonged-fasting patients

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`nutrition`, `dietetics`, `bmi`, `harris-benedict`, `enteral-feeding`, `malnutrition`, `food-drug-interactions`, `تغذية-علاجية`

## 4. Mandatory Input Parameters
- `weight_kg`
- `clinical_condition`

## 5. Deterministic Safety Dependencies
- `core.clinical_calculators`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill clinical-nutrition-dietetics
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/clinical-nutrition-dietetics/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: ASPEN / ESPEN Clinical Nutrition Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
