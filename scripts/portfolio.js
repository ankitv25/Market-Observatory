// Portfolio review uses the source book's own reference and NAV index.
let pmHorizon = "ALL";
let pmShock = "";

function pmNumber(value, digits=2, unit="") {
  return Number.isFinite(value) ? f(value,digits)+unit : "—";
}

function pmSigned(value, digits=2, unit="") {
  return Number.isFinite(value) ? sf(value,digits)+unit : "—";
}

function pmDate(day) {
  return day ? dateLabel(day) : "Date unavailable";
}

function pmPublished(live) {
  if (!live.published_at) return "";
  const timestamp=new Date(live.published_at);
  if (!Number.isFinite(timestamp.getTime())) return "";
  return timestamp.toLocaleString("en-US",{month:"short",day:"numeric",year:"numeric",hour:"numeric",minute:"2-digit",timeZone:"America/New_York",timeZoneName:"short"});
}

function pmMetric(label, value, foot, direction) {
  return '<div class="pm-metric"><span>'+esc(label)+'</span><b class="'+(Number.isFinite(direction)?cls(direction):"")+'">'+esc(value)+'</b><small>'+esc(foot)+'</small></div>';
}

function pmHeader(title, subtitle, control="") {
  return '<div class="pm-head"><div><h2>'+esc(title)+'</h2><p>'+esc(subtitle)+'</p></div>'+control+'</div>';
}

function pmChart(rows, underwater) {
  const width=580, height=174, x0=50, x1=568, y0=9, y1=145;
  const values=rows.flatMap(r=>underwater?[r.dd]:[r.nav,r.ref]).filter(Number.isFinite);
  if (values.length<2 || rows.length<2) return '<p class="empty">Awaiting two dated NAV closes.</p>';
  const min=Math.min(...values), max=Math.max(...values);
  const pad=Math.max((max-min)*.08, underwater?.02:.03);
  const low=min-pad, high=underwater?0:max+pad;
  const first=Date.parse(rows[0].day), span=Math.max(1,Date.parse(rows.at(-1).day)-first);
  const X=r=>x0+(x1-x0)*(Date.parse(r.day)-first)/span;
  const Y=n=>y1-(n-low)/(high-low)*(y1-y0);
  const path=field=>{
    let result="", next="M";
    for (const r of rows) {
      if (!Number.isFinite(r[field])) { next="M"; continue; }
      result+=next+X(r).toFixed(2)+" "+Y(r[field]).toFixed(2);
      next="L";
    }
    return result;
  };
  const primary=path(underwater?"dd":"nav");
  let content="";
  for (let i=0;i<4;i++) {
    const v=low+(high-low)*i/3;
    content+='<path d="M'+x0+' '+Y(v)+'H'+x1+'" stroke="#dce5e7" stroke-width=".8"/><text x="'+(x0-7)+'" y="'+(Y(v)+3.5)+'" text-anchor="end">'+f(v,underwater?1:2)+(underwater?'%':'')+'</text>';
  }
  if (underwater) {
    content+='<path d="'+primary+' L'+x1+' '+Y(0)+' L'+x0+' '+Y(0)+' Z" fill="#ba7860" opacity=".17"/>';
  } else {
    content+='<path d="'+path("ref")+'" stroke="#6c62b2" stroke-dasharray="5 3" stroke-width="2" fill="none"/>';
  }
  content+='<path d="'+primary+'" stroke="'+(underwater?'#a7533d':'#07766d')+'" stroke-width="2.8" stroke-linejoin="round" fill="none"/>';
  [rows[0],rows[Math.floor((rows.length-1)/2)],rows.at(-1)].forEach((r,i)=>{
    content+='<text x="'+X(r)+'" y="167" text-anchor="'+(["start","middle","end"][i])+'">'+esc(shortDate(r.day))+'</text>';
  });
  return '<svg viewBox="0 0 '+width+' '+height+'" role="img" aria-label="'+(underwater?'Percentage below the running NAV peak':'Fund and reference NAV indices')+' from '+esc(rows[0].day)+' through '+esc(rows.at(-1).day)+'">'+content+'</svg>';
}

function pmSelect(id, caption, options) {
  return '<label class="pm-select">'+esc(caption)+'<select id="'+id+'">'+options+'</select></label>';
}

