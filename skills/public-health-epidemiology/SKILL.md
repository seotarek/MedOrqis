---
name: public-health-epidemiology
description: >-
  Public health, epidemiology, and outbreak investigation skill. Evaluates diagnostic screening metrics (sensitivity, specificity, PPV, NPV) and advises on infection prevention and control (IPC).
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 1"
  safety-class: "Class A"
  keywords:
    - epidemiology
    - public-health
    - screening
    - sensitivity
    - specificity
    - ipc
    - outbreak
    - صحة-عامة
    - وبائيات
---

# public-health-epidemiology (v2.1.0)

[![Safety Class: Class A](https://img.shields.io/badge/Safety%20Class-Class%20A-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 1](https://img.shields.io/badge/Tier-Tier%201-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Computes epidemiological indices, analyzes transmission dynamics, and references WHO infection control protocols.

### Prohibited Uses
- Issuing unverified public quarantine orders

## 2. Clinical Decision Checklist
1. Compute 2x2 contingency matrix metrics: Sensitivity, Specificity, PPV, NPV, LR+ and LR-
2. Adjust predictive values according to disease prevalence in target population
3. Identify outbreak transmission modes (airborne, droplet, contact, vector)
4. Reference WHO infection prevention and control (IPC) standards

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`epidemiology`, `public-health`, `screening`, `sensitivity`, `specificity`, `ipc`, `outbreak`, `صحة-عامة`, `وبائيات`

## 4. Mandatory Input Parameters
- `disease_metrics_or_outbreak_data`

## 5. Deterministic Safety Dependencies
- `core.citation_validator`

## 6. Execution Workflow
1. Parse and validate incoming `ClinicalContextEnvelope`.
2. Inspect epistemic provenance: Ensure no treatment or high-risk dosing is executed on `MODEL_INFERRED_HYPOTHESIS`.
3. Check for emergency red flags using `core.safety_guardrails`. If critical red flags exist, halt and return `SAFE_ABSTENTION_EMERGENCY_ESCALATION`.
4. Invoke deterministic calculators or rules via `scripts/run.py` or MCP tools.
5. Format and return structured `SkillOutputContract` with validated citations.

## 7. Installation & Invocation
- **Skills CLI**:
  ```bash
  npx skills add seotarek/MedOrqis --skill public-health-epidemiology
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/public-health-epidemiology/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: WHO Outbreak Communication & IPC Guidelines / CDC Field Epidemiology Manual
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
