---
name: clinical-safety-auditor
description: >-
  Final pre-output clinical safety auditor. Validates that outputs contain verified citations, comply with dose caps, have no missing mandatory parameters, and do not act on unverified hypotheses.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - safety-gate
    - audit
    - contraindications
    - anticoagulation-bleed
    - inter-skill-conflict
    - safe-abstention
    - تدقيق-أمان
    - أمان-سريري
---

# clinical-safety-auditor (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Acts as an immutable quality gate auditing all outgoing clinical advice against patient safety policies.

### Prohibited Uses
- Suppressing detected clinical safety warnings

## 2. Clinical Decision Checklist
1. Intercept clinical contradictions (e.g. anticoagulation in active gastrointestinal hemorrhage)
2. Enforce Epistemic Provenance Gate (halt if indication is MODEL_INFERRED_HYPOTHESIS)
3. Verify that every clinical claim maps to an authentic, un-retracted guideline citation
4. Ensure output carries the mandatory clinical governance banner

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`safety-gate`, `audit`, `contraindications`, `anticoagulation-bleed`, `inter-skill-conflict`, `safe-abstention`, `تدقيق-أمان`, `أمان-سريري`

## 4. Mandatory Input Parameters
- `proposed_output`
- `context_envelope`

## 5. Deterministic Safety Dependencies
- `core.context_validator`
- `core.citation_validator`
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
  npx skills add seotarek/MedOrqis --skill clinical-safety-auditor
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/clinical-safety-auditor/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: FDA Clinical Decision Support Software Guidance (2026) / ISO 14971 Medical Device Risk Controls
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