function pmCharts(b, details) {
  const history=details.history;
  let peak=details.initial;
  const full=history.map(r=>{
    peak=Math.max(peak,r.nav);
    return {...r,dd:100*(r.nav/peak-1)};
  });
  const periods=[["ALL","Since inception"],["3M","3 months"],["1M","1 month"]];
  const end=new Date(full.at(-1).day+"T00:00:00Z");
  const months=pmHorizon==="1M"?1:pmHorizon==="3M"?3:0;
  const boundary=new Date(Date.UTC(end.getUTCFullYear(),end.getUTCMonth()-months,1));
  const daysInMonth=new Date(Date.UTC(boundary.getUTCFullYear(),boundary.getUTCMonth()+1,0)).getUTCDate();
  boundary.setUTCDate(Math.min(end.getUTCDate(),daysInMonth));
  const range=boundary.toISOString().slice(0,10);
  const rows=months?full.filter(r=>r.day>=range):full;
  const min=Math.min(...full.map(r=>r.dd));
  const control=pmSelect("pmHorizon","History window",periods.map(([k,v])=>option(k,v,pmHorizon)).join(""));
  const legend='<span class="pm-key"><i></i>'+esc(b.name)+'</span><span class="pm-key ref"><i></i>'+esc(details.benchmark)+'</span>';
  return '<section class="pm-card pm-track">'+pmHeader("Performance and drawdown","Forward-tracked NAV · "+pmDate(full[0].day)+' – '+pmDate(full.at(-1).day),control)+
    '<div class="pm-plots"><figure><figcaption>NAV index <span>'+legend+'</span></figcaption>'+pmChart(rows,false)+
    '<p>Starting capital '+f(details.initial,0)+'. Fund NAV includes accrued costs.</p></figure>'+
    '<figure><figcaption>Underwater curve <span>Worst drawdown '+pmSigned(min,2,"%")+'</span></figcaption>'+pmChart(rows,true)+
    '<p>Distance below the fund’s running peak since inception, including its starting capital.</p></figure></div></section>';
}

function pmExposure(b) {
  const sleeves=(b.sleeves||[]).filter(s=>Number.isFinite(s.risk) && Number.isFinite(s.capital)).sort((a,z)=>z.risk-a.risk);
  const top=sleeves[0], blocks=b.blocks||[];
  const bar='<div class="pm-stack" aria-hidden="true">'+blocks.filter(r=>Number.isFinite(r.weight)&&r.weight>0).map((r,i)=>'<i style="flex:'+r.weight+';background:var(--pm-block-'+i%6+')"></i>').join("")+'</div>';
  const readable=k=>({FixedIncome:"Fixed income",RealEstate:"Real estate",AltsInsurance:"Alternatives / insurance"}[k] || k);
  const list=blocks.map((r,i)=>'<li><i style="background:var(--pm-block-'+i%6+')"></i><span>'+esc(readable(r.block))+'</span><b>'+pmNumber(r.weight,1,"%")+'</b></li>').join("");
  const concentration=top?top.sleeve+' carries '+f(top.risk,1)+'% of estimated risk on '+f(top.capital,1)+'% of model capital.':'Risk contributions unavailable.';
  const exposure='<section class="pm-card">'+pmHeader("Policy allocation","Model capital by block · "+pmDate(b.date))+
    bar+'<ul class="pm-blocks">'+list+'</ul><p class="pm-thesis">'+esc(b.thesis || "No thesis published for this book.")+'</p>'+
    (b.url?'<a class="link" href="'+esc(b.url)+'">Source portfolio book ↗</a>':'')+'</section>';
  const rows=sleeves.map(s=>'<tr><th scope="row">'+esc(s.sleeve)+'</th><td>'+pmNumber(s.capital,1,"%")+'</td><td>'+pmNumber(s.risk,1,"%")+'</td><td>'+pmSigned(s.risk-s.capital,1," pp")+'</td></tr>').join("");
  const risk='<section class="pm-card">'+pmHeader("Risk concentration","Modeled contributions · "+pmDate(b.date))+'<p class="pm-reading">'+esc(concentration)+'</p>'+
    '<div class="pm-scroll"><table><thead><tr><th>Sleeve</th><th>Capital</th><th>Risk share</th><th>Risk − capital</th></tr></thead><tbody>'+rows+'</tbody></table></div></section>';
  return '<div class="pm-grid">'+exposure+risk+'</div>';
}

