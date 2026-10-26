---
name: medorqis-orchestrator
description: >-
  Core router and clinical context envelope manager for the MedOrqis ecosystem. Coordinates clinical workflow handoffs, validates epistemic provenance, and detects inter-skill conflicts.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 1"
  safety-class: "Class A"
  keywords:
    - orchestrator
    - routing
    - clinical-context
    - epistemic-provenance
    - conflict-detection
    - workflow
    - توجيه-سريري
    - سياق-سريري
---

# medorqis-orchestrator (v2.1.0)

[![Safety Class: Class A](https://img.shields.io/badge/Safety%20Class-Class%20A-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 1](https://img.shields.io/badge/Tier-Tier%201-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Orchestrates multi-skill clinical evaluation workflows, routes patient queries, and enforces epistemic provenance boundaries.

### Prohibited Uses
- Autonomous final diagnosis
- Prescribing medications directly

## 2. Clinical Decision Checklist
1. Validate incoming JSON envelope against Draft-07 schema
2. Verify epistemic provenance of clinical indications (no MODEL_INFERRED_HYPOTHESIS dosing)
3. Screen for acute emergency red flags across all organ systems
4. Route verified context to specialized Tier 2 / Tier 3 domain skills

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`orchestrator`, `routing`, `clinical-context`, `epistemic-provenance`, `conflict-detection`, `workflow`, `توجيه-سريري`, `سياق-سريري`

## 4. Mandatory Input Parameters
- `clinical_query`
- `patient_demographics`

## 5. Deterministic Safety Dependencies
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
  npx skills add seotarek/MedOrqis --skill medorqis-orchestrator
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/medorqis-orchestrator/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: MedOrqis Architectural & Governance Framework v2.1 (ISO 14971/IEC 62304)
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
