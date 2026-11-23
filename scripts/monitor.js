"use strict";
const E=JSON.parse(document.getElementById("data").textContent), markets=E.markets;
const byId=new Map(markets.map(r=>[r.id,r])), bySymbol=new Map(markets.map(r=>[r.symbol,r]));
const sectors=markets.filter(r=>r.group==="Sectors"), curves=E.curve.rows || [];
const $=id=>document.getElementById(id);
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const f=(v,d=2)=>Number.isFinite(v)?v.toLocaleString("en-US",{minimumFractionDigits:d,maximumFractionDigits:d}):"—";
const sf=(v,d=2)=>Number.isFinite(v)?(v>=0?"+":"−")+f(Math.abs(v),d):"—";
const pct=v=>Number.isFinite(v)?sf(v)+"%":"—";
const cls=v=>v==null?"":v<0?"down":"up";
const dateLabel=s=>new Date(s.slice(0,10)+"T12:00:00Z").toLocaleDateString("en-US",{month:"short",day:"numeric",year:"numeric",timeZone:"UTC"});
const colors=["#79e5c1","#a3baff","#eac478"];
const chartState={primary:"spx",comparison:"rsp",months:6};
const repo="https://github.com/ankitv25/Market-Observatory";
let sectorWindow="pct",book="saa",filter="",group="",sort="name";
const views={
 overview:["Market overview","Closing levels, market leadership and cross-asset confirmation."],
 markets:["Cross-asset tape","Compare prices, changes and six-month trends across the covered universe."],
 rates:["Rates & macro","Treasury curve changes and the evidence behind the confirmed macro regime."],
 portfolio:["Portfolio monitor","Performance, attribution and risk across the published portfolio books."],
 pipeline:["Refresh & reliability","Every collection, validation and publication attempt, with observed source dates."],
 research:["Research desk","Daily observations, sector sensitivities and the sources behind this edition."]};