function pmMarketDetails(live) {
  if (!live?.dates?.length || !Array.isArray(live.nav) || !Number.isFinite(live.opening) || live.opening<=0) return null;
  const history=live.dates.map((day,i)=>({day,nav:live.nav[i],ref:live.benchmark_nav?.[i]}))
    .filter(r=>Number.isFinite(r.nav) && r.nav>0);
  if (!history.length || history.at(-1).day!==live.date) return null;
  return {history,initial:live.opening,benchmark:live.benchmark || "Reference"};
}

function pmPriceSummary(b, live, details) {
  if (!details) return '<section class="pm-card">'+pmHeader("Portfolio positioning","Published model · "+pmDate(b.date))+
    '<div class="pm-tiles">'+pmMetric("Stance",b.stance || "—","Published positioning")+
    pmMetric("Forecast volatility",pmNumber(b.forecast,1,"%"),"Annualized model estimate")+
    pmMetric("Construction vol cap",pmNumber(b.budget,1,"%"),"Annualized model constraint")+'</div>'+
    '<p class="pm-reading">This edition contains the allocation and risk model. A dated NAV record is unavailable.</p></section>';
  const last=details.history.at(-1), net=live.returns?.["1D"], reference=live.benchmark_returns?.["1D"];
  const active=Number.isFinite(net) && Number.isFinite(reference)?net-reference:null;
  const wording=active==null? "Reference return unavailable." :
    Math.abs(active)<.00005? "The fund and reference finished level on relative return." :
    'The fund '+(active>0?'outperformed':'underperformed')+' its reference by '+f(Math.abs(active)*100,1)+' bp.';
  const nav=last.nav, since=live.returns?.SI;
  const age=(Date.parse(E.created.slice(0,10))-Date.parse(live.date))/864e5;
  const vintage=age>7?' · '+age+' calendar days before this edition':'';
  return '<section class="pm-close"><div class="pm-close-title"><div><span class="pm-label">Published NAV · '+esc(pmDate(live.date))+esc(vintage)+'</span>'+
    '<h2>'+esc(b.name)+' NAV <strong>'+f(nav,4)+'</strong></h2><p>'+esc(wording)+'</p><small class="pm-publication">'+esc(pmPublished(live)?'Source published '+pmPublished(live):'Publication time unavailable')+'</small></div>'+
    '<div class="pm-mandate"><span>'+esc(b.stance || "Stance unavailable")+'</span><small>Model as of '+esc(pmDate(b.date))+'</small></div></div>'+
    '<div class="pm-tiles">'+pmMetric("Fund · latest valuation",pmSigned(net,2,"%"),pmSigned(live.session?.net,4," NAV pts"),net)+
    pmMetric("Reference · latest valuation",pmSigned(reference,2,"%"),details.benchmark,reference)+
    pmMetric("Active · latest valuation",pmSigned(Number.isFinite(active)?100*active:null,1," bp"),"Fund less reference",active)+
    pmMetric("Since inception",pmSigned(since,2,"%"),"From "+pmDate(live.inception),since)+
    pmMetric("Drawdown",pmSigned(live.drawdown_pct,2,"%"),"From fund high-water mark")+'</div></section>';
}

