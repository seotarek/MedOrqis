# Clinical Guidelines & Reference Logic: differential-diagnosis-cds (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: Society to Improve Diagnosis in Medicine (SIDM) / BMJ Best Practice
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Categorize potential etiologies using the VINDICATE mnemonic
2. Highlight high-morbidity 'Must-Not-Miss' diagnoses at the top of differential
3. Order prioritized diagnostic tests by diagnostic yield and invasiveness
4. Check for cognitive biases (anchoring, premature closure, availability heuristic)

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (presenting_symptoms, patient_demographics) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
