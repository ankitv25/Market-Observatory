// Every sector and style is measured on the same US trading dates. A missing
// endpoint stays missing, including when an individual ETF has a later close.
function rotationMonthEnd(day, monthsBack) {
 const [year, month, dayOfMonth] = day.split("-").map(Number);
 const last = new Date(Date.UTC(year, month - monthsBack, 0));
 last.setUTCDate(Math.min(dayOfMonth, last.getUTCDate()));
 return last.toISOString().slice(0, 10);
}

function rotationReturns(row, dates) {
 const prices = new Map(row?.history || []);
 function change(start, end) {
  const a = prices.get(start), b = prices.get(end);
  return Number.isFinite(a) && Number.isFinite(b) && a > 0 && b > 0
   ? 100 * (b / a - 1) : null;
 }
 return {
  pct: change(dates.prev, dates.end), month: change(dates.month, dates.end),
  prior: change(dates.two, dates.month), six: change(dates.six, dates.end)
 };
}

function rotationData() {
 const benchmark = byId.get("spy") || byId.get("spx");
 const anchor = benchmark || sectors.slice().sort((a,b) => b.stats.day.localeCompare(a.stats.day))[0];
 if (!anchor?.history?.length) return null;
 const history = anchor.history;
 const end = history.at(-1)[0];
 function anchorDate(months) {
  const cutoff = rotationMonthEnd(end, months);
  return history.filter(([d]) => d <= cutoff).at(-1)?.[0];
 }
 const dates = {
  end, prev: history.at(-2)?.[0], month: anchorDate(1), two: anchorDate(2), six: anchorDate(6)
 };
 const rows = sectors.map(row => ({row, ...rotationReturns(row, dates)}));
 return {dates, rows, benchmark, reference: rotationReturns(benchmark, dates)};
}

const rotationWindows = [["pct", "1D"], ["month", "1M"], ["six", "6M"]];

function sectorRotation() {
 const control = segments(rotationWindows, sectorWindow, "data-sector");
 const data = rotationData();
 if (!data) return section("Sector rotation", "US sector ETFs", '<p class="empty">Awaiting US sector closes.</p>', control);
 const {dates, rows} = data;
 const ranked = rows.filter(r => Number.isFinite(r[sectorWindow]))
  .sort((a,b) => b[sectorWindow] - a[sectorWindow] || a.row.symbol.localeCompare(b.row.symbol));
 const start = sectorWindow === "pct" ? dates.prev : dates[sectorWindow];
 if (!ranked.length) return section("Sector rotation", "US sector ETFs · through " + shortDate(dates.end),
  '<p class="empty">No sector ETFs have both closing prices for this window.</p>', control);
 const max = Math.max(.01, ...ranked.map(r => Math.abs(r[sectorWindow])));
 const tiles = ranked.map(({row, [sectorWindow]:v}) => {
  const color = v === 0 ? "164,177,177" : v > 0 ? "66,174,142" : "222,129,116";
  const strength = .1 + .48 * Math.abs(v) / max;
  const title = row.name + " · " + pct(v) + " · " + start + " to " + dates.end;
  return '<button class="tile" data-focus="'+esc(row.id)+'" title="'+esc(title)+'" style="background:rgba('+color+','+strength+')"><b>'+
   esc(row.symbol)+'</b><span>'+pct(v)+'</span><small>'+esc(row.name)+'</small></button>';
 }).join("");
 const up = ranked.filter(r => r[sectorWindow] > 0).length;
 const span = ranked[0][sectorWindow] - ranked.at(-1)[sectorWindow];
 let summary = ranked.length > 1 ? 'The spread from first to last was '+f(span)+' percentage points.' : '';
 const leader = ranked[0], dailyContext = sectorWindow === "pct" && leader[sectorWindow] > 0 && Number.isFinite(leader.month);
 if (dailyContext && leader.month < 0) summary += ' '+leader.row.name+' led this session but remains '+f(Math.abs(leader.month))+'% below its month-ago close.';
 return section("Sector rotation", "US sector ETF price returns · "+shortDate(start)+" – "+shortDate(dates.end),
  '<div class="matrix">'+tiles+'</div><div class="breadth"><b>'+up+' / '+ranked.length+'</b><div class="track"><i style="width:'+
  100*up/ranked.length+'%"></i></div></div><p class="mini rotation-summary">Sectors advancing. '+summary+'</p>', control);
}