function pmReview(b,live) {
  const portfolio=live.returns?.SI, reference=live.benchmark_returns?.SI;
  const active=Number.isFinite(portfolio) && Number.isFinite(reference)?portfolio-reference:null;
  const m=b.risk_model || {};
  const performance=[];
  if (Number.isFinite(live.drawdown_pct)) performance.push('NAV is '+f(Math.abs(live.drawdown_pct),2)+'% below its high-water mark.');
  if (active!=null) {
    performance.push('Since '+pmDate(live.inception)+', '+b.name+' returned '+pmSigned(portfolio,2,"%")+' against '+pmSigned(reference,2,"%")+' for '+live.benchmark+
      ', '+(Math.abs(active)<.00005?'matching its reference.':(active>0?'ahead by ':'behind by ')+f(Math.abs(active)*100,1)+' bp.'));
  }
  if (Number.isFinite(m.dd_limit) && Number.isFinite(live.drawdown_pct)) {
    const distance=live.drawdown_pct-m.dd_limit;
    performance.push('Its drawdown stands '+f(Math.abs(distance),2)+' percentage points '+(distance>=0?'above':'below')+' the '+pmSigned(m.dd_limit,1,"%")+' owner loss limit.');
  }
  const factors=(m.factors||[]).filter(r=>Number.isFinite(r.share)).sort((a,z)=>z.share-a.share);
  const risk=[];
  if (factors.length) risk.push(factors[0].factor+' represents '+f(factors[0].share,1)+'% of modeled portfolio risk.');
  if (Number.isFinite(b.forecast) && Number.isFinite(b.budget)) risk.push('Forecast annualized volatility is '+f(b.forecast,1)+'% against a '+f(b.budget,1)+'% construction cap.');
  const largest=(b.sleeves||[]).filter(r=>Number.isFinite(r.risk) && Number.isFinite(r.capital)).sort((a,z)=>z.risk-a.risk)[0];
  if (largest) risk.push(largest.sleeve+' is the largest sleeve risk contribution, '+f(largest.risk,1)+'% on '+f(largest.capital,1)+'% of model capital.');
  if (!performance.length && !risk.length) return "";
  return '<section class="pm-review-note"><h3>PM review</h3><div>'+
    (performance.length?'<p>'+esc(performance.join(" "))+'</p>':'')+
    (risk.length?'<p>'+esc(risk.join(" "))+' <span>Risk model dated '+esc(pmDate(b.date))+'.</span></p>':'')+'</div></section>';
}

function pmPeriods(b, live) {
  const periods=["1D","1M","3M","6M","12M","SI"];
  const format=(n,decimals,unit)=>'<td class="'+(Number.isFinite(n)?cls(n):"")+'">'+pmSigned(n,decimals,unit)+'</td>';
  const rows=periods.map(k=>{
    const fund=live.returns?.[k], reference=live.benchmark_returns?.[k];
    const active=Number.isFinite(fund)&&Number.isFinite(reference)?(fund-reference)*100:null;
    return '<tr><th scope="row">'+(k==="SI"?"Since inception":k)+'</th>'+format(fund,2,"%")+format(reference,2,"%")+format(active,1," bp")+'</tr>';
  }).join("");
  return '<section class="pm-card">'+pmHeader("Return scorecard","Cumulative returns through "+pmDate(live.date))+
    '<div class="pm-scroll"><table><thead><tr><th>Window</th><th>'+esc(b.name)+'</th><th>Benchmark</th><th>Active</th></tr></thead><tbody>'+rows+'</tbody></table></div>'+
    '<p class="pm-foot">'+esc(live.benchmark)+' is the published reference. '+esc(live.benchmark_basis || '')+'. Windows longer than the available record are blank.</p></section>';
}

function pmHoldings(live) {
  const holdings=(live.holdings||[]).filter(h=>Number.isFinite(h.weight_pct)).sort((a,b)=>b.weight_pct-a.weight_pct);
  const top=holdings.slice(0,3), share=top.reduce((sum,h)=>sum+h.weight_pct,0);
  const line=top.length?'The largest '+top.length+' position'+(top.length===1?'':'s')+' account'+(top.length===1?'s':'')+' for '+f(share,1)+'% of fund capital.':'This edition has no holdings weights.';
  return '<section class="pm-card">'+pmHeader("Vehicle concentration","Published vehicle weights · "+pmDate(live.date))+
    '<p class="pm-reading">'+esc(line)+'</p><div class="pm-scroll"><table><thead><tr><th>Vehicle</th><th>Sleeve</th><th>Fund weight</th></tr></thead><tbody>'+
    holdings.map(h=>'<tr><th scope="row">'+esc(h.ticker)+'</th><td class="pm-name">'+esc(h.sleeve || "Unclassified")+'</td><td>'+pmNumber(h.weight_pct,2,"%")+'</td></tr>').join("")+
    '</tbody></table></div></section>';
}

