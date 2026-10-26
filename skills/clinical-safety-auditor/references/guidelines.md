# Clinical Guidelines & Reference Logic: clinical-safety-auditor (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: FDA Clinical Decision Support Software Guidance (2026) / ISO 14971 Medical Device Risk Controls
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Intercept clinical contradictions (e.g. anticoagulation in active gastrointestinal hemorrhage)
2. Enforce Epistemic Provenance Gate (halt if indication is MODEL_INFERRED_HYPOTHESIS)
3. Verify that every clinical claim maps to an authentic, un-retracted guideline citation
4. Ensure output carries the mandatory clinical governance banner

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (proposed_output, context_envelope) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
