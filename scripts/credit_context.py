"""Monthly Federal Reserve research context, retained with its published vintage."""
import csv
import io
import math
from datetime import date, datetime
from context_data import read_text

URL = "https://www.federalreserve.gov/econres/notes/feds-notes/ebp_csv.csv"


def parse_credit_context(raw, retrieved_at):
    cutoff = datetime.fromisoformat(retrieved_at).date()
    records = {}
    for record in csv.DictReader(io.StringIO(raw)):
        day = date.fromisoformat(record["date"])
        if day > cutoff:
            continue
        try:
            spread, premium = float(record["gz_spread"]), float(record["ebp"])
        except (ValueError, TypeError):
            continue
        if math.isfinite(spread) and math.isfinite(premium) and spread >= 0:
            records[day.isoformat()] = dict(date=day.isoformat(), gz_spread=spread, ebp=premium)
    if len(records) < 2:
        raise ValueError("Monthly credit context needs two observations")
    return dict(source="Federal Reserve Board staff research", url=URL,
                frequency="Monthly", units="percentage points", retrieved_at=retrieved_at,
                rows=[records[k] for k in sorted(records)[-36:]])


def collect_credit_context(retrieved_at):
    return parse_credit_context(read_text(URL), retrieved_at)
