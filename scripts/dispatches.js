// Editorial copy uses the same dated observations as the tape. Compare daily
// returns only when the two instruments span the same pair of session dates.
function dispatchPeriodsMatch(a, b, period = "pct") {
  if (!a || !b || a.stats.day !== b.stats.day) return false;
  const anchor = period === "six" ? "base" : "previous_day";
  return Boolean(a.stats[anchor]) && a.stats[anchor] === b.stats[anchor]
    && Number.isFinite(a.stats[period]) && Number.isFinite(b.stats[period]);
}

function dispatchGap(a, b, period = "pct") {
  return dispatchPeriodsMatch(a, b, period) ? a.stats[period] - b.stats[period] : null;
}

function dispatchComparison(subject, gap, peer) {
  if (Math.abs(gap) < .005) return subject + " finishes level with " + peer;
  return subject + (gap > 0 ? " outpaces " : " trails ") + peer + " by " + f(Math.abs(gap)) + " pp";
}

function dispatchVerb(value) {
  return value > 0 ? "rose" : value < 0 ? "fell" : "finished flat";
}

function dispatchPrecision(r) {
  if (r.group === "FX" && r.id !== "dxy") return 4;
  return ["natgas","copper","silver"].includes(r.id) ? 3 : 2;
}

function dispatchPoint(r) {
  return f(r.stats.last, dispatchPrecision(r)) + " " + r.unit;
}

function dispatchFallback(rows) {
  const ordered = [...rows].filter(r => Number.isFinite(r.stats.pct)).sort((a,b) => b.stats.day.localeCompare(a.stats.day));
  if (!ordered.length) return ["Session comparison pending", "A dated comparison will appear when closing prices are available."];
  const r = ordered[0], s = r.stats;
  const context = Number.isFinite(s.six) ? " Its six-month price change was " + pct(s.six) + "." : "";
  return [r.name + " closes at " + dispatchPoint(r), "From " + shortDate(s.previous_day) + " to " + shortDate(s.day) + ", " + r.name + " " + dispatchVerb(s.pct) + " (" + pct(s.pct) + ")." + context];
}

function dispatchAmericas(rows) {
  const small = byId.get("rut"), large = byId.get("spx"), tsx = byId.get("tsx");
  const gap = dispatchGap(small, large);
  if (gap === null) return dispatchFallback(rows);
  const headline = dispatchComparison("The Russell 2000", gap, "the S&P 500");
  const dow = byId.get("dji"), nasdaq = byId.get("ixic");
  const us = [large,small,dow,nasdaq].filter(r => dispatchPeriodsMatch(r,large));
  const lower = us.filter(r => r.stats.pct < 0).length, higher = us.filter(r => r.stats.pct > 0).length;
  let copy = lower === us.length ? "Every tracked US benchmark in the table fell." : higher === us.length ? "Gains reached every tracked US benchmark in the table." : higher + " of " + us.length + " US benchmarks in the table closed higher.";
  const six = dispatchGap(small, large, "six");
  if (six !== null && Math.abs(gap) >= .005 && Math.abs(six) >= .005) {
    const ahead = six > 0 ? "ahead of" : "behind";
    copy += " Small caps are " + f(Math.abs(six)) + " percentage points " + ahead + " the S&P over six months. The daily ranking " + (gap * six > 0 ? "echoed that longer trend." : "ran against that longer trend.");
  }
  if (dispatchPeriodsMatch(tsx, large)) copy += " In Canada, the TSX " + dispatchVerb(tsx.stats.pct) + " (" + pct(tsx.stats.pct) + ") in local currency.";
  return [headline, copy];
}

function dispatchEurope(rows) {
  const uk = byId.get("ftse"), euro = byId.get("stoxx50"), gap = dispatchGap(uk,euro);
  if (gap === null) return dispatchFallback(rows);
  const opposed = uk.stats.pct * euro.stats.pct < 0;
  const headline = opposed
    ? (uk.stats.pct > 0 ? "London rises as eurozone blue chips slip" : "Eurozone blue chips rise as London slips")
    : dispatchComparison("The FTSE 100", gap, "the Euro STOXX 50");
  let copy = "The FTSE 100 moved " + sf(uk.stats.change) + " index points in London and the Euro STOXX 50 moved " + sf(euro.stats.change) + " in the euro area.";
  const six = dispatchGap(uk, euro, "six");
  if (six !== null && Math.abs(six) >= .005) copy += " Over six months, " + (six > 0 ? "London leads eurozone blue chips" : "eurozone blue chips lead London") + " by " + f(Math.abs(six)) + " percentage points in local-currency price terms.";
  return [headline, copy];
}

