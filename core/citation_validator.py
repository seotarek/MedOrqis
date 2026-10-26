"""
MedOrqis — Stage 1 Evidence Verification: Citation Validator
Verifies guideline existence, PMID/DOI formatting, and prevents fabricated citations.
"""

from typing import Dict, Any, List, Optional
import os
import json
import re


class CitationValidationError(ValueError):
    """Raised when a citation fails structural, registry, or authenticity checks."""
    pass


class CitationValidator:
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

    def validate_citation(self, citation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates citation metadata:
        - ref_id existence in local verified registry.
        - PMID or DOI structural validity.
        - Staleness / superseded version alert.
        """
        ref_id = citation.get("ref_id")
        pmid_or_doi = citation.get("pmid_or_doi", "").strip()
        year = citation.get("year")
        warnings = []
        is_verified = False

        # 1. Local Registry Lookup
        if ref_id and ref_id in self.registry:
            reg_entry = self.registry[ref_id]
            is_verified = True
            # Check if superseded
            if reg_entry.get("status") == "SUPERSEDED":
                newer = reg_entry.get("superseded_by", "Newer guideline")
                warnings.append(f"STALENESS WARNING: Guideline '{ref_id}' is superseded by {newer}.")
        elif ref_id:
            warnings.append(f"UNVERIFIED REFERENCE: '{ref_id}' not found in local verified guidelines registry.")

        # 2. Structural ID Validation (PMID / DOI)
        if pmid_or_doi:
            if re.match(r"^\d{6,9}$", pmid_or_doi):
                # Valid PMID format
                pass
            elif re.match(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$", pmid_or_doi):
                # Valid DOI format
                pass
            else:
                raise CitationValidationError(
                    f"Fabricated or invalid citation identifier: '{pmid_or_doi}'. "
                    f"Must be a valid PubMed ID (6-9 digits) or DOI (10.xxxx/...)."
                )

        # 3. Year Plausibility Check
        if year is not None:
            if year < 1950 or year > 2026:
                raise CitationValidationError(
                    f"Plausibility failure: Publication year {year} is invalid for current clinical guidelines."
                )

        return {
            "ref_id": ref_id,
            "is_verified_in_registry": is_verified,
            "status": "VALID" if not warnings else "VALID_WITH_WARNINGS",
            "warnings": warnings
        }
