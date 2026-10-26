---
name: radiology-medical-imaging
description: >-
  Medical imaging appropriateness and report analysis skill. Implements ACR Appropriateness Criteria, checks contrast nephropathy/allergy risks, and ensures radiation/pregnancy safety.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 2"
  safety-class: "Class B"
  keywords:
    - radiology
    - imaging
    - mri
    - ct-scan
    - x-ray
    - ultrasound
    - acr-criteria
    - alara
    - أشعة
    - تصوير-طبي
---

# radiology-medical-imaging (v2.1.0)

[![Safety Class: Class B](https://img.shields.io/badge/Safety%20Class-Class%20B-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 2](https://img.shields.io/badge/Tier-Tier%202-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Selects appropriate imaging modalities based on clinical presentation and radiation risk vs diagnostic yield.

### Prohibited Uses
- Primary reading of raw radiological DICOM images
- Ordering contrast in severe acute kidney injury without prophylaxis

## 2. Clinical Decision Checklist
1. Consult ACR Appropriateness Criteria for target clinical indication
2. Screen for pregnancy in female patients before ordering ionizing radiation (ALARA principle)
3. Calculate eGFR prior to iodinated CT or gadolinium MRI contrast administration
4. Check for severe contrast allergy history and prescribe premedication protocol if indicated

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`radiology`, `imaging`, `mri`, `ct-scan`, `x-ray`, `ultrasound`, `acr-criteria`, `alara`, `أشعة`, `تصوير-طبي`

## 4. Mandatory Input Parameters
- `clinical_indication`
- `patient_demographics`

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
  npx skills add seotarek/MedOrqis --skill radiology-medical-imaging
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/radiology-medical-imaging/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: ACR Appropriateness Criteria (2024) / ESUR Contrast Media Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