// Competition ranking preserves ties at the same precision as the table.
function rotationRanks(rows, key) {
 const sorted = rows.filter(r => Number.isFinite(r[key])).slice()
  .sort((a,b) => b[key] - a[key] || a.row.symbol.localeCompare(b.row.symbol));
 const ranks = new Map();
 let previous, rank;
 sorted.forEach((r,i) => {
  const value = Number(r[key].toLocaleString("en-US", {maximumFractionDigits:2,useGrouping:false}));
  if (i === 0 || previous !== value) rank = i+1;
  ranks.set(r.row.id, rank);
  previous = value;
 });
 return ranks;
}

function rotationRankingNote(rows, current, previous, comparable) {
 const leaders = rows.filter(r => current.get(r.row.id) === 1);
 if (!leaders.length) return 'A monthly ranking needs both US closing prices for each ETF.';
 const names = new Intl.ListFormat("en-US", {style:"long",type:"conjunction"});
 const ties = names.format(leaders.map(r => r.row.name));
 let text = ties + (leaders.length > 1 ? " share the one-month lead at " : " leads the month at ")+pct(leaders[0].month)+".";
 if (!comparable) return text;
 const moves = rows.filter(r => current.has(r.row.id)).map(r => ({
  name:r.row.name, gain:previous.get(r.row.id)-current.get(r.row.id)
 }));
 const best = Math.max(...moves.map(r => r.gain));
 if (best > 0) {
  const gainers = moves.filter(r => r.gain === best);
  text += " "+names.format(gainers.map(r => r.name))+(gainers.length === 1 ? " climbed " : " each climbed ")+
   best+(best === 1 ? " place" : " places")+" from the previous month.";
 } else if (moves.every(r => r.gain === 0)) text += " The order is unchanged from the prior month.";
 return text;
}

function rotationStyles(dates) {
 const specifications = [
  ["Small vs. large cap","iwm","spy"], ["Equal vs. cap weight","rsp","spy"],
  ["Growth vs. value","iwf","iwd"], ["Momentum vs. large cap","mtum","spy"], ["Quality vs. large cap","qual","spy"]
 ];
 const pairs = specifications.map(([name,left,right]) => {
  const a = byId.get(left), b = byId.get(right);
  const lhs = rotationReturns(a, dates).month, rhs = rotationReturns(b, dates).month;
  const gap = Number.isFinite(lhs) && Number.isFinite(rhs) ? lhs-rhs : null;
  return {name, a, b, gap};
 });
 const scale = Math.max(.01, ...pairs.map(p => Math.abs(p.gap || 0)));
 const bars = pairs.map(({name,a,b,gap}) => {
  const magnitude = Math.abs(gap||0)/scale*50;
  const bar = Number.isFinite(gap) ? '<i style="left:'+(gap < 0 ? 50-magnitude : 50)+'%;width:'+magnitude+'%;background:'+
   (gap < 0 ? '#b16e64' : '#3c8876')+'"></i>' : '';
  return '<div class="rotation-pair"><div class="spread"><b>'+esc(name)+'</b><strong class="'+cls(gap)+'">'+
   (Number.isFinite(gap) ? sf(gap)+' pp' : '—')+'</strong></div><div class="rotation-axis" aria-hidden="true">'+bar+
   '</div><small class="mini">'+esc((a?.symbol || '—')+' minus '+(b?.symbol || '—'))+'</small></div>';
 }).join("");
 const [size,weight] = pairs;
 let read = '';
 if (Number.isFinite(size.gap) && Number.isFinite(weight.gap)) {
  if (size.gap > 0 && weight.gap > 0) read = 'Small caps and equal weight both beat cap-weighted large caps over the month. Leadership extended beyond the largest US names.';
  else if (size.gap < 0 && weight.gap < 0) read = 'Small caps and equal weight both trailed cap-weighted large caps over the month. The largest names had the relative advantage.';
  else if (size.gap * weight.gap < 0) read = size.gap > 0 ?
   'Small caps beat large caps over the month, even as equal weight lagged within the S&P 500. The two measures of breadth diverged.' :
   'Equal weight beat cap weight within the S&P 500, even as small caps lagged. Broader leadership inside large caps has yet to extend down the size spectrum.';
 }
 return '<aside class="rotation-styles"><h3>Size &amp; style spreads</h3><p class="note">One-month return of the first ETF minus the second, in percentage points.</p>'+
  bars+(read?'<p class="rotation-note">'+read+'</p>':'')+'</aside>';
}

