"""Catch session-date, rebalance and hidden-holding errors in daily attribution."""
from datetime import date
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"scripts"))
from daily_bridge import adjusted_history, prior_session_attribution


class PriorSessionAttributionTests(unittest.TestCase):
    def setUp(self):
        # Day one starts 60/40. A rises 10%, B falls 5%, gross gain is 4 NAV
        # points, and the publisher carries the resulting relative weights.
        self.fee = 100*.0015/252
        self.source = {
            "dates": ["2026-11-10", "2026-11-11", "2026-11-12"],
            "holdings": {"SAA": {"A":66/104, "B":38/104}},
            "trades": {"SAA":[]},
            "series": {"SAA":[100, round(104-self.fee,4),105]},
            "facts": {"SAA":{"fee_bps":15,"dealing_bps":10}},
        }
        self.prices = {"A":{"2026-11-10":100,"2026-11-11":110},
                       "B":{"2026-11-10":100,"2026-11-11":95}}
        self.today = date(2026,11,14)

    def bridge(self):
        return prior_session_attribution(self.source,"SAA",self.prices,self.today)

    def test_recovers_prior_day_opening_exposure_and_reconciles_nav(self):
        result = self.bridge()
        moves = {r["ticker"]:r for r in result["holding_moves"]}
        self.assertAlmostEqual(moves["A"]["opening_weight_pct"],60)
        self.assertAlmostEqual(moves["B"]["opening_weight_pct"],40)
        self.assertAlmostEqual(moves["A"]["points"],6)
        self.assertAlmostEqual(moves["B"]["points"],-2)
        self.assertEqual(result["start"],"2026-11-10")
        self.assertEqual(result["end"],"2026-11-11")
        self.assertEqual(result["holdings_date"],"2026-11-12")
        self.assertLess(abs(result["residual"]),0.00005)
        self.assertAlmostEqual(result["net"],sum(r["points"] for r in moves.values())
                               + result["fee"] + result["dealing"] + result["residual"])

    def test_following_session_trade_prevents_carry_back(self):
        self.source["trades"]["SAA"]=[{"date":"2026-11-12","turnover":2.3}]
        self.assertIsNone(self.bridge())

    def test_prior_session_trade_cost_is_included(self):
        self.source["trades"]["SAA"]=[{"date":"2026-11-11","turnover":3.25}]
        self.source["series"]["SAA"][1]=round(104-self.fee-.00325,4)
        result=self.bridge()
        self.assertAlmostEqual(result["dealing"],-.00325)

    def test_missing_position_suppresses_attribution(self):
        del self.source["holdings"]["SAA"]["B"]
        self.assertIsNone(self.bridge())

    def test_missing_exact_date_suppresses_attribution(self):
        self.prices["A"]["2026-11-12"]=self.prices["A"].pop("2026-11-11")
        self.assertIsNone(self.bridge())

    def test_rounding_tolerance_cannot_hide_economic_residual(self):
        self.source["series"]["SAA"][1]+=.005
        self.assertIsNone(self.bridge())

    def test_current_date_quote_does_not_qualify_as_completed(self):
        self.today=date(2026,11,11)
        self.assertIsNone(self.bridge())

    def test_nonfinite_price_suppresses_attribution(self):
        self.prices["A"]["2026-11-11"]=float("nan")
        self.assertIsNone(self.bridge())

    def test_short_record_returns_no_attribution(self):
        self.source["dates"]=self.source["dates"][-2:]
        self.assertIsNone(self.bridge())

    def test_price_fetch_preserves_dates_and_uses_adjusted_close(self):
        payload={"meta":{"exchangeTimezoneName":"America/New_York"},
                 "timestamp":[1794330000,1794416400],
                 "indicators":{"adjclose":[{"adjclose":[100,110]}],
                               "quote":[{"close":[101,111]}]}}
        with patch("daily_bridge.chart",return_value=payload) as chart:
            history=adjusted_history(self.source)
        self.assertEqual(chart.call_count,2)
        self.assertEqual(list(history["A"].values()),[100,110])


if __name__ == "__main__":
    unittest.main()
