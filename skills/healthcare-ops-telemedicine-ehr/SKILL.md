---
name: healthcare-ops-telemedicine-ehr
description: >-
  Health operations, telemedicine intake, and EHR integration skill. Maps unstructured clinical narratives to HL7 FHIR resources and verifies telemedicine intake safety criteria.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 1"
  safety-class: "Class A"
  keywords:
    - telemedicine
    - hl7
    - fhir
    - ehr
    - intake-triage
    - scheduling
    - interoperability
    - طب-عن-بعد
    - سجلات-صحية
---

# healthcare-ops-telemedicine-ehr (v2.1.0)

[![Safety Class: Class A](https://img.shields.io/badge/Safety%20Class-Class%20A-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 1](https://img.shields.io/badge/Tier-Tier%201-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Facilitates structured clinical data exchange via HL7 FHIR and manages digital clinical intake protocols.

### Prohibited Uses
- Bypassing patient informed consent
- Altering audit trails

## 2. Clinical Decision Checklist
1. Verify patient identity and jurisdiction licensure for telemedicine consult
2. Map clinical entities to HL7 FHIR R4 resources (Patient, Condition, MedicationRequest)
3. Check telemedicine appropriateness (screen out unstable red-flag emergencies)
4. Confirm transmission encryption and audit logging conformance

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`telemedicine`, `hl7`, `fhir`, `ehr`, `intake-triage`, `scheduling`, `interoperability`, `طب-عن-بعد`, `سجلات-صحية`

## 4. Mandatory Input Parameters
- `intake_payload`
- `target_fhir_resource`

## 5. Deterministic Safety Dependencies
- `core.phi_deidentifier`
- `core.terminology_connectors`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill healthcare-ops-telemedicine-ehr
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/healthcare-ops-telemedicine-ehr/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: HL7 FHIR R4 Specification / ATA Telemedicine Practice Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
