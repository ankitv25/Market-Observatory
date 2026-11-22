function validPipelineRecord(record) {
  const object=value=>value!==null && typeof value==="object" && !Array.isArray(value);
  if (!object(record) || !Array.isArray(record.recent) || !object(record.counts)) return false;
  if (Object.values(record.counts).some(n=>!Number.isInteger(n) || n<0)) return false;
  return record.recent.every(run=> {
    if (!object(run) || !Array.isArray(run.stages) || !run.stages.every(object)) return false;
    if (run.target!=null && !object(run.target)) return false;
    if (run.sources!=null && !object(run.sources)) return false;
    const sources=run.sources || {};
    return [sources.groups,sources.transport].every(group=>group==null || object(group) && Object.values(group).every(object));
  });
}
function pipelineRunKey(run) {
  return [run.kind,run.run_id || run.started,run.attempt || "1"].join("/");
}
function pipelineRepositoryLink(value) {
  return typeof value==="string" && /^https:\/\/github\.com\/ankitv25\/Market-Observatory(?:\/|$)/.test(value) ? value : "";
}
let pipelineState=validPipelineRecord(E.pipeline) ? E.pipeline : {recent:[],counts:{}};
let pipelineLiveState="Saved with this reader";
function pipelineDuration(start,end) {
  const seconds=(Date.parse(end)-Date.parse(start))/1000;
  return Number.isFinite(seconds)&&seconds>=0 ? (seconds>=60?f(seconds/60,1)+' min':f(seconds,0)+' sec') : '—';
}
function pipelinePanel() {
  const runs=pipelineState.recent || [], counts=pipelineState.counts || {};
  const lastCollection=pipelineState.last_success?.refresh || runs.find(r=>r.kind==='refresh'&&r.status==='success');
  const lastPublication=pipelineState.last_success?.pages || runs.find(r=>r.kind==='pages'&&r.status==='success');
  const cards=[['Last verified collection',lastCollection?.finished],['Last verified publication',lastPublication?.finished]];
  const schedule=Array.isArray(E.refresh?.slots)?E.refresh.slots:[];
  const rows=runs.map(run=>{
    const target=run.target || {};
    const late=Number.isFinite(target.lateness_seconds)?f(target.lateness_seconds/60,0)+' min after target':'—';
    const heading={pages:'Dashboard publication',refresh:'Data collection'}[run.kind] || 'Pipeline execution';
    const stages=(run.stages || []).map(step=>'<tr><th scope="row">'+esc(step.name)+'</th><td>'+esc(step.status)+'</td><td>'+esc(pipelineDuration(step.started,step.finished))+'</td><td>'+esc(step.error || step.reason || '')+'</td></tr>').join('');
    const source=run.sources || {};
    const groups=Object.entries(source.groups || {}).map(([name,g])=>'<tr><th scope="row">'+esc(name)+'</th><td>'+esc(g.first===g.last?g.last:g.first+' – '+g.last)+'</td><td>'+esc(g.instruments)+'</td></tr>').join('');
    const transport=Object.entries(source.transport || {}).map(([name,s])=>'<li><b>'+esc(name)+':</b> '+esc(s.outcome)+' · '+esc(freshnessTime(s.finished_at))+(s.error?' · '+esc(s.error):'')+'</li>').join('');
    const link=pipelineRepositoryLink(run.run_url)?'<a href="'+esc(run.run_url)+'">Execution record ↗</a>':'';
    return '<details class="pipeline-run" data-run-key="'+esc(pipelineRunKey(run))+'"><summary><span class="pipeline-badge '+esc(run.status)+'">'+esc(run.status)+'</span><b>'+heading+'</b><span>'+esc(freshnessTime(run.started))+'</span><span>'+esc(target.name || 'Publication check')+'</span></summary><div class="pipeline-detail">'+
      '<p>'+link+(target.at?' · Target '+esc(freshnessTime(target.at))+' · Started '+late:'')+'</p>'+
      (target.missed_slots?.length?'<p class="pipeline-warning">'+target.missed_slots.length+' earlier target(s) passed without an edition. Recovery does not reconstruct missed intraday observations.</p>':'')+
      (run.edition?'<p>Edition: '+esc(freshnessTime(run.edition))+'. Completed: '+esc(freshnessTime(run.finished))+'.</p>':'')+
      '<div class="tablebox"><table><thead><tr><th>Stage</th><th>Outcome</th><th>Elapsed</th><th>Detail</th></tr></thead><tbody>'+stages+'</tbody></table></div>'+
      (groups?'<h3>Observation dates in this run</h3><p>Expected US close: '+esc(source.expected_us_close)+' · '+esc(source.core_current)+' of '+esc(source.core_total)+' core instruments current. Treasury: '+esc(source.treasury || 'Unavailable')+' · Macro: '+esc(source.macro || 'Unavailable')+'.</p><div class="tablebox"><table><thead><tr><th>Market group</th><th>Observed range</th><th>Instruments</th></tr></thead><tbody>'+groups+'</tbody></table></div>':'')+
      (transport?'<h3>Source collection</h3><ul>'+transport+'</ul>':'')+'</div></details>';
  }).join('');
  return '<section id="pipeline-panel" class="pipeline-panel"><div class="pipeline-intro"><h2>From source to published edition</h2><p>A successful collection means the saved edition passed validation. Source observation dates determine freshness. A skipped check collected no new data.</p><p class="pipeline-live">'+esc(pipelineLiveState)+' · '+esc(freshnessTime(pipelineState.checked_at))+'</p></div>'+
    '<div class="pipeline-cards">'+cards.map(([label,value])=>'<div><span>'+label+'</span><b>'+esc(value?freshnessTime(value):'Not yet recorded')+'</b></div>').join('')+'<div><span>Recent recorded outcomes</span><b>'+esc(counts.success || 0)+' passed · '+esc(counts.failed || 0)+' failed · '+esc(counts.skipped || 0)+' skipped</b></div></div>'+
    '<div class="pipeline-schedule">'+schedule.map(slot=>'<div><b>'+esc(slot.time)+'</b><span>'+esc(slot.name)+'</span></div>').join('')+'</div><p class="pipeline-note">All targets are New York time. Weekends: 10:17. Catch-up checks are requested every 15 minutes. GitHub can delay or drop scheduled starts; missed targets remain visible. A browser can show the last saved edition while a new collection is running.</p>'+
    '<h2>Execution ledger</h2><p class="pipeline-note">Most recent '+runs.length+' recorded attempts. '+(pipelineRepositoryLink(pipelineState.archive)?'<a href="'+esc(pipelineState.archive)+'">Complete repository history ↗</a>':'The durable ledger starts with this release.')+'</p>'+ (rows || '<p class="pipeline-empty">No executions recorded by the new pipeline yet. Prior successful editions remain in the edition log.</p>')+'</section>';
}
async function checkPipeline() {
  if(!['http:','https:'].includes(location.protocol))return;
  const url=E.pipeline?.live_url;
  if(typeof url!=='string' || !url.startsWith('https://raw.githubusercontent.com/ankitv25/Market-Observatory/main/'))return;
  try {
    const response=await fetch(url+'?check='+Date.now(),{cache:'no-store'});
    if(!response.ok)throw Error('Ledger fetch failed');
    const record=await response.json();
    if(!validPipelineRecord(record) || !Number.isFinite(Date.parse(record.checked_at)))throw Error('Ledger shape invalid');
    pipelineState=record;pipelineLiveState='Checked against repository';
  } catch {pipelineLiveState='Live ledger unavailable · retaining displayed records';}
  renderFreshness();
  const panel=$('pipeline-panel');
  if(panel) {
    const open=[...panel.querySelectorAll('details[open]')].map(d=>d.dataset.runKey);
    panel.outerHTML=pipelinePanel();
    [...$('pipeline-panel').querySelectorAll('details')].forEach(d=>d.open=open.includes(d.dataset.runKey));
  }
}
if(typeof window.setInterval==='function') {
  window.setInterval(checkPipeline,300000);
  window.addEventListener('focus',checkPipeline);
  checkPipeline();
}
