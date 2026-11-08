"""Build a reproducible market edition for the repository and its offline reader."""
import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from context_data import collect_curve, collect_macro, collect_books
from graphics import render_graphics
from markets import collect, INSTRUMENTS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dashboard/latest.json"
ET = ZoneInfo("America/New_York")
SECTORS = {"XLB", "XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLK", "XLRE", "XLU"}
GROUPS = ["Indices", "Sectors", "Styles", "Global", "Futures", "FX", "Credit", "Alternatives"]


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + "\n")


def stats(row):
    history = row["history"]
    (previous_day, previous), (day, last) = history[-2:]
    anchor = date.fromisoformat(day)
    # Use a calendar six-month anchor with an eligible observation on or before it.
    import calendar
    month = (anchor.month - 7) % 12 + 1
    year = anchor.year - (anchor.month <= 6)
    target = date(year, month, min(anchor.day, calendar.monthrange(year, month)[1])).isoformat()
    base = next(((d, v) for d, v in reversed(history) if d <= target), None)
    return dict(day=day, previous_day=previous_day, last=last, change=last-previous,
                pct=(last/previous-1)*100 if previous > 0 and last >= 0 else None,
                six=(last/base[1]-1)*100 if base and base[1] > 0 and last >= 0 else None,
                base=base[0] if base else None)


def pct(value):
    return "—" if value is None else f"{value:+.2f}%"


def market_rows(fetched, previous, now):
    rows = {r["id"]: r for r in previous}
    for row in fetched:
        clean = {}
        for day, value in row["history"]:
            if date.fromisoformat(day) <= now.date() and math.isfinite(value):
                clean[day] = float(value)
        row = dict(row, history=sorted(clean.items()))
        prior = rows.get(row["id"])
        if len(clean) >= 2 and (not prior or row["history"][-1][0] >= prior["history"][-1][0]):
            rows[row["id"]] = row
    return [dict(r, stats=stats(r)) for r in rows.values()]


def readings(edition):
    rows = edition["markets"]
    result = []
    sp = next((r for r in rows if r["symbol"] == "^GSPC"), None)
    if sp:
        s = sp["stats"]
        result.append(("US equities", f"The S&P 500 reached {s['last']:,.2f} on {s['day']}, a move of {s['change']:+,.2f} points ({pct(s['pct'])}) against {s['previous_day']}." +
                       (f" Its six-month price change was {pct(s['six'])} from {s['base']}." if s["six"] is not None else "")))
    sectors = [r for r in rows if r["symbol"] in SECTORS and r["stats"]["pct"] is not None]
    if sectors:
        day = max(r["stats"]["day"] for r in sectors)
        sectors = sorted((r for r in sectors if r["stats"]["day"] == day), key=lambda r:r["stats"]["pct"])
        result.append(("Sector participation", f"{sum(r['stats']['pct'] > 0 for r in sectors)} of {len(sectors)} reporting sector ETFs rose on {day}. {sectors[-1]['name']} led at {pct(sectors[-1]['stats']['pct'])}; {sectors[0]['name']} finished at {pct(sectors[0]['stats']['pct'])}."))
    by_id = {r["id"]: r for r in rows}
    growth, value = by_id.get("iwf"), by_id.get("iwd")
    if growth and value:
        g, v = growth["stats"], value["stats"]
        if g["day"] == v["day"] and g["previous_day"] == v["previous_day"] and None not in (g["pct"], v["pct"]):
            spread = g["pct"] - v["pct"]
            result.append(("Equity style", f"On {g['day']} large-cap growth ({pct(g['pct'])}) finished {abs(spread):.2f} percentage points {'ahead of' if spread >= 0 else 'behind'} large-cap value ({pct(v['pct'])}), measured by IWF and IWD."))
    oil = by_id.get("wti")
    if oil and oil.get("contract"):
        o = oil["stats"]
        result.append(("Energy", f"The {oil['contract']} WTI contract closed at ${o['last']:.2f}/bbl on {o['day']}, {o['change']:+.2f} dollars per barrel against its own {o['previous_day']} close."))
    pairs = [r for r in edition["curve"].get("rows", []) if {"2Y","10Y"} <= r["rates"].keys()]
    if len(pairs) >= 2:
        prior, last = pairs[-2:]
        slope = lambda r: 100*(r["rates"]["10Y"]-r["rates"]["2Y"])
        delta = slope(last)-slope(prior)
        result.append(("US rates", f"On {last['date']} the 2-year par yield was {last['rates']['2Y']:.2f}% and the 10-year was {last['rates']['10Y']:.2f}%. The 2s10s spread stood at {slope(last):+.0f} bp, changing by {delta:+.0f} bp versus {prior['date']}."))
    macro = edition["macro"]
    if macro.get("regime"):
        result.append(("Macro backdrop", f"The latest available MRS observation is {macro['date']}. Its regime is {macro['regime']} with a composite score of {macro['score']}."))
    return result


