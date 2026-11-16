"""Project the Asset Allocation publisher's forward NAV and dated construction analytics."""
from calendar import monthrange
from datetime import date, datetime
import json
import math
import re
from zoneinfo import ZoneInfo


REPOSITORY = "ankitv25/Asset-Allocation"
# The source rounds closing NAV to four decimals and turnover percentage to two.
NAV_ROUNDING = 0.000101


def parse_nav(raw):
    match = re.fullmatch(r"\s*window\.LIVE_NAV\s*=\s*([\s\S]+?)\s*;?\s*", raw)
    if not match:
        raise ValueError("Unexpected live NAV envelope")
    return json.loads(match[1])


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("Non-numeric portfolio figure")
    return value


def reconcile(actual, expected, tolerance, label):
    if abs(number(actual) - number(expected)) > tolerance:
        raise ValueError(f"Unreconciled {label}: {actual} vs {expected}")


def period_returns(source, name, nav, dates, opening):
    """Check publisher returns against the rounded NAV series, never partial-fill a horizon."""
    levels = dict(zip(dates, nav))
    end = date.fromisoformat(dates[-1])
    metrics = {"1D": (nav[-1] / nav[-2] - 1) * 100}
    for months in (1, 3, 6, 12):
        key = f"{months}M"
        year, m = divmod(end.year * 12 + end.month - 1 - months, 12)
        cutoff = date(year, m + 1, min(end.day, monthrange(year, m + 1)[1])).isoformat()
        anchor = next((d for d in reversed(dates) if d <= cutoff), None)
        published = source["periods"][name][key]
        if anchor is None:
            if published is not None:
                raise ValueError("Return predates portfolio inception")
            metrics[key] = None
        else:
            calculated = nav[-1] / levels[anchor] - 1
            reconcile(published, calculated, NAV_ROUNDING / min(nav[-1], levels[anchor]) * 2, key)
            metrics[key] = 100 * published
    inception = nav[-1] / opening - 1
    reconcile(source["periods"][name]["SI"], inception, NAV_ROUNDING / opening, name + " inception")
    metrics["SI"] = 100 * source["periods"][name]["SI"]
    return metrics


def holding_returns(source, history):
    """Use the adjusted prices on the source's two exact valuation dates."""
    start, end = source["dates"][-2:]
    returns = {}
    for ticker, prices in history.items():
        first, last = prices.get(start), prices.get(end)
        if isinstance(first, (int, float)) and isinstance(last, (int, float)) and first > 0 and last > 0:
            returns[ticker] = last/first-1
    return returns


def session_attribution(nav, dates, weights, returns, trades, facts):
    start, end = dates[-2:]
    previous, last = nav[-2:]
    turnover = sum(number(t["turnover"]) for t in trades if t["date"] == end)
    fee = -previous * number(facts["fee_bps"]) / 10000 / 252
    dealing = -previous * number(facts["dealing_bps"]) / 10000 * turnover / 100
    net = last - previous
    gross = net - fee - dealing
    result = dict(start=start, end=end, net=net, gross=gross, fee=fee, dealing=dealing,
                  turnover_pct=turnover, holding_moves=[], residual=None,
                  basis="Gross implied from the published NAV change and modeled fee and dealing charges.")
    if weights and weights.keys() <= returns.keys():
        moves = [dict(ticker=t, points=previous * number(weight) * number(returns[t]))
                 for t, weight in weights.items()]
        discrepancy = gross - sum(row["points"] for row in moves)
        # Fund history is rounded to 4dp, trading volume to 0.01% of NAV.
        tolerance = NAV_ROUNDING + previous * facts["dealing_bps"] / 10000 * 0.00005
        if abs(discrepancy) <= tolerance:
            result.update(holding_moves=sorted(moves, key=lambda row: -abs(row["points"])),
                          residual=discrepancy,
                          basis="Opening-session holdings × dividend-adjusted ETF close returns. Residual includes source rounding.")
    return result


def risk_projection(book):
    risk = book["risk"]
    stress = book.get("stress_forward") or {}
    div = book.get("diversification") or {}
    result = {k: risk.get(k) for k in ("dd_limit", "dd_budget", "cdar_cap", "equity_alert", "equity_factor_share")}
    result.update({k: div.get(k) for k in ("diversification_ratio", "effective_bets", "avg_pairwise_corr")})
    result.update(limit_kind=risk.get("limit_kind"),
                  scenario_basis=(stress.get("basis") or {}).get("scenarios"),
                  factors=risk.get("factors", []),
                  scenarios=[dict(name=r["name"], portfolio_pct=number(r["daa"]), policy_pct=number(r["saa"]))
                             for r in stress.get("scenarios", [])],
                  scenario_reference=(stress.get("labels") or {}).get("base"),
                  constraints=book["construction"].get("constraints", []))
    return result


