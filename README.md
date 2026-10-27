# MedOrqis — Medical AI Skills Ecosystem (v2.1.1)

[![Live Interactive Catalog](https://img.shields.io/badge/Live_Catalog-seotarek.github.io%2FMedOrqis-00e5a3?style=for-the-badge&logo=google-chrome&logoColor=black)](https://seotarek.github.io/MedOrqis/)
[![Skills CLI](https://img.shields.io/badge/Skills_CLI-npx_skills_add_seotarek%2FMedOrqis-6366f1?style=for-the-badge&logo=vercel)](https://github.com/vercel-labs/skills)
[![npm version](https://img.shields.io/badge/npm-v2.1.1-cb3837?style=for-the-badge&logo=npm)](https://www.npmjs.com/package/medorqis)
[![Verification: 36/36 Passed (100%)](https://img.shields.io/badge/Verification-36%2F36%20Passed%20(100%25)-brightgreen.svg?style=for-the-badge)](tests/reports/VERIFICATION_REPORT.md)
[![GitHub CI](https://img.shields.io/badge/GitHub_CI-passing-success.svg?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/seotarek/MedOrqis/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg?style=for-the-badge)](LICENSE)

**MedOrqis** is an open-source, evidence-grounded, cross-platform ecosystem of **24 specialized clinical AI skills**, **12 deterministic zero-token clinical calculators & safety engines**, and multi-platform adapters (Skills CLI, Claude Code, Gemini CLI, Model Context Protocol, and OpenAI).

> [!TIP]
> 🌐 **Interactive Web Hub & Live Zero-Token Calculators**:  
> Explore the live searchable 24-skill catalog, test interactive clinical calculators (ESC 2024 CHA₂DS₂-VA, CKD-EPI 2021, Bedside Schwartz, HAS-BLED, NEWS2, DDI Checker), and inspect dialect benchmarks directly in your browser at **[https://seotarek.github.io/MedOrqis/](https://seotarek.github.io/MedOrqis/)**.
> 
> ⚡ **Fleet Install in 1-Second (Claude Code, Cursor, Codex, Antigravity, OpenCode)**:  
> ```bash
> npx skills add seotarek/MedOrqis
> ```

Built with an **evidence-first, patient-safety-first architecture**, MedOrqis eliminates medical hallucination risks in high-stakes clinical calculations by executing arithmetic, unit conversions, PHI scrubbing, negation parsing, and drug interaction screenings through a **local, deterministic Python core with zero LLM API token overhead**.

---

## ⚡ 1-Minute Quick Start & Integration Options

### 🛠️ Option 1: One-Command Fleet Install (Skills CLI)
Install all 24 skills directly into your active coding agent workspace (Claude Code, Cursor, Antigravity, OpenCode, Codex):
```bash
# Install the complete MedOrqis ecosystem (all 24 skills)
npx skills add seotarek/MedOrqis

# Or install specific clinical skills:
npx skills add seotarek/MedOrqis --skill emergency-triage-redflags
npx skills add seotarek/MedOrqis --skill pharmacology-dosing-interactions
npx skills add seotarek/MedOrqis --skill pediatrics-neonatology
```

> ⭐ **Support Open-Source Clinical AI**: If MedOrqis helps your workflow or coding agents, please give the repo a **[Star on GitHub](https://github.com/seotarek/MedOrqis)** — it helps the project reach more clinicians and medical AI engineers!

---

### 📦 Option 2: NPX & NPM Interactive Terminal Package (`medorqis`)
Explore the catalog and copy prompts directly in your terminal:
```bash
# Run interactive CLI browser
npx medorqis

# List all 24 skills grouped by safety tier
npx medorqis list

# Print copyable Universal AI Prompt for web chat models
npx medorqis prompt

# Print MCP configuration JSON block
npx medorqis mcp
```
Or install globally or as a project dependency:
```bash
npm install -g medorqis
# or in Node.js apps:
npm install medorqis
```

---

### ⚡ Option 3: Universal AI Model Prompting (Zero Install — Any Model)
You do not need to install anything or run code to use MedOrqis with LLMs! You can send the repository link and prompt directly to **ChatGPT (with web access), Claude 3.5 Sonnet, Google Gemini, Cursor, Grok, or Antigravity**:

> **Copy & Paste into any AI model:**
> ```text
> Read the open-source clinical AI skills ecosystem MedOrqis at:
> https://github.com/seotarek/MedOrqis (Web catalog: https://seotarek.github.io/MedOrqis/)
> 
> You are now operating under MedOrqis clinical governance rules (v2.1.1):
> 1. Enforce zero-hallucination deterministic standards for all medical risk scores and formulas (CHA2DS2-VA ESC 2024, CKD-EPI 2021, Bedside Schwartz, Cockcroft-Gault, Wells DVT/PE, CURB-65, HAS-BLED, NEWS2, Pediatric Dose Capping).
> 2. Epistemic provenance: Never recommend high-risk interventions based on unconfirmed model hypotheses.
> 3. Missing Age Gatekeeper: If patient age is unrecorded, do NOT assume a default adult age (30); immediately flag SAFE_ABSTENTION_DATA_DEFICIT.
> 4. Sentinel Emergency Red Flags: Immediate emergency redirection on acute stroke (FAST), ACS crushing chest pain, anaphylaxis, septic shock, or anticoagulation + active bleeding.
> 5. Provide evidence-grounded differential diagnosis, drug interaction screening, and red-flag triage across all 24 MedOrqis clinical domains.
> 
> Please summarize your activated clinical skills and await clinical input.
> ```

---

### 🔌 Option 4: Model Context Protocol (MCP Server)
Run the local MCP stdio server:
```bash
python3 mcp_server/medorqis_mcp_server.py
```
Add to your Claude Desktop configuration (`claude_desktop_config.json`):
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

### 🐍 Option 5: Local Python Developer Setup
```bash
git clone https://github.com/seotarek/MedOrqis.git
cd MedOrqis
python3 -m pip install -e .
```

---

## 🧮 Pure Deterministic Clinical Calculators (`core/clinical_calculators.py`)

All medical calculations in MedOrqis execute with **zero LLM API token overhead and strict mathematical determinism** via pure Python functions in [`core/clinical_calculators.py`](core/clinical_calculators.py):

| # | Clinical Calculator | Function Name | Clinical Guideline & Standard | Target Population | Safety Gate & Boundary Enforcement |
|---|---|---|---|---|---|
| **1** | **CHA₂DS₂-VA** | `calculate_cha2ds2_va_esc2024` | ESC Guidelines 2024 (Sex-Neutral) | Adults ($\ge 18\text{y}$) with AF | Refuses if Age missing (`SAFE_ABSTENTION_DATA_DEFICIT`). Removes 1-point female bias. |
| **2** | **CHA₂DS₂-VASc** | `calculate_cha2ds2_vasc_aha2023` | ACC/AHA/ACCP/HRS 2023 | Adults ($\ge 18\text{y}$) with AF | Historical comparative baseline for US guidelines ($+1$ for female sex). |
| **3** | **CKD-EPI 2021** | `calculate_ckd_epi_2021_egfr` | NKF-ASN Task Force / NEJM 2021 | Adults ($\ge 18\text{y}$) | Race-free adult eGFR formula. **Hard Refusal** if Age $< 18$ years (`SAFE_REFUSAL_PEDIATRIC`). |
| **4** | **Bedside Schwartz** | `calculate_bedside_schwartz_egfr` | Schwartz GJ et al. (JASN 2009) | Pediatrics ($< 18\text{y}$) | Height-based eGFR ($0.413 \times \text{Ht}/\text{SCr}$). **Hard Refusal** if Age $\ge 18$ years (`SAFE_REFUSAL_ADULT`). |
| **5** | **Cockcroft-Gault** | `calculate_cockcroft_gault_crcl` | FDA Renal Dosing Standards | Adults ($\ge 18\text{y}$) | Automatically calculates IBW and Adjusted Body Weight (AdjBW $0.4$) if BMI $\ge 30$. |
| **6** | **HAS-BLED** | `calculate_has_bled_score` | Pisters R et al. (Chest 2010) | Adults on Anticoagulation | Flags High Bleeding Risk ($\ge 3$); warns against unmonitored DOAC initiation. |
| **7** | **CURB-65** | `calculate_curb65_score` | British Thoracic Society (BTS) | Adults with CAP | Stratifies 30-day mortality risk (Outpatient vs Inpatient vs ICU admission). |
| **8** | **NEWS2** | `calculate_news2_score` | Royal College of Physicians (2017) | Acute Inpatient Care | Physiological aggregate triage across 6 vital signs; automated sepsis escalation. |
| **9** | **Wells DVT Criteria** | `calculate_wells_dvt_score` | Wells PS et al. (NEJM 2003) | Suspected DVT | Pre-test probability (Unlikely vs Likely); dictates D-dimer vs Compression Ultrasound. |
| **10** | **Wells PE Criteria** | `calculate_wells_pe_score` | Wells PS et al. (Ann Intern Med 2001) | Suspected PE | Pre-test probability (Unlikely vs Likely); dictates D-dimer vs CT Pulmonary Angiography. |

*(Auxiliary dosing & safety engines: `calculate_pediatric_weight_dose` & `calculate_mosteller_bsa` in `core/clinical_calculators.py`, and Contraindicated DDI Screening in `core/safety_guardrails.py`)*.

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

## 🌐 Multilingual & Dialect Regression Benchmark

MedOrqis includes a deterministic natural language processing normalizer verified across **126 curated synthetic test fixtures**:
- **100 Syntactic Negation Sentences**: Handcrafted fixtures verifying regex boundary detection and clause-stop logic across 8 dialects and languages: Modern Standard Arabic (`ar-MSA`), Egyptian (`ar-EG`), Gulf (`ar-GULF`), Levantine (`ar-LEV`), Maghrebi (`ar-MAG`), English (`en-US/GB`), French (`fr-FR`), and Spanish (`es-ES`).
- **10 BiDi & Unit Token Strings**: Numerical and unit strings verifying bidirectional layout preservation (e.g. Arabic RTL mixing English numbers/units like "500 mg").
- **16 Trade Brand-to-INN Mappings**: Lookup fixtures mapping regional commercial trade brand names to generic International Nonproprietary Names (e.g. Panadol $\to$ Paracetamol).

> [!CAUTION]
> **Two-Axis Governance Separation**:
> - **Automated Syntactic Unit-Test Pass Rate**: **100.0% (126/126 passed)**.
> - **Bedside Real-World Clinical Validation**: **0.0% (UNVALIDATED IN-VIVO / PENDING CLINICAL TRIALS)**.
> 
> See full breakdown and statistical caveats in [LANGUAGE_COVERAGE_MATRIX.md](LANGUAGE_COVERAGE_MATRIX.md).

---

## 🧪 Automated Verification & Provenance

Execute cryptographic file integrity verification and the harmonized clinical test suite (all 36 unit, safety, multilingual, and adapter tests):
```bash
# 1. Verify SHA-256 cryptographic fingerprints across all 45 modules
python3 core/integrity_manifest.py --verify

# 2. Execute the harmonized clinical test suite
python3 tests/run_all_tests.py
```
This automatically verifies:
1. `tests/unit/test_clinical_calculators.py`: Boundary and formula correctness for all 12 clinical engines.
2. `tests/safety/test_safety_and_provenance.py`: Epistemic provenance gates, missing age gatekeeper, sentinel emergency red-flags, and contraindicated DDIs.
3. `tests/multilingual/test_multilingual_benchmark.py`: Negation preservation, BiDi unit fidelity, and brand-to-INN mapping across 126 test cases.
4. `tests/platform_adapters/test_security_and_adapters.py`: SHA-256 cryptographic file integrity manifest, PHI scrubbing, prompt injection defense, and MCP JSON-RPC protocol.

Artifacts generated:
- [VERIFICATION_REPORT.md](tests/reports/VERIFICATION_REPORT.md)
- [LANGUAGE_COVERAGE_MATRIX.md](LANGUAGE_COVERAGE_MATRIX.md)
- [file_integrity_manifest.json](governance/file_integrity_manifest.json)

---

## ⚖️ Governance & Regulatory Disclaimer
MedOrqis is an open-source clinical reference architecture and research framework. It is **NOT** a certified Medical Device (SaMD) and does not autonomously diagnose or prescribe. Clinical Decision Support outputs must always be reviewed by a licensed healthcare professional. See [MEDICAL_DISCLAIMER.md](MEDICAL_DISCLAIMER.md) and [SAFETY_AND_GOVERNANCE.md](SAFETY_AND_GOVERNANCE.md).

---

## 📜 License
Licensed under the [Apache License, Version 2.0](LICENSE).
Medical vocabularies and guidelines are attributed in [DATA_LICENSES_AND_ATTRIBUTIONS.md](DATA_LICENSES_AND_ATTRIBUTIONS.md).
