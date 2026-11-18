function freshnessTime(value) {
  const date = new Date(value);
  return Number.isFinite(date.valueOf()) ? date.toLocaleString("en-US", {
    timeZone:"America/New_York", month:"short", day:"numeric", hour:"numeric",
    minute:"2-digit", timeZoneName:"short"
  }) : "Unavailable";
}
function freshness(now = new Date()) {
  const schedule = E.refresh;
  if (!schedule) return '';
  const instants = schedule.targets.map(t=>new Date(t));
  const due = instants.filter(t=>t<=now).at(-1);
  const next = instants.find(t=>t>now);
  const missed = due && Date.parse(E.created)<due.valueOf();
  const delayed = missed && now-due>3600000;
  const close = byId.get("spx")?.stats.day;
  const ny = new Intl.DateTimeFormat("en-CA", {timeZone:"America/New_York",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",hourCycle:"h23",minute:"2-digit",weekday:"short"}).formatToParts(now);
  const parts=Object.fromEntries(ny.map(p=>[p.type,p.value]));
  const today=parts.year+"-"+parts.month+"-"+parts.day;
  const awaitingClose=close && close<today && !["Sat","Sun"].includes(parts.weekday) && (Number(parts.hour)>16 || (Number(parts.hour)===16 && Number(parts.minute)>=17));
  const label = awaitingClose ? "Awaiting newer US close" : delayed ? "Refresh overdue" : missed ? "Refresh due" : "Collected";
  const families = [
    ["US equities", markets.filter(r=>r.group==="Indices").map(r=>r.stats.day)],
    ["Global equities", markets.filter(r=>r.group==="Global").map(r=>r.stats.day)],
    ["FX & futures", markets.filter(r=>["FX","Futures"].includes(r.group)).map(r=>r.stats.day)],
    ["Treasury yields", [curves.at(-1)?.date]],
    ["Portfolio NAV", Object.values(E.books||{}).map(b=>b.live?.date)],
    ["Confirmed macro", [E.macro?.date]]
  ];
  const dates = families.map(([name,days])=>{
    const sorted=days.filter(Boolean).sort();
    const range=sorted.length ? sorted[0]===sorted.at(-1) ? dateLabel(sorted[0]) : shortDate(sorted[0])+" – "+dateLabel(sorted.at(-1)) : "Awaiting source";
    return '<tr><th scope="row">'+name+'</th><td>'+esc(range)+'</td></tr>';
  }).join("");
  const history=schedule.recent.map(r=>'<li><span>'+esc(freshnessTime(r.created))+'</span><span>'+r.notes+' source notes</span>'+
    (r.url?'<a href="'+esc(r.url)+'">Run ↗</a>':'<span>Local refresh</span>')+'</li>').join("");
  return '<details id="cadence-details" class="freshness '+(delayed||awaitingClose?'overdue':'')+'"><summary><span><i aria-hidden="true"></i><b>'+label+'</b> '+esc(freshnessTime(E.created))+
    ' · US close '+esc(close?shortDate(close):'unavailable')+'</span><span>'+(missed?'Target was '+freshnessTime(due):next?'Next target '+freshnessTime(next):'See daily schedule')+' <b class="freshness-more">Cadence &amp; sources ▾</b></span></summary>'+
    '<div class="freshness-body"><div><h3>Automatic daily refresh</h3><p>Weekdays at <b>'+esc(schedule.weekdays.join(", "))+'</b>. Weekends at <b>'+esc(schedule.weekends.join(", "))+
    '</b>. All times America/New_York, with daylight saving changes.</p><p>Checks every 15 minutes retry missed targets. Delayed US closing prices are retried hourly. Exchange holidays can retain the preceding close. GitHub may delay starts. The reader checks for a newer edition every five minutes and loads it automatically.</p><p>Price tables use completed vendor daily bars. Portfolio valuations and the monthly macro model keep their own source dates.</p>'+
    '<a href="'+esc(schedule.workflow)+'">Refresh runs ↗</a> · <a href="'+repo+'/blob/main/CADENCE.md">Full edition ledger ↗</a></div>'+
    '<div><h3>Observation dates</h3><table>'+dates+'</table></div><div><h3>Recent refreshes</h3><ul>'+history+'</ul></div></div></details>';
}
function renderFreshness() {
  const open=$("cadence-details")?.open;
  $("freshness").innerHTML=freshness();
  if($("cadence-details"))$("cadence-details").open=Boolean(open);
}
async function checkNewEdition() {
  if (!["http:","https:"].includes(location.protocol)) return;
  try {
    const response=await fetch("status.json?check="+Date.now(), {cache:"no-store"});
    if (!response.ok) return;
    const status=await response.json();
    if (Date.parse(status.created)>Date.parse(E.created)) {
      try {sessionStorage.setItem("observatory-book",book)} catch {}
      const destination=new URL(location.href);
      destination.searchParams.set("edition",status.created);
      location.replace(destination.href);
    }
  } catch {}
}
if(typeof window.setInterval==="function") {
  try {
    const saved=sessionStorage.getItem("observatory-book");
    if(Object.hasOwn(E.books||{},saved))book=saved;
  } catch {}
  window.setInterval(renderFreshness,60000);
  window.setInterval(checkNewEdition,300000);
  window.addEventListener("focus",checkNewEdition);
  document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")checkNewEdition()});
  checkNewEdition();
}
