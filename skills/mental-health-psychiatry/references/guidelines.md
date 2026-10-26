# Clinical Guidelines & Reference Logic: mental-health-psychiatry (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: APA Practice Guidelines / Columbia Suicide Severity Rating Scale (C-SSRS)
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Screen for active suicidal ideation with intent or plan (Columbia-Suicide Severity Rating Scale)
2. Trigger immediate emergency escalation and provide localized 24/7 crisis hotline contact numbers
3. Monitor psychotropic combinations for Serotonin Syndrome (MAOIs + SSRIs) and QTc prolongation
4. Screen for Neuroleptic Malignant Syndrome in patients on antipsychotic therapy

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (mental_health_symptoms) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
