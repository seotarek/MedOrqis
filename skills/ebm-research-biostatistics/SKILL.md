---
name: ebm-research-biostatistics
description: >-
  Evidence-Based Medicine (EBM) research assistant. Formulates PICO questions, conducts CASP and RoB-2 critical appraisals, evaluates GRADE evidence certainty, and interprets biostatistical metrics.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 1"
  safety-class: "Class A"
  keywords:
    - ebm
    - biostatistics
    - pico
    - casp
    - rob-2
    - grade
    - odds-ratio
    - relative-risk
    - nnt
    - cochrane
    - طب-مسند-بالدليل
    - إحصاء-حيوي
---

# ebm-research-biostatistics (v2.1.0)

[![Safety Class: Class A](https://img.shields.io/badge/Safety%20Class-Class%20A-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 1](https://img.shields.io/badge/Tier-Tier%201-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Appraises clinical study designs, computes biostatistical parameters (OR, RR, NNT), and assigns GRADE certainty.

### Prohibited Uses
- Fabricating citations or clinical trial results
- Direct clinical care without clinician review

## 2. Clinical Decision Checklist
1. Formulate structured PICO clinical question
2. Verify PMIDs and DOIs against immutable verified guidelines registry
3. Execute RoB-2 / ROBINS-I risk of bias critical appraisal
4. Assign GRADE certainty of evidence (High, Moderate, Low, Very Low)

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`ebm`, `biostatistics`, `pico`, `casp`, `rob-2`, `grade`, `odds-ratio`, `relative-risk`, `nnt`, `cochrane`, `طب-مسند-بالدليل`, `إحصاء-حيوي`

## 4. Mandatory Input Parameters
- `study_abstract_or_claim`
- `study_type`

## 5. Deterministic Safety Dependencies
- `core.citation_validator`
- `core.claim_entailment_verifier`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill ebm-research-biostatistics
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/ebm-research-biostatistics/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: Cochrane Handbook for Systematic Reviews / GRADE Working Group
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
