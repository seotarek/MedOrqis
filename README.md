# MedOrqis — Medical AI Skills Ecosystem (v2.1.1)

[![Live Interactive Catalog](https://img.shields.io/badge/Live_Catalog-seotarek.github.io%2FMedOrqis-00e5a3?style=for-the-badge&logo=google-chrome&logoColor=black)](https://seotarek.github.io/MedOrqis/)
[![Skills CLI](https://img.shields.io/badge/Skills_CLI-npx_skills_add_seotarek%2FMedOrqis-6366f1?style=for-the-badge&logo=vercel)](https://github.com/vercel-labs/skills)
[![npm version](https://img.shields.io/badge/npm-v2.1.1-cb3837?style=for-the-badge&logo=npm)](https://www.npmjs.com/package/medorqis)
[![Verification: 100% Passed](https://img.shields.io/badge/Verification-100%25%20Passed-brightgreen.svg?style=for-the-badge)](tests/reports/VERIFICATION_REPORT.md)
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

## 🧮 The 12 Deterministic Zero-Token Clinical Calculators & Guardrails

All medical calculations in MedOrqis run in a pure Python deterministic engine with **zero token cost and mathematical invariance**.

| # | Calculator / Engine | Clinical Guideline & Standard | Safety Class | Deterministic Formula / Rule | Guardrail & Provenance Enforcement | Local Python Module |
|---|---|---|---|---|---|---|
| **1** | **CHA₂DS₂-VA** | ESC Guidelines 2024 (Sex-Neutral) | Class C | $\text{CHF}(1) + \text{HTN}(1) + \text{Age}(\ge 75: 2, 65\text{--}74: 1) + \text{DM}(1) + \text{Stroke}(2) + \text{Vasc}(1)$ | Refuses calculation if Age missing (`SAFE_ABSTENTION_DATA_DEFICIT`). Removes 1-point female bias. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **2** | **CHA₂DS₂-VASc** | ACC/AHA/ACCP/HRS 2023 | Class C | Traditional sex-differentiated stroke score ($+1$ for female sex). | Historical comparative baseline for US hospital guidelines. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **3** | **CKD-EPI 2021** | NKF-ASN Task Force / NEJM 2021 | Class C | Race-free adult creatinine eGFR formula ($142 \times \min(\text{SCr}/\kappa, 1)^\alpha \times \dots$). | **Hard Refusal** if patient Age $< 18$ years (`SAFE_REFUSAL_PEDIATRIC`). | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **4** | **Bedside Schwartz (2009)** | Schwartz GJ et al. (JASN 2009) | Class C | $\text{eGFR} = 0.413 \times \text{Height (cm)} / \text{SCr (mg/dL)}$. | **Hard Refusal** if patient Age $\ge 18$ years (`SAFE_REFUSAL_ADULT`). | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **5** | **Cockcroft-Gault CrCl** | FDA Renal Dosing Labeling Standards | Class C | $[(140 - \text{Age}) \times \text{Weight}] / (72 \times \text{SCr}) \times (0.85 \text{ if female})$. | Automatically calculates Ideal Body Weight (IBW) and Adjusted Body Weight (AdjBW $0.4$) if BMI $\ge 30$. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **6** | **Pediatric Dose Capper** | Nelson Pediatrics / AAP | Class C | $\text{Dose} = \min(\text{Weight (kg)} \times \text{mg/kg}, \text{Adult Max Ceiling})$. | Prevents fatal pediatric overdose by locking to adult maximum single and daily doses. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **7** | **HAS-BLED Bleeding Risk** | Pisters R et al. (Chest 2010) | Class C | HTN, Abnormal renal/liver, Stroke, Bleeding, Labile INR, Elderly ($>65$), Drugs/Alcohol. | Flags High Bleeding Risk ($\ge 3$); warns against unmonitored anticoagulation. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **8** | **CURB-65 Pneumonia** | British Thoracic Society (BTS) | Class C | Confusion, Urea $>7\,\text{mmol/L}$, $\text{RR} \ge 30$, $\text{BP} < 90/60$, $\text{Age} \ge 65$. | Stratifies 30-day mortality and dictates Outpatient vs Inpatient vs ICU admission. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **9** | **NEWS2 Early Warning** | Royal College of Physicians (2017) | Class C | Physiological scoring across RR, $\text{SpO}_2$, Temp, SBP, Pulse, Consciousness. | Automated sentinel sepsis and clinical deterioration escalation. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **10** | **Wells DVT Criteria** | Wells PS et al. (NEJM 2003) | Class C | Pre-test clinical probability of Deep Vein Thrombosis. | Categorizes DVT Unlikely vs Likely; guides D-dimer vs Compression Ultrasound. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **11** | **Wells PE Criteria** | Wells PS et al. (Ann Intern Med 2001) | Class C | Pre-test clinical probability of Pulmonary Embolism. | Categorizes PE Unlikely vs Likely; guides CT Pulmonary Angiography escalation. | [`core/clinical_calculators.py`](core/clinical_calculators.py) |
| **12** | **Deterministic DDI Engine** | FDA Black Box / Hansten & Horn | Class C | High-consequence contraindicated drug-drug interaction pairs. | Blocks fatal co-prescriptions (Warfarin + NSAIDs, Apixaban + Diclofenac, Sildenafil + Nitrates). | [`core/safety_guardrails.py`](core/safety_guardrails.py) |

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

Execute the harmonized clinical test suite (all 36 unit, safety, multilingual, and adapter tests):
```bash
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
