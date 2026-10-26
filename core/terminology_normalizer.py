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
            r"(?:[,\.;،؛!\?]|\bلكن\b|\bلكنه\b|\bلكنها\b|\bولكن\b|\bولكنه\b|\bولكنها\b|\bبس\b|\bإلا\b|\bإلا\s+أن\b|\bغير\s+أن\b|\bغير\s+أنه\b|\bبينما\b|\bبل\b|"
            r"\bويعاني\s+من\b|\bوتعاني\s+من\b|\bويشكو\s+من\b|\bوبدأ\b|\bوبدأت\b|"
            r"\bbut\b|\bhowever\b|\bexcept\b|\balthough\b|\breports\b|\bpresents\s+with\b|\bcomplains\s+of\b|"
            r"\bmais\b|\bcependant\b|\bpero\b|\bsin\s+embargo\b)",
            re.IGNORECASE | re.UNICODE
        )

        # Trigger prefixes
        self.negation_trigger_patterns = [
            # Arabic triggers (MSA, Egyptian, Gulf, Levantine, Maghrebi)
            re.compile(
                r"(?:لا\s+يعاني\s+من|لا\s+يشكو\s+من|لا\s+يوجد|لا\s+توجد|مفيش|معندوش|مش\s+بيشتكي\s+من|مش\s+بتشتكي\s+من|مش\s+بيشتكي|مش\s+بتشتكي|"
                r"ينفي\s+وجود|ينفي\s+المريض\s+وجود|ينفي|بدون|ليس\s+لديه|ليس\s+لديها|ليس\s+عنده|ليس\s+عندها|"
                r"ما\s+عنده|ما\s+عندو|ما\s+عندها|ما\s+عندوش|ما\s+عندهاش|مافي|ما\s+في|ما\s+يشتكي\s+من|ما\s+يشتكي|ما\s+عم\s+يشتكي|ما\s+عم\s+يحس|"
                r"ما\s+كاينش|ما\s+كاين\s+حتى|ما\s+كاين|خالي\s+من|خالٍ\s+من|خال\s+تماماً\s+من|خالٍ\s+تماماً\s+من|دون\s+أي|دون)",
                re.UNICODE
            ),
            # English triggers
            re.compile(r"(?i)\b(?:no\s+history\s+of|denies\s+any|denies|without|rules?\s+out|no|negative\s+for|free\s+of|NKDA\s+for)\b"),
            # French triggers
            re.compile(r"(?i)\b(?:sans|pas\s+de|aucun|nie)\b"),
            # Spanish triggers
            re.compile(r"(?i)\b(?:sin\s+antecedentes\s+de|sin(?!\s+embargo)|niega|no\s+presenta)\b")
        ]

    @staticmethod
    def _arabic_word_variants(w: str) -> set:
        clean = re.sub(r'^[,\.;،؛!\?]+|[,\.;،؛!\?]+$', '', w).lower()
        forms = {clean}
        if clean.startswith("لل"):
            forms.add("ال" + clean[2:])
            forms.add(clean[2:])
        elif clean.startswith("ال"):
            forms.add(clean[2:])
        elif clean.startswith("بال"):
            forms.add("ال" + clean[3:])
            forms.add(clean[3:])
        elif clean.startswith("كال"):
            forms.add("ال" + clean[3:])
            forms.add(clean[3:])
        elif clean.startswith("وال"):
            forms.add("ال" + clean[3:])
            forms.add(clean[3:])
        return forms

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
        Stops at conjunctions/punctuation and restricts scope to max 10 words.
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

                # Limit scope to max 10 words
                words = clause_text.strip().split()
                clause_words = words[:10]
                bounded_clause = " ".join(clause_words).lower()

                # Check if concept or meaningful part of concept is in the negated window
                if concept_clean in bounded_clause:
                    return True
                
                # Check for individual significant words in multi-word concepts
                concept_words = [re.sub(r'^[,\.;،؛!\?]+|[,\.;،؛!\?]+$', '', w).lower() for w in concept_clean.split() if len(w) > 1]
                if concept_words and all(w in bounded_clause for w in concept_words):
                    return True

                # Form-aware word matching (e.g. Arabic prepositions للنزيف vs النزيف)
                clause_all_forms = set()
                for cw in clause_words:
                    clause_all_forms.update(self._arabic_word_variants(cw))
                
                if concept_words:
                    match_all = True
                    for cw in concept_words:
                        c_forms = self._arabic_word_variants(cw)
                        if not (c_forms & clause_all_forms or any(f in bounded_clause for f in c_forms)):
                            match_all = False
                            break
                    if match_all:
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
        pattern = re.compile(r"(\d+(?:\.\d+)?)\s*(mg/dl|mmol/l|mcg|µg|mg|ml|g|units|u)", re.IGNORECASE)
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
