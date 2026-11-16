"""Shared New York refresh schedule, run selection and reader metadata."""
from datetime import datetime, time, timedelta
import json
import os
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ZONE = ZoneInfo("America/New_York")
WEEKDAY_TIMES = ("07:17", "13:17", "18:47", "22:47")
WEEKEND_TIMES = ("10:17",)
WORKFLOW = "https://github.com/ankitv25/Market-Observatory/actions/workflows/refresh.yml"


def targets(now):
    day = now.astimezone(ZONE).date()
    times = []
    for offset in range(-8, 15):
        current = day + timedelta(days=offset)
        for value in WEEKDAY_TIMES if current.weekday() < 5 else WEEKEND_TIMES:
            times.append(datetime.combine(current, time.fromisoformat(value), ZONE))
    return times


def refresh_due(created, now):
    latest = max(t for t in targets(now) if t <= now)
    return datetime.fromisoformat(created) < latest


def metadata(created):
    now = datetime.fromisoformat(created)
    ledger = ROOT / "CADENCE.md"
    recent = []
    for line in ledger.read_text().splitlines():
        fields = line.strip("|").split("|")
        if len(fields) != 7 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*", fields[0]):
            continue
        if datetime.fromisoformat(fields[0]) > now:
            continue
        link = re.search(r"\]\((https://github.com/[^)]+)\)", fields[6])
        recent.append(dict(created=fields[0], markets=fields[2], treasury=fields[3],
                           notes=int(fields[4]), url=link[1] if link else None))
    return dict(timezone=ZONE.key, weekdays=list(WEEKDAY_TIMES), weekends=list(WEEKEND_TIMES),
                targets=[t.isoformat() for t in targets(now)], workflow=WORKFLOW,
                catchup="Hourly at minute 43", recent=recent[-6:][::-1])


if __name__ == "__main__":
    latest = json.loads((ROOT / "dashboard/latest.json").read_text())
    now = datetime.now(ZONE)
    run = os.environ.get("GITHUB_EVENT_NAME") != "schedule" or refresh_due(latest["created"], now)
    decision = "true" if run else "false"
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
            stream.write(f"due={decision}\n")
    print(f"Refresh due={decision}. Last edition {latest['created']}, checked {now.isoformat()}.")
