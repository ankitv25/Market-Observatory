const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const scripts = path.join(root, "scripts");
const modules = ["rotation", "dispatches", "spotlight", "theses", "portfolio", "freshness", "intelligence", "pipeline-view"]
  .map(name => fs.readFileSync(path.join(scripts, name + ".js"), "utf8")).join("\n");
const application = fs.readFileSync(path.join(scripts, "monitor.js"), "utf8")
  .replace("/*EDITION_MODULES*/", modules);

function openEdition(edition) {
  const nodes = new Map([["data", {textContent: JSON.stringify(edition)}]]);
  const context = vm.createContext({
    document: {
      getElementById(id) {
        if (!nodes.has(id)) nodes.set(id, {innerHTML: "", textContent: "", value: ""});
        return nodes.get(id);
      },
      body: {classList: {toggle() {}}},
      addEventListener() {}
    },
    location: {hash: "#overview"},
    window: {addEventListener() {}, scrollTo() {}},
    requestAnimationFrame() {},
  });
  vm.runInContext(application, context);
  return {nodes, run: code => vm.runInContext(code, context)};
}

const archives = path.join(root, "editions", "2026-11");
const editions = fs.readdirSync(archives).filter(name => name.endsWith(".json"))
  .map(name => JSON.parse(fs.readFileSync(path.join(archives, name))));
editions.push(JSON.parse(fs.readFileSync(path.join(root, "dashboard/latest.json"))));

for (const edition of editions) {
  const {nodes, run} = openEdition(edition);
  for (const view of ["overview", "markets", "rates", "portfolio", "research", "pipeline"]) {
    run('location.hash = "#' + view + '"; render();');
    assert(!/\b(?:NaN|undefined|Infinity)\b/.test(nodes.get("content").innerHTML),
      edition.created + " invalid text in " + view);
    assert(nodes.get("content").innerHTML.length > 100, view + " rendered no content");
  }
  run('location.hash = "#portfolio";');
  for (const id of Object.keys(edition.books || {})) {
    run('book = "' + id + '"; render();');
    assert(!/\b(?:NaN|undefined|Infinity)\b/.test(nodes.get("content").innerHTML));
  }
}

const {run} = openEdition(editions.at(-1));
assert.equal(run('rotationMonthEnd("2024-03-31", 1)'), "2024-02-29");
assert.equal(run('rotationMonthEnd("2026-01-31", 6)'), "2025-07-31");
assert.equal(run('rotationReturns({history:[["2026-01-01",100],["2026-01-03",110]]},{prev:"2026-01-02",end:"2026-01-03"}).pct'), null);
assert(Math.abs(run('rotationReturns({history:[["2026-01-01",100],["2026-01-03",110]]},{prev:"2026-01-01",end:"2026-01-03"}).pct') - 10) < 1e-10);
assert.equal(run('thesisCorrelation([{x:1,y:3},{x:2,y:5},{x:3,y:7}])'), 1);
assert.equal(run('thesisCorrelation([{x:1,y:3},{x:2,y:2},{x:3,y:1}])'), -1);
assert.equal(run('thesisCorrelation([{x:1,y:1},{x:1,y:2}])'), null);
assert.equal(run('thesisMatched({history:[["2026-01-01",100],["2026-01-03",110]]},{history:[["2026-01-02",100],["2026-01-03",110]]}).length'), 0);
assert.equal(run('dispatchGap({stats:{day:"2026-01-03",previous_day:"2026-01-01",pct:2}},{stats:{day:"2026-01-03",previous_day:"2026-01-02",pct:1}})'), null);
assert.equal(run('pulseRecord({history:Array.from({length:62},(_,i)=>[new Date(Date.UTC(2026,0,1+i)).toISOString().slice(0,10),100])}).smaller'), 0);

const embedded = fs.readFileSync(path.join(root, "dashboard/observatory.html"), "utf8")
  .match(/<script>([\s\S]*)<\/script>/)[1];
new vm.Script(embedded);
assert(embedded.includes("function portfolioHealth()"));
console.log("Dashboard replay passed for " + editions.length + " editions, six views and all books; interval and financial calculations checked.");

// The status bar must not request a Thanksgiving close, and must recognize an early close.
const calendarEdition=JSON.parse(JSON.stringify(editions.at(-1)));
calendarEdition.refresh={calendar:{holidays:{2026:"11-26"},early_closes:{2026:"11-27"}}};
const calendarReader=openEdition({...calendarEdition,refresh:undefined});
// readerExpectedClose also runs without metadata for historical offline editions.
assert.equal(calendarReader.run('readerExpectedClose(new Date("2026-11-22T12:00:00-05:00"))'),"2026-11-20");

calendarReader.run('E.refresh={calendar:{holidays:{2026:"11-26"},early_closes:{2026:"11-27"}}}');
assert.equal(calendarReader.run('readerExpectedClose(new Date("2026-11-26T17:00:00-05:00"))'),"2026-11-25");
assert.equal(calendarReader.run('readerExpectedClose(new Date("2026-11-27T13:11:00-05:00"))'),"2026-11-27");
assert.equal(run('validPipelineRecord({recent:[null],counts:{success:1}})'),false);
assert.equal(run('validPipelineRecord({recent:[{stages:[],sources:{groups:{a:null}}}],counts:{}})'),false);

assert(run('intelligenceSourceAudit({sources:[{id:"spx",name:"Test index",used_in_score:true}]},{evidence:[]})').includes('Context / excluded'));
assert(!run('intelligenceSourceAudit({sources:[{id:"spx",name:"Test index",used_in_score:true}]},{evidence:[]})').includes('<td>Scored</td>'));

const healthyReader=openEdition({...editions.at(-1),issues:[],market_health:{checked:62,live:62,archive:0,retained:0,missing:0}});
assert(healthyReader.run('sourceStatus()').includes('Refresh successful'));
assert(healthyReader.run('sourceStatus()').includes('62 of 62 market feeds refreshed'));
const partialReader=openEdition({...editions.at(-1),issues:['Awaiting a new source response for Brent crude'],market_health:{checked:62,live:61,archive:0,retained:1,missing:0}});
assert(partialReader.run('sourceStatus()').includes('Edition updated · source delays'));
assert(!partialReader.run('sourceStatus()').includes('Refresh successful'));
