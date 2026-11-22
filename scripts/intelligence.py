"""Deterministic market assessments from an edition's dated observations.

These rules summarize price evidence. They do not estimate event probabilities
or infer an economic cause from a price move. No network calls occur here.
"""
from calendar import monthrange
from datetime import date, datetime, timedelta
import math
from statistics import mean, median
from cadence import expected_close, session_day, HOLIDAYS, CALENDAR_SOURCE

VERSION = "1.1"
SECTORS = "xlk xlc xly xlp xle xlf xlv xli xlb xlre xlu".split()
SIGNALS = (
    ("us_equity", "US equity direction", ["spx", "rut"], .25, "%"),
    ("global_equity", "International equity direction", ["efa", "eem"], .25, "%"),
    ("breadth", "US sector participation", SECTORS, 70, "% advancing"),
    ("participation", "Small-cap and equal-weight participation", ["iwm", "rsp", "spy"], .15, "pp"),
    ("volatility", "Equity volatility", ["vix"], 5.0, "%"),
    ("credit", "High-yield versus short Treasuries", ["hyg", "shy"], .10, "pp"),
)
CONTEXT_IDS = ["dxy", "wti", "copper", "gold"]


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def weekdays_between(start, end):
    """Count Monday–Friday dates after start through end, without a holiday calendar."""
    if start > end:
        return -weekdays_between(end, start)
    return sum((start+timedelta(days=i)).weekday() < 5 for i in range(1, (end-start).days+1))


def expected_session(created):
    """Use the shared NYSE holiday and early-close calendar."""
    stamp = datetime.fromisoformat(created.replace("Z", "+00:00"))
    if stamp.utcoffset() is None:
        raise ValueError("Edition time needs a timezone")
    return date.fromisoformat(expected_close(stamp))


def source_status(observed, expected, *, monthly=False, allow_lag=False):
    if not observed:
        return dict(date=None, age_business_days=None, status="missing", reason="Observation unavailable.")
    try:
        day = date.fromisoformat(observed)
    except (TypeError, ValueError):
        return dict(date=observed, age_business_days=None, status="missing", reason="Observation date is invalid.")
    age = weekdays_between(day, expected)
    if day > expected:
        status, reason = "future", "Observation is later than the latest expected completed US session."
    elif monthly:
        status = "current" if (expected-day).days <= 45 else "stale"
        reason = "Monthly context is excluded from the market score. Vintage is " + day.isoformat() + "."
    elif day == expected:
        status, reason = "current", "Aligned with the latest expected completed US session."
    elif age == 1 and allow_lag:
        status, reason = "lagged", "One weekday behind, within the context publication-lag allowance."
    else:
        status, reason = "stale", str(age) + " weekdays behind the expected session. Scored price signals require that exact session."
    return dict(date=observed, age_business_days=age, status=status, reason=reason)


def series_points(row):
    points = {}
    for item in row.get("history", []):
        if len(item) != 2 or not finite(item[1]) or item[1] <= 0:
            continue
        try:
            day = date.fromisoformat(item[0]).isoformat()
        except (ValueError, TypeError):
            continue
        points[day] = item[1]
    return dict(sorted(points.items()))


def signed(value, suffix="", precision=2):
    return f"{value:+.{precision}f}{suffix}"


def direction(value, threshold):
    """Treat floating-point rounding at an exact threshold symmetrically."""
    if value >= threshold-1e-9:
        return 1
    if value <= -threshold+1e-9:
        return -1
    return 0


def reading(vote):
    return {-1:"risk-off", 0:"neutral", 1:"risk-on"}.get(vote, "unavailable")


