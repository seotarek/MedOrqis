"""
MedOrqis — Fail-Safe Clinical Guardrails & Red-Flag Escalation Engine (v2.1)
Multi-layered defense: Red flag detection with negation filtering, critical DDI checks,
missing-data gating, conflict resolution, and safe abstention.
"""

from typing import Dict, Any, List, Optional
import os
import json
import uuid
from datetime import datetime, timezone

from core.terminology_normalizer import TerminologyNormalizer


class SafetyGuardrailsEngine:
    def __init__(
        self,
        red_flags_path: Optional[str] = None,
        ddi_path: Optional[str] = None
    ):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        if red_flags_path is None:
            red_flags_path = os.path.join(base_dir, "dictionaries", "red_flag_rules.json")
        if ddi_path is None:
            ddi_path = os.path.join(base_dir, "dictionaries", "critical_drug_interactions.json")

        self.red_flags_path = red_flags_path
        self.ddi_path = ddi_path
        self.normalizer = TerminologyNormalizer()
        self._load_rules()

    def _load_rules(self):
        # 1. Red flag symptom rules
        if os.path.exists(self.red_flags_path):
            with open(self.red_flags_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.rules = data.get("rules", [])
        else:
            self.rules = []

        # 2. Critical drug-drug interaction rules
        if os.path.exists(self.ddi_path):
            with open(self.ddi_path, "r", encoding="utf-8") as f:
                ddi_data = json.load(f)
                self.ddi_rules = ddi_data.get("rules", [])
        else:
            self.ddi_rules = []

    def check_drug_interactions(
        self,
        medications: List[str],
        patient_demographics: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluates a list of patient medications against critical DDI rules.
        Normalizes trade names to INN (e.g. Concor -> Bisoprolol, Voltaren -> Ibuprofen/Diclofenac).
        Returns a list of detected drug interactions and contraindications.
        """
        detected_ddis = []
        if not medications:
            return detected_ddis

        demographics = patient_demographics or {}
        is_pregnant = demographics.get("pregnancy_status") in ["PREGNANT", "CONFIRMED_PREGNANT", True]

        # Normalize all medications to INN
        normalized_meds = []
        for med in medications:
            med_str = str(med).strip()
            norm = self.normalizer.normalize_brand_name(med_str)
            inn = norm.get("inn_name", norm.get("inn", med_str)).lower().strip()
            normalized_meds.append((med_str, inn))

        # Check pair-wise interactions
        for rule in self.ddi_rules:
            criteria = rule.get("trigger_criteria", {})
            d_a = criteria.get("drug_a_inn", "").lower().strip()
            d_b = criteria.get("drug_b_inn", "").lower().strip()
            action = rule.get("clinical_action", {})

            # Pregnancy teratogen check
            if d_b == "pregnancy":
                for orig_name, inn_name in normalized_meds:
                    if d_a in inn_name or inn_name in d_a or d_a in orig_name.lower():
                        if is_pregnant:
                            detected_ddis.append({
                                "rule_id": rule.get("rule_id"),
                                "rule_name": rule.get("rule_name"),
                                "severity": rule.get("severity"),
                                "drugs_involved": [orig_name, "pregnancy"],
                                "contraindicated": action.get("contraindicated", True),
                                "explanation": action.get("explanation"),
                                "immediate_action": action.get("immediate_action"),
                                "source_authority": rule.get("source_authority")
                            })
                continue

            # Standard drug-drug interaction check
            matched_a = None
            matched_b = None

            for orig_name, inn_name in normalized_meds:
                if d_a in inn_name or inn_name in d_a or d_a in orig_name.lower():
                    matched_a = orig_name
                if d_b in inn_name or inn_name in d_b or d_b in orig_name.lower():
                    matched_b = orig_name

            if matched_a and matched_b and matched_a != matched_b:
                detected_ddis.append({
                    "rule_id": rule.get("rule_id"),
                    "rule_name": rule.get("rule_name"),
                    "severity": rule.get("severity"),
                    "drugs_involved": [matched_a, matched_b],
                    "contraindicated": action.get("contraindicated", True),
                    "explanation": action.get("explanation"),
                    "immediate_action": action.get("immediate_action"),
                    "source_authority": rule.get("source_authority")
                })

        return detected_ddis

    def evaluate_safety(
        self,
        envelope: Dict[str, Any],
        proposed_actions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes a 4-layer clinical safety evaluation:
        1. Red-flag symptom & vital detection (with negation boundary filtering).
        2. Critical drug-drug interaction screening (DDI engine).
        3. Missing data gatekeeper.
        4. Inter-skill conflict detector & governance banner.
        """
        verdict_id = f"VERDICT-{uuid.uuid4().hex[:8].upper()}"
        timestamp = datetime.now(timezone.utc).isoformat()

        demographics = envelope.get("patient_demographics", {})
        age = demographics.get("age_years", 30)
        sex = demographics.get("biological_sex", "UNKNOWN")
        pregnancy = demographics.get("pregnancy_status", "UNKNOWN")

        # Extract items with strict negation filtering
        items = envelope.get("provenance_items", [])
        patient_concepts = set()
        active_medications = []

        for item in items:
            key = item.get("concept_key", "").lower().strip()
            val = str(item.get("value", "")).strip()
            val_lower = val.lower()

            # Check if item is explicitly marked negated
            if item.get("is_negated") is True:
                continue

            # Check if concept is negated within text narrative via TerminologyNormalizer
            is_negated_in_text = (
                self.normalizer.extract_negation_status(val, key) or
                self.normalizer.extract_negation_status(val, val)
            )
            if is_negated_in_text:
                continue

            patient_concepts.add(key)
            patient_concepts.add(val_lower)

            # Collect active medications
            if "medication" in key or item.get("category") == "MEDICATION" or "drug" in key:
                active_medications.append(val or key)

        # Also collect active medications from active_allergies or prescription fields if present
        for med in envelope.get("current_medications", []):
            active_medications.append(str(med))

        # Layer 1: Evaluate Red Flag Rules
        detected_red_flags = []
        emergency_redirection = False

        for rule in self.rules:
            # Check population match
            target_pop = rule.get("target_population", {})
            age_group = target_pop.get("age_group", "ALL")
            if age_group == "PEDIATRIC" and age >= 18:
                continue
            if age_group == "NEONATE" and age > 0.08:
                continue
            if age_group == "GERIATRIC" and age < 65:
                continue

            # Check trigger criteria
            trigger_criteria = rule.get("trigger_criteria", {})
            required_concepts = trigger_criteria.get("symptom_keys", [])

            # Match criteria against affirmed (non-negated) concepts only
            matched_count = sum(1 for c in required_concepts if any(c.lower() in p for p in patient_concepts))
            if matched_count >= len(required_concepts) and len(required_concepts) > 0:
                action = rule.get("clinical_action", {})
                detected_red_flags.append({
                    "flag_id": rule.get("rule_id"),
                    "symptom_or_vital": rule.get("rule_name"),
                    "clinical_urgency": rule.get("severity", "EMERGENCY_ED"),
                    "escalation_target": action.get("immediate_action", "Emergency Department")
                })
                if rule.get("severity") in ["NEVER_EVENT_ABSOLUTE", "HIGH_CRITICAL"]:
                    emergency_redirection = True

        # Layer 2: Missing Data Checks
        missing_data = []
        if age is None:
            missing_data.append("Patient age is missing.")
        if age is not None and age < 18 and demographics.get("weight_kg") is None:
            missing_data.append("Patient weight is missing for pediatric evaluation.")
        if sex == "FEMALE" and (12 <= age <= 55) and pregnancy == "UNKNOWN":
            missing_data.append("Pregnancy status is unverified for female of reproductive age.")

        # Layer 3: Inter-Skill Conflicts & Drug-Drug Interactions
        conflicts = []

        # 3a. Bleeding + Anticoagulation Conflict
        has_anticoagulation = any(
            "anticoagulant" in c or "warfarin" in c or "apixaban" in c or "heparin" in c or "rivaroxaban" in c
            for c in patient_concepts
        )
        has_active_bleeding = any(
            "gi_bleed" in c or "melena" in c or "hematemesis" in c or "intracranial_hemorrhage" in c or "نزيف" in c
            for c in patient_concepts
        )

        if has_anticoagulation and has_active_bleeding:
            conflicts.append({
                "skill_a": "Cardiology / Anticoagulation",
                "skill_b": "Gastroenterology / Emergency Bleeding",
                "conflict_type": "LETHAL_CONTRAINDICATION_INTERACTION",
                "resolution": "Anticoagulation must be withheld immediately. Emergency endoscopy and reversal protocol required."
            })
            emergency_redirection = True

        # 3b. Deterministic Critical DDI Engine
        detected_ddis = self.check_drug_interactions(active_medications, demographics)
        for ddi in detected_ddis:
            conflicts.append({
                "skill_a": "Pharmacology",
                "skill_b": "Clinical Safety",
                "conflict_type": f"CRITICAL_DDI_{ddi['severity']}",
                "resolution": f"{ddi['rule_name']}: {ddi['immediate_action']}"
            })
            if ddi.get("severity") in ["NEVER_EVENT_ABSOLUTE", "HIGH_CRITICAL"]:
                emergency_redirection = True

        # Layer 4: Determine Gate Status and Action Plan
        if emergency_redirection:
            status = "SAFE_ABSTENTION_EMERGENCY_ESCALATION"
            user_msg = "EMERGENCY CLINICAL RED FLAG DETECTED. Immediate in-person emergency evaluation is required. Do not wait for online assessments."
            clinician_sum = f"Critical red flags detected: {[f['symptom_or_vital'] for f in detected_red_flags]}. Immediate emergency escalation initiated."
        elif missing_data:
            status = "SAFE_ABSTENTION_DATA_DEFICIT"
            user_msg = f"Assessment paused for patient safety. Mandatory clinical data missing: {', '.join(missing_data)}."
            clinician_sum = f"Safe abstention triggered due to missing parameters: {missing_data}."
        else:
            status = "PASSED_PROCEED"
            user_msg = "Clinical safety gate passed. No acute emergency red flags detected."
            clinician_sum = "All safety checks passed. Context ready for non-emergency clinical decision support."

        return {
            "verdict_id": verdict_id,
            "timestamp": timestamp,
            "gate_status": status,
            "red_flags_detected": detected_red_flags,
            "critical_ddis_detected": detected_ddis,
            "missing_mandatory_data": missing_data,
            "provenance_violations": [],
            "inter_skill_conflicts": conflicts,
            "governance_banner": "ALGORITHMICALLY VERIFIED REFERENCE ENGINE — REQUIRES LICENSED CLINICIAN REVIEW PRIOR TO CLINICAL APPLICATION",
            "action_plan": {
                "user_safe_message": user_msg,
                "clinician_summary": clinician_sum,
                "emergency_redirection_required": emergency_redirection,
                "emergency_contacts": ["123 (Egypt)", "997 (Saudi Arabia)", "911 (US)", "112 (EU/UK)"] if emergency_redirection else []
            }
        }
