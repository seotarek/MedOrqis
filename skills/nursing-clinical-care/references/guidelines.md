# Clinical Guidelines & Reference Logic: nursing-clinical-care (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: Royal College of Physicians NEWS2 Guidelines / NPUAP Braden Scale
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Compute National Early Warning Score 2 (NEWS2) from 6 physiological parameters
2. Trigger rapid response team escalation for NEWS2 score >= 5 or single parameter score of 3
3. Assess Braden Scale for pressure ulcer risk and mandate repositioning schedules
4. Verify fall risk precautions and maintain bedside safety barriers

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (vital_signs, mental_status) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
