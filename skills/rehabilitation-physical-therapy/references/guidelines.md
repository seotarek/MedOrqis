# Clinical Guidelines & Reference Logic: rehabilitation-physical-therapy (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: AHA/ASA Stroke Rehabilitation Guidelines / APTA Practice Guidelines
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Verify surgical clearance and weight-bearing status before initiating mobilization
2. Screen for acute DVT using Wells DVT Criteria before calf manipulation or leg exercise
3. Monitor hemodynamic tolerance during orthostatic position changes (prevent syncopal falls)
4. Structure progressive neuro-rehabilitation exercises following acute ischemic stroke

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (surgical_or_neurological_status, mobility_level) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
