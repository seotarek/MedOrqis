# Clinical Guidelines & Reference Logic: ebm-research-biostatistics (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: Cochrane Handbook for Systematic Reviews / GRADE Working Group
- **Applicable Safety Class**: Class A (Tier 1)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Formulate structured PICO clinical question
2. Verify PMIDs and DOIs against immutable verified guidelines registry
3. Execute RoB-2 / ROBINS-I risk of bias critical appraisal
4. Assign GRADE certainty of evidence (High, Moderate, Low, Very Low)

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (study_abstract_or_claim, study_type) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
