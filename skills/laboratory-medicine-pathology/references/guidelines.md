# Clinical Guidelines & Reference Logic: laboratory-medicine-pathology (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: CLSI Laboratory Safety & Panic Value Guidelines / IFCC LOINC Standards
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Screen reported lab values against emergency panic alert thresholds
2. Harmonize unit discrepancies (e.g. serum creatinine mg/dL vs umol/L, glucose mg/dL vs mmol/L)
3. Map lab test to standardized LOINC concept code
4. Recommend immediate clinician notification for critical panic results

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (test_name, value, unit) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
