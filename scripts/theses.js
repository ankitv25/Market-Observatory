// Portfolio positions use the published book. The adjoining chart uses price proxies.
let thesisBookId = "saa";
let thesisPairId = "";
const thesisPairs = [
  {id:"tlt", sleeve:"US Treasuries (long)", label:"Long Treasuries", question:"Did long Treasuries cushion equity declines?"},
  {id:"tip", sleeve:"TIPS", label:"Inflation-linked Treasuries", question:"Did inflation-linked bonds hold up on equity down days?"},
  {id:"igf", sleeve:"Listed infrastructure", label:"Listed infrastructure", question:"How closely did listed infrastructure follow equities?"},
  {id:"vnq", sleeve:"Listed real estate", label:"Listed property", question:"How much equity sensitivity showed up in listed property?"},
  {id:"dbmf", sleeve:"Managed futures (trend)", label:"Managed futures", question:"When equities slipped, did the trend proxy gain?"},
  {id:"gld", sleeve:"Gold", label:"Gold", question:"Did gold provide a counterweight on equity down days?"},
  {id:"eem", sleeve:"Emerging-market equity", label:"Emerging-market equities", question:"How tightly did emerging markets track US stocks?"},
  {id:"ief", sleeve:"US Treasuries (intermediate)", label:"Intermediate Treasuries", question:"Did intermediate Treasuries rise on equity down days?"},
  {id:"lqd", sleeve:"IG corporate credit", label:"Investment-grade credit", question:"How much did corporate bond prices move with equities?"},
  {id:"efa", sleeve:"Developed ex-US equity", label:"Developed ex-US equities", question:"How much did developed overseas markets move with US stocks?"}
];
const thesisDefaultPair = {saa:"tlt", certain:"tip", endowment:"igf", daa:"eem", alpha:"dbmf"};

function thesisReturns(row) {
  const daily = new Map();
  const history = row?.history || [];
  for (let i = 1; i < history.length; i++) {
    const [start, first] = history[i-1], [end, last] = history[i];
    const gap = (Date.parse(end) - Date.parse(start)) / 864e5;
    if (gap > 0 && gap <= 5 && Number.isFinite(first) && first > 0 && Number.isFinite(last) && last > 0) {
      daily.set(start + "/" + end, last / first - 1);
    }
  }
  return daily;
}

function thesisMatched(left, right) {
  const matched = [], other = thesisReturns(right);
  for (const [interval, x] of thesisReturns(left)) {
    if (other.has(interval)) matched.push({day:interval.split("/")[1], x, y:other.get(interval)});
  }
  return matched;
}

function thesisCorrelation(rows) {
  if (rows.length < 2 || rows.every(r=>r.x===rows[0].x) || rows.every(r=>r.y===rows[0].y)) return null;
  const mx = rows.reduce((sum, r) => sum + r.x, 0) / rows.length;
  const my = rows.reduce((sum, r) => sum + r.y, 0) / rows.length;
  let xx = 0, yy = 0, xy = 0;
  for (const row of rows) {
    const x = row.x - mx, y = row.y - my;
    xx += x*x;
    yy += y*y;
    xy += x*y;
  }
  return xx && yy ? Math.min(1, Math.max(-1, xy / Math.sqrt(xx*yy))) : null;
}

function thesisSeries(matched) {
  const series = [];
  // Keep windows with undefined correlation so the chart breaks at that date.
  for (let i = Math.max(62,matched.length-127); i < matched.length; i++) {
    series.push({day:matched[i].day, value:thesisCorrelation(matched.slice(i-62,i+1))});
  }
  return series;
}