def project_books(source, live, returns, revision, published_at, history=None):
    dates = [date.fromisoformat(d).isoformat() for d in live["dates"]]
    published = datetime.fromisoformat(published_at.replace("Z","+00:00"))
    if published.utcoffset() is None:
        raise ValueError("Missing NAV publication timezone")
    publication_day = published.astimezone(ZoneInfo("America/New_York")).date().isoformat()
    opening = number(live["nav0"])
    if (len(dates) < 2 or dates != sorted(set(dates)) or dates[0] != live["inception"] or
            dates[-1] != live["asof"] or dates[-1] > publication_day or dates[-1] > datetime.now(ZoneInfo("America/New_York")).date().isoformat() or opening <= 0):
        raise ValueError("Inconsistent dates or opening NAV")
    books = {}
    for key in source["order"]:
        book = source["books"][key]
        portfolio = source["portfolios"][key]
        name = portfolio["name"]
        facts = live["facts"][name]
        benchmark = live["ref_of"][name]
        nav = live["series"][name]
        ref = live["ref_series"].get(benchmark, live["series"].get(benchmark))
        book_date = date.fromisoformat(book["asof"]).isoformat()
        if (facts["reference"] != benchmark or book["portfolio"]["key"] != key or
                book["portfolio"]["name"] != name or book_date > datetime.now(ZoneInfo("America/New_York")).date().isoformat() or
                not ref or len(nav) != len(dates) or len(ref) != len(dates) or
                any(number(v) <= 0 for v in nav + ref)):
            raise ValueError(f"Invalid NAV/benchmark alignment for {name}")
        if book_date == dates[-1]:
            reconcile(book["portfolio"]["nav"], nav[-1], .0051, name + " report NAV")
        daily = live["day"][name]
        reconcile(daily["pts"], nav[-1]-nav[-2], NAV_ROUNDING, name + " daily move")
        reconcile(daily["dd"], nav[-1]/max(nav)-1, NAV_ROUNDING/min(nav), name + " drawdown")
        if "chg" in daily:
            reconcile(daily["chg"], nav[-1]/nav[-2]-1, NAV_ROUNDING/nav[-2], name + " daily return")
        bridge = live["bridge"][name]
        total = number(bridge["total"])
        vehicles = {k: number(v) for k, v in bridge["vehicles"].items()}
        expenses = number(bridge["fee"])+number(bridge["dealing"])
        reconcile(sum(vehicles.values())+expenses, total, 1e-6, name + " holdings")
        reconcile(total, nav[-1]-opening, NAV_ROUNDING, name + " NAV since inception")
        weights = live["holdings"][name]
        if any(number(w) <= 0 for w in weights.values()) or not .99 <= sum(weights.values()) <= 1.000001:
            raise ValueError("Invalid live holding weights")
        # The publisher excludes positions below 0.05% from its holdings payload.
        holdings = sorted((dict(ticker=t, sleeve=live["labels"].get(live["ticker_sleeve"].get(t), t),
                                weight_pct=w*100) for t,w in weights.items()), key=lambda h: -h["weight_pct"])
        risk = book["risk"]
        projected = dict(
            date=dates[-1], published_at=published_at, inception=dates[0], opening=opening, benchmark=benchmark,
            dates=dates, nav=nav, benchmark_nav=ref, returns=period_returns(live, name, nav, dates, opening),
            benchmark_returns=period_returns(live, benchmark, ref, dates, opening),
            drawdown_pct=100*(nav[-1]/max(opening,max(nav))-1), fee_bps=facts["fee_bps"], dealing_bps=facts["dealing_bps"],
            pricing=facts["pricing"], holdings=holdings, currency=facts["currency"],
            benchmark_basis="SPY dividend-adjusted close" if benchmark=="S&P 500" else
                "Daily-rebalanced ACWI and AGG ETF total-return blend" if benchmark.startswith("ACWI ") else benchmark,
            source=f"https://github.com/{REPOSITORY}/blob/{revision}/data/live_nav.js",
            bridge=dict(vehicles=vehicles, fee=bridge["fee"], dealing=bridge["dealing"], total=total),
            session=session_attribution(nav, dates, weights, returns, live["trades"][name], facts))
        if history:
            from daily_bridge import prior_session_attribution
            completed = prior_session_attribution(live, name, history)
            if completed:
                projected["completed_session"] = completed
        factor = live.get("factor") or {}
        model = (factor.get("funds") or {}).get(name)
        if model and factor["asof"] == dates[-1] and factor["inception"] == dates[0]:
            factors = [dict(name=r["name"], exposure=number(r["exposure"]), points=number(r["contrib"])) for r in model["factors"]]
            net = sum(r["points"] for r in factors) + sum(number(model[k]) for k in ("costs", "cash", "residual"))
            reconcile(net, total, 1e-6, name + " factor attribution")
            reconcile(model["total"], total, 1e-6, name + " factor total")
            projected["factor_attribution"] = {k: model[k] for k in ("cash","residual","costs")}
            projected["factor_attribution"].update(rows=factors, window=factor["window"])
        books[key] = dict(name=name, role=portfolio["role"], date=book_date, growth=book["positioning"].get("growth_weight"),
                          stance=book["positioning"].get("stance"), forecast=risk.get("forecast_vol"),
                          budget=risk.get("vol_budget"), sleeves=risk.get("risk_contributions", []),
                          blocks=book["construction"].get("blocks", []), thesis=book["portfolio"].get("thesis"),
                          url="https://ankitv25.github.io/Asset-Allocation/?p="+key,
                          risk_model=risk_projection(book), live=projected)
    return books