const labels={overview:"Overview",markets:"Market tape",rates:"Rates & macro",portfolio:"Portfolio monitor",research:"Research desk",pipeline:"Refresh & reliability"};
function section(title,sub,body,control=""){return '<section class="card"><div class="head"><div><h2>'+esc(title)+'</h2><p class="sub">'+esc(sub)+'</p></div>'+control+'</div>'+body+'</section>'}
function option(v,t,selected){return '<option value="'+esc(v)+'" '+(selected===v?'selected':'')+'>'+esc(t)+'</option>'}
function segments(values,active,attribute){return '<div class="seg">'+values.map(([value,label])=>'<button '+attribute+'="'+value+'" class="'+(active==value?'on':'')+'" aria-pressed="'+(active==value)+'">'+label+'</button>').join("")+'</div>'}
function dots(text,color){return '<span><i style="background:'+color+'"></i>'+esc(text)+'</span>'}
function xy(values,w,h){let lo=Math.min(...values),range=Math.max(...values)-lo||1;return values.map((v,i)=>(i*w/Math.max(1,values.length-1)).toFixed(1)+','+(h-2-(h-4)*(v-lo)/range).toFixed(1)).join(" ")}
function spark(row){const values=row.history.slice(-22).map(h=>h[1]);return '<svg role="img" aria-label="Last 22 observations" class="spark" viewBox="0 0 85 36" preserveAspectRatio="none"><polyline fill="none" stroke="'+(values.at(-1)>=values[0]?'#269780':'#b75c55')+'" stroke-width="1.8" points="'+xy(values,85,36)+'"/></svg>'}
function relativeChart(){
 const p=byId.get(chartState.primary), q=byId.get(chartState.comparison);
 const end=new Date(p.stats.day+"T00:00:00Z"),cut=new Date(end);
 cut.setUTCDate(1);cut.setUTCMonth(cut.getUTCMonth()-chartState.months);
 const maxDay=new Date(Date.UTC(cut.getUTCFullYear(),cut.getUTCMonth()+1,0)).getUTCDate();
 cut.setUTCDate(Math.min(end.getUTCDate(),maxDay));
 const qValues=new Map(q?.history||[]),endDate=cut.toISOString().slice(0,10);
 const pairs=p.history.filter(([d,v])=>d>=endDate && (!q||qValues.has(d)));
 const head='<div class="head"><div><p class="eyebrow">Price performance</p><h2>Benchmark comparison</h2></div>'+segments([[1,"1M"],[3,"3M"],[6,"6M"],[12,"1Y"]],chartState.months,"data-months")+'</div>';
 const selections='<div class="tools"><select aria-label="Primary instrument" id="primary">'+markets.map(r=>option(r.id,r.name,chartState.primary)).join("")+'</select><select aria-label="Comparison instrument" id="comparison">'+option("","No comparison",chartState.comparison)+markets.filter(r=>r.id!==p.id).map(r=>option(r.id,r.name,chartState.comparison)).join("")+'</select></div>';
 if(pairs.length<2||pairs[0][1]<=0||(q&&qValues.get(pairs[0][0])<=0))return '<section class="card dark" id="comparisonPanel">'+head+selections+'<p class="empty">Insufficient overlapping history to rebase this pair.</p></section>';
 const series=[pairs.map(pair=>100*(pair[1]/pairs[0][1]-1))];
 if(q)series.push(pairs.map(([d])=>100*(qValues.get(d)/qValues.get(pairs[0][0])-1)));
 const lo=Math.min(0,...series.flat()),hi=Math.max(0,...series.flat()),pad=Math.max(.1,(hi-lo)*.1);
 const bottom=lo-pad,top=hi+pad,X=i=>52+572*(Date.parse(pairs[i][0])-Date.parse(pairs[0][0]))/(Date.parse(pairs.at(-1)[0])-Date.parse(pairs[0][0])),Y=v=>170-153*(v-bottom)/(top-bottom);
 let svg='';
 for(let i=0;i<5;i++){let val=bottom+(top-bottom)*i/4,y=Y(val);svg+='<path d="M50 '+y+' H626" stroke="#496076" stroke-width=".7"/><text x="43" y="'+(y+4)+'" text-anchor="end" fill="#b4c6d7">'+sf(val,1)+'%</text>'}
 series.forEach((arr,n)=>{const path=arr.map((v,i)=>(i?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1)).join(" ");
 if(n===0)svg+='<path d="'+path+' L'+X(arr.length-1)+' 170 L52 170 Z" fill="#72dfc1" opacity=".065"/>';
 svg+='<path d="'+path+'" fill="none" stroke="'+colors[n]+'" stroke-width="2.6"/><circle cx="'+X(arr.length-1)+'" cy="'+Y(arr.at(-1))+'" r="3" fill="'+colors[n]+'"/>'});
 for(let i=0;i<4;i++){let j=Math.round(i*(pairs.length-1)/3);svg+='<text x="'+X(j)+'" y="194" fill="#b4c6d7" text-anchor="'+(i===0?'start':i===3?'end':'middle')+'">'+esc(pairs[j][0].slice(5))+'</text>'}
 window.plotPoints=pairs.map(([d],i)=>({d,x:X(i),values:series.map(a=>a[i])}));
 return '<section class="card dark" id="comparisonPanel">'+head+selections+'<div class="legend" style="margin:12px 0 2px">'+dots(p.name+' '+pct(series[0].at(-1)),colors[0])+(q?dots(q.name+' '+pct(series[1].at(-1)),colors[1]):'')+'</div><svg role="img" aria-label="Cumulative percentage price changes over common observations" id="comparisonChart" class="chart" viewBox="0 0 650 201">'+svg+'<line id="cross" stroke="#d5e6f1" y1="12" y2="170" stroke-dasharray="3 3" visibility="hidden"/></svg><div id="hover" class="chartHelp">Rebased at '+esc(pairs[0][0])+' · through '+esc(pairs.at(-1)[0])+'</div></section>';
}
function curvePanel(){
 const c=curves.at(-1),p=curves.at(-2),targetDate=c?Date.parse(c.date)-30*864e5:0,old=curves.filter(r=>Date.parse(r.date)<=targetDate).at(-1);
 if(!c||!p)return section("Treasury curve","","Awaiting observations.");
 const tenors=["1M","3M","6M","1Y","2Y","3Y","5Y","7Y","10Y","20Y","30Y"].filter(k=>c.rates[k]!=null);
 const series=[c,old].filter(Boolean),values=series.flatMap(r=>tenors.map(k=>r.rates[k]).filter(Number.isFinite)),lo=Math.min(...values)-.08,hi=Math.max(...values)+.08;
 const X=i=>45+470*i/(tenors.length-1),Y=v=>125-(v-lo)*108/(hi-lo);
 let svg='';for(let i=0;i<4;i++){let v=lo+(hi-lo)*i/3;svg+='<path d="M41 '+Y(v)+' H518" stroke="#dce5ed"/><text x="35" y="'+(Y(v)+3)+'" text-anchor="end" fill="#64798b">'+f(v,2)+'</text>'}
 series.forEach((r,j)=>{let arr=tenors.map((k,i)=>[i,r.rates[k]]).filter(a=>Number.isFinite(a[1]));svg+='<path fill="none" stroke="'+(j?'#8b9fb3':'#2562b6')+'" stroke-width="'+(j?2:3)+'" stroke-dasharray="'+(j?'4 4':'none')+'" d="'+arr.map(([i,v],k)=>(k?'L':'M')+X(i)+' '+Y(v)).join(' ')+'"/>'});
 tenors.forEach((k,i)=>svg+='<text x="'+X(i)+'" y="147" fill="#52677c" text-anchor="middle">'+k+'</text>');
 return section("Treasury curve","Nominal yield (%) · equally spaced maturities",'<svg role="img" aria-label="US yield curve and previous month" class="chart" viewBox="0 0 550 155">'+svg+'</svg><div class="legend">'+dots(c.date,'#2562b6')+(old?dots(old.date,'#8b9fb3'):'')+'</div>', '<a class="link" href="#rates">Rates desk ↗</a>');
}
function regimePanel(){const m=E.macro||{},pillars=Object.entries(m.pillars||{});
 return section("Macro regime",m.source||"Confirmed monthly score",'<div class="spread"><b class="chartValue">'+esc(m.regime||"—")+'</b><span class="pill">'+sf(m.score,2)+' z</span></div><p class="note">'+esc(m.note||"")+'</p><div class="bars" style="margin-top:14px">'+pillars.map(([k,v])=>'<div class="barrow"><span>'+esc(k[0].toUpperCase()+k.slice(1))+'</span><div class="track"><i style="width:'+Math.min(100,Math.abs(v)*40)+'%;background:'+(v>=0?'#188674':'#b66558')+'"></i></div><b>'+sf(v,2)+'</b></div>').join('')+'</div><div class="mini" style="margin-top:10px">Scored through '+esc(m.date||"—")+'</div>','<a class="link" href="https://ankitv25.github.io/Macro-Regime-Score/">MRS ↗</a>')}
