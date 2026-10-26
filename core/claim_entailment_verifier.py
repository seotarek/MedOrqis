"""
MedOrqis — Stage 2 Evidence Verification: Claim Entailment Verifier (v2.1)
Checks alignment between clinical recommendations and referenced guideline scopes,
detecting population mismatches, clinical contradictions, and cross-domain mismatches.
"""

from typing import Dict, Any, List, Optional
import os
import json


class ClaimEntailmentVerifier:
    def __init__(self, registry_path: Optional[str] = None):
        if registry_path is None:
            registry_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "dictionaries",
                "verified_guidelines_registry.json"
            )
        self.registry_path = registry_path
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.registry = {item["ref_id"]: item for item in data.get("guidelines", [])}
        else:
            self.registry = {}

    def verify_claim_entailment(
        self,
        claim_text: str,
        ref_id: str,
        patient_age_years: Optional[float] = None,
        patient_is_pregnant: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluates whether a cited guideline genuinely supports the clinical claim.
        1. Checks for population mismatches (Adult vs Pediatric, Pregnancy).
        2. Checks against prohibited or contradicted clinical claims in the guideline.
        3. Validates clinical domain keywords to detect irrelevant citations.
        """
        guideline = self.registry.get(ref_id)
        if not guideline:
            return {
                "ref_id": ref_id,
                "entailment_status": "INSUFFICIENT_EVIDENCE",
                "grade_certainty": "LOW_GRADE_C",
                "rationale": f"Guideline '{ref_id}' not found in registry to verify entailment.",
                "population_mismatch_detected": False
            }

        target_pop = guideline.get("target_population", "").upper()
        pop_mismatch = False
        mismatch_reason = ""

        # 1. Check pediatric vs adult population mismatch
        if patient_age_years is not None:
            if patient_age_years < 18 and "ADULT" in target_pop and "PEDIATRIC" not in target_pop:
                pop_mismatch = True
                mismatch_reason = f"POPULATION MISMATCH: Guideline '{ref_id}' is validated only for {target_pop}, but patient is {patient_age_years} years old."
            elif patient_age_years >= 18 and "PEDIATRIC" in target_pop and "ADULT" not in target_pop:
                pop_mismatch = True
                mismatch_reason = f"POPULATION MISMATCH: Pediatric guideline '{ref_id}' cannot be applied directly to adult patient ({patient_age_years}y)."

        # Check pregnancy
        if patient_is_pregnant and "PREGNANCY_EXCLUDED" in target_pop:
            pop_mismatch = True
            mismatch_reason = f"POPULATION MISMATCH: Guideline '{ref_id}' explicitly excludes pregnant patients."

        if pop_mismatch:
            return {
                "ref_id": ref_id,
                "entailment_status": "POPULATION_MISMATCH",
                "grade_certainty": "LOW_GRADE_C",
                "rationale": mismatch_reason,
                "population_mismatch_detected": True
            }

        claim_lower = claim_text.lower().strip()

        # 2. Check for contraindicated or prohibited claims
        prohibited_claims = guideline.get("prohibited_or_contraindicated_claims", [])
        for prohibited in prohibited_claims:
            p_lower = prohibited.lower()
            # If significant keywords of the prohibited claim appear together in claim_text
            p_words = [w for w in p_lower.split() if len(w) > 3]
            match_count = sum(1 for w in p_words if w in claim_lower)
            if p_lower in claim_lower or (p_words and match_count >= len(p_words) - 1):
                return {
                    "ref_id": ref_id,
                    "entailment_status": "CONTRADICTED",
                    "grade_certainty": "LOW_GRADE_C",
                    "rationale": f"CONTRADICTION DETECTED: Claim contradicts guideline '{ref_id}' recommendations: '{prohibited}'.",
                    "population_mismatch_detected": False,
                    "is_contraindicated": True
                }


        # 3. Check domain keywords alignment
        domain_keywords = guideline.get("clinical_domain_keywords", [])
        if domain_keywords:
            matched_keywords = [kw for kw in domain_keywords if kw.lower() in claim_lower]
            if not matched_keywords:
                return {
                    "ref_id": ref_id,
                    "entailment_status": "UNSUPPORTED_DOMAIN_MISMATCH",
                    "grade_certainty": "LOW_GRADE_C",
                    "rationale": f"DOMAIN MISMATCH: Claim does not contain relevant clinical keywords for guideline '{ref_id}' ({guideline.get('title')}).",
                    "population_mismatch_detected": False
                }

        # 4. Baseline supported check
        grade = guideline.get("grade_evidence_level", "MODERATE_GRADE_B")
        return {
            "ref_id": ref_id,
            "entailment_status": "SUPPORTED",
            "grade_certainty": grade,
            "rationale": f"Claim aligns with {guideline.get('title')} ({guideline.get('source_authority')}).",
            "population_mismatch_detected": False
        }
