# Changelog

All notable changes to the MedOrqis Medical AI Skills Ecosystem are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