const marketDesks = [
 {name:"Equities", label:"S&P 500", id:"spx", companion:"rut", detail:"equities", color:"#5356a5"},
 {name:"Rates", label:"US 10-year", id:"yield10", companion:"yield2", detail:"sovereign-rates", color:"#368397"},
 {name:"Credit", label:"IG corporates", id:"lqd", companion:"hyg", detail:"credit", color:"#597f73"},
 {name:"FX", label:"Dollar index", id:"dxy", companion:"usdjpy", detail:"fx-and-global-sessions", color:"#ac7851"},
 {name:"Commodities", label:"WTI crude", id:"wti", companion:"gold", detail:"commodities-and-futures", color:"#9d6960"},
 {name:"Alternatives", label:"Listed property", id:"vnq", companion:"dbmf", detail:"alternatives-and-real-estate", color:"#856a93"}
];
const regions = {
 "Americas":["spx","ixic","dji","rut","tsx"],
 "Europe":["stoxx50","ftse"],
 "Asia":["nikkei","hsi","nifty"]
};
let moversSide="gainers",region="Americas";
const deskGroups={equities:"Indices",credit:"Credit","fx-and-global-sessions":"FX","commodities-and-futures":"Futures","alternatives-and-real-estate":"Alternatives"};

function shortDate(day) {
 return new Date(day+"T12:00:00Z").toLocaleDateString("en-US",{month:"short",day:"numeric",timeZone:"UTC"});
}
function marketQuote(id) {
 if (!id.startsWith("yield")) return byId.get(id);
 const tenor=id==="yield10"?"10Y":"2Y";
 const observations=curves.filter(c=>Number.isFinite(c.rates[tenor]));
 if(observations.length<2)return null;
 const current=observations.at(-1), prior=observations.at(-2);
 return {id,symbol:tenor,name:"US "+tenor+" Treasury",unit:"%",history:observations.map(c=>[c.date,c.rates[tenor]]),
  stats:{day:current.date,last:current.rates[tenor],change:100*(current.rates[tenor]-prior.rates[tenor])},yield:true};
}
function quoteTarget(row){
 return row.yield?'data-rates="1"':'data-focus="'+esc(row.id)+'"';
}
function dailyMove(row){
 if(row.yield)return sf(row.stats.change,0)+" bp";
 return sf(row.stats.change,dispatchPrecision(row))+" "+row.unit;
}
function quoteStrip(){
 const quotes=["spx","dji","ixic","rut","yield10","vix","wti","btc"].map(marketQuote).filter(Boolean).map(row=>{
  const quote=row.session_quote;
  return quote && quote.day>row.stats.day ? {...row,stats:{...row.stats,...quote},intraday:true} : row;
 });
 return '<div class="quotes" role="region" aria-label="Benchmark closes">'+quotes.map(r=>
  '<button class="quote" '+quoteTarget(r)+' title="'+esc(r.name+' · '+r.stats.day)+'"><span>'+esc(r.name)+'</span><b>'+
  f(r.stats.last)+(r.yield?"%":"")+'</b><small class="'+cls(r.stats.change)+'">'+dailyMove(r)+(r.yield?'':' · '+pct(r.stats.pct))+'</small><time>'+ (r.intraday?esc(freshnessTime(r.stats.observed_at))+' · quote':shortDate(r.stats.day)+' close')+'</time></button>').join("")+'</div>';
}
function leadChart(row){
 const history=row.history.slice(-22), values=history.map(p=>p[1]), path=xy(values,320,62);
 return '<figure class="close-figure"><figcaption><b>'+esc(row.name)+'</b><span>'+history.length+' closes</span></figcaption>'+
  '<svg viewBox="0 0 320 66" preserveAspectRatio="none" role="img" aria-label="'+esc(row.name+' closing levels across '+history.length+' observations')+'">'+
  '<path d="M0 20H320 M0 44H320" stroke="#486b60" stroke-dasharray="2 4"/>'+
  '<polygon points="0,66 '+path+' 320,66" fill="#659e85" opacity=".15"/><polyline points="'+path+'" stroke="#9ee6c5" stroke-width="2.3" fill="none"/></svg>'+
  '<div><span>'+shortDate(history[0][0])+'</span><span>'+shortDate(history.at(-1)[0])+' · '+f(values.at(-1),dispatchPrecision(row))+' '+esc(row.unit)+'</span></div></figure>';
}
function marketLead(){
 const sp=byId.get("spx"), session=sp.stats;
 const featured=pulsePicks.find(p=>p.row.stats.day===session.day)?.row || sp;
 const winners=sectors.filter(r=>dispatchPeriodsMatch(r,sp) && r.stats.pct>0);
 const covered=sectors.filter(r=>dispatchPeriodsMatch(r,sp)).length;
 const headline=featured.yield ?
  featured.name+' yield '+(featured.stats.change===0?'holds at '+f(featured.stats.last)+'%':(featured.stats.change>0?'rises ':'falls ')+f(Math.abs(featured.stats.change),0)+' bp') :
  featured.name+(featured.group==='Credit'?' ETF':'')+(featured.stats.change===0?' finishes flat':(featured.stats.change>0?' rises ':' falls ')+f(Math.abs(featured.stats.pct))+'%');

 const close='The S&P 500 closed at '+f(session.last)+', '+sf(session.change)+' points ('+pct(session.pct)+') on '+shortDate(session.day)+'.';
 const breadth=covered?' '+winners.length+' of '+covered+' US sectors advanced.':'';
 const subtitle=featured.id===sp?close+breadth:
  (featured.yield?'The yield finished at '+f(featured.stats.last)+'%. ':featured.name+' closed at '+dispatchPoint(featured)+', '+dailyMove(featured)+' on the session. ')+close+breadth;
 return '<section class="lead"><div><div class="lead-date">THE MARKET CLOSE <span>'+esc(dateLabel(featured.stats.day))+'</span></div><h1>'+esc(headline)+'</h1>'+
  '<p>'+esc(subtitle)+'</p></div>'+leadChart(featured)+'</section>';
}
function deskTable(){
 const lines=marketDesks.map(d=>{
  const r=marketQuote(d.id),other=marketQuote(d.companion);
  if(!r)return '<tr><td>'+esc(d.name)+'</td><td colspan="5">Awaiting observation</td></tr>';
  const compare=other?'<span>'+esc(other.name)+' '+(other.yield?f(other.stats.last)+'%':pct(other.stats.pct))+' · '+shortDate(other.stats.day)+'</span>':'';
  return '<tr><td><a class="desk-link" style="--desk:'+d.color+'" href="'+(d.id==="yield10"?"#rates":"#markets")+'" data-desk="'+esc(d.detail)+'">'+d.name+'</a></td><td><button '+quoteTarget(r)+'>'+d.label+'</button><span>'+esc(r.contract||r.symbol)+' · '+shortDate(r.stats.day)+'</span></td>'+
   '<td class="desk-level">'+f(r.stats.last)+(r.yield?'%':'')+'<span>'+esc(r.yield?'par yield':r.unit)+'</span></td><td class="desk-move '+cls(r.stats.change)+'"><b>'+(r.yield?dailyMove(r):pct(r.stats.pct))+'</b>'+
   (r.yield?'':'<span>'+dailyMove(r)+'</span>')+'</td><td class="desk-trend">'+spark(r)+'</td><td class="desk-peer">'+compare+'</td></tr>';
 }).join('');
 return '<section class="home-panel desk-panel"><div class="panel-head"><h2>Cross-asset board</h2><a href="#markets">Full tape ↗</a></div>'+
 '<table class="desk-table"><thead><tr><th>Desk</th><th>Benchmark</th><th>Last</th><th>1 day</th><th class="desk-trend">22 closes</th><th class="desk-peer">Also watching</th></tr></thead><tbody>'+lines+'</tbody></table></section>';
}
function movers(){
 const session=byId.get("spx").stats, increasing=moversSide==="gainers";
 const eligible=markets.filter(r=>r.stats.day===session.day && r.stats.previous_day===session.previous_day && Number.isFinite(r.stats.pct));
 const ranked=eligible.filter(r=>increasing?r.stats.pct>0:r.stats.pct<0)
  .sort((a,b)=>increasing?b.stats.pct-a.stats.pct:a.stats.pct-b.stats.pct).slice(0,5);
 const rows=ranked.map((r,i)=>'<li><span class="rank">'+String(i+1).padStart(2,"0")+'</span><button data-focus="'+r.id+'"><b>'+esc(r.name)+'</b><small>'+f(r.stats.last,dispatchPrecision(r))+' '+esc(r.unit)+'</small></button><div class="mover-change"><strong class="'+cls(r.stats.pct)+'">'+pct(r.stats.pct)+'</strong><small>'+dailyMove(r)+'</small></div></li>').join("");
 return '<section class="home-panel movers-panel"><div class="panel-head"><h2>Market movers</h2></div><div class="mover-tabs">'+segments([["gainers","Gainers"],["decliners","Decliners"]],moversSide,"data-movers")+'</div>'+
 '<ol>'+rows+'</ol>'+(ranked.length?'':'<p class="empty">No qualifying moves.</p>')+'<small class="universe">'+eligible.length+' tracked instruments · '+shortDate(session.day)+' close</small></section>';
}
function worldMarkets(){
 const rows=regions[region].map(id=>byId.get(id)).filter(Boolean);
 return '<section class="home-panel world-panel"><div class="panel-head"><h2>World indices</h2>'+segments(Object.keys(regions).map(r=>[r,r]),region,"data-region")+'</div>'+
 '<div class="world-grid">'+rows.map(r=>'<button data-focus="'+r.id+'"><span>'+esc(r.name)+'</span><b>'+f(r.stats.last)+'</b><small class="'+cls(r.stats.pct)+'">'+sf(r.stats.change)+' pts · '+pct(r.stats.pct)+'</small><em>'+shortDate(r.stats.day)+' local close</em></button>').join("")+'</div></section>';
}
function overview(){
 const jumps=[["dispatches","Market dispatches"],["active-charts","Moves in focus"],["rotation-detail","Sector leadership"],["portfolio-brief","Portfolio thesis"]];
 const contents='<div class="edition-contents" aria-label="Overview sections">'+jumps.filter(([id])=>id!=="active-charts"||pulsePicks.length).map(([target,label])=>'<button data-jump="'+target+'">'+label+' <span aria-hidden="true">↓</span></button>').join("")+'<a href="#portfolio">Portfolio monitor ↗</a></div>';
 return quoteStrip()+marketLead()+marketIntelligence()+contents+'<div class="home-grid">'+deskTable()+movers()+'</div>'+worldMarkets()+
  '<div class="grid">'+relativeChart()+sectorRotation()+'</div>'+activeCharts()+marketDispatches()+rotationDetail()+
  '<div class="grid equal">'+curvePanel()+regimePanel()+'</div>'+overviewTheses()+intelligenceHistory();
}
function marketTable(){
 const rows=markets.filter(r=>(!group||r.group===group)&&(r.name+' '+r.symbol).toLowerCase().includes(filter.toLowerCase())).sort((a,b)=>sort==='name'?a.name.localeCompare(b.name):(b.stats[sort]??-Infinity)-(a.stats[sort]??-Infinity));
 return '<div class="tablebox"><table><thead><tr><th>Instrument</th><th>Last</th><th>Unit</th><th>Change</th><th>1D</th><th>6M</th><th>Observed</th></tr></thead><tbody>'+rows.map(r=>'<tr><td><button data-focus="'+r.id+'">'+esc(r.name)+'</button><small>'+esc(r.symbol)+'</small></td><td>'+f(r.stats.last,r.group==='FX'?4:2)+'</td><td>'+esc(r.unit)+'</td><td>'+sf(r.stats.change,r.group==='FX'?4:2)+'</td><td class="'+cls(r.stats.pct)+'">'+pct(r.stats.pct)+'</td><td class="'+cls(r.stats.six)+'">'+pct(r.stats.six)+'</td><td>'+r.stats.day+'</td></tr>').join("")+'</tbody></table></div>'+(rows.length?'':'<p class="empty">No matching instruments.</p>');
}
function tape(){return section("Market tape",markets.length+" covered instruments · select a name to open its chart",'<div class="tools"><input id="search" placeholder="Search name or ticker" aria-label="Search name or ticker"><select id="group" aria-label="Asset group">'+option("","All asset groups",group)+[...new Set(markets.map(r=>r.group))].map(g=>option(g,g,group)).join("")+'</select><select id="sort" aria-label="Sort instruments">'+[["name","Name A–Z"],["pct","Largest daily return"],["six","Largest six-month return"]].map(([k,v])=>option(k,v,sort)).join("")+'</select></div><div id="table">'+marketTable()+'</div>')}
function rates(){const c=curves.at(-1),p=curves.at(-2);return '<div class="grid equal">'+curvePanel()+regimePanel()+'</div><div class="section">'+section("Term structure",c?E.curve.source+' · '+c.date:'Awaiting data',c&&p?'<div class="tablebox"><table><thead><tr><th>Maturity</th><th>Yield</th><th>Previous</th><th>Move (bp)</th></tr></thead><tbody>'+Object.entries(c.rates).map(([k,v])=>'<tr><td>'+esc(k)+'</td><td>'+f(v)+'%</td><td>'+f(p.rates[k])+'%</td><td>'+sf((v-p.rates[k])*100,0)+'</td></tr>').join("")+'</tbody></table></div>':'')+'</div>'}
function research(){
 const notes=section("Closing commentary","Each observation retains its own source date.",'<div class="readlist">'+E.readings.map(([label,body])=>'<div><b>'+esc(label)+'</b><p>'+esc(body)+'</p></div>').join("")+'</div>');
 const sp=byId.get('spx');
 function deltas(row){return new Map(row.history.slice(1).flatMap(([day,v],i)=>{const prev=row.history[i];return prev[1]>0&&Date.parse(day)-Date.parse(prev[0])<=5*864e5?[[prev[0]+'/'+day,v/prev[1]-1]]:[]}))}
 const bm=deltas(sp);
 const betas=sectors.map(r=>{const own=deltas(r),pairs=[...own].filter(([k])=>bm.has(k)).slice(-63);
 if(pairs.length<40)return [r,null,pairs.length];const mean=arr=>arr.reduce((a,b)=>a+b,0)/arr.length;
 const x=pairs.map(([k])=>bm.get(k)),y=pairs.map(p=>p[1]),xm=mean(x),ym=mean(y);
 const den=x.reduce((s,v)=>s+(v-xm)**2,0);return [r,den?x.reduce((s,v,i)=>s+(v-xm)*(y[i]-ym),0)/den:null,pairs.length]});
 return '<div class="grid equal">'+notes+section("Sector beta","S&P 500 · up to 63 matched daily price-return intervals",'<div class="tablebox"><table><thead><tr><th>Sector</th><th>Beta</th><th>Observations</th></tr></thead><tbody>'+betas.sort((a,b)=>(b[1]??-Infinity)-(a[1]??-Infinity)).map(([r,v,n])=>'<tr><td><button data-focus="'+r.id+'">'+esc(r.name)+'</button></td><td>'+f(v)+'</td><td>'+n+'</td></tr>').join('')+'</tbody></table></div>','<a class="link" href="'+repo+'/blob/main/dashboard/RESEARCH.md">Notebook ↗</a>')+'</div><div class="section">'+section("Source ledger","Instrument basis, observation date and original provider",'<div class="tablebox"><table><thead><tr><th>Instrument</th><th>Observed</th><th>Basis</th><th>Source</th></tr></thead><tbody>'+markets.map(r=>'<tr><td>'+esc(r.name)+'</td><td>'+r.stats.day+'</td><td>'+esc(r.basis)+'</td><td><a href="'+esc(r.url)+'">'+esc(r.source)+'</a></td></tr>').join("")+'</tbody></table></div>')+'</div>';
}
function render(){
 renderFreshness();
 const hash=location.hash.slice(1),view=Object.hasOwn(views,hash)?hash:"overview";
 document.body.classList.toggle("front-page",view==="overview");
 const sourceDate=view==="portfolio" ? (E.books?.[book]?.live?.date || E.books?.[book]?.date) : byId.get("spx").stats.day;
 $("editionDate").textContent=(view==="portfolio"?"Portfolio valuation · ":"US session · ")+(sourceDate?dateLabel(sourceDate):"Awaiting source");
 $("navigation").innerHTML=Object.keys(views).map(k=>'<a href="#'+k+'" '+(view===k?'aria-current="page" class="on"':'')+'>'+labels[k]+'</a>').join("");
 $("title").textContent=views[view][0];$("dek").textContent=views[view][1];
 $("content").innerHTML=({overview,markets:tape,rates,portfolio:portfolioHealth,research,pipeline:pipelinePanel})[view]();
 if($("search"))$("search").value=filter;
}
function focusChart(id){
 chartState.primary=id;
 if(chartState.comparison===id)chartState.comparison=id==="spx"?"rsp":"spx";
 if(location.hash!=="#overview")location.hash="overview";else render();
 requestAnimationFrame(()=>$("comparisonPanel")?.scrollIntoView({behavior:"smooth",block:"center"}));
}
document.addEventListener("click",e=>{
 if(handleIntelligenceControl(e))return;
 const bookLink=e.target.closest("a[data-open-book]");
 if(bookLink)book=bookLink.dataset.openBook;
 const desk=e.target.closest("a[data-desk]");
 if(desk && Object.hasOwn(deskGroups,desk.dataset.desk)){group=deskGroups[desk.dataset.desk];filter="";sort="name"}
 const b=e.target.closest("button");if(!b)return;
 if(b.dataset.jump)$(b.dataset.jump)?.scrollIntoView({block:"start"});
 else if(b.dataset.rates)location.hash="rates";
 else if(b.dataset.movers){moversSide=b.dataset.movers;document.querySelector(".movers-panel").outerHTML=movers();document.querySelector('[data-movers="'+moversSide+'"]').focus({preventScroll:true})}
 else if(b.dataset.region){region=b.dataset.region;document.querySelector(".world-panel").outerHTML=worldMarkets();document.querySelector('[data-region="'+region+'"]').focus({preventScroll:true})}
 else if(b.dataset.focus)focusChart(b.dataset.focus);
 else if(b.dataset.months){chartState.months=Number(b.dataset.months);render()}
 else if(b.dataset.sector){sectorWindow=b.dataset.sector;b.closest(".card").outerHTML=sectorRotation();document.querySelector('[data-sector="'+sectorWindow+'"]').focus({preventScroll:true})}});
