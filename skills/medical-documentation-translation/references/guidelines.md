# Clinical Guidelines & Reference Logic: medical-documentation-translation (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: Joint Commission SBAR Standards / AAHIM Clinical Documentation Guidelines
- **Applicable Safety Class**: Class A (Tier 1)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. De-identify Protected Health Information (HIPAA 18, National IDs, MRNs)
2. Extract verified clinical findings into SOAP / SBAR structured sections
3. Preserve clause-bounded negation polarity across multilingual translations
4. Maintain bidirectional unit fidelity (prevent decimal inversion and mg vs mcg errors)

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (encounter_narrative, format_type) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
