"""
Multilingual Semantic Invariance & Negation Benchmark
Validates negation polarity preservation, BiDi unit fidelity, and brand-to-INN mapping.
"""

import unittest
import json
import os
from core.terminology_normalizer import TerminologyNormalizer


class TestMultilingualBenchmark(unittest.TestCase):

    def setUp(self):
        self.normalizer = TerminologyNormalizer()
        fixtures_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "fixtures",
            "multilingual_clinical_cases.json"
        )
        with open(fixtures_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.cases = data.get("cases", [])

    def test_negation_preservation_benchmark(self):
        """Negation preservation rate must achieve 100% across all evaluated languages/dialects."""
        negation_cases = [c for c in self.cases if c.get("task") == "NEGATION_PRESERVATION"]
        self.assertGreater(len(negation_cases), 0)

        for case in negation_cases:
            detected_neg = self.normalizer.extract_negation_status(
                text=case["input_text"],
                concept=case["concept"]
            )
            self.assertEqual(
                detected_neg,
                case["expected_negation"],
                f"Failed negation check in {case['language']} ({case['dialect']}) for case {case['id']}: '{case['input_text']}'"
            )

    def test_bidi_unit_fidelity_benchmark(self):
        """BiDi numeric and unit fidelity must achieve 100% accuracy."""
        bidi_cases = [c for c in self.cases if c.get("task") == "BIDI_UNIT_FIDELITY"]
        self.assertGreater(len(bidi_cases), 0)

        for case in bidi_cases:
            res = self.normalizer.verify_bidi_unit_integrity(
                value_text=case["input_text"],
                expected_unit=case["expected_unit"]
            )
            self.assertTrue(res["is_valid"], f"Failed extraction for case {case['id']}")
            self.assertEqual(res["extracted_value"], case["expected_val"])
            self.assertEqual(res["extracted_unit"], case["expected_unit"])
            self.assertFalse(res["unit_mismatch"])

    def test_brand_to_inn_normalization_benchmark(self):
        """Regional brand mapping to INN must achieve 100% on registered catalog."""
        brand_cases = [c for c in self.cases if c.get("task") == "BRAND_TO_INN"]
        self.assertGreater(len(brand_cases), 0)

        for case in brand_cases:
            norm_res = self.normalizer.normalize_brand_name(case["brand_input"])
            self.assertTrue(norm_res["is_mapped"], f"Failed to map brand: {case['brand_input']}")
            self.assertEqual(norm_res["inn_name"], case["expected_inn"])


if __name__ == "__main__":
    unittest.main()