function pmCompleted(live) {
  const latest=live.session || {};
  const session=latest.holding_moves?.length ? latest : live.completed_session;
  if (!session?.holding_moves?.length || !session.start || !session.end) return "";
  const moves=session.holding_moves.filter(r=>Number.isFinite(r.points)).sort((a,b)=>b.points-a.points);
  const scale=Math.max(.000001,...moves.map(r=>Math.abs(r.points)));
  const bars=moves.map(r=>{
    const size=48*Math.abs(r.points)/scale;
    const left=r.points>=0?50:50-size;
    return '<li><span>'+esc(r.ticker)+'</span><i aria-hidden="true"><em style="left:'+left.toFixed(3)+'%;width:'+size.toFixed(3)+'%;background:'+(r.points>=0?'#168372':'#b45a42')+'"></em></i><b class="'+cls(r.points)+'">'+pmSigned(r.points,4)+'</b></li>';
  }).join("");
  const largest=moves.find(r=>r.points>0), weakest=moves.filter(r=>r.points<0).at(-1);
  const story=[
    largest?largest.ticker+' contributed '+f(largest.points,4)+' points.':"",
    weakest?weakest.ticker+' cost '+f(-weakest.points,4)+' points.':""
  ].filter(Boolean).join(" ");
  return '<section class="pm-card pm-completed">'+pmHeader("Completed-session contributors",pmDate(session.start)+' → '+pmDate(session.end)+' · NAV points')+
    '<div class="pm-grid"><div><p class="pm-reading">'+esc(story)+'</p><ul class="pm-contributors">'+bars+'</ul></div><div><h3>Reconciled session</h3>'+
    '<div class="pm-cashlist">'+pmCashRow("Vehicle estimates",moves.reduce((sum,r)=>sum+r.points,0))+
    pmCashRow("Fee · estimated",session.fee)+pmCashRow("Dealing · estimated",session.dealing)+pmCashRow("Balance / rounding",session.residual)+
    pmCashRow("Published NAV change",session.net,true)+'</div><p class="pm-foot">'+esc(session.basis || "Reconstructed from published holdings and adjusted ETF prices.")+'</p></div></div></section>';
}

function pmCashRow(label,value,strong=false) {
  return '<div class="pm-cashrow'+(strong?' total':'')+'"><span>'+esc(label)+'</span><b class="'+(Number.isFinite(value)?cls(value):"")+'">'+pmSigned(value,4)+'</b></div>';
}

