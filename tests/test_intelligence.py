"""Regression checks for scored market windows, source eligibility and context."""
from copy import deepcopy
from datetime import date, timedelta
import json
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from intelligence import (SIGNALS, build_intelligence, direction, expected_session,
                          source_status, summarize)


def edition_fixture():
    end = date(2026,11,20)
    days = []
    current = end
    while len(days)<70:
        if current.weekday()<5:
            days.append(current.isoformat())
        current -= timedelta(days=1)
    days.reverse()
    ids = list(dict.fromkeys(k for signal in SIGNALS for k in signal[2]))
    changes = {identifier:1 for identifier in ids}
    changes.update(iwm=2,rsp=2,spy=1,vix=-10,hyg=.5,shy=0)
    rows = [
        dict(id=identifier,name=identifier.upper(),source="Test source",
             history=[[d,100.0] for d in days[:-1]]+[[days[-1],100*(1+changes[identifier]/100)]])
        for identifier in ids
    ]
    return dict(created="2026-11-22T10:00:00-05:00",markets=rows,curve={"rows":[]},macro={})


def row(edition,identifier):
    return next(r for r in edition["markets"] if r["id"]==identifier)


def signal(result,identifier,window=0):
    return next(r for r in result["windows"][window]["evidence"] if r["id"]==identifier)


class IntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.edition=edition_fixture()

    def test_expected_close_weekend_holiday_and_early_close(self):
        self.assertEqual(expected_session("2026-11-22T18:00:00-05:00"),date(2026,11,20))
        self.assertEqual(expected_session("2026-11-23T09:00:00-05:00"),date(2026,11,20))
        self.assertEqual(expected_session("2026-11-26T18:00:00-05:00"),date(2026,11,25))
        self.assertEqual(expected_session("2026-11-27T13:05:00-05:00"),date(2026,11,25))
        self.assertEqual(expected_session("2026-11-27T13:11:00-05:00"),date(2026,11,27))

    def test_timezone_is_required(self):
        with self.assertRaises(ValueError):
            expected_session("2026-11-22T10:00:00")

    def test_scored_series_are_strict_context_may_lag_one_weekday(self):
        expected=date(2026,11,20)
        self.assertEqual(source_status("2026-11-19",expected)["status"],"stale")
        self.assertEqual(source_status("2026-11-19",expected,allow_lag=True)["status"],"lagged")
        self.assertEqual(source_status("2026-11-18",expected,allow_lag=True)["status"],"stale")
        self.assertEqual(source_status("2026-11-23",expected)["status"],"future")

    def test_unanimous_positive_evidence_and_confidence(self):
        result=build_intelligence(self.edition)
        self.assertEqual(result["regime"],"risk-on")
        self.assertEqual(result["confidence"],100)
        self.assertEqual(result["windows"][0]["coverage"]["eligible"],6)
        self.assertIn("benchmark median",result["summary"])
        self.assertIn("not an estimated probability",result["methodology"]["confidence_note"])

    def test_price_threshold_is_inclusive_despite_float_rounding(self):
        for identifier in ("spx","rut"):
            row(self.edition,identifier)["history"][-1][1]=100.25
        self.assertEqual(signal(build_intelligence(self.edition),"us_equity")["vote"],1)
        self.assertEqual(direction(-.25,.25),-1)
        self.assertEqual(direction(.2499,.25),0)

    def test_breadth_uses_only_matched_eligible_sectors(self):
        for identifier in ("xlk","xlc","xly"):
            row(self.edition,identifier)["history"].pop()
        result=build_intelligence(self.edition)
        self.assertEqual(signal(result,"breadth")["status"],"included")
        self.assertIn("8 of 8",signal(result,"breadth")["detail"])
        self.assertFalse(next(s for s in result["sources"] if s["id"]=="xlk")["used_in_score"])
        row(self.edition,"xlp")["history"].pop()
        self.assertEqual(signal(build_intelligence(self.edition),"breadth")["status"],"excluded")

    def test_non_matching_pair_is_excluded_despite_fresh_end(self):
        row(self.edition,"eem")["history"].pop(-2)
        result=build_intelligence(self.edition)
        self.assertEqual(signal(result,"global_equity")["status"],"excluded")
        self.assertIn("matched endpoints",signal(result,"global_equity")["reason"])
        self.assertEqual(result["confidence"],83)

    def test_stale_reference_cannot_supply_current_regime(self):
        for r in self.edition["markets"]:
            r["history"]=r["history"][:-1]
        result=build_intelligence(self.edition)
        self.assertEqual(result["regime"],"insufficient evidence")
        self.assertEqual(result["confidence"],0)
        self.assertTrue(all(r["status"]=="excluded" for r in result["windows"][0]["evidence"]))

    def test_requires_volatility_or_credit_confirmation(self):
        self.edition["markets"]=[r for r in self.edition["markets"] if r["id"] not in ("vix","hyg","shy")]
        result=build_intelligence(self.edition)
        self.assertEqual(result["windows"][0]["coverage"]["eligible"],4)
        self.assertEqual(result["regime"],"insufficient evidence")

    def test_four_positive_two_negative_votes_produce_mixed_and_conflict(self):
        row(self.edition,"vix")["history"][-1][1]=110
        row(self.edition,"hyg")["history"][-1][1]=99.5
        result=build_intelligence(self.edition)
        self.assertEqual(result["regime"],"mixed")
        self.assertEqual(result["confidence"],67)
        self.assertTrue(result["windows"][0]["conflicts"])

    def test_one_opposing_vote_can_coexist_with_directional_regime(self):
        row(self.edition,"vix")["history"][-1][1]=110
        result=build_intelligence(self.edition)
        self.assertEqual(result["regime"],"risk-on")
        self.assertEqual(result["confidence"],83)
        self.assertIn("counterweight",result["summary"])

    def test_periods_and_prior_windows_use_one_five_twenty_one_intervals(self):
        days=[d for d,_ in row(self.edition,"spx")["history"]]
        result=build_intelligence(self.edition)
        for w,n in zip(result["windows"],(1,5,21)):
            self.assertEqual(w["start"],days[-1-n])
            self.assertEqual(w["end"],days[-1])
            self.assertEqual(w["previous"]["end"],days[-1-n])
            self.assertEqual(w["previous"]["start"],days[-1-2*n])
        self.assertAlmostEqual(signal(result,"us_equity",1)["threshold"],.25*math.sqrt(5),places=6)

    def test_nonfinite_and_future_market_quotes_are_excluded(self):
        row(self.edition,"vix")["history"][-1][1]=float("nan")
        row(self.edition,"hyg")["history"].append(["2026-11-23",110])
        result=build_intelligence(self.edition)
        self.assertEqual(signal(result,"volatility")["status"],"excluded")
        self.assertEqual(signal(result,"credit")["status"],"excluded")
        json.dumps(result,allow_nan=False)

    def test_future_or_stale_curve_never_changes_votes(self):
        before=build_intelligence(self.edition)
        self.edition["curve"]={"rows":[
            {"date":"2026-11-23","rates":{"2Y":4,"10Y":5,"30Y":5.5}},
            {"date":"2026-11-24","rates":{"2Y":5,"10Y":6,"30Y":6.5}}]}
        after=build_intelligence(self.edition)
        self.assertEqual(before["regime"],after["regime"])
        self.assertEqual(before["confidence"],after["confidence"])
        self.assertEqual(next(c for c in after["context"] if c["id"]=="rates")["status"],"future")
        self.assertFalse(next(s for s in after["sources"] if s["id"]=="rates")["used_in_score"])

    def test_stale_monthly_macro_is_excluded_from_current_score(self):
        self.edition["macro"]={"date":"2026-09-30","score":2.5,"regime":"Expansion"}
        result=build_intelligence(self.edition)
        self.assertEqual(next(c for c in result["context"] if c["id"]=="macro")["status"],"stale")
        self.assertEqual(result["regime"],"risk-on")

    def test_credit_context_uses_month_end_basis_points_and_consecutive_months(self):
        self.edition["credit_context"]={"source":"Fed staff","url":"https://example.org","rows":[
            {"date":"2026-09-01","gz_spread":1.2,"ebp":-.1},
            {"date":"2026-10-01","gz_spread":1.00456,"ebp":-.26533}]}
        result=build_intelligence(self.edition)
        context=next(c for c in result["context"] if c["id"]=="credit_spreads")
        self.assertEqual(context["date"],"2026-10-31")
        self.assertEqual(context["status"],"current")
        metrics={m["label"]:m["value"] for m in context["metrics"]}
        self.assertAlmostEqual(metrics["GZ corporate spread"],100.456)
        self.assertAlmostEqual(metrics["Excess bond premium"],-26.533)
        self.assertAlmostEqual(metrics["GZ corporate spread month-on-month"],-19.544)
        self.assertEqual(result["confidence"],100)

    def test_missing_month_is_not_labeled_month_on_month(self):
        self.edition["credit_context"]={"rows":[
            {"date":"2026-08-01","gz_spread":1.2,"ebp":-.1},
            {"date":"2026-10-01","gz_spread":1.0,"ebp":-.2}]}
        context=next(c for c in build_intelligence(self.edition)["context"] if c["id"]=="credit_spreads")
        self.assertEqual(len(context["metrics"]),2)

    def test_empty_edition_has_no_manufactured_regime(self):
        self.edition["markets"]=[]
        result=build_intelligence(self.edition)
        self.assertIsNone(result["asof"])
        self.assertEqual(result["regime"],"insufficient evidence")
        self.assertEqual(result["confidence"],0)

    def test_results_are_deterministic_and_preserve_input(self):
        original=deepcopy(self.edition)
        first=build_intelligence(self.edition)
        self.assertEqual(first,build_intelligence(self.edition))
        self.assertEqual(original,self.edition)


if __name__=="__main__":
    unittest.main()
