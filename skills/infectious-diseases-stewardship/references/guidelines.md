# Clinical Guidelines & Reference Logic: infectious-diseases-stewardship (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: IDSA Guidelines / Sanford Guide to Antimicrobial Therapy (2024) / WHO AWaRe
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Categorize antimicrobial regimen into WHO AWaRe classification (Access, Watch, Reserve)
2. Differentiate true IgE-mediated beta-lactam anaphylaxis from mild cutaneous adverse reactions
3. Calculate Cockcroft-Gault CrCl to adjust aminoglycoside / vancomycin dosing intervals
4. Recommend structured de-escalation from broad-spectrum to narrow-spectrum upon culture sensitivity

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (infection_site, patient_demographics, allergies) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