def evidence(signal, rows, points, audit, start, end, sessions, historical=False):
    key, label, ids, daily_threshold, unit = signal
    threshold = daily_threshold if key == "breadth" else daily_threshold*math.sqrt(sessions)
    values, reasons, inputs = {}, [], []
    for identifier in ids:
        record, source = rows.get(identifier), audit.get(identifier)
        history = points.get(identifier, {})
        inputs.append(dict(id=identifier, name=record.get("name", identifier) if record else identifier,
                           day=source.get("date") if source else None, source=record.get("source") if record else None))
        if not record:
            reasons.append(identifier.upper() + " is missing")
        elif not historical and source["status"] != "current":
            reasons.append(identifier.upper() + " is " + source["status"])
        elif not start or start not in history or end not in history:
            reasons.append(identifier.upper() + " lacks both matched endpoints")
        else:
            values[identifier] = 100*(history[end]/history[start]-1)
    for item in inputs:
        item["eligible"] = item["id"] in values
    available = len(values) >= 8 if key == "breadth" else len(values) == len(ids)
    result = dict(id=key, label=label, status="excluded", vote=None, reading="unavailable", value=None,
                  unit=unit, threshold=round(threshold, 6), start=start, end=end, detail="",
                  reason="; ".join(reasons), inputs=inputs)
    if not available:
        return result
    if key == "breadth":
        up = sum(value > 0 for value in values.values())
        value = 100*up/len(values)
        vote = 1 if value >= 70 else -1 if value <= 30 else 0
        detail = f"{up} of {len(values)} matched sector ETFs advanced. The signal thresholds are 70% and 30%."
    elif key == "participation":
        gaps = [values["iwm"]-values["spy"], values["rsp"]-values["spy"]]
        value = mean(gaps)
        vote = direction(value, threshold)
        detail = f"IWM minus SPY {signed(gaps[0], ' pp')}, RSP minus SPY {signed(gaps[1], ' pp')}. The reading uses their mean."
    elif key == "credit":
        value = values["hyg"]-values["shy"]
        vote = direction(value, threshold)
        detail = f"HYG {signed(values['hyg'], '%')} versus SHY {signed(values['shy'], '%')}. ETF price-only relative return includes duration and distribution effects."
    elif key == "volatility":
        value = values["vix"]
        vote = -direction(value, threshold)
        detail = f"VIX moved {signed(value, '%')}. Rising implied equity volatility supplies defensive evidence."
    else:
        value = median(values.values())
        vote = direction(value, threshold)
        detail = ", ".join(identifier.upper() + " " + signed(change, "%") for identifier, change in values.items()) + ". The reading uses the median return."
    result.update(status="included", vote=vote, reading=reading(vote), value=round(value, 6), detail=detail,
                  reason="Matched start and end observations." + (" Coverage is partial." if reasons else ""))
    return result


def summarize(evidence_rows):
    included = [row for row in evidence_rows if row["status"] == "included"]
    votes = [row["vote"] for row in included]
    positive, negative = votes.count(1), votes.count(-1)
    coverage = len(included)/len(SIGNALS)
    agreement = max(positive, negative)/len(included) if included else 0
    confidence = round(100*coverage*agreement)
    score = mean(votes) if votes else None
    ids = {row["id"] for row in included}
    enough = len(included) >= 4 and bool(ids & {"us_equity", "global_equity"}) and bool(ids & {"volatility", "credit"})
    if not enough:
        regime = "insufficient evidence"
    elif positive >= math.ceil(2*len(included)/3) and negative <= 1:
        regime = "risk-on"
    elif negative >= math.ceil(2*len(included)/3) and positive <= 1:
        regime = "risk-off"
    else:
        regime = "mixed"
    return dict(regime=regime, score=round(score, 4) if score is not None else None, confidence=confidence,
                coverage=dict(eligible=len(included), total=len(SIGNALS), ratio=round(coverage,4), agreement=round(agreement,4)),
                counts=dict(positive=positive, negative=negative, neutral=votes.count(0)))


