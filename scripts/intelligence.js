// Interpretations and source eligibility are supplied by the versioned edition model.
let intelligenceHorizon = "daily";

function intelligenceDate(day) {
  return day && Number.isFinite(Date.parse(day)) ? dateLabel(day.slice(0,10)) : "Date unavailable";
}

function intelligenceTime(value) {
  const time=new Date(value);
  return Number.isFinite(time.valueOf()) ? time.toLocaleString("en-US",{timeZone:"America/New_York",month:"short",day:"numeric",hour:"numeric",minute:"2-digit",timeZoneName:"short"}) : "Time unavailable";
}

function intelligenceConfidence(value) {
  return Number.isFinite(value) ? Math.max(0,Math.min(100,value)) : null;
}

function intelligenceNarrative(window, intelligence) {
  const summary=window.summary || intelligence.summary || "The edition has insufficient evidence for a cross-market assessment.";
  const previous=window.previous;
  const transition=window.transition || (previous?.regime ? 'The preceding '+window.sessions+'-session window was '+previous.regime+'.' : "");
  const previousInterval=previous?.start && previous?.end ? 'Previous window '+intelligenceDate(previous.start)+' – '+intelligenceDate(previous.end) : '';
  const dateRange=window.start && window.end ? intelligenceDate(window.start)+' – '+intelligenceDate(window.end) : intelligenceDate(intelligence.asof);
  return '<div class="intel-narrative"><span class="intel-horizon-label">'+esc(window.label || window.id)+' · '+esc(dateRange)+'</span>'+
    '<h3>'+esc(window.regime || intelligence.regime || "Awaiting assessment")+'</h3>'+
    '<div class="intel-summary"><p>'+esc(summary)+'</p>'+(transition?'<p class="intel-transition">'+esc(transition)+(previousInterval?'<span>'+esc(previousInterval)+'</span>':'')+'</p>':"")+'</div></div>';
}

function intelligenceConfidencePanel(window, intelligence) {
  const confidence=intelligenceConfidence(window.confidence), coverage=window.coverage || {};
  const count=Number.isFinite(coverage.eligible)&&Number.isFinite(coverage.total)?coverage.eligible+' of '+coverage.total+' signals eligible':"Signal coverage unavailable";
  const strength=confidence==null?"Unavailable":f(confidence,0)+' / 100';
  const note="A rule-based score combining signal agreement with eligible source coverage.";
  return '<aside class="intel-confidence"><h4>Heuristic confidence</h4><div class="intel-confidence-row"><strong>'+esc(strength)+'</strong></div>'+
    '<div class="intel-meter" aria-hidden="true"><i style="width:'+(confidence??0)+'%"></i></div><p>'+esc(note)+'</p><p class="intel-coverage">'+esc(count)+'</p></aside>';
}

function intelligenceEvidence(window) {
  const eligible=(window.evidence || []).filter(row=>row.status==="included");
  const direction=Math.sign(window.score || 0);
  const supporting=eligible.filter(row=>direction===0?row.vote===0:Math.sign(row.vote)===direction).slice(0,3);
  const opposing=window.conflicts || [];
  const evidence=supporting.map(row=>'<li><strong>'+esc(row.label)+'.</strong> '+esc(row.detail || row.reading || "")+'</li>').join("");
  const conflict=opposing.slice(0,3).map(row=>'<li>'+esc(row)+'</li>').join("");
  const supportEmpty=direction===0 ? 'The composite contains offsetting signals. Review their individual readings below.' : 'The eligible set supplies too little agreement for a directional confirmation.';
  const conflictEmpty=eligible.length?'The eligible directional signals contain no opposing vote in this window.':'No eligible signals are available to test the assessment.';
  return '<div class="intel-evidence"><div><h4>Evidence behind the view</h4><ul>'+(evidence || '<li>'+esc(supportEmpty)+'</li>')+'</ul></div>'+
    '<div class="intel-conflicts"><h4>What challenges the view</h4><ul>'+(conflict || '<li>'+esc(conflictEmpty)+'</li>')+'</ul></div></div>';
}

function intelligenceDrivers(intelligence) {
  const drivers=intelligence.drivers || [];
  return drivers.length ? '<div class="intel-drivers"><h4>Latest session: possible market drivers</h4><p class="intel-driver-note">Price evidence suggests hypotheses. Economic releases and funding data are needed to establish the cause.</p><div>'+drivers.map(driver=>'<article><span class="intel-horizon-label">'+esc(driver.status)+'</span><h4>'+esc(driver.title)+'</h4><p>'+esc(driver.evidence)+'</p><p><strong>Confirmation to seek.</strong> '+esc(driver.confirmation)+'</p></article>').join('')+'</div></div>' : '';
}

