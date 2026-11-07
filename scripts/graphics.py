"""Build self-contained SVG charts for the repository's GitHub dashboard."""

import calendar
import html
import math
from datetime import date
from pathlib import Path


INK = "#152b2b"
PAPER = "#faf8f1"
TEAL = "#007965"
CORAL = "#aa483f"
GOLD = "#f6c47d"
PALE = "#a4bdb3"
MUTED = "#506360"
RULE = "#cdd4ca"
WIDTH = 940

SECTORS = {
    "XLB": "Materials", "XLC": "Communication Services",
    "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
    "XLE": "Energy", "XLF": "Financials", "XLV": "Health Care",
    "XLI": "Industrials", "XLK": "Information Technology",
    "XLRE": "Real Estate", "XLU": "Utilities",
}


def esc(value):
    return html.escape(str(value), quote=True)


def finite(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def day(value):
    return date.fromisoformat(str(value)[:10])


def label_date(value):
    return value.strftime("%b %d, %Y").replace(" 0", " ")


def points(series):
    cleaned = {}
    for raw_day, raw_value in series.get("history", []):
        value = finite(raw_value)
        if value is None:
            continue
        try:
            cleaned[day(raw_day)] = value
        except ValueError:
            continue
    return sorted(cleaned.items())


def six_month_anchor(end):
    month = (end.month - 7) % 12 + 1
    year = end.year - (end.month <= 6)
    return date(year, month, min(end.day, calendar.monthrange(year, month)[1]))


def fmt_signed(value, decimals=2):
    return f"{value:+,.{decimals}f}".replace("-", "−")


def txt(x, y, value, size=16, color=INK, *, weight="normal", anchor="start",
        face="sans", spacing=0):
    families = {
        "sans": "system-ui,-apple-system,Segoe UI,Arial,sans-serif",
        "serif": "Georgia,Times New Roman,serif",
        "mono": "ui-monospace,SFMono-Regular,Consolas,monospace",
    }
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" '
            f'font-family="{families[face]}" font-weight="{weight}" '
            f'letter-spacing="{spacing}" text-anchor="{anchor}">{esc(value)}</text>')


def line(x1, y1, x2, y2, color=RULE, width=1, dash=""):
    stroke_dash = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{color}" stroke-width="{width}"{stroke_dash}/>')


def rect(x, y, w, h, fill):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}"/>'


def circle(x, y, r, fill):
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}"/>'


def path(vertices):
    return " ".join(f'{"M" if i == 0 else "L"}{x:.2f},{y:.2f}' for i, (x, y) in enumerate(vertices))


def svg(height, title, description, elements):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
            f'width="{WIDTH}" height="{height}" role="img" aria-labelledby="title desc">\n'
            f'<title id="title">{esc(title)}</title>\n<desc id="desc">{esc(description)}</desc>\n'
            + "\n".join(elements) + "\n</svg>\n")