def window_assessment(identifier, label, sessions, offset, calendar, rows, points, audit, historical=False, expected=None):
    end_index = len(calendar)-1-offset
    start_index = end_index-sessions
    start = calendar[start_index] if start_index >= 0 else None
    end = calendar[end_index] if end_index >= 0 else None
    evidence_rows = [evidence(spec, rows, points, audit, start, end, sessions, historical) for spec in SIGNALS]
    invalid_reference = None
    if start and end:
        start_day,end_day = date.fromisoformat(start),date.fromisoformat(end)
        expected_intervals = sum(session_day(start_day+timedelta(days=i)) for i in range(1,(end_day-start_day).days+1))
        if expected_intervals != sessions:
            invalid_reference = "Reference history has gaps in the selected trading-session window."
    if not historical and expected and end != expected:
        invalid_reference = "The reference endpoint is older than the expected completed session."
    if invalid_reference:
        for item in evidence_rows:
            item.update(status="excluded",vote=None,reading="unavailable",reason=invalid_reference)
    assessment = summarize(evidence_rows)
    counts, coverage = assessment["counts"], assessment["coverage"]
    summary = (f"{counts['positive']} of {coverage['eligible']} eligible domains support risk-taking and "
               f"{counts['negative']} support a defensive reading. {counts['neutral']} are inside the neutral bands.")
    if assessment["regime"] == "insufficient evidence":
        summary = f"Only {coverage['eligible']} of six domains are eligible, or a required equity and risk-confirmation pair is incomplete."
    bullish = [row["label"] for row in evidence_rows if row["vote"] == 1]
    bearish = [row["label"] for row in evidence_rows if row["vote"] == -1]
    conflicts = []
    if bullish and bearish:
        conflicts.append("Risk-taking evidence comes from " + ", ".join(bullish) + ". Defensive evidence comes from " + ", ".join(bearish) + ".")
    return dict(id=identifier, label=label, sessions=sessions, start=start, end=end,
                evidence=evidence_rows, summary=executive_summary(evidence_rows,assessment,summary), conflicts=conflicts, **assessment)


def executive_summary(evidence_rows, assessment, counts_text):
    if assessment["regime"] == "insufficient evidence":
        return counts_text
    eligible = {r["id"]:r for r in evidence_rows if r["status"]=="included"}
    pieces = []
    us, global_equity = eligible.get("us_equity"),eligible.get("global_equity")
    if us:
        text = "The US equity benchmark median returned "+signed(us["value"],"%")
        if global_equity:
            text += ", against "+signed(global_equity["value"],"%")+" for developed ex-US and emerging-market ETFs"
        pieces.append(text+".")
    elif global_equity:
        pieces.append("Developed ex-US and emerging-market ETFs returned a median "+signed(global_equity["value"],"%")+".")
    volatility,credit = eligible.get("volatility"),eligible.get("credit")
    if volatility:
        pieces.append("VIX changed "+signed(volatility["value"],"%")+".")
    if credit:
        pieces.append("High-yield ETF prices "+("outpaced" if credit["value"]>0 else "trailed" if credit["value"]<0 else "matched")+
                      " short Treasuries"+(" by "+f"{abs(credit['value']):.2f}"+" pp." if credit["value"] else "."))
    dissent = [r["label"].lower() for r in eligible.values()
               if r["vote"] and assessment["score"] is not None and r["vote"]*assessment["score"]<0]
    if dissent:
        pieces.append("The counterweight is "+", ".join(dissent)+".")
    return " ".join(pieces) if pieces else counts_text


