"""
MedOrqis — Terminology Connectors Interface
Standardized adapters for WHO ICD-11, NLM RxNav/UMLS, and FHIR Terminology Servers.
"""

from typing import Dict, Any, Optional
import os


class TerminologyConnector:
    """Base connector interface for external clinical coding terminologies."""
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("TERMINOLOGY_API_KEY")
        self.base_url = base_url

    def lookup_concept(self, term: str) -> Dict[str, Any]:
        raise NotImplementedError


class ICD11Connector(TerminologyConnector):
    """Connector for WHO ICD-11 API."""
    def lookup_concept(self, term: str) -> Dict[str, Any]:
        term_clean = term.strip().lower()
        # Seeded local offline fallback
        offline_table = {
            "atrial fibrillation": {"code": "BC81.3", "title": "Atrial fibrillation"},
            "type 2 diabetes": {"code": "5A11", "title": "Type 2 diabetes mellitus"},
            "hypertension": {"code": "BA00", "title": "Essential hypertension"},
            "pneumonia": {"code": "CA40", "title": "Pneumonia"},
            "pulmonary embolism": {"code": "BD00", "title": "Pulmonary embolism"}
        }
        for k, v in offline_table.items():
            if k in term_clean:
                return {
                    "terminology": "ICD-11",
                    "code": v["code"],
                    "display": v["title"],
                    "source": "OFFLINE_SEED_CACHE"
                }

        return {
            "terminology": "ICD-11",
            "code": "UNKNOWN",
            "display": term,
            "source": "UNMAPPED_OFFLINE"
        }


class RxNavConnector(TerminologyConnector):
    """Connector for NLM RxNav API for RxNorm / INN mapping."""
    def lookup_drug(self, drug_name: str) -> Dict[str, Any]:
        name_clean = drug_name.strip().lower()
        offline_table = {
            "warfarin": {"rxcui": "11289", "inn": "warfarin"},
            "apixaban": {"rxcui": "1364430", "inn": "apixaban"},
            "metformin": {"rxcui": "6809", "inn": "metformin"},
            "amoxicillin": {"rxcui": "723", "inn": "amoxicillin"},
            "lisinopril": {"rxcui": "29046", "inn": "lisinopril"}
        }
        for k, v in offline_table.items():
            if k in name_clean:
                return {
                    "terminology": "RxNorm",
                    "rxcui": v["rxcui"],
                    "inn": v["inn"],
                    "source": "OFFLINE_SEED_CACHE"
                }

        return {
            "terminology": "RxNorm",
            "rxcui": "UNKNOWN",
            "inn": drug_name,
            "source": "UNMAPPED_OFFLINE"
        }
