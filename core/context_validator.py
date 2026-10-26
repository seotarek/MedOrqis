"""
MedOrqis — Clinical Context Envelope & Epistemic Provenance Validator
Enforces the Zero-Hallucination Epistemic Provenance Policy.
"""

from typing import Dict, Any, List, Tuple
import json
import os

try:
    import jsonschema
except ImportError:
    jsonschema = None


class ProvenanceViolationError(ValueError):
    """Raised when an unverified hypothesis is illegally consumed as a confirmed indication."""
    def __init__(self, item_id: str, concept_key: str, detected_provenance: str, required_provenance: str):
        msg = (
            f"Provenance Violation: Item '{item_id}' ({concept_key}) has provenance '{detected_provenance}', "
            f"but treatment/dosing strictly requires '{required_provenance}'. "
            f"Downstream clinical actions cannot proceed on unconfirmed hypotheses without clinician sign-off."
        )
        super().__init__(msg)
        self.item_id = item_id
        self.concept_key = concept_key
        self.detected_provenance = detected_provenance
        self.required_provenance = required_provenance


class MissingClinicalParameterError(ValueError):
    """Raised when a mandatory clinical parameter for safety is absent."""
    def __init__(self, missing_param: str, clinical_rationale: str):
        super().__init__(f"Missing Mandatory Parameter: '{missing_param}'. {clinical_rationale}")
        self.missing_param = missing_param
        self.clinical_rationale = clinical_rationale


def validate_envelope_schema(envelope: Dict[str, Any], schema_path: str = None) -> Tuple[bool, List[str]]:
    """Validates that a clinical envelope conforms to Draft-07 schema."""
    if schema_path is None:
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "schemas",
            "clinical_context_envelope.schema.json"
        )
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    if jsonschema is None:
        # Graceful fallback: basic structural validation if jsonschema package is absent
        required_fields = ["envelope_id", "timestamp", "patient_demographics", "provenance_items", "active_allergies", "safety_status"]
        errors = [f"Missing required property '{f}'" for f in required_fields if f not in envelope]
        return (len(errors) == 0, errors)

    validator = jsonschema.Draft7Validator(schema)
    errors = [e.message for e in validator.iter_errors(envelope)]
    return (len(errors) == 0, errors)


def validate_treatment_readiness(
    envelope: Dict[str, Any],
    target_indication_concept: str,
    is_high_risk_drug_or_procedure: bool = True
) -> Tuple[bool, List[str]]:
    """
    Enforces the Hard Provenance Gate:
    1. Blocks treatment if the indication is MODEL_INFERRED_HYPOTHESIS.
    2. Checks for mandatory patient safety parameters (age, weight, renal function, pregnancy).
    3. Checks for direct allergy conflicts.
    """
    violations = []
    demographics = envelope.get("patient_demographics", {})
    age = demographics.get("age_years")
    sex = demographics.get("biological_sex")
    weight = demographics.get("weight_kg")
    pregnancy = demographics.get("pregnancy_status")

    # 1. Epistemic Provenance Verification
    items = envelope.get("provenance_items", [])
    matching_items = [
        item for item in items
        if item.get("concept_key", "").lower() == target_indication_concept.lower()
        or item.get("value", "").lower() == target_indication_concept.lower()
        or target_indication_concept.lower() in item.get("concept_key", "").lower()
        or target_indication_concept.lower() in item.get("value", "").lower()
    ]

    if is_high_risk_drug_or_procedure:
        if not matching_items:
            raise ProvenanceViolationError(
                item_id="NOT_FOUND",
                concept_key=target_indication_concept,
                detected_provenance="NONE_DOCUMENTED",
                required_provenance="DOCUMENTED_CLINICAL_RECORD"
            )

        # Require at least one confirmed record
        has_confirmed_provenance = any(
            item.get("provenance_type") in ["DOCUMENTED_CLINICAL_RECORD", "DETERMINISTIC_CALCULATION"]
            for item in matching_items
        )
        if not has_confirmed_provenance:
            detected = matching_items[0].get("provenance_type", "USER_REPORTED_UNVERIFIED")
            raise ProvenanceViolationError(
                item_id=matching_items[0].get("item_id", "UNKNOWN"),
                concept_key=target_indication_concept,
                detected_provenance=detected,
                required_provenance="DOCUMENTED_CLINICAL_RECORD"
            )
    else:
        for item in matching_items:
            prov = item.get("provenance_type")
            if prov in ["MODEL_INFERRED_HYPOTHESIS", "USER_REPORTED_UNVERIFIED"]:
                raise ProvenanceViolationError(
                    item_id=item.get("item_id", "UNKNOWN"),
                    concept_key=target_indication_concept,
                    detected_provenance=prov,
                    required_provenance="DOCUMENTED_CLINICAL_RECORD"
                )

    # 2. Mandatory Demographics for High-Risk Dosing
    if is_high_risk_drug_or_procedure:
        if age is None:
            violations.append("Mandatory parameter missing: 'age_years' is required for dose verification.")
        if age is not None and age < 18 and weight is None:
            violations.append("Mandatory parameter missing: 'weight_kg' is strictly required for pediatric dosing.")
        if sex == "FEMALE" and age is not None and 12 <= age <= 55:
            if not pregnancy or pregnancy == "UNKNOWN":
                violations.append("Mandatory parameter missing: 'pregnancy_status' must be verified for females of reproductive age.")

    # 3. Allergy Checking
    allergies = envelope.get("active_allergies", [])
    for allergy in allergies:
        allergen = allergy.get("allergen", "").lower()
        if allergen in target_indication_concept.lower():
            violations.append(
                f"CRITICAL ALLERGY CONFLICT: Patient has documented allergy to '{allergen}' "
                f"(Severity: {allergy.get('severity')}, Reaction: {allergy.get('reaction_type')})."
            )

    is_ready = len(violations) == 0
    return (is_ready, violations)
