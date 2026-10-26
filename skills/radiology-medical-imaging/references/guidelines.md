# Clinical Guidelines & Reference Logic: radiology-medical-imaging (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: ACR Appropriateness Criteria (2024) / ESUR Contrast Media Guidelines
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Consult ACR Appropriateness Criteria for target clinical indication
2. Screen for pregnancy in female patients before ordering ionizing radiation (ALARA principle)
3. Calculate eGFR prior to iodinated CT or gadolinium MRI contrast administration
4. Check for severe contrast allergy history and prescribe premedication protocol if indicated

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (clinical_indication, patient_demographics) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
