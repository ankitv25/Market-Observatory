import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from edition_quality import quality_errors

# Immutable historical fixture. New editions exercise the same gate in verify.py.
FIXTURE=json.loads((ROOT/"editions/2026-11/20261107T172033-0500.json").read_text())


class QualityGateTest(unittest.TestCase):
    def test_known_good_edition(self):
        self.assertEqual(quality_errors(FIXTURE),[])

    def test_equities_only_cannot_publish_as_multi_asset(self):
        edition=dict(FIXTURE, markets=[r for r in FIXTURE["markets"] if r["group"] in ("Indices","Sectors")])
        self.assertTrue(any("FX: missing" in msg for msg in quality_errors(edition)))

    def test_unit_and_horizon_errors_are_detected(self):
        edition=copy.deepcopy(FIXTURE)
        metrics=edition["markets"][0]["stats"]
        metrics["pct"]*=100
        metrics["six"]+=1
        metrics["base"]="2000-01-01"
        errors=quality_errors(edition)
        for field in ("pct","six","anchor"):
            self.assertTrue(any(field in msg for msg in errors))

    def test_relabelled_index_fails_registry_match(self):
        edition=copy.deepcopy(FIXTURE)
        index=next(r for r in edition["markets"] if r["id"] == "spx")
        index.update(symbol="SPY",unit="GBP",group="FX")
        self.assertTrue(any("registry" in error for error in quality_errors(edition)))

    def test_future_curve_and_macro_cannot_pass(self):
        edition=copy.deepcopy(FIXTURE)
        edition["curve"]["rows"][-1]["date"]="2099-01-01"
        edition["macro"]["date"]="2099-01-01"
        errors=quality_errors(edition)
        for category in ("curve","Macro"):
            self.assertTrue(any(category in msg for msg in errors))
