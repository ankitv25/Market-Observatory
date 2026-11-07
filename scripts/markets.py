"""Daily, dated market histories for Market Observatory (Python standard library).

collect() returns one record per available instrument. Only completed daily bars
are included. The dashboard uses the final two available closes for day change.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import calendar
import json
import math
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

LAB = "https://raw.githubusercontent.com/ankitv25/Convexity-Lab-RM/HEAD/data/lab"
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/"
PRICE_BASIS = "ETF session close, price only"
INDEX_BASIS = "Cash index session close, index points"
FX_BASIS = "Daily spot close, expressed in the quote currency"
FUTURES_BASIS = "Named delivery contract, vendor daily closing price"
# Group, unit, basis, then the instruments in dashboard order.
UNIVERSE = [
    ("Indices", "pts", INDEX_BASIS, [
        ("spx", "^GSPC", "S&P 500"), ("ixic", "^IXIC", "Nasdaq Composite"),
        ("ndx", "^NDX", "Nasdaq 100"), ("dji", "^DJI", "Dow Industrials"),
        ("rut", "^RUT", "Russell 2000")]),
    ("Sectors", "USD", PRICE_BASIS, [
        ("xlk", "XLK", "Technology"), ("xlc", "XLC", "Communication Services"),
        ("xly", "XLY", "Consumer Discretionary"), ("xlp", "XLP", "Consumer Staples"),
        ("xle", "XLE", "Energy"), ("xlf", "XLF", "Financials"),
        ("xlv", "XLV", "Health Care"), ("xli", "XLI", "Industrials"),
        ("xlb", "XLB", "Materials"), ("xlre", "XLRE", "Real Estate"),
        ("xlu", "XLU", "Utilities")]),
    ("Styles", "USD", PRICE_BASIS, [
        ("spy", "SPY", "US large cap"), ("rsp", "RSP", "Equal-weight S&P 500"),
        ("iwf", "IWF", "US large-cap growth"), ("iwd", "IWD", "US large-cap value"),
        ("iwm", "IWM", "US small cap"), ("mtum", "MTUM", "US momentum"),
        ("qual", "QUAL", "US quality")]),
    ("Global", "pts", INDEX_BASIS, [
        ("stoxx50", "^STOXX50E", "Euro STOXX 50"), ("ftse", "^FTSE", "FTSE 100"),
        ("nikkei", "^N225", "Nikkei 225"), ("hsi", "^HSI", "Hang Seng"),
        ("nifty", "^NSEI", "Nifty 50"), ("tsx", "^GSPTSE", "S&P/TSX Composite")]),
    ("Global", "USD", PRICE_BASIS, [
        ("acwi", "ACWI", "All-country equity"), ("efa", "EFA", "Developed ex-US/Canada"),
        ("eem", "EEM", "Emerging markets")]),
    ("Credit", "USD", PRICE_BASIS, [
        ("shy", "SHY", "Short Treasuries"), ("ief", "IEF", "Intermediate Treasuries"),
        ("tlt", "TLT", "Long Treasuries"), ("tip", "TIP", "Inflation-linked Treasuries"),
        ("lqd", "LQD", "Investment-grade credit"), ("hyg", "HYG", "High-yield credit"),
        ("mbb", "MBB", "Agency mortgages"), ("mub", "MUB", "Municipal bonds"),
        ("emb", "EMB", "EM dollar debt"), ("bkln", "BKLN", "Senior loans")]),
    ("Alternatives", "USD", PRICE_BASIS, [
        ("vnq", "VNQ", "Listed real estate"), ("igf", "IGF", "Listed infrastructure"),
        ("dbmf", "DBMF", "Managed futures"), ("gld", "GLD", "Physical gold ETF")]),
    ("Alternatives", "USD/BTC", "UTC daily spot close", [("btc", "BTC-USD", "Bitcoin")]),
    ("Alternatives", "pts", INDEX_BASIS, [("vix", "^VIX", "Cboe VIX")]),
    ("FX", "pts", INDEX_BASIS, [("dxy", "DX-Y.NYB", "US Dollar Index")]),
    ("FX", "USD/EUR", FX_BASIS, [("eurusd", "EURUSD=X", "EUR/USD")]),
    ("FX", "JPY/USD", FX_BASIS, [("usdjpy", "JPY=X", "USD/JPY")]),
    ("FX", "USD/GBP", FX_BASIS, [("gbpusd", "GBPUSD=X", "GBP/USD")]),
    ("FX", "CHF/USD", FX_BASIS, [("usdchf", "CHF=X", "USD/CHF")]),
    ("Futures", "USD/bbl", FUTURES_BASIS, [
        ("wti", "CL=F", "WTI crude"), ("brent", "BZ=F", "Brent crude")]),
    ("Futures", "USD/MMBtu", FUTURES_BASIS, [("natgas", "NG=F", "Natural gas")]),
    ("Futures", "USD/oz", FUTURES_BASIS, [
        ("gold", "GC=F", "Gold"), ("silver", "SI=F", "Silver")]),
    ("Futures", "USD/lb", FUTURES_BASIS, [("copper", "HG=F", "Copper")]),
    ("Futures", "US¢/bu", FUTURES_BASIS, [("corn", "ZC=F", "Corn")]),
    ("Futures", "pts", FUTURES_BASIS, [
        ("es", "ES=F", "S&P 500 E-mini"), ("zn", "ZN=F", "10Y Treasury note")]),
]

INSTRUMENTS = [dict(id=key, symbol=symbol, name=name, group=group, unit=unit, basis=basis)
               for group, unit, basis, members in UNIVERSE for key, symbol, name in members]
MONTHS = "FGHJKMNQUVXZ"
FETCH_ERRORS = (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError,
                IndexError, TypeError, ZoneInfoNotFoundError)


def get_json(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urlopen(request, timeout=12) as response:
        return json.load(response)


def chart(symbol, span="1y"):
    query = f"{YAHOO}{quote(symbol, safe='')}?range={span}&interval=1d"
    result = get_json(query)["chart"]
    if result.get("error") or not result.get("result"):
        raise ValueError(f"No daily history for {symbol}")
    payload = result["result"][0]
    if payload["meta"]["symbol"].upper() != symbol.upper():
        raise ValueError(f"Unexpected series returned for {symbol}")
    return payload


def closed_history(payload, now):
    meta = payload["meta"]
    local_zone = ZoneInfo(meta["exchangeTimezoneName"])
    today = now.astimezone(local_zone).date()
    session = meta.get("currentTradingPeriod", {}).get("regular", {})
    points = {}
    for stamp, close in zip(payload["timestamp"], payload["indicators"]["quote"][0]["close"]):
        if close is None or not math.isfinite(close):
            continue
        day = datetime.fromtimestamp(stamp, local_zone).date()
        # Current-day points can be partial. If source session bounds do not
        # identify a completed session for this day, defer it until tomorrow.
        if day > today:
            continue
        if day == today:
            end = session.get("end")
            if not end or datetime.fromtimestamp(end, local_zone).date() != day or now.timestamp() < end + 60:
                continue
        points[day.isoformat()] = close
    history = [[day, points[day]] for day in sorted(points)]
    if len(history) < 2:
        raise ValueError("Fewer than two completed observations")
    return history


def dated_future(spec, generic, now):
    meta = generic["meta"]
    root = spec["symbol"].split("=")[0]
    suffix = meta["exchangeName"]
    match = re.search(r"\b([A-Z][a-z]{2})[ -](\d{4}|\d{2})\b", meta.get("shortName", ""))
    if match and match[1] in calendar.month_abbr:
        month = list(calendar.month_abbr).index(match[1])
        candidates = [(month, int(match[2]) % 100)]
    else:
        # Some continuous symbols omit delivery month. Resolve by matching
        # two dated closes on the same sessions, never by assuming a roll day.
        month_index = now.year * 12 + now.month - 1
        candidates = [((month_index+i) % 12 + 1, ((month_index+i) // 12) % 100) for i in range(5)]

    generic_last = closed_history(generic, now)[-2:]
    for month, year in candidates:
        symbol = f"{root}{MONTHS[month-1]}{year:02}.{suffix}"
        try:
            payload = chart(symbol)
            history = closed_history(payload, now)
            dated_days = dict(history[-5:])
            # When the vendor states the delivery month, the named contract is
            # authoritative even if the continuous series crossed a roll today.
            if len(candidates) == 1 or all(
                day in dated_days and math.isclose(value, dated_days[day], abs_tol=0.00001)
                for day, value in generic_last
            ):
                return symbol, history, f"{calendar.month_abbr[month]} {2000+year}"
        except FETCH_ERRORS:
            continue
    raise ValueError(f"Could not resolve the named {root} contract")


def live_record(spec, now):
    symbol = spec["symbol"]
    payload = chart(symbol)
    instrument = spec.copy()
    if spec["group"] == "Futures":
        symbol, history, delivery = dated_future(spec, payload, now)
        instrument.update(symbol=symbol, contract=delivery, basis=f"{FUTURES_BASIS} · {delivery}")
    else:
        history = closed_history(payload, now)
    return dict(instrument, history=history, source="Yahoo Finance",
                url=f"https://finance.yahoo.com/quote/{quote(symbol, safe='')}/history/")


def archived_series(failed):
    """Exact-symbol fallback. An ETF is never substituted for its index."""
    archived = {}
    for filename in ["global-markets", "bond-market"]:
        url = f"{LAB}/{filename}.json"
        try:
            items = get_json(url)["instruments"]
            archived.update({item["symbol"]: (item, url) for item in items})
        except FETCH_ERRORS:
            continue
    for spec in failed:
        symbol = spec["symbol"]
        try:
            if symbol in archived:
                item, url = archived[symbol]
            elif spec["group"] == "Sectors":
                url = f"{LAB}/market-{symbol}.json"
                item = get_json(url)
            else:
                continue
            if item.get("symbol") != symbol:
                continue
            rows = {}
            as_of = date.fromisoformat(item["asOf"][:10])
            # The archives may compact old data to month-end. Limit history
            # to the uncompressed year preceding this file's own observation.
            for row in item["history"]:
                day = date.fromisoformat(row["date"])
                value = row.get("close")
                if as_of - timedelta(days=366) <= day <= as_of and value is not None and math.isfinite(value):
                    rows[day.isoformat()] = value
            if len(rows) >= 2:
                yield dict(spec, history=[[day, rows[day]] for day in sorted(rows)],
                           source="Convexity Lab archive", url=url,
                           basis=f"{spec['basis']} · archived snapshot")
        except FETCH_ERRORS:
            continue


def collect():
    """Return available histories in registry order and log missing coverage."""
    now = datetime.now(timezone.utc)

    def fetch(spec):
        try:
            return live_record(spec, now)
        except FETCH_ERRORS as exc:
            print(f"markets: {spec['symbol']} unavailable ({exc})", file=sys.stderr)
            return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        records = list(executor.map(fetch, INSTRUMENTS))
    found = {row["id"]: row for row in records if row}
    failed = [spec for spec in INSTRUMENTS if spec["id"] not in found]
    if failed:
        for row in archived_series(failed):
            found[row["id"]] = row
    return [found[spec["id"]] for spec in INSTRUMENTS if spec["id"] in found]