function pmBridge(live) {
  const s=live.session||{}, matches=s.end===live.date && !!s.start;
  const start=s.start?pmDate(s.start):"Prior close";
  const sub=matches?start+' → '+pmDate(s.end)+' · NAV points':'Daily components unavailable for this valuation';
  const moves=matches?(s.holding_moves||[]).filter(r=>Number.isFinite(r.points)).sort((a,b)=>Math.abs(b.points)-Math.abs(a.points)):[];
  let daily='<p class="empty">Daily attribution unavailable in this edition.</p>';
  if (matches) {
    daily='<div class="pm-cashlist">'+pmCashRow("Gross investment move · inferred",s.gross)+pmCashRow("Management fee · estimated",s.fee)+pmCashRow("Dealing · estimated",s.dealing)+pmCashRow("Net change in NAV",s.net,true)+'</div>';
    if (moves.length) {
      const sum=moves.reduce((t,r)=>t+r.points,0);
      daily+='<details class="pm-more"><summary>Daily vehicle estimates</summary><div class="pm-cashlist">'+
        moves.map(r=>pmCashRow(r.ticker,r.points)).join("")+
        pmCashRow("Gross less listed estimates",Number.isFinite(s.gross)?s.gross-sum:null,true)+'</div></details>';
    }
    if (s.basis) daily+='<p class="pm-foot">'+esc(s.basis)+'</p>';
  }
  const bridge=live.bridge||{}, vehicle=Object.entries(bridge.vehicles||{}).filter(([,v])=>Number.isFinite(v)).sort((a,b)=>b[1]-a[1]);
  const largestGain=vehicle.find(([,n])=>n>0), largestLoss=vehicle.filter(([,n])=>n<0).at(-1);
  const observations=[
    largestGain?largestGain[0]+' added '+f(largestGain[1],3)+' NAV points.':null,
    largestLoss?largestLoss[0]+' detracted '+f(-largestLoss[1],3)+' points.':null
  ].filter(Boolean).join(" ");
  let record="";
  if (Number.isFinite(bridge.total)) {
    const gross=vehicle.reduce((acc,[,v])=>acc+v,0);
    const residual=[bridge.fee,bridge.dealing].every(Number.isFinite) && vehicle.length?bridge.total-gross-bridge.fee-bridge.dealing:null;
    record='<div class="pm-bridge-history"><h3>Since-inception contributors</h3><span class="mini">'+esc(pmDate(live.inception))+' – '+esc(pmDate(live.date))+' · NAV points</span><p>'+esc(observations)+'</p>'+
      '<details class="pm-more"><summary>Inspect cumulative bridge</summary><div class="pm-cashlist">'+vehicle.map(([label,v])=>pmCashRow(label,v)).join("")+
      pmCashRow("Management fees",bridge.fee)+pmCashRow("Dealing costs",bridge.dealing)+pmCashRow("Balance / rounding",residual)+pmCashRow("Net NAV change",bridge.total,true)+'</div></details></div>';
  }
    const factor=live.factor_attribution;
  if (factor?.rows?.length) {
    const rows=factor.rows.filter(r=>Number.isFinite(r.points)).sort((a,b)=>Math.abs(b.points)-Math.abs(a.points));
    record+='<details class="pm-more pm-factor-detail"><summary>Modeled factor attribution since inception</summary>'+
      '<p class="pm-foot">'+esc(pmDate(live.inception))+' – '+esc(pmDate(live.date))+' · NAV points. Publisher factor model uses '+esc(typeof factor.window==="object" ? ((factor.window.beta_obs || "—")+" beta observations from "+(factor.window.beta_start || "—")) : (factor.window || "its disclosed estimation window"))+'.</p>'+
      '<div class="pm-cashlist">'+rows.map(r=>pmCashRow(r.name,r.points)).join("")+
      pmCashRow("Cash",factor.cash)+pmCashRow("Costs",factor.costs)+pmCashRow("Unexplained residual",factor.residual)+
      pmCashRow("Net NAV change",bridge.total,true)+'</div></details>';
  }
  return '<section class="pm-card">'+pmHeader("Daily valuation bridge",sub)+daily+record+'</section>';
}

function pmConstraints(model) {
  const caps=[
    ["Drawdown construction cap",model.dd_budget],
    ["Conditional drawdown-at-risk cap",model.cdar_cap]
  ].filter(([,v])=>Number.isFinite(v));
  if (Number.isFinite(model.dd_limit)) caps.push(["Owner loss limit",model.dd_limit]);
  const rows=(model.constraints||[]).map(c=>'<tr><th scope="row">'+esc(c.sleeve)+'</th><td>'+pmNumber(c.floor,1,"%")+'</td><td>'+pmNumber(c.current,1,"%")+'</td><td>'+pmNumber(c.ceiling,1,"%")+'</td></tr>').join("");
  return (caps.length?'<ul class="pm-blocks simple pm-caps">'+caps.map(([k,v])=>'<li><span>'+esc(k)+'</span><b>'+pmNumber(v,1,"%")+'</b></li>').join("")+'</ul>':'')+
    (rows?'<details class="pm-more"><summary>Inspect construction bounds</summary><div class="pm-scroll"><table><thead><tr><th>Sleeve</th><th>Floor</th><th>Model weight</th><th>Ceiling</th></tr></thead><tbody>'+rows+'</tbody></table></div></details>':'');
}