document.addEventListener("change",e=>{if(thesisControls(e) || handlePortfolioControl(e))return;
 const {id,value}=e.target;
 if(id==="primary"){chartState.primary=value;if(value===chartState.comparison)chartState.comparison="";render()}
 else if(id==="comparison"){chartState.comparison=value;render()}
 else if(id==="group"||id==="sort"){if(id==="group")group=value;else sort=value;$("table").innerHTML=marketTable()}});
document.addEventListener("input",e=>{if(e.target.id==="search"){filter=e.target.value;$("table").innerHTML=marketTable()}});
document.addEventListener("pointermove",e=>{const svg=e.target.closest("#comparisonChart");if(!svg||!window.plotPoints?.length)return;
 const point=new DOMPoint(e.clientX,e.clientY).matrixTransform(svg.getScreenCTM().inverse());
 const item=window.plotPoints.reduce((a,b)=>Math.abs(a.x-point.x)<Math.abs(b.x-point.x)?a:b);
 $("cross").setAttribute("x1",item.x);$("cross").setAttribute("x2",item.x);$("cross").setAttribute("visibility","visible");
 $("hover").textContent=item.d+" · "+item.values.map((v,i)=>(i?byId.get(chartState.comparison):byId.get(chartState.primary)).name+" "+pct(v)).join("  /  ");});
window.addEventListener("hashchange",()=>{render();window.scrollTo(0,0)});
/*EDITION_MODULES*/
$("editionDate").textContent="US session · "+dateLabel(byId.get("spx").stats.day);
$("compiled").textContent="Edition compiled "+E.created;
$("alerts").innerHTML=sourceStatus();
render();
