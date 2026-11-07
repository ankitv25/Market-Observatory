"""Official nominal Treasury curves and a vintage-aligned public macro snapshot."""

import csv
import io
import json
import math
import re
from datetime import date, datetime, timedelta
from urllib.error import URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


TREASURY_ROOT = (
    "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/"
)
H15_URL = (
    "https://www.federalreserve.gov/datadownload/Output.aspx?rel=H15"
    "&series=bf17364827e38702b42a58cf8eaa3f78&lastobs=300&from=&to="
    "&filetype=csv&label=include&layout=seriescolumn"
)
MRS_REPO = "ankitv25/Macro-Regime-Score"
CORE_TENORS = {"3M", "2Y", "5Y", "10Y", "30Y"}


def read_text(url):
    request = Request(url, headers={
        "User-Agent": "Market-Observatory/1.0 (+https://github.com/ankitv25/Market-Observatory)"
    })
    with urlopen(request, timeout=15) as response:
        return response.read().decode("utf-8-sig")


def numeric(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite observation")
    return number


def treasury_year(year):
    url = (
        f"{TREASURY_ROOT}daily-treasury-rates.csv/{year}/all"
        "?type=daily_treasury_yield_curve&page&_format=csv"
    )
    table = csv.DictReader(io.StringIO(read_text(url)))
    if "Date" not in (table.fieldnames or []):
        raise ValueError("Treasury CSV has no Date column")
    result = {}
    for record in table:
        obs_date = datetime.strptime(record["Date"], "%m/%d/%Y").date()
        rates = {}
        for field, value in record.items():
            match = re.fullmatch(r"(\d+(?:\.\d+)?) (Mo|Yr)", field or "")
            if match and value and value.strip() not in ("N/A", "ND"):
                unit = "M" if match[2] == "Mo" else "Y"
                rates[match[1] + unit] = numeric(value)
        if CORE_TENORS <= rates.keys():
            result[obs_date] = rates
    return result


def h15_curve():
    rows = iter(csv.reader(io.StringIO(read_text(H15_URL))))
    header = next((row for row in rows if row and row[0] == "Time Period"), None)
    if not header:
        raise ValueError("H.15 CSV has no Time Period header")
    maturities = {}
    for index, field in enumerate(header):
        match = re.fullmatch(r"RIFLGFC([MY])(\d{2})_N\.B", field)
        if match:
            maturities[index] = str(int(match[2])) + match[1]
    result = {}
    for row in rows:
        if not row:
            continue
        observation_date = date.fromisoformat(row[0])
        rates = {
            label: numeric(row[index])
            for index, label in maturities.items()
            if index < len(row) and row[index].strip() not in ("", "ND", "N/A")
        }
        if CORE_TENORS <= rates.keys():
            result[observation_date] = rates
    return result


def collect_curve():
    """Return daily par yields in percentage points, retaining missing tenors as absent."""
    today = datetime.now(ZoneInfo("America/New_York")).date()
    start = today - timedelta(days=220)

    def pack(data, source, url):
        rows = [{"date": day.isoformat(), "rates": data[day]}
                for day in sorted(data) if start <= day <= today]
        if len(rows) < 100 or (date.fromisoformat(rows[-1]["date"])
                               - date.fromisoformat(rows[0]["date"])).days < 184:
            raise ValueError("Curve history does not cover six months")
        return {"source": source, "url": url, "rows": rows}

    try:
        history = treasury_year(today.year)
        if start.year != today.year:
            history.update(treasury_year(start.year))
        return pack(history, "U.S. Treasury daily par yield curve",
                    TREASURY_ROOT + "TextView?type=daily_treasury_yield_curve")
    except (URLError, OSError, ValueError) as primary_failure:
        try:
            return pack(h15_curve(), "Federal Reserve H.15 · U.S. Treasury constant maturities",
                        H15_URL)
        except (URLError, OSError, ValueError) as secondary_failure:
            raise RuntimeError(
                f"Treasury curve unavailable ({primary_failure}); H.15 unavailable ({secondary_failure})"
            ) from secondary_failure


def collect_macro():
    """Read all MRS inputs from one immutable public commit and one scored month."""
    rev = json.loads(read_text(f"https://api.github.com/repos/{MRS_REPO}/commits/HEAD"))["sha"]
    if not re.fullmatch(r"[a-f0-9]{40}", rev):
        raise ValueError("Invalid MRS source revision")
    base = f"https://raw.githubusercontent.com/{MRS_REPO}/{rev}/dashboard/data/"

    def read_json(name):
        return json.loads(read_text(f"{base}{name}.json"))

    metadata = read_json("metadata")
    month = date.fromisoformat(metadata["data_through"]).isoformat()
    composite = next((row for row in read_json("composite_history") if row["date"] == month), None)
    pillars = next((row for row in read_json("pillars_wide") if row["date"] == month), None)
    if not composite or not pillars:
        raise ValueError(f"Incomplete MRS snapshot for {month}")
    score = numeric(metadata["latest_composite_z"])
    regime = metadata["latest_regime_confirmed"]
    if (not math.isclose(score, numeric(composite["composite"]), abs_tol=0.0001)
            or regime != composite["regime_confirmed"]):
        raise ValueError("MRS metadata does not reconcile to composite history")
    pillar_scores = {key: numeric(pillars[key + "_score"])
                     for key in ("growth", "credit", "stress", "inflation", "liquidity")}
    parts = [f"The confirmed monthly composite is {score:+.2f}z."]
    if composite.get("top_support") and composite.get("top_drag"):
        parts.append(f"{composite['top_support'].capitalize()} supplied the strongest support. "
                     f"{composite['top_drag'].capitalize()} was the largest drag.")
    return {
        "source": f"Macro Regime Score {metadata['version']}",
        "url": f"https://github.com/{MRS_REPO}/tree/{rev}/dashboard/data",
        "date": month,
        "score": score,
        "regime": regime,
        "pillars": pillar_scores,
        "note": " ".join(parts),
        "source_generated_at": metadata["generated_at"],
    }