function dispatchAsia(rows) {
  if (rows.length < 2 || !rows.every(r => dispatchPeriodsMatch(r,rows[0]))) return dispatchFallback(rows);
  const ranked = [...rows].sort((a,b) => b.stats.pct - a.stats.pct);
  const top = ranked[0], last = ranked.at(-1), rising = ranked.filter(r => r.stats.pct > 0);
  const falling = ranked.filter(r => r.stats.pct < 0);
  const place = {nikkei:"Japan",hsi:"Hong Kong",nifty:"India"};
  const headline = rising.length === 1 && falling.length === rows.length-1
    ? place[top.id] + " rises as its regional peers fall"
    : falling.length === 1 && rising.length === rows.length-1
    ? place[last.id] + " falls as its regional peers rise"
    : dispatchComparison(top.name,top.stats.pct-last.stats.pct,last.name);
  let copy = "The strongest local close was " + top.name + " (" + pct(top.stats.pct) + "), against " + pct(last.stats.pct) + " for the " + last.name + ".";
  if (rows.every(r => dispatchPeriodsMatch(r,rows[0],"six"))) {
    const longLeader = [...rows].sort((a,b) => b.stats.six - a.stats.six)[0];
    copy += " " + place[longLeader.id] + (longLeader.id === top.id ? " also leads" : " still leads") + " these markets over six months at " + pct(longLeader.stats.six) + ".";
  }
  return [headline, copy];
}

function dispatchRatesRows() {
  return ["2Y","5Y","10Y","30Y"].flatMap(tenor => {
    const dates = curves.filter(r => Number.isFinite(r.rates[tenor]));
    if (dates.length < 2) return [];
    const day = dates.at(-1), prior = dates.at(-2), last = day.rates[tenor];
    const target = new Date(day.date + "T00:00:00Z");
    const monthDay = target.getUTCDate();
    target.setUTCDate(1);
    target.setUTCMonth(target.getUTCMonth()-6);
    const lastMonthDay = new Date(Date.UTC(target.getUTCFullYear(),target.getUTCMonth()+1,0)).getUTCDate();
    target.setUTCDate(Math.min(monthDay,lastMonthDay));
    const anchor = target.toISOString().slice(0,10);
    const base = dates.filter(r => r.date <= anchor).at(-1);
    return [{id:tenor, name:tenor.slice(0,-1)+"-year Treasury", unit:"%", yield:true,
      stats:{day:day.date, previous_day:prior.date, last,
        change:Math.round(100*(last-prior.rates[tenor])), base:base?.date,
        six:base ? Math.round(100*(last-base.rates[tenor])) : null}}];
  });
}

function dispatchRates(rows) {
  const two = rows.find(r => r.id === "2Y"), ten = rows.find(r => r.id === "10Y");
  if (!two || !ten || two.stats.day !== ten.stats.day || two.stats.previous_day !== ten.stats.previous_day) {
    return ["Treasury yields by maturity", "Each tenor is dated separately. The curve comparison requires matching observations at two and ten years."];
  }
  const spread = Math.round(100*(ten.stats.last-two.stats.last)), change = ten.stats.change-two.stats.change;
  const headline = change ? "The 2s10s curve " + (change > 0 ? "steepens " : "flattens ") + Math.abs(change) + " bp" : "The 2s10s curve holds its slope";
  const relation = spread === 0 ? "equal to the two-year yield" : f(Math.abs(spread),0) + " bp " + (spread > 0 ? "above" : "below") + " the two-year";
  const copy = "The 10-year finished at " + f(ten.stats.last) + "%, " + relation + ". The two-year yield " + dispatchVerb(two.stats.change)
    + " (" + sf(two.stats.change,0) + " bp), versus " + sf(ten.stats.change,0) + " bp at ten years. "
    + (change === 0 ? "Both ends moved by the same amount." : "The " + (Math.abs(two.stats.change) === Math.abs(ten.stats.change) ? "two maturities moved equally in opposite directions." : Math.abs(two.stats.change) > Math.abs(ten.stats.change) ? "larger repricing came at the short end." : "larger repricing came at the long end."));
  return [headline, copy];
}

function dispatchCredit(rows) {
  const high = byId.get("hyg"), ig = byId.get("lqd"), loans = byId.get("bkln");
  const gap = dispatchGap(high, ig);
  if (gap === null) return dispatchFallback(rows);
  const headline = dispatchComparison("High yield", gap, "investment grade");
  const both = high.stats.pct * ig.stats.pct > 0;
  let copy = both ? "Both corporate bond ETFs " + dispatchVerb(high.stats.pct) + ". " : "Corporate bond prices were mixed. ";
  copy += "HYG closed at $" + f(high.stats.last) + " and LQD at $" + f(ig.stats.last) + ".";
  if (dispatchPeriodsMatch(loans,high)) copy += " Floating-rate loans " + dispatchVerb(loans.stats.pct) + " (" + pct(loans.stats.pct) + "), giving a shorter-duration credit comparison.";
  copy += " Coupon income and duration differences matter when translating these price moves into a credit view.";
  return [headline, copy];
}

