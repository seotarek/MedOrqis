# MedOrqis — Medical AI Skills Catalog (v2.1.0)

[![Verification: 100% Passed](https://img.shields.io/badge/Verification-100%25%20Passed-brightgreen.svg)](tests/reports/VERIFICATION_REPORT.md)
[![Safety: IEC 62304 / ISO 14971](https://img.shields.io/badge/Safety%20Class-Class%20A%20%7C%20B%20%7C%20C-red.svg)](SAFETY_AND_GOVERNANCE.md)
[![Skills: 24 Registered](https://img.shields.io/badge/Skills-24%20Medical%20Skills-teal.svg)](skills/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

Welcome to the official catalog of **MedOrqis (v2.1.0)** — an evidence-grounded, cross-platform ecosystem of **24 risk-stratified medical AI skills**, deterministic zero-token clinical calculators, and multi-platform adapters (Skills CLI, Claude Code, Gemini CLI, Model Context Protocol, and OpenAI).

---

## ⚡ Architecture & Zero-Token Foundation

1. **Zero LLM Token Overhead**:
   - All high-stakes calculations ($\text{CHA}_2\text{DS}_2\text{-VA}$ ESC 2024, $\text{CHA}_2\text{DS}_2\text{-VASc}$ AHA 2023, race-free CKD-EPI 2021, Bedside Schwartz pediatric eGFR, Cockcroft-Gault CrCl with obesity IBW/AdjBW, pediatric weight dose capping, HAS-BLED bleeding risk, NEWS2 inpatient deterioration score, CURB-65 pneumonia risk, Wells DVT & PE), critical drug-drug interaction (DDI) screening, PHI redaction, and prompt injection defense execute **locally in deterministic Python Standard Library** with zero API token consumption.
2. **Epistemic Provenance Enforcement**:
   - Downstream skills are architecturally prohibited from dosing or recommending irreversible treatments based on an AI hypothesis (`MODEL_INFERRED_HYPOTHESIS`) or empty provenance. High-risk actions strictly require confirmed `DOCUMENTED_CLINICAL_RECORD` provenance.
3. **Multilingual Negation & BiDi Fidelity**:
   - 100% negation preservation with clause-stop boundaries (`لكن`, `إلا`, `بينما`, `but`, `however`, `mais`, `pero`) across Modern Standard Arabic, Egyptian Arabic, Gulf Arabic, Levantine Arabic, Maghrebi Arabic, English, French, and Spanish, with BiDi numerical layout protection.


---

## 📦 Quick Installation & Multi-Platform Usage

### 1. Install via Skills CLI (`npx skills`)
Install the entire MedOrqis ecosystem into your active agent workspace:
```bash
npx skills add seotarek/MedOrqis
```
Or install individual skills by name:
```bash
npx skills add seotarek/MedOrqis --skill emergency-triage-redflags
npx skills add seotarek/MedOrqis --skill pharmacology-dosing-interactions
npx skills add seotarek/MedOrqis --skill pediatrics-neonatology
```

### 2. Model Context Protocol (MCP) Server
Launch the live stdio JSON-RPC 2.0 daemon:
```bash
python3 mcp_server/medorqis_mcp_server.py
```
Add to your Claude Desktop or Cursor configuration (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "medorqis": {
      "command": "python3",
      "args": ["/absolute/path/to/MedOrqis/mcp_server/medorqis_mcp_server.py"]
    }
  }
}
```

#### Available MCP Tools:
- `calculate_clinical_score`: Zero-token calculations for CHA2DS2-VA (ESC 2024), CHA2DS2-VASc (AHA 2023), CKD-EPI 2021, Bedside Schwartz pediatric eGFR, Cockcroft-Gault CrCl, Pediatric Dose Capping, Mosteller BSA, HAS-BLED bleeding risk, NEWS2 deterioration score, CURB-65 pneumonia severity, Wells DVT and PE.
- `check_drug_interactions`: Screens regimens against lethal contraindications (Warfarin+NSAID, DOAC+NSAID, Sildenafil+Nitrates, Spironolactone+ACEi, pregnancy teratogens) with regional trade brand mapping (Egyptian, Gulf, International).
- `check_red_flags`: Evaluates multi-symptom clinical emergency red flags with clause-stop negation filtering.
- `scrub_phi`: Redacts Egyptian National IDs (14 digits), Saudi Iqamas (10 digits), MRNs, phone numbers, and emails.
- `scan_prompt_security`: Defends against clinical prompt injection and safety rule override attacks.


### 3. Claude Code CLI
MedOrqis is packaged for Claude Code under `adapters/claude/claude-skill-package.json`. Place in `~/.claude/skills/` or use directly within Claude Code.

### 4. Gemini CLI Extension
Configured via `adapters/gemini/gemini-extension.json` and guided by `adapters/gemini/GEMINI.md`.

### 5. Local Python Developer Setup
```bash
git clone https://github.com/seotarek/MedOrqis.git
cd MedOrqis
python3 -m pip install -e .
python3 tests/run_all_tests.py
```

---

## 📋 The 24-Skill Master Matrix

| # | Skill Name | Tier | Safety Class | Key Keywords (EN & AR) | Primary Focus | Installation Command |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | [`medorqis-orchestrator`](skills/medorqis-orchestrator/) | Tier 1 | Class A | `orchestrator`, `routing`, `provenance`, `توجيه-سريري` | Context envelope routing & conflict detection | `npx skills add seotarek/MedOrqis --skill medorqis-orchestrator` |
| **02** | [`ebm-research-biostatistics`](skills/ebm-research-biostatistics/) | Tier 1 | Class A | `ebm`, `pico`, `rob-2`, `grade`, `nnt`, `طب-مسند-بالدليل` | Evidence appraisal, CASP, RoB-2, GRADE | `npx skills add seotarek/MedOrqis --skill ebm-research-biostatistics` |
| **03** | [`medical-documentation-translation`](skills/medical-documentation-translation/) | Tier 1 | Class A | `soap`, `sbar`, `translation`, `bidi`, `توثيق-طبي` | SOAP notes, SBAR handoffs, BiDi translation | `npx skills add seotarek/MedOrqis --skill medical-documentation-translation` |
| **04** | [`healthcare-ops-telemedicine-ehr`](skills/healthcare-ops-telemedicine-ehr/) | Tier 1 | Class A | `telemedicine`, `hl7`, `fhir`, `ehr`, `طب-عن-بعد` | HL7 FHIR resource mapping & intake triage | `npx skills add seotarek/MedOrqis --skill healthcare-ops-telemedicine-ehr` |
| **05** | [`health-cybersecurity-privacy`](skills/health-cybersecurity-privacy/) | Tier 1 | Class A | `phi`, `hipaa`, `gdpr`, `pdpl`, `خصوصية-المرضى` | PHI scrubbing & prompt injection defense | `npx skills add seotarek/MedOrqis --skill health-cybersecurity-privacy` |
| **06** | [`public-health-epidemiology`](skills/public-health-epidemiology/) | Tier 1 | Class A | `epidemiology`, `screening`, `ipc`, `صحة-عامة` | Outbreak dynamics, screening metrics, IPC | `npx skills add seotarek/MedOrqis --skill public-health-epidemiology` |
| **07** | [`differential-diagnosis-cds`](skills/differential-diagnosis-cds/) | Tier 2 | Class B | `differential`, `vindicate`, `cds`, `تشخيص-تفريقي` | VINDICATE differential diagnosis & workup | `npx skills add seotarek/MedOrqis --skill differential-diagnosis-cds` |
| **08** | [`laboratory-medicine-pathology`](skills/laboratory-medicine-pathology/) | Tier 2 | Class B | `labs`, `panic-values`, `loinc`, `تحاليل-طبية` | Critical lab alert panic thresholds & LOINC | `npx skills add seotarek/MedOrqis --skill laboratory-medicine-pathology` |
| **09** | [`radiology-medical-imaging`](skills/radiology-medical-imaging/) | Tier 2 | Class B | `radiology`, `mri`, `ct-scan`, `alara`, `أشعة` | ACR Appropriateness & contrast safety | `npx skills add seotarek/MedOrqis --skill radiology-medical-imaging` |
| **10** | [`internal-medicine-chronic`](skills/internal-medicine-chronic/) | Tier 2 | Class B | `chronic-disease`, `diabetes`, `ckd`, `أمراض-مزمنة` | Multi-morbidity chronic care plans (KDIGO/ADA) | `npx skills add seotarek/MedOrqis --skill internal-medicine-chronic` |
| **11** | [`infectious-diseases-stewardship`](skills/infectious-diseases-stewardship/) | Tier 2 | Class B | `antimicrobial`, `antibiotics`, `idsa`, `مضادات-حيوية` | Antimicrobial stewardship & antibiogram checks | `npx skills add seotarek/MedOrqis --skill infectious-diseases-stewardship` |
| **12** | [`nursing-clinical-care`](skills/nursing-clinical-care/) | Tier 2 | Class B | `nursing`, `news2`, `braden-scale`, `تمريض` | NEWS2 early warning score & Braden scale | `npx skills add seotarek/MedOrqis --skill nursing-clinical-care` |
| **13** | [`clinical-nutrition-dietetics`](skills/clinical-nutrition-dietetics/) | Tier 2 | Class B | `nutrition`, `dietetics`, `bmi`, `تغذية-علاجية` | Caloric/protein requirements & enteral diets | `npx skills add seotarek/MedOrqis --skill clinical-nutrition-dietetics` |
| **14** | [`rehabilitation-physical-therapy`](skills/rehabilitation-physical-therapy/) | Tier 2 | Class B | `physical-therapy`, `rehab`, `fim`, `علاج-طبيعي` | Post-op and stroke mobility protocols | `npx skills add seotarek/MedOrqis --skill rehabilitation-physical-therapy` |
| **15** | [`emergency-triage-redflags`](skills/emergency-triage-redflags/) | Tier 3 | Class C | `emergency`, `red-flags`, `abcde`, `طوارئ` | Time-sensitive triage & emergency redirection | `npx skills add seotarek/MedOrqis --skill emergency-triage-redflags` |
| **16** | [`clinical-safety-auditor`](skills/clinical-safety-auditor/) | Tier 3 | Class C | `safety-gate`, `audit`, `anticoagulation`, `تدقيق-أمان` | Pre-output audit gate & conflict interception | `npx skills add seotarek/MedOrqis --skill clinical-safety-auditor` |
| **17** | [`pharmacology-dosing-interactions`](skills/pharmacology-dosing-interactions/) | Tier 3 | Class C | `pharmacology`, `cockcroft-gault`, `ddi`, `جرعات-دوائية` | Renal/hepatic adjustments & lethal DDI blocks | `npx skills add seotarek/MedOrqis --skill pharmacology-dosing-interactions` |
| **18** | [`clinical-toxicology-overdose`](skills/clinical-toxicology-overdose/) | Tier 3 | Class C | `toxicology`, `toxidrome`, `antidote`, `تسمم` | Toxidrome recognition & antidote triage | `npx skills add seotarek/MedOrqis --skill clinical-toxicology-overdose` |
| **19** | [`pediatrics-neonatology`](skills/pediatrics-neonatology/) | Tier 3 | Class C | `pediatrics`, `dose-capping`, `apgar`, `طب-أطفال` | Pediatric weight dosing & adult dose hard-caps | `npx skills add seotarek/MedOrqis --skill pediatrics-neonatology` |
| **20** | [`obstetrics-gynecology`](skills/obstetrics-gynecology/) | Tier 3 | Class C | `obgyn`, `pregnancy`, `pre-eclampsia`, `نساء-وتوليد` | Maternal red flags & pregnancy drug safety | `npx skills add seotarek/MedOrqis --skill obstetrics-gynecology` |
| **21** | [`geriatrics-polypharmacy`](skills/geriatrics-polypharmacy/) | Tier 3 | Class C | `geriatrics`, `beers-criteria`, `stopp-start`, `طب-المسنين` | 2023 AGS Beers Criteria & fall risk screening | `npx skills add seotarek/MedOrqis --skill geriatrics-polypharmacy` |
| **22** | [`mental-health-psychiatry`](skills/mental-health-psychiatry/) | Tier 3 | Class C | `psychiatry`, `suicide-screening`, `crisis`, `طب-نفسي` | Suicide crisis escalation & psychotropic checks | `npx skills add seotarek/MedOrqis --skill mental-health-psychiatry` |
| **23** | [`perioperative-surgical-care`](skills/perioperative-surgical-care/) | Tier 3 | Class C | `surgery`, `rcri`, `pre-op-clearance`, `جراحة` | RCRI cardiac risk & antithrombotic bridging | `npx skills add seotarek/MedOrqis --skill perioperative-surgical-care` |
| **24** | [`oncology-palliative-care`](skills/oncology-palliative-care/) | Tier 3 | Class C | `oncology`, `palliative`, `febrile-neutropenia`, `أورام` | Oncologic emergencies & opioid conversions | `npx skills add seotarek/MedOrqis --skill oncology-palliative-care` |

---

## 🔍 Detailed Skill Profiles

### Tier 1: Governance, Research & Operations (Class A)

#### 1. `medorqis-orchestrator`
- **Purpose**: Coordinates multi-skill clinical evaluation workflows, routes patient queries, and enforces epistemic provenance boundaries.
- **Keywords**: `orchestrator`, `routing`, `clinical-context`, `epistemic-provenance`, `conflict-detection`, `workflow`, `توجيه-سريري`, `سياق-سريري`
- **Deterministic Dependencies**: `core.context_validator`, `core.safety_guardrails`
- **Prohibited Uses**: Autonomous final diagnosis; direct medication prescribing.
- **Guideline Authority**: MedOrqis Architectural & Governance Framework v2.0 (ISO 14971/IEC 62304)

#### 2. `ebm-research-biostatistics`
- **Purpose**: Formulates PICO clinical questions, conducts CASP and RoB-2 risk of bias appraisals, computes biostatistical parameters (OR, RR, NNT), and assigns GRADE evidence certainty.
- **Keywords**: `ebm`, `biostatistics`, `pico`, `casp`, `rob-2`, `grade`, `odds-ratio`, `relative-risk`, `nnt`, `cochrane`, `طب-مسند-بالدليل`, `إحصاء-حيوي`
- **Deterministic Dependencies**: `core.citation_validator`, `core.claim_entailment_verifier`
- **Prohibited Uses**: Fabricating citations or trial results; unsupervised clinical care.
- **Guideline Authority**: Cochrane Handbook for Systematic Reviews / GRADE Working Group

#### 3. `medical-documentation-translation`
- **Purpose**: Synthesizes clinical encounters into standardized SOAP notes and SBAR handoffs. Provides semantic-preserving cross-lingual translation with strict negation polarity preservation.
- **Keywords**: `soap`, `sbar`, `clinical-notes`, `medical-translation`, `bidi`, `negation`, `terminology`, `ترجمة-طبية`, `توثيق-طبي`
- **Deterministic Dependencies**: `core.terminology_normalizer`, `core.phi_deidentifier`
- **Prohibited Uses**: Altering documented clinical facts; unsupervised patient discharge.
- **Guideline Authority**: Joint Commission SBAR Standards / AAHIM Clinical Documentation Guidelines

#### 4. `healthcare-ops-telemedicine-ehr`
- **Purpose**: Facilitates structured clinical data exchange via HL7 FHIR R4 and manages digital telemedicine intake triage criteria.
- **Keywords**: `telemedicine`, `hl7`, `fhir`, `ehr`, `intake-triage`, `scheduling`, `interoperability`, `طب-عن-بعد`, `سجلات-صحية`
- **Deterministic Dependencies**: `core.phi_deidentifier`, `core.terminology_connectors`
- **Prohibited Uses**: Bypassing informed consent; altering audit trails.
- **Guideline Authority**: HL7 FHIR R4 Specification / ATA Telemedicine Practice Guidelines

#### 5. `health-cybersecurity-privacy`
- **Purpose**: De-identifies Protected Health Information (HIPAA Safe Harbor, GDPR, Egyptian PDPL, Saudi PDPL) and blocks prompt injections attempting to bypass clinical safety bounds.
- **Keywords**: `phi`, `hipaa`, `gdpr`, `pdpl`, `de-identification`, `prompt-injection`, `redaction`, `أمان-صحي`, `خصوصية-المرضى`
- **Deterministic Dependencies**: `core.phi_deidentifier`, `core.prompt_security_guard`
- **Prohibited Uses**: Transmitting raw identified patient data to public services.
- **Guideline Authority**: HIPAA Privacy Rule / EU GDPR Article 9 / ISO 27799 Health Informatics

#### 6. `public-health-epidemiology`
- **Purpose**: Computes epidemiological screening indices (sensitivity, specificity, PPV, NPV), analyzes disease outbreak transmission dynamics, and references infection prevention protocols.
- **Keywords**: `epidemiology`, `public-health`, `screening`, `sensitivity`, `specificity`, `ipc`, `outbreak`, `صحة-عامة`, `وبائيات`
- **Deterministic Dependencies**: `core.citation_validator`
- **Prohibited Uses**: Issuing unverified public quarantine orders.
- **Guideline Authority**: WHO Outbreak Communication Guidelines / CDC Field Epidemiology Manual

---

### Tier 2: Diagnostic & Chronic Care Support (Class B)

#### 7. `differential-diagnosis-cds`
- **Purpose**: Constructs structured VINDICATE differential diagnoses, highlights must-not-miss life-threatening conditions, and proposes prioritized diagnostic workups.
- **Keywords**: `differential-diagnosis`, `vindicate`, `clinical-decision-support`, `cds`, `symptom-checker`, `workup`, `تشخيص-تفريقي`
- **Deterministic Dependencies**: `core.context_validator`, `core.safety_guardrails`
- **Prohibited Uses**: Autonomous definitive diagnosis; excluding emergency conditions without objective tests.
- **Guideline Authority**: Society to Improve Diagnosis in Medicine (SIDM) / BMJ Best Practice

#### 8. `laboratory-medicine-pathology`
- **Purpose**: Interprets lab profiles (CBC, BMP, LFTs, Coagulation, ABG), flags critical panic thresholds, and maps parameters to LOINC concepts.
- **Keywords**: `laboratory`, `panic-values`, `loinc`, `critical-labs`, `biochemistry`, `hematology`, `pathology`, `تحاليل-طبية`, `قيم-حرجة`
- **Deterministic Dependencies**: `core.context_validator`
- **Prohibited Uses**: Overriding clinical lab delta checks; ignoring critical panic value alerts.
- **Guideline Authority**: CLSI Laboratory Safety & Panic Value Guidelines / IFCC LOINC Standards

#### 9. `radiology-medical-imaging`
- **Purpose**: Selects appropriate imaging modalities based on clinical presentation and radiation risk vs diagnostic yield using ACR Appropriateness Criteria.
- **Keywords**: `radiology`, `imaging`, `mri`, `ct-scan`, `x-ray`, `ultrasound`, `acr-criteria`, `alara`, `أشعة`, `تصوير-طبي`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.context_validator`
- **Prohibited Uses**: Primary reading of raw DICOM images; ordering IV contrast in acute kidney injury without prophylaxis.
- **Guideline Authority**: ACR Appropriateness Criteria (2024) / ESUR Contrast Media Guidelines

#### 10. `internal-medicine-chronic`
- **Purpose**: Formulates guideline-concordant care plans for diabetes, hypertension, heart failure, and chronic kidney disease across multi-morbid patients.
- **Keywords**: `internal-medicine`, `chronic-disease`, `diabetes`, `hypertension`, `ckd`, `copd`, `heart-failure`, `kdigo`, `باطنة`, `أمراض-مزمنة`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.safety_guardrails`
- **Prohibited Uses**: Autonomous insulin dose titration without blood glucose logs.
- **Guideline Authority**: ADA Standards of Care in Diabetes 2024 / KDIGO CKD Guidelines / ESC Heart Failure Guidelines

#### 11. `infectious-diseases-stewardship`
- **Purpose**: Recommends guideline-directed antimicrobial regimens, dosage adjustments for renal clearance, and prevents inappropriate broad-spectrum antibiotic usage.
- **Keywords**: `infectious-diseases`, `antimicrobial-stewardship`, `antibiotics`, `sepsis`, `antibiogram`, `resistance`, `idsa`, `مضادات-حيوية`, `أمراض-معدية`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.context_validator`
- **Prohibited Uses**: Ignoring local antibiograms or positive blood culture sensitivities.
- **Guideline Authority**: IDSA Guidelines / Sanford Guide to Antimicrobial Therapy / WHO AWaRe

#### 12. `nursing-clinical-care`
- **Purpose**: Computes National Early Warning Scores (NEWS2), monitors pressure ulcer risk via Braden Scale, and supports inpatient nursing care plans.
- **Keywords**: `nursing`, `news2`, `braden-scale`, `vital-signs`, `wound-care`, `patient-safety`, `care-plan`, `تمريض`, `رعاية-سريرية`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.safety_guardrails`
- **Prohibited Uses**: Discontinuing nursing vital sign observations in high-risk patients.
- **Guideline Authority**: Royal College of Physicians NEWS2 Guidelines / NPUAP Braden Scale

#### 13. `clinical-nutrition-dietetics`
- **Purpose**: Calculates basal metabolic and protein requirements, manages therapeutic diet restrictions, and screens for food-drug interactions.
- **Keywords**: `nutrition`, `dietetics`, `bmi`, `harris-benedict`, `enteral-feeding`, `malnutrition`, `food-drug-interactions`, `تغذية-علاجية`
- **Deterministic Dependencies**: `core.clinical_calculators`
- **Prohibited Uses**: Formulating TPN without daily electrolyte and liver function monitoring.
- **Guideline Authority**: ASPEN / ESPEN Clinical Nutrition Guidelines

#### 14. `rehabilitation-physical-therapy`
- **Purpose**: Designs post-operative, stroke, and musculoskeletal recovery protocols while evaluating hemodynamic and spinal exercise contraindications.
- **Keywords**: `physical-therapy`, `rehabilitation`, `stroke-rehab`, `post-op-rehab`, `mobility`, `fim`, `علاج-طبيعي`, `تأهيل`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.safety_guardrails`
- **Prohibited Uses**: Mobilizing patients with unstable spinal fractures or acute untreated DVT.
- **Guideline Authority**: AHA/ASA Stroke Rehabilitation Guidelines / APTA Practice Guidelines

---

### Tier 3: High-Risk, Emergency & Vulnerable Populations (Class C)

#### 15. `emergency-triage-redflags`
- **Purpose**: Identifies time-sensitive, life-threatening clinical emergencies (ABCDE primary survey, Sepsis, ACS, Acute Stroke, Anaphylaxis) and directs patients to emergency care immediately.
- **Keywords**: `emergency`, `red-flags`, `triage`, `abcde`, `chest-pain`, `stroke`, `anaphylaxis`, `trauma`, `طوارئ`, `علامات-خطيرة`
- **Deterministic Dependencies**: `core.safety_guardrails`
- **Prohibited Uses**: Delaying emergency medical transfer; outpatient management of unstable patients.
- **Guideline Authority**: Manchester Triage System / Emergency Severity Index (ESI) / Surviving Sepsis 2021 / AHA ACLS

#### 16. `clinical-safety-auditor`
- **Purpose**: Pre-output clinical safety auditor. Intercepts clinical contradictions (such as anticoagulants during an active gastrointestinal bleed), enforces dose caps, and checks epistemic provenance.
- **Keywords**: `safety-gate`, `audit`, `contraindications`, `anticoagulation-bleed`, `inter-skill-conflict`, `safe-abstention`, `تدقيق-أمان`, `أمان-سريري`
- **Deterministic Dependencies**: `core.context_validator`, `core.citation_validator`, `core.safety_guardrails`
- **Prohibited Uses**: Suppressing detected safety alerts; allowing unvalidated hypotheses to trigger medication changes.
- **Guideline Authority**: FDA Clinical Decision Support Guidance / ISO 14971 Medical Device Risk Controls

#### 17. `pharmacology-dosing-interactions`
- **Purpose**: Calculates precise drug dosages based on weight and renal function (Cockcroft-Gault / eGFR) and blocks fatal drug-drug interactions.
- **Keywords**: `pharmacology`, `drug-interactions`, `renal-dosing`, `cockcroft-gault`, `hepatic-adjustment`, `crcl`, `ddi`, `صيدلة-إكلينيكية`, `جرعات-دوائية`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.context_validator`
- **Prohibited Uses**: Calculating chemotherapy or NTI dosing without serum levels and renal markers.
- **Guideline Authority**: FDA Drug Labeling / BNF / Stockley's Drug Interactions (2024)

#### 18. `clinical-toxicology-overdose`
- **Purpose**: Recognizes acute toxidromes (anticholinergic, cholinergic, opioid, sympathomimetic, sedative), advises on specific antidotes (e.g. naloxone), and escalates to Poison Control.
- **Keywords**: `toxicology`, `overdose`, `toxidrome`, `antidote`, `naloxone`, `poison-control`, `paracetamol-overdose`, `تسمم`, `جرعة-زائدة`
- **Deterministic Dependencies**: `core.safety_guardrails`
- **Prohibited Uses**: Recommending induction of emesis or home remedies for caustic ingestions.
- **Guideline Authority**: American Academy of Clinical Toxicology (AACT) / EAPCCT Guidelines

#### 19. `pediatrics-neonatology`
- **Purpose**: Enforces strict weight-based pediatric dosing with hard adult maximum dose caps. Flags age-weight unit confusion and screens for neonatal red flags.
- **Keywords**: `pediatrics`, `neonatology`, `pediatric-dosing`, `weight-based-dosing`, `dose-capping`, `apgar`, `طب-أطفال`, `حديثي-الولادة`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.context_validator`, `core.safety_guardrails`
- **Prohibited Uses**: Dosing pediatric medications without verified weight in kilograms.
- **Guideline Authority**: Nelson Textbook of Pediatrics (22nd Ed) / AAP Guidelines / WHO IMCI

#### 20. `obstetrics-gynecology`
- **Purpose**: Screens for pre-eclampsia/eclampsia, ectopic pregnancy, postpartum hemorrhage, and verifies medication safety during pregnancy and lactation.
- **Keywords**: `obgyn`, `pregnancy`, `lactation`, `teratogenic`, `pre-eclampsia`, `gestational-diabetes`, `postpartum`, `نساء-وتوليد`, `حمل-ورضاعة`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.context_validator`, `core.safety_guardrails`
- **Prohibited Uses**: Prescribing Category X or known teratogenic agents (ACE inhibitors, ARBs, methotrexate, isotretinoin) in pregnancy.
- **Guideline Authority**: ACOG Practice Bulletins / RCOG Green-top Guidelines / Briggs Drugs in Pregnancy

#### 21. `geriatrics-polypharmacy`
- **Purpose**: Reviews elderly medication regimens against the 2023 AGS Beers Criteria and STOPP/START v3, flags anticholinergic cognitive burden, and identifies fall risks.
- **Keywords**: `geriatrics`, `polypharmacy`, `beers-criteria`, `stopp-start`, `fall-risk`, `anticholinergic-burden`, `طب-المسنين`, `تعدد-الأدوية`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.context_validator`
- **Prohibited Uses**: Abruptly discontinuing chronic psychoactive or cardiac medications without tapering.
- **Guideline Authority**: 2023 AGS Beers Criteria / STOPP/START Criteria Version 3

#### 22. `mental-health-psychiatry`
- **Purpose**: Detects acute psychiatric crises (active suicidal ideation, severe psychosis, mania), initiates emergency crisis redirection, and monitors psychotropic drug interactions (Serotonin Syndrome, QTc prolongation).
- **Keywords**: `psychiatry`, `mental-health`, `suicide-screening`, `crisis-triage`, `ssri`, `qt-prolongation`, `depression`, `صحة-نفسية`, `طب-نفسي`
- **Deterministic Dependencies**: `core.safety_guardrails`
- **Prohibited Uses**: Delaying crisis intervention for suicidal patients; autonomous medication changes in severe psychiatric conditions.
- **Guideline Authority**: APA Practice Guidelines / Columbia Suicide Severity Rating Scale (C-SSRS)

#### 23. `perioperative-surgical-care`
- **Purpose**: Calculates Revised Cardiac Risk Index (RCRI), guides pre-operative antithrombotic interruption and bridging, and evaluates for acute surgical abdomen.
- **Keywords**: `surgery`, `perioperative`, `rcri`, `pre-op-clearance`, `anticoagulation-bridging`, `who-surgical-checklist`, `جراحة`, `تخدير`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.safety_guardrails`
- **Prohibited Uses**: Permitting elective surgery in unstratified high-risk cardiac patients.
- **Guideline Authority**: 2024 AHA/ACC Perioperative Cardiovascular Evaluation Guidelines / ASA Physical Status

#### 24. `oncology-palliative-care`
- **Purpose**: Identifies oncologic emergencies (febrile neutropenia, cord compression, tumor lysis) requiring immediate admission, and provides palliative pain and opioid rotation algorithms.
- **Keywords**: `oncology`, `palliative-care`, `febrile-neutropenia`, `pain-management`, `opioid-conversion`, `tumor-lysis`, `أورام`, `رعاية-تلطيفية`
- **Deterministic Dependencies**: `core.clinical_calculators`, `core.safety_guardrails`
- **Prohibited Uses**: Delaying broad-spectrum antibiotics in suspected neutropenic fever; prescribing chemotherapy without oncology sign-off.
- **Guideline Authority**: ASCO / NCCN Clinical Practice Guidelines / ESMO Palliative Care Guidelines

---

## 🛡️ Clinical Governance & Safety Verification

All 24 skills and deterministic calculators are verified against published clinical literature without statistical approximations.
- Full automated test suite: `python3 tests/run_all_tests.py`
- Formal verification report: [tests/reports/VERIFICATION_REPORT.md](tests/reports/VERIFICATION_REPORT.md)
- Clinical specialist review register: [governance/clinical_review_registry.json](governance/clinical_review_registry.json)
