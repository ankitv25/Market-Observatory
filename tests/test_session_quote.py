import unittest
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from markets import session_quote


class SessionQuoteTest(unittest.TestCase):
    def test_partial_quote_uses_prior_session_without_changing_history(self):
        now=datetime(2026,11,20,18,tzinfo=timezone.utc)
        history=[["2026-11-19",100]]
        payload={"meta":{"regularMarketTime":now.timestamp(),"regularMarketPrice":102,"exchangeTimezoneName":"America/New_York"}}
        quote=session_quote(payload,history,now)
        self.assertAlmostEqual(quote["pct"],2)
        self.assertEqual(quote["previous_day"],"2026-11-19")
        self.assertEqual(history,[["2026-11-19",100]])
        payload["meta"]["regularMarketTime"]+=60
        self.assertIsNone(session_quote(payload,history,now))

    def test_complete_close_still_uses_previous_day(self):
        now=datetime(2026,11,20,22,tzinfo=timezone.utc)
        payload={"meta":{"regularMarketTime":now.timestamp(),"regularMarketPrice":102,"exchangeTimezoneName":"America/New_York"}}
        quote=session_quote(payload,[["2026-11-19",100],["2026-11-20",102]],now)
        self.assertEqual(quote["previous_day"],"2026-11-19")
