# Clinical Guidelines & Reference Logic: medorqis-orchestrator (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: MedOrqis Architectural & Governance Framework v2.1 (ISO 14971/IEC 62304)
- **Applicable Safety Class**: Class A (Tier 1)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Validate incoming JSON envelope against Draft-07 schema
2. Verify epistemic provenance of clinical indications (no MODEL_INFERRED_HYPOTHESIS dosing)
3. Screen for acute emergency red flags across all organ systems
4. Route verified context to specialized Tier 2 / Tier 3 domain skills

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (clinical_query, patient_demographics) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