function dispatchFx(rows) {
  const index = byId.get("dxy");
  if (!index || !Number.isFinite(index.stats.pct)) return dispatchFallback(rows);
  const quotes = rows.filter(r => r.id !== "dxy" && dispatchPeriodsMatch(r,index) && r.stats.last > 0);
  if (!quotes.length) return dispatchFallback(rows);
  // Measure the USD move as units of each peer currency per dollar.
  // EUR/USD and GBP/USD require the return on the reciprocal price.
  const peers = {eurusd:"euro",gbpusd:"pound",usdjpy:"yen",usdchf:"Swiss franc"};
  const changes = quotes.map(r => ({r, usd:r.id.startsWith("usd") ? r.stats.pct : -100*r.stats.pct/(100+r.stats.pct)}));
  const up = changes.filter(c => c.usd > 0).length, down = changes.filter(c => c.usd < 0).length;
  const breadth = changes.length === 4 ? "all four tracked peers" : changes.length === 1 ? "the " + peers[changes[0].r.id] : changes.length + " reporting peers";
  const headline = up === changes.length ? "Dollar gains against " + breadth
    : down === changes.length ? "Dollar falls against " + breadth : "Dollar pairs give a mixed reading";
  const largest = changes.reduce((a,b) => Math.abs(a.usd) >= Math.abs(b.usd) ? a : b);
  const copy = "The dollar index " + dispatchVerb(index.stats.pct) + " (" + pct(index.stats.pct) + ") to " + f(index.stats.last) + ". The biggest bilateral move was against the " + peers[largest.r.id] + ", where one US dollar bought " + (Math.abs(largest.usd) < .005 ? "roughly the same amount of currency." : f(Math.abs(largest.usd)) + "% " + (largest.usd > 0 ? "more" : "less") + " currency than at the previous close.");
  return [headline, copy];
}

function dispatchCommodities(rows) {
  const oil = byId.get("wti"), copper = byId.get("copper"), gold = byId.get("gold");
  if (dispatchGap(oil,copper) === null || !oil.contract) return dispatchFallback(rows);
  const opposite = oil.stats.pct*copper.stats.pct < 0;
  const headline = opposite
    ? (oil.stats.pct > 0 ? "Crude advances as copper retreats" : "Copper advances as crude retreats")
    : dispatchComparison("WTI crude",oil.stats.pct-copper.stats.pct,"copper");
  let copy = "The " + oil.contract + " WTI contract " + dispatchVerb(oil.stats.pct) + " " + (oil.stats.change === 0 ? "at " : "$" + f(Math.abs(oil.stats.change)) + " a barrel to ") + "$" + f(oil.stats.last) + ". Copper finished " + pct(copper.stats.pct) + ".";
  if (dispatchPeriodsMatch(gold,oil)) {
    const metals = copper.stats.pct*gold.stats.pct > 0;
    copy += " Gold " + dispatchVerb(gold.stats.pct) + " (" + pct(gold.stats.pct) + ")";
    copy += metals && opposite ? ", leaving both metals on the other side of the oil move." : metals ? ", moving in the same direction as copper." : ".";
  }
  return [headline, copy];
}

function dispatchAlternatives(rows) {
  const spy = byId.get("spy"), managed = byId.get("dbmf"), re = byId.get("vnq"), infra = byId.get("igf");
  if (dispatchGap(managed,spy) === null) return dispatchFallback(rows);
  const opposing = managed.stats.pct * spy.stats.pct < 0;
  const headline = opposing ? "Managed futures " + (managed.stats.pct > 0 ? "gain as US equities fall" : "fall as US equities gain") : dispatchComparison("DBMF", managed.stats.pct-spy.stats.pct, "US large caps");
  let copy = "DBMF " + dispatchVerb(managed.stats.pct) + " (" + pct(managed.stats.pct) + ") against " + pct(spy.stats.pct) + " for SPY.";
  const gap = dispatchGap(infra,re);
  if (gap !== null) copy += " Among listed real assets, infrastructure " + (Math.abs(gap) < .005 ? "matched property." : (gap > 0 ? "led" : "trailed") + " property by " + f(Math.abs(gap)) + " percentage points.");
  const longer = dispatchGap(managed,spy,"six");
  if (longer !== null && Math.abs(longer) >= .005) copy += " Over six months, DBMF " + (longer > 0 ? "leads" : "lags") + " SPY by " + f(Math.abs(longer)) + " percentage points on price.";
  return [headline, copy];
}