function pmStress(b) {
  const m=b.risk_model || {}, cases=(m.scenarios||[]).filter(s=>Number.isFinite(s.portfolio_pct)).sort((a,z)=>a.portfolio_pct-z.portfolio_pct);
  const factors=(m.factors||[]).filter(r=>Number.isFinite(r.share));
  const forecast=b.forecast,budget=b.budget,util=Number.isFinite(forecast)&&budget>0?100*forecast/budget:null;
  const distribution=factors.map(r=>'<li><span>'+esc(r.factor)+'</span><b>'+pmSigned(r.share,1,"%")+'</b></li>').join("");
  const risk='<section class="pm-card">'+pmHeader("Construction constraints","Published risk model · "+pmDate(b.date))+
    '<div class="pm-tiles compact">'+pmMetric("Forecast volatility",pmNumber(forecast,1,"%"),"Annualized")+
    pmMetric("Volatility cap",pmNumber(budget,1,"%"),"Construction constraint")+
    pmMetric("Cap utilization",pmNumber(util,0,"%"),"Forecast ÷ construction cap")+'</div>'+pmConstraints(m)+
    (factors.length?'<h3 class="pm-smallhead">Share of modeled risk</h3><ul class="pm-blocks simple">'+distribution+'</ul>':'')+
    (Number.isFinite(m.effective_bets)?'<p class="pm-foot">Model-implied effective bets '+pmNumber(m.effective_bets,1)+' · diversification ratio '+pmNumber(m.diversification_ratio,2)+'×.</p>':'')+'</section>';
  const worst=cases[0], selected=cases.find(s=>s.name===pmShock) || worst;
  if (!selected) return '<div class="pm-grid">'+risk+'<section class="pm-card">'+pmHeader("Scenario losses","Published shock analysis")+'<p class="empty">Scenario estimates unavailable in this edition.</p></section></div>';
  const select=pmSelect("pmShock","Inspect scenario",cases.map(s=>option(s.name,s.name,selected.name)).join(""));
  let comparison='';
  if (Number.isFinite(selected.policy_pct)) {
    comparison='<p>Against '+esc(m.scenario_reference || 'its policy weights')+' '+pmSigned(selected.policy_pct,1,"%")+' · difference '+pmSigned(selected.portfolio_pct-selected.policy_pct,1," pp")+'.</p>';
  }
  const bound=Math.max(.01,...cases.map(s=>Math.abs(s.portfolio_pct)));
  const ladder=cases.map(s=>'<li><span>'+esc(s.name)+'</span><i aria-hidden="true"><em style="width:'+f(Math.abs(s.portfolio_pct)/bound*100,2)+'%;background:'+(s.portfolio_pct<0?'#b86750':'#18786b')+'"></em></i><b>'+pmSigned(s.portfolio_pct,1,"%")+'</b></li>').join("");
  const shock='<section class="pm-card">'+pmHeader("Scenario losses","Hypothetical shocks to model weights · "+pmDate(b.date))+
    '<ul class="pm-scenarios">'+ladder+'</ul><div class="pm-stress-inspect">'+select+'<b>'+pmSigned(selected.portfolio_pct,1,"%")+'</b>'+comparison+'</div></section>';
  return '<div class="pm-grid">'+risk+shock+'</div>';
}

function portfolioHealth() {
  const books=Object.entries(E.books||{}), current=books.find(([k])=>k===book)||books[0];
  if (!current) return section("Portfolio review","No published books in this edition.",'<a class="link" href="https://ankitv25.github.io/Asset-Allocation/">Open portfolio publisher ↗</a>');
  const [key,b]=current,live=b.live || {},details=pmMarketDetails(live);
  const picker=pmSelect("book","Portfolio",books.map(([k,v])=>option(k,v.name,key)).join(""));
  const toolbar='<div class="pm-toolbar">'+picker+'<p>'+esc(b.role || "")+'</p>'+
    (live.source?'<a class="link" href="'+esc(live.source)+'">NAV source ↗</a>':'')+'</div>';
  const record=details ? pmCharts(b,details)+pmCompleted(live)+'<div class="pm-grid">'+pmBridge(live)+pmPeriods(b,live)+'</div>':'';
  return '<div class="pm-review">'+toolbar+pmPriceSummary(b,live,details)+pmReview(b,live)+record+pmStress(b)+pmExposure(b)+
    (details?pmHoldings(live):"")+'</div>';
}

function handlePortfolioControl(event) {
  const {id,value}=event.target;
  if (!["book","pmShock","pmHorizon"].includes(id)) return false;
  if (id==="book") { book=value; pmShock=""; }
  if (id==="pmShock") pmShock=value;
  if (id==="pmHorizon") pmHorizon=value;
  $("content").innerHTML=portfolioHealth();
  const selected=E.books?.[book];
  if(selected)$("editionDate").textContent="Portfolio valuation · "+pmDate(selected.live?.date || selected.date);
  $(id)?.focus({preventScroll:true});
  return true;
}
