# MedOrqis — Data Licenses, Attribution & Redistribution Policy

## 1. Proprietary & Restricted Medical Terminology Policy
To ensure full compliance with international copyright and data licensing standards:
- **No Unlicensed Database Dumps**: This repository does NOT dump, redistribute, or mirror full proprietary or restricted terminology databases (e.g., full SNOMED CT releases, LOINC databases, or proprietary drug compendia).
- **Curated Educational Subset**: Local dictionaries (`dictionaries/`) contain only small, license-compliant reference subsets (<200 high-frequency terms) explicitly selected for testing deterministic algorithms, negation detection, and safety guardrails.
- **Official API Connectors**: For production or institutional deployments requiring comprehensive terminology coverage, MedOrqis provides standard connector interfaces (`core/terminology_connectors.py`) that integrate with official APIs and FHIR Terminology Servers using your institution's authorized credentials:
  - **WHO ICD-11 API**: Access via [WHO ICD-11 Maintenance Platform](https://icd.who.int/icdapi).
  - **NLM UMLS & RxNav API**: Access via [U.S. National Library of Medicine](https://rxnav.nlm.nih.gov/).
  - **SNOMED CT International**: Access via national release centers under SNOMED International affiliate licenses.
  - **LOINC (Regenstrief Institute)**: Access subject to the [LOINC Terms of Use](https://loinc.org/terms-of-use/).

## 2. Clinical Guideline Attributions
Clinical calculators and rules embedded in `core/clinical_calculators.py` and `dictionaries/` are derived from peer-reviewed scientific literature and public health guidelines:
1. **CHA2DS2-VA (ESC 2024)**: European Society of Cardiology (ESC) Guidelines for the management of atrial fibrillation (Van Gelder IC, et al., *Eur Heart J* 2024; DOI: 10.1093/eurheartj/ehae176).
2. **CHA2DS2-VASc (ACC/AHA 2023)**: Joglar JA, et al. 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation. *Circulation* 2024;149:e1–e156.
3. **CKD-EPI 2021 (Race-Free eGFR)**: Inker LA, Eneanya ND, et al. New Creatinine- and Cystatin C–Based Equations to Estimate GFR without Race. *N Engl J Med* 2021;385:1737-1749.
4. **Cockcroft-Gault CrCl (1976)**: Cockcroft DW, Gault MH. Prediction of creatinine clearance from serum creatinine. *Nephron* 1976;16(1):31-41.
5. **CURB-65 (BTS/Lim 2003)**: Lim WS, van der Eerden MM, et al. Defining community acquired pneumonia severity on presentation to hospital: an international derivation and validation study. *Thorax* 2003;58(5):377-382.
6. **Wells Criteria for DVT & PE**: Wells PS, et al. *Thromb Haemost* 2000;83(3):416-420 and *Lancet* 1997;350(9094):1795-1798.
7. **Mosteller Body Surface Area**: Mosteller RD. Simplified calculation of body-surface area. *N Engl J Med* 1987;317(17):1098.

## 3. Open Source Software Components
Core architecture relies primarily on Python Standard Library. Optional adapters and schema validation libraries:
- `jsonschema`: MIT License (Julian Berman).
- `pydantic`: MIT License (Samuel Colvin).
- `mcp` (Model Context Protocol Python SDK): MIT License (Anthropic).
