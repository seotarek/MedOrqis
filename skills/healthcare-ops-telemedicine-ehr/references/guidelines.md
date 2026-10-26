# Clinical Guidelines & Reference Logic: healthcare-ops-telemedicine-ehr (v2.1.0)

## Governing Guideline Authority
- **Authority Body**: HL7 FHIR R4 Specification / ATA Telemedicine Practice Guidelines
- **Applicable Safety Class**: Class A (Tier 1)
- **Human Clinical Sign-Off**: REFERENCE_SEED_REQUIRES_CLINICAL_SIGN_OFF

## Clinical Decision Checklist
1. Verify patient identity and jurisdiction licensure for telemedicine consult
2. Map clinical entities to HL7 FHIR R4 resources (Patient, Condition, MedicationRequest)
3. Check telemedicine appropriateness (screen out unstable red-flag emergencies)
4. Confirm transmission encryption and audit logging conformance

## Deterministic Rule Constraints
1. Epistemic Provenance Lockdown:
   Outputs from this skill carry structured provenance. Indications must be verified as `DOCUMENTED_CLINICAL_RECORD` before triggering irreversible or high-risk actions.
2. Safe Abstention Default:
   If any mandatory parameter (intake_payload, target_fhir_resource) is missing, the skill returns a structured safe abstention request rather than assuming default normal values.
3. Clause-Bounded Negation Polarity:
   Negation is strictly bounded by conjunctions (e.g. 'but', 'لكن') and limited to a 5-word window to prevent false-negative emergency suppression.
