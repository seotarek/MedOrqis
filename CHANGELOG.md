# Changelog

All notable changes to the MedOrqis Medical AI Skills Ecosystem are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-10-26

### Added
- **Deterministic Pediatric & Risk Calculators (`core/clinical_calculators.py`)**:
  - `calculate_bedside_schwartz_egfr`: Bedside Schwartz pediatric equation ($0.413 \times \text{Height} / \text{SCr}$) with strict pediatric validation ($\text{age} < 18$).
  - `calculate_has_bled_score`: Atrial fibrillation bleeding risk score (0-9 points) with age-informed validation.
  - `calculate_news2_score`: Royal College of Physicians National Early Warning Score 2 (7 vital parameters) with emergency escalation threshold alerts.
  - Hardened `calculate_curb65_score` with physiological plausibility bounds (RR 0-100, SBP 21-350) and pediatric age refusal.
- **Critical Drug-Drug Interaction (DDI) Engine (`core/safety_guardrails.py`)**:
  - Real-time screening for lethal contraindications: Warfarin + NSAID, DOAC + NSAID, Sildenafil + Nitroglycerin, Spironolactone + ACEi, and pregnancy teratogens.
  - Regional trade brand name mapping to INN across Egyptian, Gulf/Saudi, Levantine, Maghrebi, and International markets.
- **Negation Polarity Clause Boundary Protection (`core/terminology_normalizer.py`)**:
  - Clause-stop boundaries (`لكن`, `إلا`, `بينما`, `بل`, `but`, `however`, `mais`, `pero`) with max 5-word scope, preventing false negation propagation to affirmed symptoms.
- **Clinical Governance Separation (`governance/clinical_review_registry.json`)**:
  - Formal ISO 14971 / IEC 62304 separation of algorithmic verification (with SHA-256 hashes) from human clinical specialist sign-off.
- **Platform Adapters & Standards Compliance**:
  - OpenAI Structured Outputs: Enforced `"strict": true` and `"additionalProperties": false`.
  - Skills CLI: Standardized `allowed-tools: bash` as a scalar string across all 24 skills.
  - MCP Server: Added `check_drug_interactions` and `scan_prompt_security` tools.
  - GitHub Pages: Automated web catalog deployment on `https://seotarek.github.io/MedOrqis/`.
- **Harmonized Benchmark & Test Suite (`tests/`)**:
  - Expanded test suite to 31 tests with 100% pass rate.
  - Expanded multilingual benchmark to 34 real-world clinical cases across 8 languages and dialects.

## [2.0.0] - 2026-10-26


### Added
- **Core Deterministic Engines (`core/`)**:
  - `clinical_calculators.py`: CHA2DS2-VA (ESC 2024), CHA2DS2-VASc (AHA 2023), CKD-EPI 2021 (race-free), Cockcroft-Gault CrCl (IBW/AdjBW), Pediatric Dose Capping, Mosteller BSA, CURB-65, and Wells DVT/PE.
  - `context_validator.py`: Draft-07 schema validation and hard Epistemic Provenance Rule enforcement (blocking dosing on `MODEL_INFERRED_HYPOTHESIS`).
  - `citation_validator.py`: Stage 1 citation integrity and version staleness detection.
  - `claim_entailment_verifier.py`: Stage 2 claim-source support and pediatric/adult population mismatch detection.
  - `phi_deidentifier.py`: HIPAA 18 scrubbing plus Egyptian 14-digit National IDs and Saudi 10-digit National IDs/Iqamas.
  - `prompt_security_guard.py`: Adversarial prompt injection and dosing cap bypass defense.
  - `safety_guardrails.py`: Age-stratified red-flag triage, missing data gatekeeper, and inter-skill conflict resolution.
  - `terminology_normalizer.py`: 100% negation preservation across Arabic (MSA, Egyptian, Gulf), English, French, and Spanish; BiDi unit and decimal fidelity.
  - `terminology_connectors.py`: API connectors for ICD-11, RxNorm/UMLS, and FHIR terminology servers.
- **24 Medical AI Skills (`skills/`)**:
  - Tier 1 (Class A): `medorqis-orchestrator`, `ebm-research-biostatistics`, `medical-documentation-translation`, `healthcare-ops-telemedicine-ehr`, `health-cybersecurity-privacy`, `public-health-epidemiology`.
  - Tier 2 (Class B): `differential-diagnosis-cds`, `laboratory-medicine-pathology`, `radiology-medical-imaging`, `internal-medicine-chronic`, `infectious-diseases-stewardship`, `nursing-clinical-care`, `clinical-nutrition-dietetics`, `rehabilitation-physical-therapy`.
  - Tier 3 (Class C): `emergency-triage-redflags`, `clinical-safety-auditor`, `pharmacology-dosing-interactions`, `clinical-toxicology-overdose`, `pediatrics-neonatology`, `obstetrics-gynecology`, `geriatrics-polypharmacy`, `mental-health-psychiatry`, `perioperative-surgical-care`, `oncology-palliative-care`.
- **Platform Adapters (`adapters/`)**:
  - Claude Code & Agent Skills packaging manifest.
  - Gemini CLI Extension manifest (`gemini-extension.json` + `GEMINI.md`).
  - OpenAI Assistants / Strict Structured Function Calling definitions.
  - Standalone Model Context Protocol (MCP) JSON-RPC 2.0 stdio server (`mcp_server/medorqis_mcp_server.py`).
- **Comprehensive Verification Suite (`tests/`)**:
  - Master test runner `tests/run_all_tests.py` auto-generating `tests/reports/VERIFICATION_REPORT.md` and `LANGUAGE_COVERAGE_MATRIX.md`.
  - 21 automated integration and boundary test cases achieving 100% pass rate.