function intelligenceConsiderations(intelligence) {
  const views=intelligence.considerations || [];
  if (!views.length) return "";
  return '<div class="intel-considerations">'+views.map(view=>'<div><span class="intel-horizon-label">'+esc(view.horizon)+' considerations</span><h4>'+esc(view.title)+'</h4><p>'+esc(view.text)+'</p></div>').join("")+'</div>';
}

function intelligenceTriggers(intelligence) {
  const rows=intelligence.watchlist || [];
  if (!rows.length) return "";
  return '<div class="intel-triggers"><h4>What would change the assessment</h4><ul>'+rows.map(row=>'<li><strong>'+esc(row.label)+'.</strong> '+esc(row.condition)+' '+esc(row.why)+'</li>').join("")+'</ul></div>';
}

function intelligenceSignalAudit(window, intelligence) {
  const rows=window.evidence || [], method=intelligence.methodology || {};
  const body=rows.map(row=>{
    const sources=(row.inputs || []).map(input=>{
      const label=esc(input.name || input.id);
      const text=/^https:\/\//.test(input.source || "")?'<a href="'+esc(input.source)+'">'+label+'</a>':label;
      return text+' · '+esc(intelligenceDate(input.day))+(input.source && !/^https:\/\//.test(input.source)?' · '+esc(input.source):'');
    }).join('<br>');
    return '<tr><th scope="row">'+esc(row.label)+'</th><td>'+esc(row.status==="included"?row.reading:"Excluded")+'</td>'+
      '<td class="intel-dated">'+esc(row.start || "—")+'<br>'+esc(row.end || "—")+'</td><td>'+esc(row.status==="included"?row.detail:row.reason || "Unavailable")+
      (sources?'<span class="intel-signal-sources">'+sources+'</span>':'')+'</td></tr>';
  }).join("");
  const thresholds=(method.thresholds || []).map(row=>'<tr><th scope="row">'+esc(row.signal)+'</th><td>'+esc(row.daily)+' '+esc(row.unit)+'</td><td>'+esc(row.scaling)+'</td></tr>').join("");
  const rules=(method.rules || []).map(rule=>'<li>'+esc(rule)+'</li>').join("");
  return '<details class="intel-audit" data-intelligence-detail="signals"><summary>Inspect the six-signal assessment</summary><div class="intel-audit-body">'+
    '<div class="intel-scroll"><table><thead><tr><th>Signal</th><th>Reading</th><th>Return interval</th><th>Observation and source</th></tr></thead><tbody>'+body+'</tbody></table></div>'+
    (method.title?'<h4 class="intel-method-title">'+esc(method.title)+'</h4>':"")+(method.confidence_note?'<p>'+esc(method.confidence_note)+'</p>':"")+(rules?'<ul class="intel-rules">'+rules+'</ul>':"")+(thresholds?'<div class="intel-scroll intel-thresholds"><table><thead><tr><th>Signal</th><th>Daily cutoff</th><th>Horizon treatment</th></tr></thead><tbody>'+thresholds+'</tbody></table></div>':'')+'</div></details>';
}

function intelligenceContext(intelligence) {
  const contexts=intelligence.context || [];
  if (!contexts.length) return "";
  return '<details class="intel-audit" data-intelligence-detail="context"><summary>Policy, rates and cross-market context</summary><div class="intel-audit-body intel-context-grid">'+
    contexts.map(row=>'<article><div class="intel-context-meta"><h4>'+esc(row.label)+'</h4><span>'+esc(row.status)+' · '+esc(intelligenceDate(row.date))+'</span></div>'+
      '<b>'+esc(row.title)+'</b>'+((row.metrics || []).length?'<dl class="intel-metrics">'+row.metrics.map(metric=>'<div><dt>'+esc(metric.label)+'</dt><dd>'+f(metric.value,2)+' '+esc(metric.unit)+'</dd></div>').join('')+'</dl>':'')+'<p>'+esc(row.detail || "Awaiting source")+'</p>'+(row.reason?'<p class="intel-context-reason">'+esc(row.reason)+'</p>':'')+'</article>').join("")+'</div></details>';
}

function intelligenceSourceAudit(intelligence) {
  const sources=intelligence.sources || [];
  const excluded=sources.filter(row=>!row.used_in_score).length;
  const stale=sources.filter(row=>row.status==="stale").length;
  const unavailable=sources.filter(row=>["missing","future"].includes(row.status)).length;
  const freshness=[stale?stale+" stale":null,unavailable?unavailable+" unavailable":null,excluded+" outside score"].filter(Boolean).join(" · ");
  const body=sources.map(row=>'<tr><th scope="row">'+esc(row.name || row.id)+(row.source?'<span class="intel-signal-sources">'+esc(row.source)+'</span>':'')+'</th><td class="intel-dated">'+esc(row.date || "—")+'</td>'+
    '<td>'+esc(row.status || "Unavailable")+'</td><td>'+esc(row.used_in_score?"Scored":"Context / excluded")+'</td><td>'+esc(row.reason || "")+'</td></tr>').join("");
  const gaps=(intelligence.gaps || []).map(item=>'<li>'+esc(item)+'</li>').join("");
  return '<details class="intel-audit" data-intelligence-detail="sources"><summary>Source freshness &amp; exclusions <span>'+esc(freshness)+'</span></summary>'+
    '<div class="intel-audit-body"><div class="intel-scroll"><table><thead><tr><th>Source</th><th>Observed</th><th>Freshness</th><th>Role</th><th>Reason</th></tr></thead><tbody>'+body+'</tbody></table></div>'+
    (gaps?'<h4 class="intel-method-title">Coverage gaps</h4><ul class="intel-rules">'+gaps+'</ul>':"")+'</div></details>';
}

function marketIntelligence() {
  const intelligence=E.intelligence;
  if (!intelligence?.windows?.length) return '';
  const expected=readerExpectedClose(new Date());
  const historical=intelligence.asof && expected && intelligence.asof<expected;
  const ageNote=historical?'<p class="intel-age-warning">Historical assessment: the expected '+esc(expected)+' close is newer than this saved assessment. Use the refresh ledger to check for a delayed edition.</p>':'';
  const window=intelligence.windows.find(row=>row.id===intelligenceHorizon)||intelligence.windows[0];
  const controls=intelligence.windows.map(row=>'<button type="button" data-intelligence-horizon="'+esc(row.id)+'" aria-pressed="'+(row.id===window.id)+'">'+esc(row.label || row.id)+'</button>').join("");
  return '<section class="intel-panel" id="market-intelligence" aria-label="Market intelligence"><div class="intel-topline"><h2>Market intelligence</h2>'+
    '<p>Assessment as of '+esc(intelligenceDate(intelligence.asof))+'</p></div><div class="intel-tabs" aria-label="Assessment horizon">'+controls+'</div>'+
    ageNote+'<div class="intel-main">'+intelligenceNarrative(window,intelligence)+intelligenceConfidencePanel(window,intelligence)+'</div>'+intelligenceEvidence(window)+
    intelligenceDrivers(intelligence)+intelligenceConsiderations(intelligence)+intelligenceTriggers(intelligence)+intelligenceSignalAudit(window,intelligence)+intelligenceContext(intelligence)+intelligenceSourceAudit(intelligence)+'</section>';
}

function intelligenceHistory() {
  const intelligence=E.intelligence;
  if (!intelligence) return "";
  const rows=(intelligence.history || []).filter(row=>row.created && row.asof).slice().sort((a,b)=>b.created.localeCompare(a.created)).slice(0,10);
  const body=rows.map((row,i)=>{
    const archive=typeof row.archive==="string" && /^editions\/[a-zA-Z0-9._/-]+\.json$/.test(row.archive) && !row.archive.includes("..");
    const date=esc(intelligenceTime(row.created));
    const publication=archive?'<a href="'+repo+'/blob/main/'+esc(row.archive)+'">'+date+' ↗</a>':date;
    const repeated=rows[i+1]?.asof===row.asof;
    return '<tr><th scope="row">'+publication+'<span class="intel-history-session">'+esc(row.asof)+(repeated?' · same-session update':' · market session')+'</span></th>'+
      '<td>'+esc(row.regime || "Unavailable")+'</td><td>'+esc(Number.isFinite(row.confidence)?f(row.confidence,0)+' / 100':"—")+'</td><td class="intel-story">'+esc(row.summary || "")+'</td></tr>';
  }).join("");
  return '<section class="intel-history" id="intelligence-history"><div class="intel-history-title"><h2>How the assessment has evolved</h2><p>Archived at publication</p></div>'+
    (rows.length?'<div class="intel-scroll"><table><thead><tr><th>Edition / market session</th><th>Regime</th><th>Evidence confidence</th><th>Published assessment</th></tr></thead><tbody>'+body+'</tbody></table></div>':'<p>The assessment history starts with the first published intelligence edition.</p>')+
    '<p>Each row preserves that edition’s assessment and inputs. Evidence confidence uses the edition’s heuristic agreement and coverage measure.</p></section>';
}

function handleIntelligenceControl(event) {
  const button=event.target.closest('button[data-intelligence-horizon]');
  if (!button || !E.intelligence?.windows?.some(row=>row.id===button.dataset.intelligenceHorizon)) return false;
  const panel=$("market-intelligence");
  if (!panel) return false;
  const expanded=[...panel.querySelectorAll('details[open]')].map(row=>row.dataset.intelligenceDetail);
  intelligenceHorizon=button.dataset.intelligenceHorizon;
  panel.outerHTML=marketIntelligence();
  for (const detail of $("market-intelligence").querySelectorAll("details")) detail.open=expanded.includes(detail.dataset.intelligenceDetail);
  [...$("market-intelligence").querySelectorAll("button[data-intelligence-horizon]")].find(row=>row.dataset.intelligenceHorizon===intelligenceHorizon)?.focus({preventScroll:true});
  return true;
}
