"""
Safety and provenance verification tests.
Tests epistemic provenance blocks, missing data gating, red-flag detection, and inter-skill conflicts.
"""

import unittest
from core.context_validator import validate_treatment_readiness, ProvenanceViolationError
from core.safety_guardrails import SafetyGuardrailsEngine


class TestSafetyAndProvenance(unittest.TestCase):

    def setUp(self):
        self.guardrails = SafetyGuardrailsEngine()

    def test_epistemic_provenance_blocks_hypothesis_dosing(self):
        # An envelope where the diagnosis is only MODEL_INFERRED_HYPOTHESIS
        envelope = {
            "envelope_id": "ENV-001",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {
                "age_years": 65,
                "biological_sex": "MALE",
                "weight_kg": 80.0
            },
            "provenance_items": [
                {
                    "item_id": "ITEM-1",
                    "provenance_type": "MODEL_INFERRED_HYPOTHESIS",
                    "category": "DIAGNOSIS",
                    "concept_key": "pulmonary_embolism",
                    "value": "Suspected acute pulmonary embolism"
                }
            ],
            "active_allergies": [],
            "safety_status": {
                "red_flags_present": False,
                "safety_gate_cleared": True
            }
        }

        # Attempting to validate high-risk dosing (e.g. therapeutic anticoagulation)
        # on an unverified MODEL_INFERRED_HYPOTHESIS MUST raise ProvenanceViolationError
        with self.assertRaises(ProvenanceViolationError):
            validate_treatment_readiness(
                envelope=envelope,
                target_indication_concept="pulmonary_embolism",
                is_high_risk_drug_or_procedure=True
            )

    def test_missing_pediatric_weight_triggers_safe_abstention(self):
        envelope = {
            "envelope_id": "ENV-002",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {
                "age_years": 4,  # Pediatric patient
                "biological_sex": "FEMALE"
                # weight_kg missing!
            },
            "provenance_items": [
                {
                    "item_id": "ITEM-2",
                    "provenance_type": "DOCUMENTED_CLINICAL_RECORD",
                    "category": "DIAGNOSIS",
                    "concept_key": "acute_otitis_media",
                    "value": "Confirmed AOM"
                }
            ],
            "active_allergies": [],
            "safety_status": {
                "red_flags_present": False,
                "safety_gate_cleared": True
            }
        }

        ready, violations = validate_treatment_readiness(
            envelope=envelope,
            target_indication_concept="acute_otitis_media",
            is_high_risk_drug_or_procedure=True
        )
        self.assertFalse(ready)
        self.assertTrue(any("weight_kg" in v for v in violations))

    def test_red_flag_female_atypical_mi_detection(self):
        envelope = {
            "envelope_id": "ENV-003",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {
                "age_years": 58,
                "biological_sex": "FEMALE"
            },
            "provenance_items": [
                {"item_id": "1", "provenance_type": "USER_REPORTED_UNVERIFIED", "category": "SYMPTOM", "concept_key": "epigastric_burning", "value": "Severe burning in epigastrium"},
                {"item_id": "2", "provenance_type": "USER_REPORTED_UNVERIFIED", "category": "SYMPTOM", "concept_key": "diaphoresis", "value": "Cold sweating"},
                {"item_id": "3", "provenance_type": "USER_REPORTED_UNVERIFIED", "category": "SYMPTOM", "concept_key": "unexplained_nausea", "value": "Nausea without vomiting"}
            ],
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }

        verdict = self.guardrails.evaluate_safety(envelope)
        self.assertEqual(verdict["gate_status"], "SAFE_ABSTENTION_EMERGENCY_ESCALATION")
        self.assertTrue(verdict["action_plan"]["emergency_redirection_required"])
        self.assertTrue(any(f["flag_id"] == "RF-CARD-001" for f in verdict["red_flags_detected"]))

    def test_inter_skill_conflict_anticoagulation_and_gi_bleed(self):
        envelope = {
            "envelope_id": "ENV-004",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {"age_years": 72, "biological_sex": "MALE"},
            "provenance_items": [
                {"item_id": "1", "provenance_type": "DOCUMENTED_CLINICAL_RECORD", "category": "MEDICATION", "concept_key": "apixaban", "value": "Apixaban 5mg BID"},
                {"item_id": "2", "provenance_type": "DOCUMENTED_CLINICAL_RECORD", "category": "SYMPTOM", "concept_key": "melena", "value": "Black tarry stools for 2 days"}
            ],
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }

        verdict = self.guardrails.evaluate_safety(envelope)
        self.assertEqual(verdict["gate_status"], "SAFE_ABSTENTION_EMERGENCY_ESCALATION")
        self.assertTrue(len(verdict["inter_skill_conflicts"]) > 0)
        self.assertIn("LETHAL_CONTRAINDICATION_INTERACTION", verdict["inter_skill_conflicts"][0]["conflict_type"])

    def test_critical_drug_interactions(self):
        # 1. Warfarin + Ibuprofen (INN)
        res_inn = self.guardrails.check_drug_interactions(["warfarin", "ibuprofen"])
        self.assertGreater(len(res_inn), 0)
        self.assertTrue(any(i["rule_id"] == "DDI-WARF-NSAID-001" for i in res_inn))

        # 2. Regional Arabic brands: فولتارين (diclofenac) + إليكويس (apixaban)
        res_brand = self.guardrails.check_drug_interactions(["فولتارين", "إليكويس"])
        self.assertGreater(len(res_brand), 0)
        self.assertTrue(any("NSAID" in i["rule_id"] or "BLEED" in i["rule_id"] for i in res_brand))

        # 3. Sildenafil + Nitroglycerin (Catastrophic hypotension)
        res_nitrate = self.guardrails.check_drug_interactions(["sildenafil", "nitroglycerin"])
        self.assertGreater(len(res_nitrate), 0)
        self.assertEqual(res_nitrate[0]["severity"], "NEVER_EVENT_ABSOLUTE")



    def test_negated_symptom_does_not_trigger_red_flag(self):
        envelope = {
            "envelope_id": "ENV-005",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {"age_years": 55, "biological_sex": "MALE"},
            "provenance_items": [
                {
                    "item_id": "1",
                    "provenance_type": "DOCUMENTED_CLINICAL_RECORD",
                    "category": "SYMPTOM",
                    "concept_key": "chest_pain",
                    "value": "Patient denies any chest pain",
                    "is_negated": True
                }
            ],
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }
        verdict = self.guardrails.evaluate_safety(envelope)
        # Negated symptom should not trigger acute coronary syndrome red flag
        self.assertEqual(len(verdict["red_flags_detected"]), 0)

    def test_empty_provenance_raises_error(self):
        envelope = {
            "envelope_id": "ENV-006",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {"age_years": 45, "biological_sex": "MALE", "weight_kg": 75.0},
            "provenance_items": [],  # Completely empty provenance items
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }
        with self.assertRaises(ProvenanceViolationError):
            validate_treatment_readiness(
                envelope=envelope,
                target_indication_concept="hypertension",
                is_high_risk_drug_or_procedure=True
            )

    def test_missing_age_triggers_safe_abstention_data_deficit(self):
        # When patient_demographics does NOT specify age_years, the safety guardrails
        # MUST NEVER default to 30 years. It must pause assessment and return SAFE_ABSTENTION_DATA_DEFICIT.
        envelope = {
            "envelope_id": "ENV-007-NO-AGE",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {
                # age_years is completely omitted!
                "biological_sex": "MALE",
                "weight_kg": 70.0
            },
            "provenance_items": [
                {
                    "item_id": "1",
                    "provenance_type": "DOCUMENTED_CLINICAL_RECORD",
                    "category": "SYMPTOM",
                    "concept_key": "cough",
                    "value": "Mild non-productive cough"
                }
            ],
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }
        verdict = self.guardrails.evaluate_safety(envelope)
        self.assertEqual(verdict["gate_status"], "SAFE_ABSTENTION_DATA_DEFICIT")
        self.assertTrue(any("age_years" in item or "Patient age" in item for item in verdict["missing_mandatory_data"]))

    def test_sentinel_acute_stroke_fast_red_flag(self):
        # A single affirmed sentinel symptom (facial droop) MUST immediately trigger emergency redirection
        envelope = {
            "envelope_id": "ENV-STROKE-FAST",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {"age_years": 64, "biological_sex": "MALE"},
            "provenance_items": [
                {"item_id": "1", "provenance_type": "DOCUMENTED_CLINICAL_RECORD", "category": "SYMPTOM", "concept_key": "facial_droop", "value": "Acute right facial droop noted 30 min ago"}
            ],
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }
        verdict = self.guardrails.evaluate_safety(envelope)
        self.assertEqual(verdict["gate_status"], "SAFE_ABSTENTION_EMERGENCY_ESCALATION")
        self.assertTrue(verdict["action_plan"]["emergency_redirection_required"])
        self.assertTrue(any(f["flag_id"] == "RF-NEURO-001" for f in verdict["red_flags_detected"]))

    def test_sentinel_crushing_chest_pain_acs_red_flag(self):
        # Crushing chest pain radiating to arm MUST immediately trip RF-CARD-002
        envelope = {
            "envelope_id": "ENV-ACS-SENTINEL",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {"age_years": 52, "biological_sex": "MALE"},
            "provenance_items": [
                {"item_id": "1", "provenance_type": "USER_REPORTED_UNVERIFIED", "category": "SYMPTOM", "concept_key": "crushing_chest_pain", "value": "Sudden onset crushing retrosternal pressure"}
            ],
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }
        verdict = self.guardrails.evaluate_safety(envelope)
        self.assertEqual(verdict["gate_status"], "SAFE_ABSTENTION_EMERGENCY_ESCALATION")
        self.assertTrue(verdict["action_plan"]["emergency_redirection_required"])
        self.assertTrue(any(f["flag_id"] == "RF-CARD-002" for f in verdict["red_flags_detected"]))

    def test_sentinel_anaphylaxis_red_flag(self):
        # Acute anaphylaxis after peanut exposure
        envelope = {
            "envelope_id": "ENV-ANAPHYLAXIS",
            "timestamp": "2026-10-26T10:00:00Z",
            "patient_demographics": {"age_years": 22, "biological_sex": "FEMALE"},
            "provenance_items": [
                {"item_id": "1", "provenance_type": "DOCUMENTED_CLINICAL_RECORD", "category": "SYMPTOM", "concept_key": "anaphylaxis", "value": "Acute anaphylaxis with facial swelling"}
            ],
            "active_allergies": [],
            "safety_status": {"red_flags_present": False, "safety_gate_cleared": True}
        }
        verdict = self.guardrails.evaluate_safety(envelope)
        self.assertEqual(verdict["gate_status"], "SAFE_ABSTENTION_EMERGENCY_ESCALATION")
        self.assertTrue(verdict["action_plan"]["emergency_redirection_required"])
        self.assertTrue(any(f["flag_id"] == "RF-IMMUN-001" for f in verdict["red_flags_detected"]))


if __name__ == "__main__":
    unittest.main()


