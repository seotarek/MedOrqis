# Clinical Guidelines & Reference Logic: health-cybersecurity-privacy (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: HIPAA Privacy Rule / EU GDPR Article 9 / ISO 27799 Health Informatics
- **Applicable Safety Class**: Class A (Tier 1)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Execute regex and rule-based scan for indirect prompt injections and jailbreak bypasses
2. Redact HIPAA 18 Safe Harbor identifiers
3. Redact Egyptian 14-digit National IDs and Saudi 10-digit National IDs / Iqamas
4. Log structured de-identification audit report without persisting raw patient identifiers

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (clinical_text) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