def research_page(edition):
    sectors = [r for r in edition["markets"] if r["symbol"] in SECTORS]
    by_date = {}
    for row in sectors:
        for day, value in row["history"]:
            by_date.setdefault(day, {})[row["symbol"]] = value
    aligned = sorted(d for d,v in by_date.items() if len(v)==11)
    text = ["# Research notebook", "", f"Edition {edition['created']}. These are mechanically evaluated market questions. A personal investment view belongs in a separately authored note.", "",
            "## Has sector leadership broadened?", ""]
    if len(aligned)>=21:
        d0,d1=aligned[-21],aligned[-1]
        changes={k:by_date[d1][k]/v-1 for k,v in by_date[d0].items() if v>0}
        text += [f"Between {d0} and {d1}, **{sum(v>0 for v in changes.values())} of 11 sector proxies advanced** over 20 common session intervals. Revisit this reading after the next close. Persistent narrowing while the index rises would challenge a broad-participation interpretation.", ""]
    else:
        text += ["Awaiting 21 common observations across all 11 proxies.", ""]
    text += ["## Which sleeves move with the US equity benchmark?", "",
             "Descriptive price-return beta versus the S&P 500 over up to 63 matched daily intervals. Each observation must share both return endpoints. Table requires at least 40 matches. These are benchmark sensitivities. A risk-free series and dividend-adjusted total returns are needed for a Jensen’s alpha estimate.", "",
             "|Instrument|Beta|Correlation|Matched returns|Through|", "|---|---:|---:|---:|---|"]
    def returns(row):
        h=row["history"]
        return {(a[0],b[0]):b[1]/a[1]-1 for a,b in zip(h,h[1:]) if a[1]>0 and (date.fromisoformat(b[0])-date.fromisoformat(a[0])).days <= 5}
    benchmark=next((r for r in edition["markets"] if r["symbol"]=="^GSPC"),None)
    if benchmark:
        index=returns(benchmark)
        for r in sectors:
            own=returns(r)
            overlap=sorted(index.keys() & own.keys())[-63:]
            if len(overlap)<40: continue
            x,y=zip(*[(index[k],own[k]) for k in overlap])
            if min(statistics.variance(x),statistics.variance(y)) == 0: continue
            beta=statistics.covariance(x,y)/statistics.variance(x)
            text.append(f"|{r['name']}|{beta:.2f}|{statistics.correlation(x,y):.2f}|{len(x)}|{overlap[-1][1]}|")
    text += ["", "## Policy evidence", "",
             "Read the latest published regime beside its observation month. After a policy event, compare the decision, the participants’ projections and the change in Treasury yields on the same timeline. A daily yield change alone does not identify the cause.",
             "", "[FOMC decisions and projections](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) · [New York Fed survey](https://www.newyorkfed.org/markets/market-intelligence/survey-of-market-expectations)"]
    return "\n".join(text)+"\n"