def context_rows(edition, rows, points, audit, expected):
    result = []
    curve_rows = edition.get("curve", {}).get("rows", [])
    curve_status = source_status(curve_rows[-1]["date"] if curve_rows else None, expected, allow_lag=True)
    curve = dict(id="rates", label="Treasury curve", status=curve_status["status"], date=curve_status["date"],
                 title="Treasury observations unavailable", detail="", metrics=[], reason=curve_status["reason"])
    if len(curve_rows) >= 2:
        latest, prior = curve_rows[-1], curve_rows[-2]
        needed = ("2Y", "10Y", "30Y")
        if all(finite(r.get("rates",{}).get(k)) for r in (latest,prior) for k in needed):
            two, ten = latest["rates"]["2Y"], latest["rates"]["10Y"]
            change = {k:100*(latest["rates"][k]-prior["rates"][k]) for k in needed}
            slope = 100*(ten-two)
            slope_change = change["10Y"]-change["2Y"]
            curve.update(title="2s10s " + ("steepens" if slope_change > .005 else "flattens" if slope_change < -.005 else "holds its slope"),
                         detail=f"From {prior['date']} to {latest['date']}, the 2-year yield moved {signed(change['2Y'], ' bp')} and the 10-year {signed(change['10Y'], ' bp')}. Yield direction can reflect several forces and receives no directional vote.",
                         metrics=[dict(label="2-year yield", value=two, unit="%"),
                                  dict(label="10-year yield", value=ten, unit="%"),
                                  dict(label="2s10s", value=round(slope,4), unit="bp"),
                                  dict(label="Slope change", value=round(slope_change,4), unit="bp")])
    result.append(curve)
    dollar = points.get("dxy", {})
    dollar_status = audit.get("dxy", source_status(None, expected))
    fx = dict(id="dollar", label="Dollar", status=dollar_status["status"], date=dollar_status["date"],
              title="Dollar observation unavailable", detail="", metrics=[], reason=dollar_status["reason"])
    if len(dollar) >= 2:
        dates = list(dollar)
        change = 100*(dollar[dates[-1]]/dollar[dates[-2]]-1)
        fx.update(title="Dollar " + ("rises" if change > .005 else "falls" if change < -.005 else "is little changed"),
                  detail=f"DXY moved {signed(change, '%')} from {dates[-2]} to {dates[-1]}. A stronger dollar can accompany yield advantage or defensive demand, so it receives no directional vote.",
                  metrics=[dict(label="Dollar index", value=dollar[dates[-1]], unit="pts"), dict(label="Session change",value=round(change,6),unit="%")])
    result.append(fx)
    commodity_ids = ("wti","copper","gold")
    dates = sorted(set.intersection(*(set(points.get(k,{})) for k in commodity_ids)))
    commodity = dict(id="commodities",label="Commodity divergence",status="missing",date=None,title="Matched commodity comparison unavailable",detail="",metrics=[],reason="Oil, copper and gold need two common endpoints.")
    if len(dates) >= 2:
        start,end = dates[-2:]
        changes = {k:100*(points[k][end]/points[k][start]-1) for k in commodity_ids}
        status = source_status(end,expected,allow_lag=True)
        opposed = changes["wti"]*changes["copper"] < 0
        commodity.update(status=status["status"],date=end,title="Oil and copper diverge" if opposed else "Oil and copper move in the same direction" if changes["wti"]*changes["copper"] > 0 else "Commodity direction is mixed",
                         detail=f"From {start} to {end}, WTI {signed(changes['wti'], '%')}, copper {signed(changes['copper'], '%')}, gold {signed(changes['gold'], '%')}. The named delivery contracts retain their own pricing basis. Divergence identifies a cross-check for the next session.",
                         metrics=[dict(id=k,label=rows[k]["name"],value=round(changes[k],6),unit="%") for k in commodity_ids],reason=status["reason"])
    result.append(commodity)
    macro = edition.get("macro",{})
    macro_status = source_status(macro.get("date"),expected,monthly=True)
    result.append(dict(id="macro",label="Monthly macro context",status=macro_status["status"],date=macro.get("date"),
                       title=macro.get("regime","Macro vintage unavailable"),
                       detail="The confirmed monthly MRS vintage supplies structural context. Its own observation month governs its relevance to the market edition.",
                       metrics=[dict(label="Composite",value=macro["score"],unit="z")] if finite(macro.get("score")) else [],
                       reason=macro_status["reason"]))
    credit_source = edition.get("credit_context", {})
    credit_rows = credit_source.get("rows", [])
    credit = dict(id="credit_spreads",label="Monthly corporate credit",status="missing",date=None,
                  title="Monthly credit observation unavailable",detail="",metrics=[],
                  reason="Monthly staff-research credit measures are unavailable.")
    if credit_rows:
        latest = credit_rows[-1]
        period = date.fromisoformat(latest["date"])
        period_end = period.replace(day=monthrange(period.year,period.month)[1]).isoformat()
        status = source_status(period_end,expected,monthly=True)
        credit.update(status=status["status"],date=period_end,title=period.strftime("%B %Y")+" corporate credit",
                      reason="Monthly context is eligible within 45 calendar days after its observation month ends. "+status["reason"],
                      detail="The Gilchrist–Zakrajšek corporate spread and excess bond premium are monthly Federal Reserve staff-research measures. They supply dated credit context and carry no daily vote.",
                      source=credit_source.get("source"),url=credit_source.get("url"))
        for field,label in (("gz_spread","GZ corporate spread"),("ebp","Excess bond premium")):
            if finite(latest.get(field)):
                credit["metrics"].append(dict(label=label,value=round(100*latest[field],4),unit="bp"))
                if len(credit_rows)>1 and finite(credit_rows[-2].get(field)):
                    before = date.fromisoformat(credit_rows[-2]["date"])
                    consecutive = period.year*12+period.month-(before.year*12+before.month)==1
                    if consecutive:
                        credit["metrics"].append(dict(label=label+" month-on-month",value=round(100*(latest[field]-credit_rows[-2][field]),4),unit="bp"))
    result.append(credit)
    return result


