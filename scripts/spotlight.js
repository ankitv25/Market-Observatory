// Rank a move against the instrument's own history. Each desk can win one slot.
const pulseDesks = [
  ["US equities", ["spx", "ixic", "rut", "dji"]],
  ["International equities", ["stoxx50", "ftse", "nikkei", "nifty", "hsi", "tsx", "eem", "efa"]],
  ["Rates & credit", ["yield2", "yield10", "shy", "ief", "tlt", "hyg", "lqd", "mub", "emb", "mbb", "bkln", "tip"]],
  ["Currencies", ["eurusd", "gbpusd", "usdjpy", "usdchf", "dxy"]],
  ["Commodities", ["wti", "brent", "gold", "copper", "silver", "corn", "natgas"]],
  ["Alternatives", ["vnq", "igf", "dbmf", "btc", "vix"]]
];
function pulseRecord(row) {
  if (!row || row.history.length < 62) return null;
  const values = [];
  for (let i = row.history.length - 61; i < row.history.length; i++) {
    const [a, start] = row.history[i - 1], [b, end] = row.history[i];
    if (!Number.isFinite(start) || !Number.isFinite(end) || (!row.yield && start <= 0) || (Date.parse(b) - Date.parse(a)) / 864e5 > 5) return null;
    values.push(row.yield ? 100 * (end - start) : 100 * (end / start - 1));
  }
  const move = values.pop(), magnitude = Math.abs(move);
  // Prices used for ranking retain their source precision.
  const smaller = values.filter(v => Math.abs(v) < magnitude - 1e-8).length;
  return {row, move, smaller};
}
function pulseSelection() {
  const cutoff = Date.parse(E.created.slice(0, 10));
  const compare = (a, b) => b.smaller - a.smaller || b.row.stats.day.localeCompare(a.row.stats.day) || a.row.name.localeCompare(b.row.name);
  return pulseDesks.flatMap(([desk, ids]) => {
    const candidates = ids.map(marketQuote).filter(row => row && cutoff-Date.parse(row.stats.day) <= 4*864e5)
      .map(pulseRecord).filter(Boolean).sort(compare);
    return candidates.length ? [{...candidates[0], desk}] : [];
  }).sort(compare).slice(0,3);
}
const pulsePicks = pulseSelection();
function pulseChart(row) {
  const values = row.history.slice(-22), series = values.map(p => p[1]);
  const low = Math.min(...series), high = Math.max(...series);
  const first = Date.parse(values[0][0]), last = Date.parse(values.at(-1)[0]);
  const y = v => high === low ? 27 : 48 - (v-low)/(high-low)*42;
  const coords = values.map(([d,v]) => [(4+226*(Date.parse(d)-first)/(last-first)).toFixed(1), y(v).toFixed(1)]);
  const points = coords.map(p=>p.join(",")).join(" "), channel = series.at(-1) >= series[0] ? "#287961" : "#ad594e";
  const end = coords.at(-1);
  return '<figure class="pulse-chart"><svg viewBox="0 0 300 55" role="img" aria-label="'+esc(row.name+' last 22 closes, low '+f(low,dispatchPrecision(row))+' and high '+f(high,dispatchPrecision(row))+' '+row.unit)+'">'+
    '<path d="M4 6H230 M4 48H230" fill="none" stroke="#dbe1d9" stroke-dasharray="3 3"/><polygon points="4,50 '+points+' 230,50" fill="'+channel+'" opacity=".06"/>'+
    '<polyline points="'+points+'" fill="none" stroke="'+channel+'" stroke-width="2"/><circle cx="'+end[0]+'" cy="'+end[1]+'" r="2.8" fill="'+channel+'"/>'+
    '<g fill="#5b6d68" font-size="10" font-family="monospace"><text x="295" y="11" text-anchor="end">'+f(high,dispatchPrecision(row))+'</text><text x="295" y="50" text-anchor="end">'+f(low,dispatchPrecision(row))+'</text></g></svg>'+
    '<figcaption><span>'+shortDate(values[0][0])+'</span><span>'+shortDate(values.at(-1)[0])+' · '+esc(row.unit)+'</span></figcaption></figure>';
}
function activeCharts() {
  const cards = pulsePicks.map(({row, smaller, desk}) =>
    '<article class="pulse-card"><div class="pulse-desk">'+esc(desk)+'</div><h3><button '+quoteTarget(row)+'>'+esc(row.name)+' <span aria-hidden="true">↗</span></button></h3>'+
    '<div class="pulse-number"><b>'+f(row.stats.last,dispatchPrecision(row))+(row.yield?'%':'')+'</b><span class="'+cls(row.stats.change)+'">'+(row.yield?dailyMove(row):pct(row.stats.pct))+'</span></div>'+
    pulseChart(row)+'<p>The '+shortDate(row.stats.day)+' move exceeded <b>'+smaller+' of the prior 60</b> daily moves in magnitude.</p></article>').join('');
  if (!cards) return '';
  return '<section id="active-charts" class="pulse-section"><div class="edition-section"><div><h2>Moves in focus</h2><p>Which markets moved furthest relative to their own recent trading?</p></div>'+
    '<span class="section-meta">60-observation lookback</span></div><div class="pulse-grid">'+cards+'</div>'+
    '<details class="pulse-method"><summary>How markets are selected</summary><p>We compare the absolute one-session percentage change with the preceding 60 absolute changes in the same series. Treasury yields use basis points. The three highest counts across distinct desks are shown. Ties favor the newer observation, then the instrument name. Closes more than four calendar days old and histories with breaks over five days are excluded. A 22-close chart shows the price or yield path.</p></details></section>';
}
