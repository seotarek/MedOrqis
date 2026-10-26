# Clinical Guidelines & Reference Logic: geriatrics-polypharmacy (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: 2023 AGS Beers Criteria / STOPP/START Criteria Version 3 (2023)
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Audit medication list against 2023 American Geriatrics Society (AGS) Beers Criteria
2. Identify high anticholinergic burden drugs contributing to cognitive decline and fall risks
3. Screen for drug-drug interactions in elderly patients taking >= 5 concurrent medications
4. Formulate structured deprescribing taper plans for sedatives, hypnotics, and redundant agents

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (medication_list, patient_age_years) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
