# Clinical Guidelines & Reference Logic: pediatrics-neonatology (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: Nelson Textbook of Pediatrics (22nd Ed) / AAP Guidelines / WHO IMCI
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Verify pediatric patient weight strictly in kilograms (reject lb entries or missing weights)
2. Calculate weight-based medication dose (mg/kg) and enforce mandatory adult maximum dose cap
3. Calculate pediatric renal function via Bedside Schwartz eGFR formula (0.413 * height / Cr)
4. Screen for neonatal red flags: fever in neonate < 28 days (mandates full septic workup)

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (age_years, weight_kg) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
