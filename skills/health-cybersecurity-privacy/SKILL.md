---
name: health-cybersecurity-privacy
description: >-
  Health cybersecurity and patient privacy guardian. De-identifies Protected Health Information (HIPAA Safe Harbor, GDPR, Egyptian PDPL, Saudi PDPL) and blocks indirect prompt injection attacks.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 1"
  safety-class: "Class A"
  keywords:
    - phi
    - hipaa
    - gdpr
    - pdpl
    - de-identification
    - prompt-injection
    - redaction
    - أمان-صحي
    - خصوصية-المرضى
---

# health-cybersecurity-privacy (v2.1.0)

[![Safety Class: Class A](https://img.shields.io/badge/Safety%20Class-Class%20A-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 1](https://img.shields.io/badge/Tier-Tier%201-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Screens clinical inputs for PHI and adversarial injections before transmission or public storage.

### Prohibited Uses
- Transmitting identified patient data to public services

## 2. Clinical Decision Checklist
1. Execute regex and rule-based scan for indirect prompt injections and jailbreak bypasses
2. Redact HIPAA 18 Safe Harbor identifiers
3. Redact Egyptian 14-digit National IDs and Saudi 10-digit National IDs / Iqamas
4. Log structured de-identification audit report without persisting raw patient identifiers

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`phi`, `hipaa`, `gdpr`, `pdpl`, `de-identification`, `prompt-injection`, `redaction`, `أمان-صحي`, `خصوصية-المرضى`

## 4. Mandatory Input Parameters
- `clinical_text`

## 5. Deterministic Safety Dependencies
- `core.phi_deidentifier`
- `core.prompt_security_guard`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill health-cybersecurity-privacy
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/health-cybersecurity-privacy/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: HIPAA Privacy Rule / EU GDPR Article 9 / ISO 27799 Health Informatics
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