function thesisHistoryChart(series, symbol) {
  if (series.length < 2 || series.filter(point=>point.value!=null).length < 2) return "";
  const start = Date.parse(series[0].day), end = Date.parse(series.at(-1).day);
  if (start >= end) return "";
  const X = day => 32 + 390*(Date.parse(day)-start)/(end-start);
  const Y = val => 55 - val*43;
  let curve = "", liftPen = true;
  for (const point of series) {
    if (point.value == null) { liftPen = true; continue; }
    curve += (liftPen ? "M" : "L") + X(point.day).toFixed(1) + " " + Y(point.value).toFixed(1);
    liftPen = false;
  }
  const last = series.at(-1);
  const endpoint = last.value == null ? "" : '<circle cx="422" cy="'+Y(last.value)+'" r="3.5" fill="#176e68"/>';
  return '<figure class="thesis-chart"><figcaption>Rolling 63-session correlation · SPY / '+esc(symbol)+'</figcaption>'+
    '<svg role="img" aria-label="Rolling correlation from '+esc(series[0].day)+' to '+esc(last.day)+'" viewBox="0 0 432 125" width="100%">'+
    '<g fill="#536776" font-size="10" font-family="sans-serif">'+
    '<path d="M32 12H422 M32 98H422" stroke="#d9e1df"/><path d="M32 55H422" stroke="#98aca6" stroke-dasharray="3 3"/>'+
    '<text x="23" y="16" text-anchor="end">+1</text><text x="23" y="59" text-anchor="end">0</text><text x="23" y="102" text-anchor="end">−1</text>'+
    '<text x="32" y="119">'+esc(shortDate(series[0].day))+'</text><text x="422" y="119" text-anchor="end">'+esc(shortDate(last.day))+'</text></g>'+
    '<path d="'+curve+'" fill="none" stroke="#176e68" stroke-width="2" stroke-linejoin="round"/>'+endpoint+'</svg></figure>';
}

function thesisMetrics(items) {
  return '<dl class="thesis-metrics">'+items.map(([label,val])=>'<div><dt>'+esc(label)+'</dt><dd>'+esc(val)+'</dd></div>').join("")+'</dl>';
}

function thesisEvidence(pair, choices) {
  if (!pair) return '<p class="empty">No covered price pair for the sleeves in this edition.</p>';
  const row = byId.get(pair.id), anchor = byId.get("spy");
  const control = '<label class="thesis-choice">Market lens <select id="thesisPair">'+choices.map(p=>option(p.id,p.label,pair.id)).join("")+'</select></label>';
  const title = '<div class="thesis-subhead"><h3>'+esc(pair.question)+'</h3>'+control+'</div>';
  const matched = thesisMatched(anchor,row);
  if (matched.length < 63) return title+'<p class="empty">Only '+matched.length+' matched daily returns available. This lens needs 63.</p>';
  const series = thesisSeries(matched), current = series.at(-1), window = matched.slice(-63);
  const previous = matched.length >= 126 ? thesisCorrelation(matched.slice(-126,-63)) : null;
  const losses = window.filter(r=>r.x<0);
  const offsets = losses.filter(r=>r.y>0).length;
  const priorShift = previous == null || current.value == null ? null : current.value - previous;
  const date = dateLabel(current.day);
  const age = (Date.parse(E.created.slice(0,10)) - Date.parse(current.day)) / 864e5;
  const vintage = age > 7 ? ' This reading is '+age+' calendar days behind the edition.' : '';
  const movement = current.value == null ? "This window has no variation in at least one return series." :
    Math.abs(current.value)<.20 ? "The two price series showed little linear co-movement across these sessions." :
    current.value>0 ? "Their daily price returns tended to move together." : "Their daily price returns tended to move in opposite directions.";
  const downside = losses.length
    ? row.symbol+' gained on '+offsets+' of the '+losses.length+' sessions when SPY fell.'
    : 'SPY had no down sessions in this window.';
  const downsideReturns = losses.length ? " Across those down sessions, SPY averaged "+pct(100*losses.reduce((n,r)=>n+r.x,0)/losses.length)+" and "+row.symbol+" averaged "+pct(100*losses.reduce((n,r)=>n+r.y,0)/losses.length)+"." : "";
  return title+
    '<p class="mini thesis-asof">Price evidence through '+esc(date)+esc(vintage)+'</p>'+
    thesisMetrics([["63-session correlation",sf(current.value)],["Prior 63 sessions",sf(previous)],["Difference",sf(priorShift)]])+
    '<p class="thesis-reading">'+esc(movement+' '+downside+downsideReturns)+'</p>'+thesisHistoryChart(series,row.symbol)+
    '<details class="thesis-method"><summary>Dates and calculation</summary><p>SPY represents US equities. '+esc(row.symbol)+' represents '+esc(pair.label.toLowerCase())+
    '. Each point is a Pearson correlation of 63 daily ETF price returns with identical start and end close dates. Values between −0.20 and +0.20 are described here as weak co-movement. The comparison uses the preceding 63 non-overlapping returns. '+
    'This window ends '+esc(current.day)+' and starts with the return ending '+esc(window[0].day)+'. Distributions are excluded. The down-day count measures frequency alone.</p></details>';
}

