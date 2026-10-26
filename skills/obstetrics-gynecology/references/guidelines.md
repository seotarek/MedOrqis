# Clinical Guidelines & Reference Logic: obstetrics-gynecology (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: ACOG Practice Bulletins / RCOG Green-top Guidelines / Briggs Drugs in Pregnancy
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Screen for acute obstetric emergencies: severe pre-eclampsia (BP >= 160/110 + symptoms), ectopic pregnancy
2. Cross-check all prescribed medications against FDA/Briggs pregnancy teratogenicity registries
3. Halt administration of contraindicated teratogens (isotretinoin, valproate, ACE inhibitors, methotrexate)
4. Confirm lactation safety before authorizing maternal medication intake

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (pregnancy_status, gestational_age_weeks) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
