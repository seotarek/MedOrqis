# Clinical Guidelines & Reference Logic: pharmacology-dosing-interactions (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: FDA Drug Labeling / BNF / Stockley's Drug Interactions (2024)
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Normalize all medication brand names to international nonproprietary names (INN)
2. Evaluate full medication list against critical DDI rules (e.g. sildenafil + nitrates, warfarin + NSAIDs)
3. Calculate Cockcroft-Gault CrCl with Ideal/Adjusted Body Weight adjustments in obesity
4. Adjust dosages and dosing intervals for renally cleared medications according to CrCl

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (drug_inn, patient_demographics, renal_function) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
