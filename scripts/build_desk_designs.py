"""Render the reviewed design edition from its authored desk-by-desk specification."""
import calendar
import html
import json
import re
import statistics
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "editions/2026-11/20261107T172033-0500.json"
edition = json.loads(FIXTURE.read_text())
markets = {row["id"]: row for row in edition["markets"]}
esc = html.escape


def paired(left, right):
    def returns(row):
        return {(a, b): y / x - 1 for (a, x), (b, y) in zip(row["history"], row["history"][1:]) if x > 0}
    x, y = returns(markets[left]), returns(markets[right])
    keys = sorted(x.keys() & y.keys())
    return [(b, x[a,b], y[a,b]) for a,b in keys]


def line_chart(title, series, unit, ordinal=False):
    """Draw dated or categorical series against one labelled y scale."""
    colors = ["#007c71","#995126","#4970b7"]
    allpoints = [pt for _,points in series for pt in points]
    lo,hi=min(v for _,v in allpoints),max(v for _,v in allpoints)
    pad=max(.01,(hi-lo)*.12)
    labels = list(dict.fromkeys(k for _,points in series for k,v in points))
    if not ordinal:
        labels.sort()
    def x(k):
        if ordinal:return 71+648*labels.index(k)/max(1,len(labels)-1)
        a,b=date.fromisoformat(labels[0]),date.fromisoformat(labels[-1])
        return 71+648*(date.fromisoformat(k)-a).days/max(1,(b-a).days)
    def y(v):return 150-126*(v-lo+pad)/(hi-lo+2*pad)
    svg=[]
    for i in range(4):
        v=lo-pad+(hi-lo+2*pad)*i/3
        svg.append(f'<path d="M69 {y(v):.1f}H720" stroke="#d7e3e0"/><text x="61" y="{y(v)+4:.1f}" text-anchor="end">{v:.2f}{unit}</text>')
    for i,(name,points) in enumerate(series):
        data=" ".join(f"{x(k):.1f},{y(v):.1f}" for k,v in points)
        svg.append(f'<polyline points="{data}" stroke="{colors[i]}" fill="none" stroke-width="2.5"/>')
    for k in (labels if ordinal else [labels[0],labels[len(labels)//2],labels[-1]]):
        svg.append(f'<text x="{x(k):.1f}" y="174" text-anchor="middle">{esc(k)}</text>')
    legend=" ".join(f'<span style="--series:{colors[i]}">{esc(n)}</span>' for i,(n,_) in enumerate(series))
    return f'<figure><figcaption>{esc(title)}</figcaption><div class="legend">{legend}</div><svg role="img" aria-label="{esc(title)}" viewBox="0 0 760 182">{"".join(svg)}</svg></figure>'


def chart(kind):
    if kind=="dependence":
        series=[]
        for key in ("ief","vnq"):
            r=paired("spx",key)
            points=[]
            for i in range(max(62,len(r)-126),len(r)):
                win=r[i-62:i+1]
                points.append((r[i][0],statistics.correlation([t[1] for t in win],[t[2] for t in win])))
            series.append((markets[key]["symbol"],points))
        return line_chart("S&P 500 · rolling 63-observation price-return correlation",series,"")
    if kind=="rates":
        rs=edition["curve"]["rows"][-2:][::-1]
        tenors=["3M","1Y","2Y","5Y","10Y","20Y","30Y"]
        return line_chart("Treasury yields · selected maturities, equally spaced",[(r["date"],[(k,r["rates"][k]) for k in tenors]) for r in rs],"%",True)
    if kind=="portfolio":
        rows=edition["books"]["saa"]["sleeves"]
        return '<figure><figcaption>SAA · capital and risk shares (negative contributions extend left of zero)</figcaption><div class="legend"><span style="--series:#007c71">Capital</span><span style="--series:#995126">Risk</span></div>'+''.join(
            f'<div class="risk"><b>{esc(r["sleeve"])}</b><span class="risk-axis"><i style="left:10%;width:{r["capital"]*1.5}%"></i><i style="left:{10+min(0,r["risk"])*1.5}%;width:{abs(r["risk"])*1.5}%;background:#995126"></i></span><small>{r["capital"]:.1f}% / {r["risk"]:+.1f}%</small></div>'
            for r in rows)+'</figure>'
    symbols={"equity":("iwf","iwd"),"tape":("spx","ndx","nikkei"),"credit":("lqd","hyg","bkln"),"fx":("dxy","usdjpy"),"commodities":("wti","copper"),"alternatives":("vnq","dbmf","gld")}
    if kind not in symbols:raise ValueError(kind)
    rows=[markets[k] for k in symbols[kind]]
    aligned=sorted(set.intersection(*(set(d for d,v in r["history"]) for r in rows)))
    # Use common endpoints and disclose starting date, including for non-US venues.
    end=date.fromisoformat(aligned[-1]);m=end.year*12+end.month-7;yr,m0=divmod(m,12)
    target=date(yr,m0+1,min(end.day,calendar.monthrange(yr,m0+1)[1])).isoformat()
    base=max(d for d in aligned if d<=target)
    aligned=[d for d in aligned if d>=base]
    series=[]
    for r in rows:
        h=dict(r["history"]);series.append((r["symbol"],[(d,100*(h[d]/h[base]-1)) for d in aligned]))
    return line_chart("Cumulative price change · common dates from "+base,series,"%")


def table(block):
    rows=[[cell.strip() for cell in line.strip("|").split("|")] for line in block.splitlines()]
    assert set(rows[1][0]) <= {"-",":"}
    def cells(row,tag):return "".join(f"<{tag}>{esc(val)}</{tag}>" for val in row)
    body=[]
    for row in rows[2:]:
        assert len(row)==len(rows[0]),row
        body.append("<tr>"+cells(row,"td")+"</tr>")
    return '<div class="scroll"><table><thead><tr>'+cells(rows[0],"th")+'</tr></thead><tbody>'+''.join(body)+'</tbody></table></div>'


def render():
    source=(ROOT/"docs/DESK_DESIGNS.md").read_text().split("\n## ")[1:]
    pages=[]; links=[]
    for index,part in enumerate(source):
        name,body=part.split("\n",1);slug=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
        links.append(f'<a href="#{slug}">{esc(name)}</a>')
        blocks=[]
        for group in body.strip().split("### ")[1:]:
            heading,rest=group.split("\n",1)
            if heading=="Design contract":
                blocks.append('<details class="contract"><summary>Default view, interactions and missing-data behavior</summary><p>'+esc(rest.strip())+'</p></details>');continue
            content=[]
            for b in rest.strip().split("\n\n"):
                if b.startswith("|"):content.append(table(b))
                elif b.startswith("@chart "):content.append(chart(b.split()[1]))
                else:content.append("<p>"+esc(b)+"</p>")
            blocks.append('<section class="'+('exhibit' if '<table>' in ''.join(content) else 'analysis')+'"><h2>'+esc(heading)+'</h2>'+''.join(content)+'</section>')
        pages.append(f'<article id="{slug}"><div class="topline">DESK DESIGN EDITION <span>Historical sample · November 2026</span></div><h1>{esc(name)}</h1>'+''.join(blocks)+'</article>')
    style=(ROOT/"scripts/desk_design.css").read_text()
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Desk designs · Market Observatory</title><style>'''+style+'''</style></head><body><header><b>Market Observatory</b><a href="../">Live market edition ↗</a></header><div class="layout"><aside><div class="sideTitle">Market desks</div><nav aria-label="Desk designs">'''+''.join(links)+'''</nav></aside><main>'''+''.join(pages)+'''</main></div><script>
    function display(){const articles=[...document.querySelectorAll("article")];const key=articles.some(a=>a.id===location.hash.slice(1))?location.hash.slice(1):articles[0].id;
    for(const a of articles)a.hidden=a.id!==key;
    for(const a of document.querySelectorAll("nav a")){if(a.hash==="#"+key)a.setAttribute("aria-current","page");else a.removeAttribute("aria-current")}
    window.scrollTo(0,0);}
    display();window.addEventListener("hashchange",display);
    </script></body></html>'''
    return page


if __name__=="__main__":
    destination=Path(sys.argv[1]);destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(render())