function dispatchTable(rows, isYield, label) {
  const body = rows.map(r => {
    const s = r.stats, detail = [r.contract || "", shortDate(s.day)].filter(Boolean).join(" · ");
    const precision = dispatchPrecision(r);
    const target = r.yield ? 'data-rates="1"' : 'data-focus="' + esc(r.id) + '"';
    const move = r.yield ? sf(s.change,0) + " bp" : pct(s.pct);
    const trend = !Number.isFinite(s.six) ? "—" : r.yield ? sf(s.six,0) + " bp" : pct(s.six);
    const absolute = r.yield ? "" : '<small>' + sf(s.change,precision) + '</small>';
    return '<tr><th scope="row"><button ' + target + '>' + esc(r.name) + '</button><small>' + esc(detail) + '</small></th>'
      + '<td>' + f(s.last,precision) + '<small>' + esc(r.unit) + '</small></td>'
      + '<td title="' + esc(s.previous_day+" to "+s.day) + '" class="' + (r.yield ? "" : cls(s.pct)) + '">' + move + absolute + '</td>'
      + '<td title="' + esc(s.base ? s.base+" to "+s.day : "Six months of history unavailable") + '" class="' + (r.yield ? "" : cls(s.six)) + '">' + trend + '</td></tr>';
  }).join("");
  return '<div class="dispatch-tablewrap"><table class="dispatch-table" aria-label="' + esc(label) + ' closing observations"><thead><tr><th scope="col">Market</th><th scope="col">' + (isYield ? "Yield" : "Close") + '</th><th scope="col">Session</th><th scope="col">6 months</th></tr></thead><tbody>' + body + '</tbody></table></div>';
}

function marketDispatches() {
  const specs = [
    ["americas","Americas",["spx","ixic","dji","rut","tsx"],dispatchAmericas,"US and Canadian cash indices in local index points."],
    ["europe","Europe",["stoxx50","ftse"],dispatchEurope,"Euro area and UK indices in local currency. An unhedged dollar investor also has FX exposure."],
    ["asia","Asia-Pacific",["nikkei","hsi","nifty"],dispatchAsia,"Tokyo, Hong Kong and India cash indices, each at its local close."],
    ["rates","Sovereign rates",[],dispatchRates,"US nominal constant-maturity yields. Both changes are in basis points."],
    ["credit","Credit",["hyg","lqd","bkln","emb","mbb","mub"],dispatchCredit,"USD credit ETF prices exclude distributions. Credit spreads and carry require separate measures."],
    ["fx","Currencies",["dxy","eurusd","usdjpy","gbpusd","usdchf"],dispatchFx,"Spot pairs use the displayed quote order. The dollar index is quoted in index points."],
    ["commodities","Commodities",["wti","brent","natgas","copper","gold","silver","corn"],dispatchCommodities,"Vendor closes for the indicated delivery months. Six-month changes follow the same individual contract."],
    ["alternatives","Alternatives",["dbmf","vnq","igf","gld","btc"],dispatchAlternatives,"Listed funds use USD price changes. Bitcoin uses the UTC daily spot close."]
  ];
  const cards = specs.map(([id,label,ids,narrative,basis]) => {
    const isYield = id === "rates";
    const rows = isYield ? dispatchRatesRows() : ids.map(key => byId.get(key)).filter(Boolean);
    const dates = [...new Set(rows.map(r => r.stats.day))].sort();
    const dated = dates.length ? '<time datetime="' + esc(dates.at(-1)) + '">' + esc(dates.length > 1 ? shortDate(dates[0]) + " – " + dateLabel(dates.at(-1)) : dateLabel(dates[0])) + '</time>' : "";
    const [headline, copy] = narrative(rows);
    return '<article class="dispatch-card" data-dispatch="' + id + '"><header class="dispatch-label"><h3>' + label + '</h3>' + dated + '</header><h4>' + esc(headline)
      + '</h4><p class="dispatch-copy">' + esc(copy) + '</p>' + (rows.length ? dispatchTable(rows,isYield,label) : "")
      + '<p class="dispatch-note">' + esc(basis) + '</p></article>';
  }).join("");
  return '<section id="dispatches" class="dispatches" aria-labelledby="dispatch-title"><header class="dispatch-intro"><p class="eyebrow">Regional &amp; asset desks</p><h2 id="dispatch-title">Across the markets</h2><p>Local closes, the moves between them and how they fit the six-month trend.</p></header><div class="dispatch-grid">' + cards + '</div></section>';
}
