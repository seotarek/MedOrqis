# Clinical Guidelines & Reference Logic: oncology-palliative-care (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: ASCO / NCCN Clinical Practice Guidelines / ESMO Palliative Care Guidelines
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Screen for Febrile Neutropenia (fever >= 38.3°C with ANC < 500/uL): mandates empiric IV antipseudomonal within 1 hour
2. Detect acute spinal cord compression in metastatic cancer patients (urgent MRI + high-dose dexamethasone)
3. Calculate equianalgesic opioid conversions (morphine milligram equivalents) to prevent accidental overdose
4. Screen for acute Tumor Lysis Syndrome following cytotoxic chemotherapy initiation

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (cancer_type, current_treatment, symptoms) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