function rotationDetail() {
 const data = rotationData();
 if (!data) return '';
 const {rows, dates, reference, benchmark} = data;
 const current = rotationRanks(rows,"month"), previous = rotationRanks(rows,"prior");
 const comparable = current.size > 0 && current.size === previous.size && [...current.keys()].every(id => previous.has(id));
 const relative = benchmark?.symbol || "index";
 const sorted = rows.slice().sort((a,b) => (current.get(a.row.id) ?? Infinity)-(current.get(b.row.id) ?? Infinity) || a.row.name.localeCompare(b.row.name));
 const cells = sorted.map(r => {
  const {row} = r, rank = current.get(row.id);
  const shift = comparable && rank ? previous.get(row.id)-rank : null;
  const gap = Number.isFinite(r.month) && Number.isFinite(reference.month) ? r.month-reference.month : null;
  const rankMove = !Number.isFinite(shift) ? '—' : shift > 0 ? '↑ '+shift : shift < 0 ? '↓ '+Math.abs(shift) : 'Unch.';
  return '<tr><td><button data-focus="'+esc(row.id)+'">'+esc(row.name)+'</button><small>'+esc(row.symbol)+'</small></td>'+
   '<td>'+(rank ?? '—')+'</td>'+["pct","month","six"].map(k=>'<td class="'+cls(r[k])+'">'+pct(r[k])+'</td>').join("")+
   '<td class="'+cls(gap)+'">'+(Number.isFinite(gap)?sf(gap)+' pp':'—')+'</td><td>'+rankMove+'</td></tr>';
 }).join("");
 const table = '<div class="tablebox" role="region" aria-label="Sector return rankings" tabindex="0"><table class="rotation-scorecard"><thead><tr>'+
  '<th scope="col">Sector</th><th scope="col">1M rank</th><th scope="col">1D</th><th scope="col">1M</th><th scope="col">6M</th><th scope="col">1M vs '+esc(relative)+
  '</th><th scope="col">Rank change</th></tr></thead><tbody>'+cells+'</tbody></table></div>';
 const measured = rows.filter(r => Number.isFinite(r.month));
 const outperform = measured.filter(r => r.month > reference.month).length;
 const breadth = Number.isFinite(reference.month) && measured.length ? ' '+outperform+' of '+measured.length+' beat '+relative+
  ' over the month ('+pct(reference.month)+').' : '';
 const window = [dates.month && '1M from '+shortDate(dates.month), dates.six && '6M from '+shortDate(dates.six)].filter(Boolean).join(" · ");
 const method = 'Price returns through '+dateLabel(dates.end)+(window?' · '+window:'')+'. '+
  (comparable && dates.two ? 'Rank change compares with '+shortDate(dates.two)+' – '+shortDate(dates.month)+'. Ties share a rank.' :
   'Rank changes require the same sector coverage in both months.');
 return '<section id="rotation-detail" class="home-panel rotation-detail"><div class="panel-head"><h2>Sector leadership &amp; equity style</h2></div>'+
  '<div class="rotation-layout"><div><p class="rotation-note">'+esc(rotationRankingNote(sorted,current,previous,comparable)+breadth)+'</p>'+table+
  '<p class="mini rotation-method">'+esc(method)+'</p></div>'+rotationStyles(dates)+'</div></section>';
}