def banner(edition):
    index = next((row for row in edition["markets"]
                  if row.get("symbol", "").upper() in {"^GSPC", "SPX", "^SPX", "I:SPX"}), {})
    data = points(index)
    bg, fg = "#112c2b", "#f8f6ea"
    built = label_date(day(edition["created"]))
    parts = [rect(0, 0, WIDTH, 414, bg),
             txt(36, 42, "DAILY MARKET EDITION", 14, PALE, spacing=2),
             txt(904, 42, built, 16, fg, anchor="end"),
             line(36, 60, 904, 60, "#44625a"),
             txt(34, 137, "Market Observatory", 66, fg, face="serif", spacing=-2),
             line(36, 161, 904, 161, "#44625a"),
             txt(36, 201, "S&P 500", 21, fg, weight="600")]
    if not data:
        parts.append(txt(36, 272, "Official index close unavailable", 24, PALE))
        return svg(414, "Market Observatory", f"Edition prepared {built}. No S&P 500 index history available.", parts)
    end, close = data[-1]
    parts += [txt(34, 263, f"{close:,.2f}", 50, fg, face="serif"),
              txt(36, 330, f"Index close · {label_date(end)}", 17, PALE)]
    if len(data) >= 2:
        prev = data[-2][1]
        if prev:
            diff = close - prev
            parts.append(txt(36, 296, f"{fmt_signed(diff)} pts  ·  {fmt_signed(diff / prev * 100)}%", 19,
                             "#a5e7ba" if diff >= 0 else "#ffb0a2", weight="600"))
    anchor = six_month_anchor(end)
    window = [(d, p) for d, p in data if d >= anchor]
    lo, hi = min(v for _, v in window), max(v for _, v in window)
    x0, x1, y0, y1 = 370, 842, 217, 356
    domain = max(1, (end - window[0][0]).days)
    spread = hi - lo
    coords = [(x0 + (d - window[0][0]).days / domain * (x1 - x0),
               y1 - (v - lo) / spread * (y1 - y0) if spread else (y0 + y1) / 2)
              for d, v in window]
    parts += [txt(x0, 197, "S&P 500 INDEX LEVEL", 13, PALE, spacing=1.3)]
    for y, value in [(y0, hi), (y1, lo)]:
        parts += [line(x0, y, x1, y, "#47635b", dash="2 5"),
                  txt(904, y + 5, f"{value:,.0f}", 14, PALE, anchor="end", face="mono")]
    trace = path(coords)
    parts += [f'<path d="{trace} L{coords[-1][0]:.2f},{y1} L{x0},{y1} Z" fill="#294c43"/>',
              f'<path d="{trace}" fill="none" stroke="{GOLD}" stroke-width="2.8" stroke-linejoin="round"/>',
              circle(*coords[-1], 4, GOLD),
              txt(x0, 386, label_date(window[0][0]), 14, PALE),
              txt(x1, 386, label_date(end), 14, PALE, anchor="end")]
    return svg(414, "Market Observatory", f"S&P 500 closed at {close:,.2f} on {label_date(end)}. "
               f"The chart begins {label_date(window[0][0])}.", parts)


def sector_chart(edition):
    by_symbol = {s["symbol"]: points(s) for s in edition["markets"] if s["symbol"] in SECTORS}
    moves = []
    for symbol, name in SECTORS.items():
        data = by_symbol.get(symbol, [])
        change = None
        if len(data) >= 2 and data[-2][1]:
            change = 100 * (data[-1][1] / data[-2][1] - 1)
        moves.append((name, symbol, change, data[-1][0] if data else None))
    moves.sort(key=lambda m: (m[2] is None, -(m[2] or 0), m[0]))
    subtitle = "Session return against each ETF’s previous observed close"
    maxmove = max([abs(v) for _, _, v, _ in moves if v is not None] or [1])
    xmid, half = 545, 132
    parts = [rect(0, 0, WIDTH, 521, PAPER), txt(32, 53, "Sector rotation", 43, face="serif"),
             txt(32, 84, subtitle, 16, MUTED), line(32, 103, 908, 103),
             txt(32, 128, "SECTOR / US ETF", 13, MUTED, spacing=1.1),
             txt(xmid, 128, "0%", 13, MUTED, anchor="middle"),
             txt(762, 128, "MOVE", 13, MUTED, anchor="end", spacing=1.1),
             txt(907, 128, "CLOSE", 13, MUTED, anchor="end", spacing=1.1)]
    desc = []
    for i, (name, symbol, move, when) in enumerate(moves):
        y = 157 + i * 32
        width = abs(move or 0) / (maxmove or 1) * half
        parts += [txt(32, y, name, 16, weight="600"), txt(288, y, symbol, 14, MUTED, face="mono"),
                  line(32, y + 11, 908, y + 11, RULE, 0.65)]
        if move is not None:
            color = TEAL if move >= 0 else CORAL
            parts += [rect(xmid if move >= 0 else xmid-width, y-10, width, 8, color),
                      txt(762, y, f"{fmt_signed(move)}%", 16, color, anchor="end", face="mono")]
            desc.append(f"{name} {fmt_signed(move)}%")
        else:
            parts.append(txt(762, y, "—", 16, MUTED, anchor="end"))
        parts.append(txt(907, y, when.isoformat() if when else "—", 14, MUTED, anchor="end", face="mono"))
    parts.append(line(xmid, 137, xmid, 489, MUTED))
    return svg(521, "Sector rotation", ". ".join(desc) or "Sector market histories unavailable.", parts)


