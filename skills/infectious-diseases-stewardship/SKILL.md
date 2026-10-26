---
name: infectious-diseases-stewardship
description: >-
  Antimicrobial stewardship and infectious diseases skill. Guides empiric vs targeted antibiotic selection, prevents unnecessary broad-spectrum usage, and monitors antibiogram patterns.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - infectious-diseases
    - antimicrobial-stewardship
    - antibiotics
    - sepsis
    - antibiogram
    - resistance
    - idsa
    - مضادات-حيوية
    - أمراض-معدية
---

# infectious-diseases-stewardship (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Recommends guideline-directed antimicrobial regimens, dosage adjustments for renal function, and optimal therapy duration.

### Prohibited Uses
- Ignoring local antibiograms or positive blood culture sensitivities

## 2. Clinical Decision Checklist
1. Categorize antimicrobial regimen into WHO AWaRe classification (Access, Watch, Reserve)
2. Differentiate true IgE-mediated beta-lactam anaphylaxis from mild cutaneous adverse reactions
3. Calculate Cockcroft-Gault CrCl to adjust aminoglycoside / vancomycin dosing intervals
4. Recommend structured de-escalation from broad-spectrum to narrow-spectrum upon culture sensitivity

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`infectious-diseases`, `antimicrobial-stewardship`, `antibiotics`, `sepsis`, `antibiogram`, `resistance`, `idsa`, `مضادات-حيوية`, `أمراض-معدية`

## 4. Mandatory Input Parameters
- `infection_site`
- `patient_demographics`
- `allergies`

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
  npx skills add seotarek/MedOrqis --skill infectious-diseases-stewardship
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/infectious-diseases-stewardship/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: IDSA Guidelines / Sanford Guide to Antimicrobial Therapy (2024) / WHO AWaRe
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
