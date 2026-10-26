# Clinical Guidelines & Reference Logic: public-health-epidemiology (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: WHO Outbreak Communication & IPC Guidelines / CDC Field Epidemiology Manual
- **Applicable Safety Class**: Class A (Tier 1)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Compute 2x2 contingency matrix metrics: Sensitivity, Specificity, PPV, NPV, LR+ and LR-
2. Adjust predictive values according to disease prevalence in target population
3. Identify outbreak transmission modes (airborne, droplet, contact, vector)
4. Reference WHO infection prevention and control (IPC) standards

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (disease_metrics_or_outbreak_data) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
