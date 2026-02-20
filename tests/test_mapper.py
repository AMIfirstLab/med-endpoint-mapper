import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from endpoint_mapper.mapper import EndpointMapper, normalize


class MapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapper = EndpointMapper.from_json(ROOT / "config/endpoints.json")

    def test_normalization(self):
        self.assertEqual(normalize(" Weight-Loss (%) "), "weight loss")

    def test_alias(self):
        result = self.mapper.map("HbA1c", "metabolic")
        self.assertEqual(result.endpoint_id, "EP-MET-002")
        self.assertEqual(result.match_method, "alias")

    def test_typo_is_fuzzy_review(self):
        result = self.mapper.map("transfection efficency", "drug_delivery")
        self.assertEqual(result.endpoint_id, "EP-LNP-003")
        self.assertTrue(result.needs_review)

    def test_unknown_is_not_forced(self):
        result = self.mapper.map("serum biomarker X", "metabolic")
        self.assertEqual(result.match_method, "unmapped")


if __name__ == "__main__":
    unittest.main()
