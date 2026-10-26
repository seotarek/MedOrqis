# MedOrqis — Safety, Clinical Risk Management & Governance Framework

## 1. Regulatory & Quality Principles Alignment
MedOrqis adopts software safety engineering and risk management controls informed by international standards for health software:
- **ISO 14971:2019 / Amd 1:2020**: Application of risk management to medical devices (Hazard Analysis, Risk Estimation, Risk Mitigation, Residual Risk Evaluation).
- **IEC 62304:2006 + A1:2015**: Medical device software software life cycle processes (Software Safety Classification A, B, and C).
- **WHO Guidance (2024)**: Ethics & Governance of Artificial Intelligence for Health (Large Multi-Modal Models).
- **FDA CDS Guidance (Jan 2026)**: Criterion 4 transparency principles for non-autonomous clinical decision support software.

## 2. IEC 62304 Risk Stratification per Skill
Every skill in MedOrqis declares an explicit `SafetyClass` in its `manifest.json`:

| Safety Class | Clinical Severity Definition | Target Domains / Skills | Mandatory Engineering Controls |
| :--- | :--- | :--- | :--- |
| **Class A (Low Risk)** | No injury or damage to health is possible. Administrative, research, documentation, or public health metrics. | `ebm-research-biostatistics`, `medical-documentation-translation`, `healthcare-ops-telemedicine-ehr`, `health-cybersecurity-privacy`, `public-health-epidemiology`, `medorqis-orchestrator`. | Schema validation, zero stubs, strict citation formatting, PHI scrubbing. |
| **Class B (Moderate Risk)** | Non-serious injury is possible if clinician oversight fails. Diagnostic workups, laboratory interpretation, imaging appropriateness, chronic care protocols. | `differential-diagnosis-cds`, `laboratory-medicine-pathology`, `radiology-medical-imaging`, `internal-medicine-chronic`, `infectious-diseases-stewardship`, `nursing-clinical-care`, `clinical-nutrition-dietetics`, `rehabilitation-physical-therapy`. | Explicit uncertainty scoring, VINDICATE broad differential, must-not-miss flags, GRADE evidence certainty. |
| **Class C (High Risk)** | Serious injury or death is possible if incorrect information is acted upon. Emergency triage, high-risk dosing, acute toxicology, pediatric/neonatal care, maternal-fetal health, suicide crisis. | `emergency-triage-redflags`, `clinical-safety-auditor`, `pharmacology-dosing-interactions`, `clinical-toxicology-overdose`, `pediatrics-neonatology`, `obstetrics-gynecology`, `geriatrics-polypharmacy`, `mental-health-psychiatry`, `perioperative-surgical-care`, `oncology-palliative-care`. | **Strict Deterministic Gates**: Free-text LLM arithmetic is banned. Hard fail-safe abstention on missing/unverified data. Epistemic provenance lockdown. Qualified clinician sign-off registry check. |

## 3. The Epistemic Provenance Rule
No downstream skill (especially Pharmacology and Treatment Planning) is permitted to accept a `MODEL_INFERRED_HYPOTHESIS` as an established indication for high-risk therapy. Any clinical input without confirmed `DOCUMENTED_CLINICAL_RECORD` provenance requires explicit human clinician verification before dosing algorithms can execute.

## 4. Human Clinical Review Registry
Every calculator, rule, and skill must be tracked in `governance/clinical_review_registry.json`. Any module without qualified specialist clinical validation is assigned status `"REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF"` and automatically emits a prominent research disclaimer banner.
