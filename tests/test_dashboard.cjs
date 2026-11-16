const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const scripts = path.join(root, "scripts");
const modules = ["rotation", "dispatches", "spotlight", "theses", "portfolio", "freshness"]
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
  for (const view of ["overview", "markets", "rates", "portfolio", "research"]) {
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
console.log("Dashboard replay passed for " + editions.length + " editions, five views and all books; interval and financial calculations checked.");
