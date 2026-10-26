---
name: medical-documentation-translation
description: >-
  Clinical documentation and translation engine. Generates structured SOAP notes, SBAR handoffs, and multilingual medical translations preserving negation polarity and numeric unit fidelity.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 1"
  safety-class: "Class A"
  keywords:
    - soap
    - sbar
    - clinical-notes
    - medical-translation
    - bidi
    - negation
    - terminology
    - ترجمة-طبية
    - توثيق-طبي
---

# medical-documentation-translation (v2.1.0)

[![Safety Class: Class A](https://img.shields.io/badge/Safety%20Class-Class%20A-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 1](https://img.shields.io/badge/Tier-Tier%201-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Synthesizes medical encounters into standardized clinical documentation formats and provides semantic-preserving cross-lingual translation.

### Prohibited Uses
- Altering documented clinical facts
- Unsupervised patient discharge

## 2. Clinical Decision Checklist
1. De-identify Protected Health Information (HIPAA 18, National IDs, MRNs)
2. Extract verified clinical findings into SOAP / SBAR structured sections
3. Preserve clause-bounded negation polarity across multilingual translations
4. Maintain bidirectional unit fidelity (prevent decimal inversion and mg vs mcg errors)

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`soap`, `sbar`, `clinical-notes`, `medical-translation`, `bidi`, `negation`, `terminology`, `ترجمة-طبية`, `توثيق-طبي`

## 4. Mandatory Input Parameters
- `encounter_narrative`
- `format_type`

## 5. Deterministic Safety Dependencies
- `core.terminology_normalizer`
- `core.phi_deidentifier`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill medical-documentation-translation
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/medical-documentation-translation/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: Joint Commission SBAR Standards / AAHIM Clinical Documentation Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