def portfolio_considerations(windows, contexts, points, expected):
    daily,weekly,monthly = windows
    evidence = {row["id"]:row for row in daily["evidence"] if row["status"]=="included"}
    context = {row["id"]:row for row in contexts}
    breadth = evidence.get("breadth")
    equity_text = (f"{breadth['value']:.0f}% of matched sector ETFs advanced. " if breadth else "Current sector participation lacks eligible observations. ")
    equity_text += f"The daily, weekly and monthly readings are {daily['regime']}, {weekly['regime']} and {monthly['regime']}. "
    equity_text += "Review concentrated equity exposures and their limits alongside the direction of participation."
    rates = context["rates"]
    rates_current = rates["status"] in ("current","lagged") and bool(rates["metrics"])
    fixed_income_text = (rates["detail"]+" " if rates_current else "Current curve evidence is incomplete or outside its freshness window. ")
    credit = evidence.get("credit")
    if credit:
        fixed_income_text += f"HYG minus SHY is {signed(credit['value'],' pp')} over the scored session. "
    fixed_income_text += "Review portfolio duration, convexity and credit risk budgets separately because rate sensitivity affects the ETF comparison."
    commodities = context["commodities"]
    commodity_current = commodities["status"] in ("current","lagged") and bool(commodities["metrics"])
    commodity_text = (commodities["detail"]+" " if commodity_current else "A fresh matched oil, copper and gold comparison is unavailable. ")
    commodity_text += "Check energy, industrial-metal and precious-metal exposures separately within the commodity sleeve."
    alternative_moves = []
    for key,label in (("dbmf","Managed futures ETF"),("vnq","Listed property ETF"),("btc","Bitcoin")):
        history = points.get(key,{})
        start,end = daily["start"],daily["end"]
        if start in history and end in history and end == expected.isoformat():
            alternative_moves.append(label+" "+signed(100*(history[end]/history[start]-1),"%"))
    alternative_text = (", ".join(alternative_moves)+f" from {daily['start']} to {daily['end']}. " if alternative_moves else "Matched current alternative-asset observations are incomplete. ")
    alternative_text += "Evaluate diversifiers using their longer correlation and drawdown history when reviewing strategic allocations."
    cash_text = (f"The current price assessment is {daily['regime']}. " if daily["regime"]!="insufficient evidence" else "The current price assessment has insufficient evidence. ")
    cash_text += "Review the liquidity reserve against known cash needs, collateral requirements and the portfolio's published mandate. The price score supplies no funding-market measurement."
    considerations = [
        dict(horizon="Tactical",title="Equities",text=equity_text),
        dict(horizon="Tactical",title="Fixed income",text=fixed_income_text),
        dict(horizon="Tactical",title="Commodities",text=commodity_text),
        dict(horizon="Strategic",title="Alternatives",text=alternative_text),
        dict(horizon="Strategic",title="Cash and liquidity",text=cash_text),
    ]
    equity_rows = [evidence[k] for k in ("us_equity","global_equity") if k in evidence]
    growth_text = (", ".join(r["label"]+" "+signed(r["value"],"%") for r in equity_rows)+". " if equity_rows else "Current equity-direction evidence is incomplete. ")
    if commodity_current:
        copper = next(r for r in commodities["metrics"] if r["id"]=="copper")
        growth_text += "Copper changed "+signed(copper["value"],"%")+" at its "+commodities["date"]+" endpoint. "
    growth_text += "These price observations can be consistent with changing growth expectations; demand and earnings evidence is still required."
    inflation_text = (rates["detail"]+" " if rates_current else "A fresh nominal curve is unavailable. ")
    inflation_text += (commodities["title"]+" at "+commodities["date"]+". " if commodity_current else "")
    inflation_text += "Nominal yields and energy prices alone cannot distinguish inflation compensation, real yields and term premium."
    volatility = evidence.get("volatility")
    liquidity_text = ("VIX "+signed(volatility["value"],"%")+". " if volatility else "Current volatility evidence is incomplete. ")
    liquidity_text += ("HYG minus SHY "+signed(credit["value"]," pp")+". " if credit else "")
    liquidity_text += "Funding rates, repo conditions and market-depth measurements are absent from this edition."
    drivers = [
        dict(title="Growth expectations",status="Hypothesis awaiting confirmation",evidence=growth_text,
             confirmation="Check new activity releases, earnings revisions and sustained equity breadth over subsequent closes."),
        dict(title="Inflation and rate repricing",status="Hypothesis awaiting confirmation",evidence=inflation_text,
             confirmation="Check dated inflation releases, real yields and breakevens before attributing the nominal curve move to inflation."),
        dict(title="Liquidity stress",status="Funding evidence unavailable",evidence=liquidity_text,
             confirmation="Check repo and secured-funding spreads, bid–ask conditions and credit-spread observations before concluding that liquidity is impaired."),
    ]
    return considerations,drivers


