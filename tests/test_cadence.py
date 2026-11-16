from datetime import datetime
from pathlib import Path
import sys
import unittest
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from cadence import refresh_due, targets, ZONE


class CadenceTest(unittest.TestCase):
    def test_targets_follow_new_york_daylight_time(self):
        dates = targets(datetime(2026, 10, 31, 12, tzinfo=ZONE))
        monday = next(t for t in dates if t.isoformat().startswith("2026-11-02T07:17"))
        friday = next(t for t in dates if t.isoformat().startswith("2026-10-30T07:17"))
        self.assertEqual(friday.astimezone(ZoneInfo("UTC")).hour, 11)
        self.assertEqual(monday.astimezone(ZoneInfo("UTC")).hour, 12)

    def test_completed_slot_does_not_refetch(self):
        now = datetime(2026, 11, 16, 8, 43, tzinfo=ZONE)
        self.assertFalse(refresh_due("2026-11-16T07:21:00-05:00", now))
        self.assertTrue(refresh_due("2026-11-15T10:21:00-05:00", now))

    def test_late_start_catches_up_once(self):
        now = datetime(2026, 11, 16, 15, 43, tzinfo=ZONE)
        self.assertTrue(refresh_due("2026-11-16T07:21:00-05:00", now))
        self.assertFalse(refresh_due("2026-11-16T15:41:00-05:00", now))

    def test_weekend_has_one_target(self):
        now = datetime(2026, 11, 15, 12, tzinfo=ZONE)
        today = [t for t in targets(now) if t.date() == now.date()]
        self.assertEqual([(t.hour, t.minute) for t in today], [(10, 17)])


if __name__ == "__main__":
    unittest.main()
