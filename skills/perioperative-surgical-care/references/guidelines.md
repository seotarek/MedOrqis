# Clinical Guidelines & Reference Logic: perioperative-surgical-care (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: 2024 AHA/ACC Perioperative Cardiovascular Evaluation Guidelines / ASA Physical Status
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Compute Revised Cardiac Risk Index (RCRI) score for major non-cardiac surgery
2. Calculate pre-test probability for venous thromboembolism via Wells DVT/PE scores
3. Plan antithrombotic interruption and bridging protocol based on procedural bleeding risk
4. Enforce WHO Surgical Safety Checklist checkpoints (Sign In, Time Out, Sign Out)

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (surgical_procedure, patient_demographics, cardiac_history) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