def build_intelligence(edition):
    expected = expected_session(edition["created"])
    rows = {row["id"]:row for row in edition.get("markets",[])}
    points = {key:series_points(row) for key,row in rows.items()}
    identifiers = list(dict.fromkeys([key for signal in SIGNALS for key in signal[2]]+CONTEXT_IDS))
    audit = {}
    for key in identifiers:
        record = rows.get(key,{})
        observed = next(reversed(points.get(key,{})),None)
        audit[key] = dict(id=key,name=record.get("name",key.upper()),source=record.get("source"),
                          **source_status(observed,expected,allow_lag=key in CONTEXT_IDS))
    reference_ids = [key for key in ("spx","acwi","rut") if len(points.get(key,{})) >= 2]
    reference = next((key for key in reference_ids if list(points[key])[-1] == expected.isoformat()),next(iter(reference_ids),None))
    calendar = [day for day in points.get(reference, {}) if day <= expected.isoformat() and session_day(date.fromisoformat(day))]
    windows = []
    for identifier,label,sessions in (("daily","Daily",1),("weekly","Weekly",5),("monthly","Monthly",21)):
        current = window_assessment(identifier,label,sessions,0,calendar,rows,points,audit,expected=expected.isoformat())
        previous = window_assessment(identifier,label,sessions,sessions,calendar,rows,points,audit,historical=True)
        current["previous"] = {key:previous[key] for key in ("start","end","regime","score","confidence")}
        before_ids = {(r["id"],tuple(sorted(i["id"] for i in r["inputs"] if i["eligible"]))) for r in previous["evidence"] if r["status"]=="included"}
        current_ids = {(r["id"],tuple(sorted(i["id"] for i in r["inputs"] if i["eligible"]))) for r in current["evidence"] if r["status"]=="included"}
        if "insufficient evidence" in (previous["regime"],current["regime"]):
            transition = "Comparison unavailable because one window has insufficient evidence."
        elif before_ids != current_ids:
            transition = previous["regime"]+" → "+current["regime"]+". Coverage changed, so the score change has limited comparability."
        else:
            change = current["score"]-previous["score"]
            direction_text = "Improving" if change > .0001 else "Deteriorating" if change < -.0001 else "Stable"
            transition = previous["regime"]+" → "+current["regime"]+". "+direction_text+" directional evidence versus the preceding equal-length window."
        current["transition"] = transition
        windows.append(current)
    daily,weekly,monthly = windows
    used = {source["id"] for item in daily["evidence"] if item["status"]=="included" for source in item["inputs"] if source["eligible"]}
    sources = [dict(value,used_in_score=key in used) for key,value in audit.items()]
    contexts = context_rows(edition,rows,points,audit,expected)
    for identifier,label in (("rates","Treasury curve"),("macro","Monthly macro context"),("credit_spreads","Monthly corporate credit")):
        context = next(row for row in contexts if row["id"]==identifier)
        status = source_status(context["date"],expected,monthly=identifier in ("macro","credit_spreads"),allow_lag=identifier=="rates")
        sources.append(dict(id=identifier,name=label,used_in_score=False,**status))
    gaps = ["Daily credit spreads, funding-market measures and dealer liquidity are absent. Credit confirmation uses HYG/SHY price returns only."]
    excluded = [item["label"] for item in daily["evidence"] if item["status"]=="excluded"]
    if excluded:
        gaps.append("Daily voting coverage excludes " + ", ".join(excluded) + ".")
    stale_context = [row["label"] for row in contexts if row["status"] in ("stale","missing","future")]
    if stale_context:
        gaps.append("Older or unavailable context includes " + ", ".join(stale_context) + ".")
    if expected.year not in HOLIDAYS:
        gaps.append("The exchange calendar is unverified for this year. The date check falls back to weekdays.")
    considerations, drivers = portfolio_considerations(windows,contexts,points,expected)
    watchlist = [
        dict(label="Sector participation",condition="At least 70% of eligible sectors rise, or at most 30% rise, over matching endpoints.",why="Tests whether benchmark direction has broad participation."),
        dict(label="Volatility confirmation",condition="A daily VIX change of at least 5% in either direction.",why="Checks whether the equity move is accompanied by a change in implied volatility."),
        dict(label="Credit confirmation",condition="HYG minus SHY crosses +0.10 or −0.10 percentage points over the same session.",why="Tracks relative ETF price behavior while preserving the separate need for spread and funding data."),
        dict(label="Rates and commodity disagreement",condition="Recheck the 2s10s slope and whether oil and copper continue moving in opposite directions.",why="Helps distinguish persistent cross-market disagreement from a single observation."),
    ]
    methodology = dict(
        title="Transparent cross-asset price rules",
        calendar_source=CALENDAR_SOURCE, calendar_verified=expected.year in HOLIDAYS,
        rules=[
            "Six equally weighted domains vote +1, 0 or −1. US and international equity use median price returns. Sector breadth needs at least eight of eleven ETFs.",
            "Risk-on requires at least two thirds of eligible domains voting +1 and at most one opposing vote. Risk-off uses the symmetric rule. Other sufficient combinations are mixed.",
            "At least four of six domains, an equity-direction domain and a VIX or credit domain are required. Otherwise the reading is insufficient evidence.",
            "Daily, weekly and monthly mean one, five and 21 reference-market observation intervals. Every input to a signal uses exactly the same start and end dates.",
            "The expected session uses the shared NYSE 2026–2028 holiday and early-close calendar, with a ten-minute completion buffer. Scored US-listed instruments must match that exact session. Context series may lag by one weekday for publication.",
            "Current votes require a fresh source, complete reference-session windows and matched endpoints. Treasury yields, the dollar, commodities and the monthly MRS are explanatory context and carry no vote.",
            "Growth, inflation and liquidity interpretations are conditional hypotheses. Their stated confirmations remain necessary to establish a causal explanation.",
            "The prior comparison uses a window of the same length ending one, five or 21 reference sessions earlier, recalculated from this edition's history. Published assessment history is preserved separately.",
        ],
        thresholds=[dict(signal=spec[1],daily=spec[3],unit=spec[4],scaling="70%/30% breadth bands" if spec[0]=="breadth" else "Daily band × square root of session count") for spec in SIGNALS],
        confidence_note="The 0–100 confidence score is a heuristic agreement-and-coverage indicator. It is 100 × eligible domains / 6 × the larger directional vote count / eligible domains. It is not an estimated probability or a calibrated forecast.",
    )
    return dict(version=VERSION,created=edition["created"],asof=daily["end"],expected_session=expected.isoformat(),
                reference=reference,regime=daily["regime"],confidence=daily["confidence"],summary=daily["summary"],
                windows=windows,context=contexts,considerations=considerations,drivers=drivers,watchlist=watchlist,
                sources=sources,methodology=methodology,gaps=gaps)
