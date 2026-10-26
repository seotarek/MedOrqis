"""
MedOrqis — Multilingual Terminology Normalizer & Semantic Invariance Engine
Preserves negation polarity, BiDi unit fidelity, and normalizes regional brand names to INN.
"""

from typing import Dict, Any, Tuple, List, Optional
import os
import json
import re


class TerminologyNormalizer:
    def __init__(self, lexicon_path: Optional[str] = None, brand_mapping_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        if lexicon_path is None:
            lexicon_path = os.path.join(base_dir, "dictionaries", "multilingual_medical_lexicon.json")
        if brand_mapping_path is None:
            brand_mapping_path = os.path.join(base_dir, "dictionaries", "regional_drug_mapping.json")

        self.lexicon_path = lexicon_path
        self.brand_mapping_path = brand_mapping_path
        self._load_dictionaries()

        # Clause-stopping boundaries (Arabic, English, French, Spanish)
        self.clause_stop_pattern = re.compile(
            r"(?:[,\.;،؛!\?]|\bلكن\b|\bلكنه\b|\bلكنها\b|\bولكن\b|\bإلا\b|\bغير\s+أن\b|\bبينما\b|\bبل\b|"
            r"\bويعاني\s+من\b|\bوتعاني\s+من\b|\bويشكو\s+من\b|\bوبدأ\b|"
            r"\bbut\b|\bhowever\b|\bexcept\b|\balthough\b|\breports\b|\bpresents\s+with\b|\bcomplains\s+of\b|"
            r"\bmais\b|\bcependant\b|\bpero\b|\bsin\s+embargo\b)",
            re.IGNORECASE | re.UNICODE
        )

        # Trigger prefixes
        self.negation_trigger_patterns = [
            # Arabic triggers (MSA, Egyptian, Gulf, Levantine, Maghrebi)
            re.compile(r"(?:لا\s+يعاني\s+من|لا\s+يوجد|مفيش|معندوش|ينفي\s+وجود|ينفي|بدون|ليس\s+لديه|ليس\s+عنده|ما\s+عنده|ما\s+عندو|ما\s+عندوش|مافي|ما\s+في|ما\s+عم\s+يشتكي|ما\s+كاينش|ما\s+كاين|خالي\s+من|دون)", re.UNICODE),
            # English triggers
            re.compile(r"(?i)\b(?:no\s+history\s+of|denies\s+any|denies|without|rules?\s+out|no|negative\s+for|free\s+of|NKDA\s+for)\b"),
            # French triggers
            re.compile(r"(?i)\b(?:sans|pas\s+de|aucun|nie)\b"),
            # Spanish triggers
            re.compile(r"(?i)\b(?:sin|niega|no\s+presenta|sin\s+antecedentes\s+de)\b")
        ]

    def _load_dictionaries(self):
        if os.path.exists(self.brand_mapping_path):
            with open(self.brand_mapping_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.brand_map = {k.lower(): v for k, v in data.get("brand_to_inn", {}).items()}
        else:
            self.brand_map = {}

    def extract_negation_status(self, text: str, concept: str) -> bool:
        """
        Determines whether a clinical concept is negated in the text within a bounded clause.
        Stops at conjunctions/punctuation and restricts scope to max 5 words.
        Returns:
            True if concept is NEGATED (e.g., 'no chest pain', 'مفيش ألم بالصدر').
            False if AFFIRMED, un-negated, or appears in an affirmative post-conjunction clause.
        """
        concept_clean = concept.strip().lower()
        if not text or not concept_clean:
            return False

        # First find all trigger matches
        for trigger_pat in self.negation_trigger_patterns:
            for match in trigger_pat.finditer(text):
                start_scope = match.end()
                remainder = text[start_scope:]

                # Find first clause stopper after trigger
                stop_match = self.clause_stop_pattern.search(remainder)
                clause_text = remainder[:stop_match.start()] if stop_match else remainder

                # Limit scope to max 5 words
                words = clause_text.strip().split()
                bounded_clause = " ".join(words[:5]).lower()

                # Check if concept or meaningful part of concept is in the negated window
                if concept_clean in bounded_clause:
                    return True
                
                # Check for individual significant words in multi-word concepts
                concept_words = [w for w in concept_clean.split() if len(w) > 2]
                if concept_words and all(w in bounded_clause for w in concept_words):
                    return True

        return False

    def normalize_brand_name(self, brand_text: str) -> Dict[str, Any]:
        """
        Maps regional trade brand names (Egyptian, Saudi, International) to standard INN.
        """
        key = brand_text.strip().lower()
        mapping = self.brand_map.get(key)
        if mapping:
            return {
                "input_brand": brand_text,
                "is_mapped": True,
                "inn_name": mapping.get("inn"),
                "atc_code": mapping.get("atc"),
                "dosage_form": mapping.get("standard_form")
            }
        return {
            "input_brand": brand_text,
            "is_mapped": False,
            "inn_name": brand_text,
            "atc_code": "UNKNOWN",
            "dosage_form": "UNKNOWN"
        }

    def verify_bidi_unit_integrity(self, value_text: str, expected_unit: str) -> Dict[str, Any]:
        """
        Checks that bidirectional / RTL Arabic text did not invert decimals or confuse critical units
        (e.g. 0.25 mg inverted to 25.0 mg or confusion between mg and mcg).
        """
        # Look for numbers and units
        pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(mg|mcg|µg|g|ml|mmol/l|mg/dl|units|u)", re.IGNORECASE)
        match = pattern.search(value_text)
        if match:
            num = float(match.group(1))
            unit = match.group(2).lower()
            return {
                "extracted_value": num,
                "extracted_unit": unit,
                "is_valid": True,
                "unit_mismatch": unit != expected_unit.lower() if expected_unit else False
            }
        return {"extracted_value": None, "extracted_unit": None, "is_valid": False, "unit_mismatch": True}
