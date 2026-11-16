"""The forward NAV includes launch fees and is tracked against a book-specific reference."""
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from edition_quality import portfolio_errors
from portfolio_data import parse_nav, period_returns, project_books, session_attribution


class LivePortfolioTest(unittest.TestCase):
    def setUp(self):
        self.dates = ["2026-07-15", "2026-07-16"]
        facts = dict(reference="S&P 500", fee_bps=15, dealing_bps=10, currency="USD", pricing="adjusted")
        self.nav = [99.8994, 101.0]
        self.ref = [100, 100.5]
        periods = {k: None for k in ("1M","3M","6M","12M")}
        self.live = dict(dates=self.dates, inception=self.dates[0], asof=self.dates[-1], nav0=100,
                         periods={"Test": dict(periods, SI=.01), "S&P 500": dict(periods, SI=.005)},
                         day={"Test":{"pts":1.1006,"dd":0}}, series={"Test":self.nav,"S&P 500":self.ref},
                         ref_series={}, ref_of={"Test":"S&P 500"}, facts={"Test":facts}, labels={"US":"Equity"},
                         ticker_sleeve={"VOO":"US"}, holdings={"Test":{"VOO":1}}, trades={"Test":[]},
                         bridge={"Test":{"vehicles":{"VOO":1.101}, "fee":-.001,"dealing":-.1,"total":1}})
        portfolio = dict(name="Test", key="test", nav=101)
        self.source = dict(order=["test"], portfolios={"test":{"name":"Test","role":"policy"}},
                           books={"test":dict(asof=self.dates[-1], risk={}, construction={}, positioning={}, portfolio=portfolio)})
        self.published = "2026-07-16T18:00:00Z"

    def make_book(self):
        return project_books(self.source, self.live, {}, "1"*40, self.published)["test"]

    def test_publication_gate_detects_corrupted_nav_attribution(self):
        data = {"created": "2026-07-17T10:00:00-04:00", "books": {"test": self.make_book()}}
        self.assertEqual(portfolio_errors(data), [])
        data["books"]["test"]["live"]["session"]["net"] += .1
        self.assertTrue(portfolio_errors(data))

    def test_forward_units_and_launch_price(self):
        row = self.make_book()["live"]
        self.assertAlmostEqual(row["returns"]["SI"],1)
        self.assertAlmostEqual(row["benchmark_returns"]["SI"],.5)
        self.assertIsNone(row["returns"]["3M"])
        self.assertEqual(row["nav"][0],99.8994)
        self.assertEqual(row["opening"],100)
        self.assertEqual(row["holdings"][0]["weight_pct"],100)
        self.assertEqual(row["bridge"]["total"],1)
        self.assertEqual(row["session"]["holding_moves"],[])

    def test_explicit_calendar_anchor(self):
        days = ["2026-01-30","2026-02-27","2026-03-30","2026-03-31"]
        nav = [99,100,101,102]
        source = {"periods":{"x":{"1M":.02,"3M":None,"6M":None,"12M":None,"SI":.02}}}
        self.assertAlmostEqual(period_returns(source,"x",nav,days,100)["1M"],2)
        source["periods"]["x"]["3M"] = .03
        with self.assertRaisesRegex(ValueError,"predates"):
            period_returns(source,"x",nav,days,100)

    def test_daily_reconstruction_includes_dated_costs_and_rejects_other_price_cut(self):
        weights = {"A":.25,"B":.75}
        returns = {"A":.02,"B":-.01}
        trades = [dict(date=self.dates[0],turnover=100),dict(date=self.dates[-1],turnover=15)]
        charges = {"fee_bps":15,"dealing_bps":10}
        close = round(100+.5-.75-.015-.15/252,4)
        session = session_attribution([100,close],self.dates,weights,returns,trades,charges)
        self.assertEqual([r["ticker"] for r in session["holding_moves"]],["B","A"])
        self.assertAlmostEqual(session["dealing"],-.015)
        self.assertAlmostEqual(session["fee"],-.15/252)
        self.assertAlmostEqual(sum(r["points"] for r in session["holding_moves"])+session["fee"]+
                               session["dealing"]+session["residual"], session["net"])
        for invalid in ({"A":.02}, {"A":.02,"B":-.03}):
            mismatch = session_attribution([100,close],self.dates,weights,invalid,trades,charges)
            self.assertEqual(mismatch["holding_moves"],[])
            self.assertAlmostEqual(mismatch["net"],mismatch["gross"]+mismatch["fee"]+mismatch["dealing"])

    def test_source_alignment_and_inception_reconciliation(self):
        del self.live["series"]["S&P 500"][-1]
        with self.assertRaisesRegex(ValueError,"alignment"):
            self.make_book()
        self.ref.append(100.5)
        self.live["bridge"]["Test"]["fee"] = -1
        with self.assertRaisesRegex(ValueError,"holdings"):
            self.make_book()

    def test_no_lookahead_in_source_dates_or_javascript_evaluation(self):
        self.published="2026-07-14T21:00:00Z"
        with self.assertRaisesRegex(ValueError,"dates"):
            self.make_book()
        self.assertEqual(parse_nav('window.LIVE_NAV={"a":[1]};'),{"a":[1]})
        with self.assertRaises(ValueError):
            parse_nav("window.LIVE_NAV={};window.inject()")


if __name__ == "__main__":
    unittest.main()
