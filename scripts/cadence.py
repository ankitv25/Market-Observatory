"""Named New York collection slots and observation-date freshness."""
from datetime import date, datetime, time, timedelta
import json
import os
from pathlib import Path
import re
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
ZONE = ZoneInfo("America/New_York")
SLOTS = (("07:17", "International morning"), ("09:00", "US pre-open"),
         ("12:30", "Midday"), ("16:30", "US close"), ("22:47", "Final reconciliation"))
WEEKDAY_TIMES = tuple(value for value, _ in SLOTS)
WEEKEND_TIMES = ("10:17",)
WORKFLOW = "https://github.com/ankitv25/Market-Observatory/actions/workflows/refresh.yml"
CALENDAR_SOURCE = "https://www.nyse.com/trade/hours-calendars"
# Exchange-published calendar. A dated table also preserves the special 2028
# New Year's treatment that a generic US federal-holiday calendar would miss.
HOLIDAYS = {
    2026: "01-01 01-19 02-16 04-03 05-25 06-19 07-03 09-07 11-26 12-25",
    2027: "01-01 01-18 02-15 03-26 05-31 06-18 07-05 09-06 11-25 12-24",
    2028: "01-17 02-21 04-14 05-29 06-19 07-04 09-04 11-23 12-25",
}
EARLY_CLOSES = {2026: "11-27 12-24", 2027: "11-26", 2028: "07-03 11-24"}


def targets(now):
    day = now.astimezone(ZONE).date()
    result = []
    for offset in range(-8, 15):
        current = day + timedelta(days=offset)
        for value in WEEKDAY_TIMES if current.weekday() < 5 else WEEKEND_TIMES:
            result.append(datetime.combine(current, time.fromisoformat(value), ZONE))
    return result


def session_day(day):
    return day.weekday() < 5 and day.strftime("%m-%d") not in HOLIDAYS.get(day.year, "").split()


def expected_close(now):
    local = now.astimezone(ZONE)
    day = local.date()
    closing = time(13, 10) if day.strftime("%m-%d") in EARLY_CLOSES.get(day.year, "").split() else time(16, 10)
    if not session_day(day) or local.time() < closing:
        day -= timedelta(days=1)
    while not session_day(day):
        day -= timedelta(days=1)
    return day.isoformat()


def source_freshness(edition, now):
    expected = expected_close(now)
    markets = edition.get("markets", [])
    core = [r for r in markets if r.get("group") in ("Indices", "Sectors")]
    stale = [r.get("symbol", r.get("id")) for r in core if r.get("stats", {}).get("day", "") < expected]
    groups = {}
    for row in markets:
        groups.setdefault(row.get("group", "Other"), []).append(row.get("stats", {}).get("day"))
    observations = {key: dict(first=min(days), last=max(days), instruments=len(days))
                    for key, values in groups.items() if (days := [d for d in values if d])}
    return dict(expected_us_close=expected, core_current=len(core)-len(stale), core_total=len(core),
                core_stale=stale, groups=observations,
                treasury=(edition.get("curve", {}).get("rows") or [{}])[-1].get("date"),
                macro=edition.get("macro", {}).get("date"),
                portfolios={key: value.get("live", {}).get("date") for key,value in edition.get("books", {}).items()},
                transport=edition.get("source_status", {}), calendar_source=CALENDAR_SOURCE,
                calendar_verified=now.astimezone(ZONE).year in HOLIDAYS)


def refresh_due(created, now, edition=None):
    latest = max(t for t in targets(now) if t <= now)
    collected = datetime.fromisoformat(created)
    if collected < latest:
        return True
    # Successful transport may carry old source dates. Retry once per hour
    # while the expected completed US session remains absent.
    if edition and now-collected >= timedelta(hours=1):
        freshness = source_freshness(edition, now)
        return not freshness["core_total"] or bool(freshness["core_stale"])
    return False


def slot_decision(edition, now, event="schedule"):
    latest = max(t for t in targets(now) if t <= now)
    created = edition.get("created", "1970-01-01T00:00:00+00:00")
    collected = datetime.fromisoformat(created)
    missed = [t.isoformat() for t in targets(now) if collected < t < latest]
    label = dict(SLOTS).get(latest.strftime("%H:%M"), "Weekend review")
    return dict(due=event != "schedule" or refresh_due(created, now, edition),
                at=latest.isoformat(), name=label, lateness_seconds=round((now-latest).total_seconds()),
                missed_slots=missed, manual=event != "schedule")


def metadata(created):
    now = datetime.fromisoformat(created)
    ledger = ROOT / "CADENCE.md"
    recent = []
    for line in ledger.read_text().splitlines() if ledger.exists() else []:
        fields = [value.strip() for value in line.strip("|").split("|")]
        if len(fields) != 7 or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*", fields[0]):
            continue
        if datetime.fromisoformat(fields[0]) > now:
            continue
        link = re.search(r"\]\((https://github.com/[^)]+)\)", fields[6])
        recent.append(dict(created=fields[0], markets=fields[2], treasury=fields[3],
                           notes=int(fields[4]), url=link[1] if link else None))
    return dict(timezone=ZONE.key, weekdays=list(WEEKDAY_TIMES), weekends=list(WEEKEND_TIMES),
                slots=[dict(time=value, name=name) for value,name in SLOTS],
                calendar=dict(holidays=HOLIDAYS, early_closes=EARLY_CLOSES, source=CALENDAR_SOURCE),
                targets=[t.isoformat() for t in targets(now)], workflow=WORKFLOW,
                catchup="Every 15 minutes at 13, 28, 43 and 58", recent=recent[-6:][::-1],
                scheduling_note="GitHub queues scheduled runs and can delay or drop them. Targets are requested times.")


if __name__ == "__main__":
    latest = json.loads((ROOT / "dashboard/latest.json").read_text())
    now = datetime.now(ZONE)
    run = slot_decision(latest, now, os.environ.get("GITHUB_EVENT_NAME", "manual"))
    decision = str(run["due"]).lower()
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
            stream.write(f"due={decision}\n")
    print(json.dumps(run))
