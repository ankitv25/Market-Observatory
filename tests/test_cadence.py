from datetime import datetime
from pathlib import Path
import sys
import unittest
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from cadence import expected_close, refresh_due, slot_decision, source_freshness, targets, ZONE


class CadenceTest(unittest.TestCase):
    def test_targets_follow_new_york_daylight_time(self):
        dates = targets(datetime(2026,10,31,12,tzinfo=ZONE))
        monday = next(t for t in dates if t.isoformat().startswith("2026-11-02T09:00"))
        friday = next(t for t in dates if t.isoformat().startswith("2026-10-30T09:00"))
        self.assertEqual(friday.astimezone(ZoneInfo("UTC")).hour,13)
        self.assertEqual(monday.astimezone(ZoneInfo("UTC")).hour,14)

    def test_preopen_midday_and_close_have_distinct_slots(self):
        for hour, minute, name in [(9,1,"US pre-open"),(12,31,"Midday"),(16,31,"US close")]:
            now = datetime(2026,11,20,hour,minute,tzinfo=ZONE)
            slot = slot_decision({"created":"2026-11-19T23:00:00-05:00"},now)
            self.assertEqual(slot["name"],name)
            self.assertEqual(slot["lateness_seconds"],60)
            self.assertTrue(slot["due"])

    def test_completed_slot_and_late_coalescing(self):
        now = datetime(2026,11,20,15,43,tzinfo=ZONE)
        edition = {"created":"2026-11-19T23:00:00-05:00"}
        slot = slot_decision(edition,now)
        self.assertEqual(slot["lateness_seconds"],3*3600+13*60)
        self.assertEqual(len(slot["missed_slots"]),2)
        self.assertFalse(refresh_due("2026-11-20T15:41:00-05:00",now))
        self.assertTrue(slot_decision({"created":"2026-11-20T15:41:00-05:00"},now,"workflow_dispatch")["due"])

    def test_successful_transport_with_old_closes_retries(self):
        old = {"markets":[{"symbol":"SPY","group":"Indices","stats":{"day":"2026-11-16"}}]}
        now = datetime(2026,11,17,18,43,tzinfo=ZONE)
        self.assertTrue(refresh_due("2026-11-17T17:20:00-05:00",now,old))
        self.assertFalse(refresh_due("2026-11-17T18:20:00-05:00",now,old))
        old["markets"][0]["stats"]["day"]="2026-11-17"
        self.assertFalse(refresh_due("2026-11-17T17:20:00-05:00",now,old))

    def test_calendar_respects_holiday_and_early_close(self):
        self.assertEqual(expected_close(datetime(2026,11,26,18,tzinfo=ZONE)),"2026-11-25")
        self.assertEqual(expected_close(datetime(2026,11,27,12,tzinfo=ZONE)),"2026-11-25")
        self.assertEqual(expected_close(datetime(2026,11,27,13,17,tzinfo=ZONE)),"2026-11-27")
        self.assertEqual(expected_close(datetime(2028,1,3,9,tzinfo=ZONE)),"2027-12-31")

    def test_weekend_has_one_target_and_last_trading_date(self):
        now = datetime(2026,11,15,12,tzinfo=ZONE)
        today = [t for t in targets(now) if t.date()==now.date()]
        self.assertEqual([(t.hour,t.minute) for t in today],[(10,17)])
        self.assertEqual(expected_close(now),"2026-11-13")

    def test_family_observation_ranges_do_not_hide_retained_sources(self):
        edition={"markets":[{"symbol":"SPY","group":"Indices","stats":{"day":"2026-11-19"}},
                            {"symbol":"XLK","group":"Sectors","stats":{"day":"2026-11-20"}}],
                 "macro":{"date":"2026-09-30"},"source_status":{"Markets":{"status":"retained"}}}
        status = source_freshness(edition,datetime(2026,11,20,20,tzinfo=ZONE))
        self.assertEqual(status["core_current"],1)
        self.assertEqual(status["core_stale"],["SPY"])
        self.assertEqual(status["macro"],"2026-09-30")
        self.assertEqual(status["transport"]["Markets"]["status"],"retained")


if __name__ == "__main__":
    unittest.main()
