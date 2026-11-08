"""Independent financial checks for a candidate edition. Prices retain their native units."""
import calendar
from datetime import date, datetime
import math

from markets import INSTRUMENTS

SERIES = {r["id"]: r for r in INSTRUMENTS}

REQUIRED = {
    "US equity": ("spx", "rut"),
    "global equity": ("nikkei", "stoxx50"),
    "credit": ("lqd", "hyg"),
    "FX": ("dxy", "usdjpy"),
    "commodities": ("wti", "gold"),
    "alternatives": ("vnq", "dbmf"),
}
SECTORS = set("XLB XLC XLY XLP XLE XLF XLV XLI XLK XLRE XLU".split())


def quality_errors(edition):
    errors = []
    cutoff = datetime.fromisoformat(edition["created"]).date()
    rows = edition["markets"]
    ids = {r["id"] for r in rows}
    for group, required in REQUIRED.items():
        for key in required:
            if key not in ids:
                errors.append(f"{group}: missing core series {key}")
    if {r["symbol"] for r in rows if r["group"] == "Sectors"} != SECTORS:
        errors.append("Sector coverage differs from the 11 expected proxies")
    for row in rows:
        key, h, metrics = row["id"], row["history"], row["stats"]
        spec = SERIES.get(key)
        if spec is None or row["group"] != spec["group"] or row["unit"] != spec["unit"]:
            errors.append(f"{key}: registry classification or unit mismatch")
        elif spec["group"] != "Futures" and row["symbol"] != spec["symbol"]:
            errors.append(f"{key}: instrument symbol mismatch")
        end, last = h[-1]
        previous = h[-2][1]
        day = date.fromisoformat(end)
        if day > cutoff:
            errors.append(f"{key}: future market date")
        month_index = day.year * 12 + day.month - 1 - 6
        year, month0 = divmod(month_index, 12)
        month = month0 + 1
        target = date(year, month, min(day.day, calendar.monthrange(year, month)[1])).isoformat()
        anchor = next(((d,v) for d,v in reversed(h) if d <= target), (None,None))
        expected = {"last":last, "change":last-previous,
                    "pct":100*(last-previous)/previous if previous>0 and last>=0 else None,
                    "six":100*(last-anchor[1])/anchor[1] if anchor[1] is not None and anchor[1]>0 and last>=0 else None}
        if metrics.get("base") != anchor[0]:
            errors.append(f"{key}: six-month anchor mismatch")
        for field, value in expected.items():
            actual = metrics.get(field)
            matches = actual is None if value is None else isinstance(actual,(int,float)) and math.isclose(actual,value,abs_tol=1e-8,rel_tol=1e-9)
            if not matches:
                errors.append(f"{key}: {field} fails independent repricing")
    curves = edition["curve"]["rows"]
    curve_days = [r["date"] for r in curves]
    if len(curves)<2 or curve_days != sorted(set(curve_days)) or any(date.fromisoformat(d)>cutoff for d in curve_days):
        errors.append("Sovereign curve: invalid observation sequence")
    if curves and any(not math.isfinite(curves[-1]["rates"].get(k,math.nan)) for k in ("2Y","5Y","10Y","30Y")):
        errors.append("Sovereign curve: missing core tenor")
    macro = edition["macro"]
    if date.fromisoformat(macro["date"])>cutoff or not math.isfinite(macro["score"]):
        errors.append("Macro: invalid confirmed score or vintage")
    return errors
