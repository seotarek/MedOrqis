# Clinical Guidelines & Reference Logic: emergency-triage-redflags (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: Manchester Triage System / Emergency Severity Index (ESI) / Surviving Sepsis 2021 / AHA ACLS
- **Applicable Safety Class**: Class C (Tier 3)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Execute ABCDE Primary Survey: Airway patency, Breathing work, Circulation perfusion, Disability GCS, Exposure
2. Screen for time-sensitive emergencies: ACS, acute ischemic stroke (FAST), septic shock, anaphylaxis, tension pneumothorax
3. Filter out affirmed symptoms from negated ones (do not trigger on 'denies chest pain')
4. Execute immediate emergency redirection with local regional emergency contact numbers

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (presenting_symptoms, vital_signs) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