def readme(e):
    rows=e["markets"]
    lines=["# Market Observatory", "", "**[Open the live dashboard →](https://ankitv25.github.io/Market-Observatory/)**", "", "![Market Observatory · US market edition](assets/banner.svg)", "",
           "[Full project plan](docs/PROJECT_PLAN.md) · [Research brief](docs/Market-Observatory-Research.pdf) · [Milestones](https://github.com/ankitv25/Market-Observatory/milestones)", "",
           "**[Market tape](#market-tape) · [Sector rotation](#sector-rotation) · [Treasury curve](#treasury-curve) · [Research notebook](dashboard/RESEARCH.md) · [Cadence log](CADENCE.md) · [Work log](WORKLOG.md)**", "",
           f"Edition compiled **{e['created']}** · {len(rows)} market instruments · dated observations below. Prices and changes use each instrument’s own feed and session. Percentages use unrounded prices.", "",
           "## The daily reading",""]
    if e["issues"]:
        lines += ["**Source status.** " + " ".join(e["issues"]), ""]
    for title,body in e["readings"]: lines += [f"**{title}.** {body}", ""]
    lines += ["## Market tape","", "| Instrument | Last | Δ units | Δ % | 6 months | Observation |","|---|---:|---:|---:|---:|---|"]
    for group in dict.fromkeys(GROUPS+[r["group"] for r in rows]):
        items=[r for r in rows if r["group"]==group]
        if not items: continue
        lines.append(f"|**{group}**||||||")
        for r in items:
            s=r["stats"]
            prec=4 if r["group"]=="FX" else 2
            lines.append(f"|[{r['name']}]({r['url']}) · {r['symbol']}|{s['last']:,.{prec}f}|{s['change']:+,.{prec}f}|{pct(s['pct'])}|{pct(s['six'])}|{s['day']}|")
    lines += ["","## Sector rotation","","![Daily US sector proxy returns](assets/sectors.svg)","","## Treasury curve","","![US Treasury par yields](assets/curve.svg)",""]
    cr=e["curve"].get("rows",[])
    if len(cr)>=2:
        a,b=cr[-2:]
        lines += [f"[US Treasury par yields]({e['curve']['url']}) · {b['date']} versus {a['date']}.", "", "| Maturity | Yield | Δ bp |","|---|---:|---:|"]
        for k,v in b['rates'].items():
            change=f"{100*(v-a['rates'][k]):+.0f}" if k in a['rates'] else "—"
            lines.append(f"|{k}|{v:.2f}%|{change}|")
    lines += ["","## Edition record","",f"[Quality and source notes](dashboard/SOURCES.md) · [Archived editions](editions/) · [Refresh runs](https://github.com/ankitv25/Market-Observatory/actions/workflows/refresh.yml) · [Methodology](docs/METHODOLOGY.md)","",
              "For interactive charts, filters and source detail, download [the self-contained HTML reader](dashboard/observatory.html) using GitHub’s **Download raw file** button and open it locally. Each refresh run also provides the reader as an artifact.",""]
    return "\n".join(lines)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--render-only",action="store_true")
    args=parser.parse_args()
    prev=json.loads(DATA.read_text()) if DATA.exists() else {}
    if args.render_only:
        e=prev
    else:
        now=datetime.now(ET)
        issues=[]
        def attempt(label,fn, fallback):
            try: return fn()
            except Exception as exc:
                issues.append(f"{label} unavailable ({type(exc).__name__}).")
                print(f"{label}: {exc}",file=sys.stderr)
                return fallback
        fresh=attempt("Markets",collect,[])
        if not fresh: raise SystemExit("No market observations retrieved; preserving the last published edition")
        rows=market_rows(fresh,prev.get("markets",[]),now)
        c=attempt("Treasury",collect_curve,prev.get("curve",{}))
        m=attempt("Macro",collect_macro,prev.get("macro",{}))
        books=attempt("Portfolio books",collect_books,prev.get("books",{}))
        for key,value in [("curve",c),("macro",m)]:
            if not value and prev.get(key): issues.append(f"Missing {key} response.")
        if c.get("rows") and prev.get("curve",{}).get("rows") and c["rows"][-1]["date"] < prev["curve"]["rows"][-1]["date"]:
            c=prev["curve"]; issues.append("Treasury returned an older dataset; retained the verified curve.")
        if len(rows)<12 or not any(r["id"]=="spx" for r in rows): raise SystemExit("Core market data missing")
        fresh_ids={r["id"] for r in fresh}
        missing = [r["symbol"] for r in INSTRUMENTS if r["id"] not in {x["id"] for x in rows}]
        if missing: issues.append("No usable history for " + ", ".join(missing))
        archived = [r["symbol"] for r in fresh if r["source"] == "Convexity Lab archive"]
        if archived: issues.append("Live feed unavailable; checked archived coverage for " + ", ".join(archived))
        retained=[r["symbol"] for r in rows if r["id"] not in fresh_ids]
        if retained: issues.append("Prior observations retained for "+", ".join(retained))
        stale=[r["symbol"] for r in rows if (now.date()-date.fromisoformat(r["stats"]["day"])).days>4]
        if stale: issues.append("Observations older than four calendar days: "+", ".join(stale))
        e={"created":now.isoformat(timespec="seconds"),"markets":rows,"curve":c,"macro":m,"issues":issues,"books":books}
        e["readings"]=readings(e)
        write_json(DATA,e)
        # Each distinct publication retains its exact inputs and commentary.
        archive=ROOT/"editions"/now.strftime("%Y-%m")/(now.strftime("%Y%m%dT%H%M%S%z")+".json")
        write_json(archive,e)
        assert archive.read_bytes()==DATA.read_bytes()
        run=os.getenv("GITHUB_RUN_ID")
        link=f"[run {run}](https://github.com/ankitv25/Market-Observatory/actions/runs/{run})" if run else "local verification"
        ledger=ROOT/"CADENCE.md"
        header="# Refresh ledger\n\n| Compiled (New York) | Instruments | Latest price observation | Treasury through | Quality notes | Edition | Run |\n|---|---:|---|---|---:|---|---|\n"
        with ledger.open("a") as f:
            if ledger.stat().st_size==0:f.write(header)
            f.write(f"|{e['created']}|{len(rows)}|{max(r['stats']['day'] for r in rows)}|{c.get('rows',[{}])[-1].get('date','—') if c.get('rows') else '—'}|{len(issues)}|[snapshot]({archive.relative_to(ROOT)})|{link}|\n")
    (ROOT/"README.md").write_text(readme(e))
    render_graphics(e,ROOT/"assets")
    (ROOT/"dashboard/RESEARCH.md").write_text(research_page(e))
    notes=["# Sources and observation dates","",f"Compiled {e['created']}.","",*["- "+i for i in e['issues']], "",
           "| Instrument | Source | Basis | Observed | Six-month anchor |", "|---|---|---|---|---|"]
    for r in e["markets"]:
        notes.append(f"|{r['name']}|[{r['source']}]({r['url']})|{r['basis']}|{r['stats']['day']}|{r['stats']['base'] or '—'}|")
    (ROOT/"dashboard/SOURCES.md").write_text("\n".join(notes)+"\n")
    payload=json.dumps(e,ensure_ascii=False).replace("<","\\u003c")
    (ROOT/"dashboard/observatory.html").write_text((ROOT/"scripts/reader.html").read_text().replace("/*STYLE*/", (ROOT/"scripts/monitor.css").read_text()).replace("/*APP*/", (ROOT/"scripts/monitor.js").read_text()).replace("<!--EDITION-->",payload))
    print(f"Edition {e['created']} · {len(e['markets'])} instruments · {hashlib.sha256(DATA.read_bytes()).hexdigest()[:16]}")


if __name__=="__main__":
    main()
