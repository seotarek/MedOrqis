---
name: clinical-toxicology-overdose
description: >-
  Clinical toxicology and acute overdose management skill. Recognizes acute toxidromes (anticholinergic, cholinergic, opioid, sympathomimetic, sedative), advises on specific antidotes, and escalates to Poison Control.
allowed-tools: bash
license: Apache-2.0
compatibility: Linux, macOS, Windows (Python 3.10+, MCP stdio, Claude Code, Gemini CLI, OpenAI)
metadata:
  version: "2.1.0"
  tier: "Tier 3"
  safety-class: "Class C"
  keywords:
    - toxicology
    - overdose
    - toxidrome
    - antidote
    - naloxone
    - poison-control
    - paracetamol-overdose
    - تسمم
    - جرعة-زائدة
---

# clinical-toxicology-overdose (v2.1.0)

[![Safety Class: Class C](https://img.shields.io/badge/Safety%20Class-Class%20C-blue.svg)](../../SAFETY_AND_GOVERNANCE.md)
[![Tier: Tier 3](https://img.shields.io/badge/Tier-Tier%203-teal.svg)](../../README.md)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green.svg)](../../LICENSE)

## 1. Intended Purpose & Clinical Boundaries
Identifies toxic ingestions, advises on gastric decontamination timing, naloxone/antidote indications, and poison center contact.

### Prohibited Uses
- Recommending induction of emesis (ipecac) or home remedies for caustic ingestions

## 2. Clinical Decision Checklist
1. Identify acute clinical toxidrome based on vital signs, pupils, skin moisture, and bowel sounds
2. Check indication for specific antidotes: Naloxone (opioids), N-acetylcysteine (paracetamol), Atropine (cholinergics)
3. Determine timing window for activated charcoal (strictly within 1-2 hours of ingestion in alert patients)
4. Escalate immediately to Poison Control Center and regional emergency medical services

## 3. Keywords & Triggers (كلمات مفتاحية ومحفزات)
`toxicology`, `overdose`, `toxidrome`, `antidote`, `naloxone`, `poison-control`, `paracetamol-overdose`, `تسمم`, `جرعة-زائدة`

## 4. Mandatory Input Parameters
- `substance_ingested`
- `time_since_ingestion`
- `vital_signs`

## 5. Deterministic Safety Dependencies
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
  npx skills add seotarek/MedOrqis --skill clinical-toxicology-overdose
  ```
- **Direct CLI Execution**:
  ```bash
  python3 skills/clinical-toxicology-overdose/scripts/run.py
  ```
- **MCP Tool Invocation**: Available through the `medorqis_mcp_server.py` stdio daemon.

## 8. Clinical Reference Authority
- **Primary Source Body**: American Academy of Clinical Toxicology (AACT) / EAPCCT Guidelines
- **Review Status**: `REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF`
