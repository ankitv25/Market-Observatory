"""Reconcile one completed portfolio session using the publisher's carried holdings.

The public NAV payload exposes the latest session's beginning weights. When that
session has no trade, those weights equal the previous session's normalized
closing weights. Dividing by each vehicle's gross return and normalizing recovers
the previous session's opening weights. Every input must be available and the
result must reconcile to the public NAV before a vehicle attribution is shown.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
import math
from zoneinfo import ZoneInfo

from markets import FETCH_ERRORS, chart

# The public publisher rounds each NAV level to four decimals and a trade's
# turnover to 0.01 percent. These are absolute point rounding bounds.
NAV_ROUNDING = 0.000101


def adjusted_history(source):
    """Fetch each held vehicle once, retaining exact exchange-local dates."""
    tickers = sorted({ticker for weights in source["holdings"].values() for ticker in weights})

    def fetch(ticker):
        try:
            payload = chart(ticker, "1mo")
            zone = ZoneInfo(payload["meta"]["exchangeTimezoneName"])
            records = {}
            for stamp, value in zip(payload["timestamp"], payload["indicators"]["adjclose"][0]["adjclose"]):
                if isinstance(value, (int, float)) and math.isfinite(value) and value > 0:
                    day = datetime.fromtimestamp(stamp, zone).date().isoformat()
                    records[day] = value
            return ticker, records
        except FETCH_ERRORS:
            return ticker, {}

    with ThreadPoolExecutor(max_workers=4) as pool:
        return dict(pool.map(fetch, tickers))


def prior_session_attribution(source, name, prices, today=None):
    """Return a reconciled prior session or None when carry-back cannot be proved."""
    dates = source["dates"]
    if len(dates) < 3:
        return None
    start, end, holdings_date = dates[-3:]
    current = today or datetime.now(ZoneInfo("America/New_York")).date()
    if not start < end < holdings_date or date.fromisoformat(end) >= current:
        return None
    weights = source["holdings"][name]
    trades = source["trades"][name]
    if any(t["date"] == holdings_date and t["turnover"] != 0 for t in trades):
        return None
    # The publisher suppresses positions below 0.05%. An incomplete holdings
    # vector cannot establish a full portfolio attribution.
    if (not weights or any(not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0 for w in weights.values())
            or abs(sum(weights.values())-1) > 1e-8):
        return None
    returns = {}
    for ticker in weights:
        history = prices.get(ticker, {})
        first, last = history.get(start), history.get(end)
        if (not isinstance(first, (int, float)) or not isinstance(last, (int, float))
                or not math.isfinite(first) or not math.isfinite(last) or first <= 0 or last <= 0):
            return None
        returns[ticker] = last/first-1
    recovered = {ticker: weight/(1+returns[ticker]) for ticker, weight in weights.items()}
    scale = sum(recovered.values())
    opening_weights = {ticker: weight/scale for ticker, weight in recovered.items()}
    nav = source["series"][name]
    if len(nav) != len(dates):
        return None
    opening, closing = nav[-3:-1]
    facts = source["facts"][name]
    turnover = sum(t["turnover"] for t in trades if t["date"] == end)
    fee = -opening*facts["fee_bps"]/10000/252
    dealing = -opening*facts["dealing_bps"]/10000*turnover/100
    moves = [
        dict(ticker=ticker, points=opening*opening_weights[ticker]*returns[ticker],
             opening_weight_pct=100*opening_weights[ticker], return_pct=100*returns[ticker],
             adjusted_start=prices[ticker][start], adjusted_end=prices[ticker][end])
        for ticker in weights
    ]
    net = closing-opening
    gross = sum(row["points"] for row in moves)
    residual = net-gross-fee-dealing
    tolerance = NAV_ROUNDING + opening*facts["dealing_bps"]/10000*.00005
    if not math.isfinite(residual) or abs(residual) > tolerance:
        return None
    return dict(
        start=start, end=end, holdings_date=holdings_date, net=net, gross=gross,
        fee=fee, dealing=dealing, turnover_pct=turnover, residual=residual,
        holding_moves=sorted(moves, key=lambda row: -abs(row["points"])),
        basis="Opening weights recovered from the following session's carried holdings and "
              "dividend-adjusted ETF closes. Matched to the published NAV within its rounding precision.",
        price_source="Yahoo Finance dividend-adjusted daily closes",
        method_source="https://github.com/ankitv25/Asset-Allocation/blob/main/src/fund_nav.py",
    )
