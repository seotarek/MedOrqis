# Clinical Guidelines & Reference Logic: clinical-toxicology-overdose (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: American Academy of Clinical Toxicology (AACT) / EAPCCT Guidelines
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Identify acute clinical toxidrome based on vital signs, pupils, skin moisture, and bowel sounds
2. Check indication for specific antidotes: Naloxone (opioids), N-acetylcysteine (paracetamol), Atropine (cholinergics)
3. Determine timing window for activated charcoal (strictly within 1-2 hours of ingestion in alert patients)
4. Escalate immediately to Poison Control Center and regional emergency medical services

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (substance_ingested, time_since_ingestion, vital_signs) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
