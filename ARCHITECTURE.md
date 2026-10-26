# MedOrqis — System Architecture & Design Specification (v2.0)

## 1. System Overview
MedOrqis is designed as an evidence-grounded, modular clinical intelligence ecosystem structured into four distinct, loosely coupled layers:

```
┌─────────────────────────────────────────────────────────────┐
│                   Platform Adapters Layer                   │
│   Claude Skills  │  Gemini CLI Ext  │  MCP Server  │ OpenAI │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│           24 Risk-Stratified Medical AI Skills              │
│   Tier 1 (Class A) │ Tier 2 (Class B) │ Tier 3 (Class C)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│            Core Deterministic Engines (Zero Token)          │
│ Calculators │ Context Gate │ Safety Rules │ PHI │ Normalizer│
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│       Reference Dictionaries & Standard Terminology         │
│ Red Flags │ DDI │ Lexicon (AR/EN/FR/ES) │ Regional INN Maps │
└─────────────────────────────────────────────────────────────┘
```

## 2. Zero-Token Deterministic Core
High-risk clinical decisions and mathematical computations must never rely on probabilistic LLM token generation. The `core/` package executes:
- **Clinical Calculators**: Pure functions implementing ESC 2024, ACC/AHA 2023, CKD-EPI 2021, Cockcroft-Gault, CURB-65, Wells DVT/PE, and pediatric dose capping.
- **Epistemic Provenance Gate**: `core/context_validator.py` blocks any downstream dosing or irreversible therapy on inputs tagged `MODEL_INFERRED_HYPOTHESIS`.
- **PHI Scrubbing**: Regex-based de-identification of HIPAA 18, Egyptian 14-digit National IDs, and Saudi 10-digit National IDs.
- **Prompt Security**: Direct and indirect prompt injection defense.
- **Multilingual Semantic Normalization**: 100% negation polarity preservation and BiDi decimal/unit fidelity.

## 3. The 24-Skill Taxonomy

### Tier 1: Governance, Research & Operations (Class A)
1. `medorqis-orchestrator`: Context envelope routing and conflict resolution.
2. `ebm-research-biostatistics`: PICO, CASP, RoB-2, and GRADE certainty.
3. `medical-documentation-translation`: SOAP, SBAR, and BiDi multilingual translation.
4. `healthcare-ops-telemedicine-ehr`: HL7 FHIR mapping and telemedicine intake.
5. `health-cybersecurity-privacy`: PHI scrubbing and prompt security.
6. `public-health-epidemiology`: Screening metrics (sens/spec) and IPC protocols.

### Tier 2: Diagnostic & Chronic Care Support (Class B)
7. `differential-diagnosis-cds`: VINDICATE differential framework.
8. `laboratory-medicine-pathology`: Critical panic values and LOINC mapping.
9. `radiology-medical-imaging`: ACR Appropriateness Criteria and radiation safety.
10. `internal-medicine-chronic`: Multi-morbidity chronic disease care plans.
11. `infectious-diseases-stewardship`: Antimicrobial stewardship and resistance awareness.
12. `nursing-clinical-care`: NEWS2 early warning score and Braden scale.
13. `clinical-nutrition-dietetics`: Caloric requirements and food-drug interactions.
14. `rehabilitation-physical-therapy`: Post-op and stroke rehab protocols.

### Tier 3: High-Risk, Emergency & Vulnerable Populations (Class C)
15. `emergency-triage-redflags`: ABCDE primary survey and emergency redirection.
16. `clinical-safety-auditor`: Pre-output verification and safety gate check.
17. `pharmacology-dosing-interactions`: Renal/hepatic adjustments and DDI checks.
18. `clinical-toxicology-overdose`: Toxidromes, antidotes, and Poison Control escalation.
19. `pediatrics-neonatology`: Weight-based dose capping and pediatric safety.
20. `obstetrics-gynecology`: Maternal-fetal safety and pre-eclampsia triage.
21. `geriatrics-polypharmacy`: 2023 Beers Criteria and STOPP/START.
22. `mental-health-psychiatry`: Suicide crisis escalation and psychotropic monitoring.
23. `perioperative-surgical-care`: RCRI pre-op risk and anticoagulation bridging.
24. `oncology-palliative-care`: Oncologic emergencies and palliative pain control.