function overviewTheses() {
  const books = Object.entries(E.books || {}).filter(([,b])=>b && typeof b==="object");
  const header = '<div class="panel-head"><h2>Portfolio thesis &amp; cross-market evidence</h2><a href="#portfolio" data-open-book="'+esc(thesisBookId)+'">Portfolio monitor ↗</a></div>';
  if (!books.length) return '<section id="portfolio-brief" class="home-panel thesis-panel">'+header+'<p class="empty">No published portfolio snapshot in this edition.</p></section>';
  const [key,b] = books.find(([id])=>id===thesisBookId) || books[0];
  const sleeves = b.sleeves || [];
  const choices = thesisPairs.filter(p=>byId.has("spy") && byId.has(p.id) && sleeves.some(s=>s.sleeve===p.sleeve && s.capital>0));
  const pair = choices.find(p=>p.id===(thesisPairId || thesisDefaultPair[key])) || choices[0];
  const top = sleeves.filter(s=>Number.isFinite(s.risk) && Number.isFinite(s.capital)).sort((a,b)=>b.risk-a.risk)[0];
  const related = pair && sleeves.find(s=>s.sleeve===pair.sleeve);
  const metrics = [
    ["Published stance",b.stance || "—"],
    ["Forecast volatility",Number.isFinite(b.forecast)?f(b.forecast,1)+"%":"—"],
    ["Construction vol. cap",Number.isFinite(b.budget)?f(b.budget,1)+"%":"—"]
  ];
  const bookAge = (Date.parse(E.created.slice(0,10)) - Date.parse(b.date)) / 864e5;
  const bookDate = b.date ? dateLabel(b.date)+(bookAge>7?" · "+bookAge+" calendar days before this edition":"") : "Date unavailable";
  const concentration = top ? top.sleeve+' accounts for '+f(top.risk,1)+'% of modeled portfolio risk on '+f(top.capital,1)+'% of capital.' : "";
  const lensWeight = related && related!==top ? ' The '+pair.label.toLowerCase()+' sleeve has a '+f(related.capital,1)+'% capital weight.' : "";
  return '<section id="portfolio-brief" class="home-panel thesis-panel">'+header+
    '<div class="thesis-layout"><article class="thesis-book"><div class="thesis-subhead"><h3>'+esc(b.name)+' investment thesis</h3>'+
    '<label class="thesis-choice">Book <select id="thesisBook">'+books.map(([id,book])=>option(id,book.name,key)).join("")+'</select></label></div>'+
    '<p class="mini thesis-asof">Published positioning · '+esc(bookDate)+'</p>'+
    (b.thesis ? '<blockquote class="thesis-published">'+esc(b.thesis)+'</blockquote>' : '<p class="empty">Thesis text unavailable for this book.</p>')+
    thesisMetrics(metrics)+'<p class="thesis-reading">'+esc(concentration+lensWeight)+'</p>'+
    (b.url?'<a class="link" href="'+esc(b.url)+'">Published portfolio book ↗</a>':'')+'</article>'+
    '<article class="thesis-evidence">'+thesisEvidence(pair, choices)+'</article></div></section>';
}

function thesisControls(event) {
  const {id,value} = event.target;
  if (id !== "thesisBook" && id !== "thesisPair") return false;
  if (id === "thesisBook") { thesisBookId = value; thesisPairId = ""; }
  else thesisPairId = value;
  $("portfolio-brief").outerHTML = overviewTheses();
  $(id)?.focus({preventScroll:true});
  return true;
}
