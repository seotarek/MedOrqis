# Clinical Guidelines & Reference Logic: clinical-nutrition-dietetics (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: ASPEN / ESPEN Clinical Nutrition Guidelines
- **Applicable Safety Class**: Class B (Tier 2)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Calculate Basal Metabolic Rate (BMR) via Harris-Benedict or Mifflin-St Jeor formula
2. Adjust target protein intake based on clinical state (0.8 g/kg for stable CKD, 1.5-2.0 g/kg for ICU/sepsis)
3. Check for food-drug interactions (e.g. grapefruit and CYP3A4 statins, vitamin K and warfarin)
4. Screen for Refeeding Syndrome risk in severely malnourished or prolonged-fasting patients

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (weight_kg, clinical_condition) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
