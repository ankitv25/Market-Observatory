"""Check the same artifacts readers see on GitHub and in the offline edition."""
from datetime import date, datetime
from edition_quality import quality_errors
import json
import math
from pathlib import Path
import re
from xml.etree import ElementTree

root=Path(__file__).resolve().parents[1]
data=json.loads((root/"dashboard/latest.json").read_text())
errors=quality_errors(data)
if errors:
    raise SystemExit("Financial quality checks failed:\n" + "\n".join(errors))
rows=data["markets"]
assert len(rows)==len({r["id"] for r in rows})
observed=set()
for row in rows:
    dates=[d for d,_ in row["history"]]
    assert len(dates)>=2 and dates==sorted(set(dates)),row["id"]
    assert all(math.isfinite(v) for _,v in row["history"])
    s=row["stats"]
    assert s["day"]==dates[-1] and s["previous_day"]==dates[-2]
    assert s["day"]<=datetime.fromisoformat(data["created"]).date().isoformat()
    assert math.isclose(s["change"],row["history"][-1][1]-row["history"][-2][1])
    assert row["url"].startswith("https://") and row["basis"]
    if row["group"]=="Sectors": observed.add(row["symbol"])
    if row["group"]=="Futures": assert row.get("contract"),row["symbol"]
assert len(observed)==11, "All eleven sector ETFs are required for the core edition"
assert any(r["id"]=="spx" for r in rows)
assert len(data["curve"]["rows"])>1 and data["macro"].get("regime"),"Missing analytical context"
readme=(root/"README.md").read_text()
assert data["created"] in readme
for path in re.findall(r'\]\(([^)#]+)\)',readme):
    if not path.startswith(("http://","https://")):
        assert (root/path).exists(),path
for name in ["banner","sectors","curve"]: ElementTree.parse(root/f"assets/{name}.svg")
html=(root/"dashboard/observatory.html").read_text()
embedded=re.search(r'<script id="data" type="application/json">(.*?)</script>',html,re.S)
assert json.loads(embedded[1])==data
ledger=(root/"CADENCE.md").read_text().splitlines()[-1]
archive=re.search(r'\[snapshot\]\((.*?)\)',ledger)[1]
assert json.loads((root/archive).read_text())==data
print(f"Verified {len(rows)} rows, 11 sectors, 3 charts, archive, links and offline edition.")