def treasury_chart(edition):
    rows = sorted(edition.get("curve", {}).get("rows", []), key=lambda r: r["date"])
    terms = ["1M", "3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
    terms = [t for t in terms if any(finite(r["rates"].get(t)) is not None for r in rows[-2:])]
    curves = [(r["date"], [finite(r["rates"].get(t)) for t in terms]) for r in rows[-2:]]
    values = [rate for _, rates in curves for rate in rates if rate is not None]
    parts = [rect(0, 0, WIDTH, 422, PAPER), txt(32, 53, "Treasury curve", 43, face="serif"),
             txt(32, 84, "US Treasury nominal par yields · equally spaced tenors", 16, MUTED),
             line(32, 103, 908, 103)]
    if not values:
        parts.append(txt(32, 180, "Treasury observations unavailable", 22, MUTED))
        return svg(422, "Treasury curve", "No Treasury observations were available for this edition.", parts)
    lo = math.floor((min(values) - 0.03)*4)/4
    hi = math.ceil((max(values) + 0.03)*4)/4
    x0, x1, yt, yb = 85, 875, 167, 306
    xs = ([x0 + i*(x1-x0)/(len(terms)-1) for i in range(len(terms))]
          if len(terms) > 1 else [(x0 + x1) / 2])
    for j in range(3):
        value = lo + (hi-lo)*j/2
        y = yb - (yb-yt)*j/2
        parts += [txt(62, y+5, f"{value:.2f}%", 13, MUTED, face="mono", anchor="end"),
                  line(x0, y, x1, y, RULE, dash="2 5")]
    for i, (obs_date, rates) in enumerate(curves):
        current = i == len(curves)-1
        color, thickness = (TEAL, 3) if current else ("#a36c47", 2)
        legend_x = 650 if current else 360
        parts += [line(legend_x, 133, legend_x+27, 133, color, thickness, "" if current else "5 4"),
                  txt(legend_x+37, 138, f"{'Latest' if current else 'Prior'} · {obs_date}", 15, MUTED)]
        prev = None
        for x, rate in zip(xs, rates):
            if rate is None:
                prev = None
                continue
            y = yb - (rate-lo)/(hi-lo)*(yb-yt)
            if prev is not None:
                parts.append(line(*prev, x, y, color, thickness, "" if current else "5 4"))
            parts.append(circle(x, y, 3.5 if current else 2, color))
            prev = (x, y)
    parts += [line(32, 352, 908, 352), txt(32, 378, "Δ bp", 14, MUTED)]
    for i, (term, x) in enumerate(zip(terms, xs)):
        parts.append(txt(x, 334, term, 15, INK, anchor="middle", weight="600"))
        vals = [rates[i] for _, rates in curves]
        change = fmt_signed((vals[1]-vals[0])*100, 0) if len(vals) == 2 and None not in vals else "—"
        parts.append(txt(x, 378, change, 15, MUTED, anchor="middle", face="mono"))
    return svg(422, "Treasury curve", "Observed par yields by maturity, with change since the prior "
               f"observation in basis points. Latest date {curves[-1][0]}.", parts)


def render_graphics(edition, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, generator in [("banner", banner), ("sectors", sector_chart), ("curve", treasury_chart)]:
        (out_dir / f"{name}.svg").write_text(generator(edition), encoding="utf-8")
