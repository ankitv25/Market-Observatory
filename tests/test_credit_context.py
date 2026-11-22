import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from credit_context import parse_credit_context


class CreditContextTest(unittest.TestCase):
    def test_units_missing_values_and_future_observations(self):
        csv = "date,gz_spread,ebp\n2026-08-01,1.2,-.1\n2026-09-01,NaN,.2\n2026-10-01,1.4,-.2\n2027-01-01,3,2\n"
        result = parse_credit_context(csv, "2026-11-21T10:00:00-05:00")
        self.assertEqual(len(result["rows"]), 2)
        self.assertEqual(result["rows"][-1]["gz_spread"], 1.4)
        self.assertEqual(result["rows"][-1]["ebp"], -.2)

    def test_missing_history_rejected(self):
        with self.assertRaises(ValueError):
            parse_credit_context("date,gz_spread,ebp\n2026-10-01,.,.\n", "2026-11-21T10:00:00-05:00")
