# MedOrqis — Medical AI Skills Ecosystem (v2.0)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Verification: 100% Passed](https://img.shields.io/badge/Verification-100%25%20Passed-brightgreen.svg)](tests/reports/VERIFICATION_REPORT.md)
[![Safety: IEC 62304 / ISO 14971 Aligned](https://img.shields.io/badge/Safety%20Class-Class%20A%20%7C%20B%20%7C%20C-red.svg)](SAFETY_AND_GOVERNANCE.md)
[![Skills Catalog: 24 Skills](https://img.shields.io/badge/Catalog-SKILLS.md-teal.svg)](SKILLS.md)
[![Showcase: Interactive Hub](https://img.shields.io/badge/Showcase-Web%20Catalog-00e5a3.svg)](https://seotarek.github.io/MedOrqis/)
[![MCP: Enabled](https://img.shields.io/badge/MCP-JSON--RPC%202.0-purple.svg)](mcp_server/medorqis_mcp_server.py)

**MedOrqis** is an open-source, evidence-grounded, cross-platform ecosystem of **24 medical AI skills**, deterministic clinical engines, and platform adapters (Skills CLI, Claude Code, Gemini CLI, Model Context Protocol, and OpenAI).

> 🌐 **Interactive Web Hub**: Explore the live searchable catalog and zero-token clinical calculators at [seotarek.github.io/MedOrqis](https://seotarek.github.io/MedOrqis/) or review [SKILLS.md](SKILLS.md).

Built with an **evidence-first, patient-safety-first architecture**, MedOrqis completely eliminates medical hallucination risks in high-stakes clinical calculations by executing arithmetic, unit conversions, PHI scrubbing, negation parsing, and drug interaction screenings through a **local, deterministic Python core with zero LLM API token overhead**.

---

## ⚡ Key Highlights & Token Economics

1. **Zero-Token Deterministic Core (`core/`)**:
   - High-risk calculations (stroke risk, race-free eGFR, creatinine clearance, pediatric dosing caps, pneumonia severity, DVT/PE probabilities) run locally in pure Python with **zero token cost**.
   - PHI de-identification (HIPAA Safe Harbor, Egyptian 14-digit National IDs, Saudi 10-digit National IDs/Iqamas) and prompt injection defense run locally and deterministically.
2. **Epistemic Provenance Rule**:
   - `core/context_validator.py` enforces a hard architectural gate: no downstream skill can prescribe or dose medications based on a `MODEL_INFERRED_HYPOTHESIS`. High-risk clinical decisions strictly require confirmed `DOCUMENTED_CLINICAL_RECORD` provenance.
3. **Cross-Platform Compatibility**:
   - **Claude Code & Agent Skills**: Native `.claude/skills/` support.
   - **Gemini CLI Extension**: `gemini-extension.json` with `GEMINI.md` context.
   - **Model Context Protocol (MCP)**: Standalone stdio JSON-RPC server (`mcp_server/medorqis_mcp_server.py`).
   - **OpenAI**: Strict Structured Outputs and Assistant function schemas.
4. **Quantifiable Multilingual Semantic Invariance**:
   - **100% Negation Preservation**: Preserves clinical negation in Modern Standard Arabic, Egyptian Arabic, Gulf Arabic, English, French, and Spanish.
   - **BiDi Unit Fidelity**: Prevents decimal inversion (e.g. `0.25 mg`) and critical unit confusion (`mg` vs `mcg`).

---

## 🏥 The 24-Skill Risk-Stratified Taxonomy

### Tier 1: Governance, Research & Operations (Class A)
- `medorqis-orchestrator`: Context envelope routing and conflict resolution.
- `ebm-research-biostatistics`: PICO, CASP, RoB-2 appraisal, and GRADE certainty.
- `medical-documentation-translation`: SOAP, SBAR, and BiDi multilingual medical translation.
- `healthcare-ops-telemedicine-ehr`: HL7 FHIR mapping and telemedicine intake.
- `health-cybersecurity-privacy`: PHI scrubbing and prompt injection defense.
- `public-health-epidemiology`: Screening metrics (sens/spec) and IPC protocols.

### Tier 2: Diagnostic & Chronic Care Support (Class B)
- `differential-diagnosis-cds`: VINDICATE differential framework.
- `laboratory-medicine-pathology`: Critical panic values and LOINC mapping.
- `radiology-medical-imaging`: ACR Appropriateness Criteria and radiation safety.
- `internal-medicine-chronic`: Multi-morbidity chronic disease care plans.
- `infectious-diseases-stewardship`: Antimicrobial stewardship and resistance awareness.
- `nursing-clinical-care`: NEWS2 early warning score and Braden scale.
- `clinical-nutrition-dietetics`: Caloric requirements and food-drug interactions.
- `rehabilitation-physical-therapy`: Post-op and stroke rehab protocols.

### Tier 3: High-Risk, Emergency & Vulnerable Populations (Class C)
- `emergency-triage-redflags`: ABCDE primary survey and emergency redirection.
- `clinical-safety-auditor`: Pre-output verification and safety gate check.
- `pharmacology-dosing-interactions`: Renal/hepatic adjustments and DDI checks.
- `clinical-toxicology-overdose`: Toxidromes, antidotes, and Poison Control escalation.
- `pediatrics-neonatology`: Weight-based dose capping and pediatric safety.
- `obstetrics-gynecology`: Maternal-fetal safety and pre-eclampsia triage.
- `geriatrics-polypharmacy`: 2023 Beers Criteria and STOPP/START.
- `mental-health-psychiatry`: Suicide crisis escalation and psychotropic monitoring.
- `perioperative-surgical-care`: RCRI pre-op risk and anticoagulation bridging.
- `oncology-palliative-care`: Oncologic emergencies and palliative pain control.

---

## 🚀 Quick Start & Verification

### 1. Install via Skills CLI (Recommended)
Add MedOrqis to your active AI agent workspace with a single command:
```bash
npx skills add seotarek/MedOrqis
```
Or install specific skills:
```bash
npx skills add seotarek/MedOrqis --skill emergency-triage-redflags
npx skills add seotarek/MedOrqis --skill pharmacology-dosing-interactions
```

### 2. Local Python Developer Setup
Clone the repository and install core dependencies:
```bash
git clone https://github.com/seotarek/MedOrqis.git
cd MedOrqis
python3 -m pip install -e .
```

### 2. Run the Verification Suite
Execute all 4 verification test suites with a single command:
```bash
python3 tests/run_all_tests.py
```
This automatically executes:
1. `tests/unit/test_clinical_calculators.py`
2. `tests/safety/test_safety_and_provenance.py`
3. `tests/multilingual/test_multilingual_benchmark.py`
4. `tests/platform_adapters/test_security_and_adapters.py`

And generates:
- [VERIFICATION_REPORT.md](tests/reports/VERIFICATION_REPORT.md)
- [LANGUAGE_COVERAGE_MATRIX.md](LANGUAGE_COVERAGE_MATRIX.md)

### 3. Launch the MCP Server
```bash
python3 mcp_server/medorqis_mcp_server.py
```
Add to your Claude Desktop config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "medorqis": {
      "command": "python3",
      "args": ["/path/to/MedOrqis/mcp_server/medorqis_mcp_server.py"]
    }
  }
}
```

---

## ⚖️ Governance & Regulatory Disclaimer
MedOrqis is an open-source clinical reference architecture and research framework. It is **NOT** a certified Medical Device (SaMD) and does not autonomously diagnose or prescribe. Clinical Decision Support must always be reviewed by a licensed healthcare professional. See [MEDICAL_DISCLAIMER.md](MEDICAL_DISCLAIMER.md) and [SAFETY_AND_GOVERNANCE.md](SAFETY_AND_GOVERNANCE.md) for full details.

---

## 📜 License
Licensed under the [Apache License, Version 2.0](LICENSE).
Medical vocabularies and guidelines are attributed in [DATA_LICENSES_AND_ATTRIBUTIONS.md](DATA_LICENSES_AND_ATTRIBUTIONS.md).
