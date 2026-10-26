# Clinical Guidelines & Reference Logic: internal-medicine-chronic (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: ADA Standards of Care in Diabetes 2024 / KDIGO CKD Guidelines / ESC Heart Failure Guidelines
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Calculate CHA2DS2-VA (ESC 2024) stroke risk for patients with atrial fibrillation
2. Calculate race-free CKD-EPI 2021 eGFR and assign KDIGO G/A staging
3. Reconcile multi-drug regimens for drug-disease contraindications (e.g. NSAIDs in CKD/HF)
4. Set individualized HbA1c and blood pressure targets according to patient frailty and life expectancy

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (chronic_conditions, current_medications) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
