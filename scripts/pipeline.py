"""Transactional edition publication and durable, bounded per-run audit records."""
import argparse
import base64
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

from cadence import ROOT, ZONE, slot_decision, source_freshness

GENERATED = ("README.md", "CADENCE.md", "assets", "dashboard", "editions")
SITE_URL = "https://ankitv25.github.io/Market-Observatory/"
REPO = os.environ.get("GITHUB_REPOSITORY", "ankitv25/Market-Observatory")
STATE = Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir())) / "market-pipeline-state.json"


def timestamp():
    return datetime.now(ZONE).isoformat(timespec="seconds")


def json_write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)+"\n")


def immutable_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Attempt to replace immutable artifact {path}")
        return
    with path.open("xb") as output:
        output.write(data)


def command(args, cwd=ROOT):
    completed = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.stdout:
        print(completed.stdout[-5000:], flush=True)
    if completed.returncode:
        raise RuntimeError(" ".join(args[:3])+": "+completed.stdout[-1600:])
    return completed.stdout.strip()


class Journal:
    def __init__(self, kind, root=None):
        self.root = root or ROOT
        started = timestamp()
        run_id = os.environ.get("GITHUB_RUN_ID") or datetime.now(ZONE).strftime("%Y%m%dT%H%M%S%f")
        attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
        self.data = dict(kind=kind, run_id=run_id, attempt=attempt, event=os.environ.get("GITHUB_EVENT_NAME", "local"),
                         started=started, finished=None, status="running", stages=[],
                         run_url=f"https://github.com/{REPO}/actions/runs/{run_id}" if os.environ.get("GITHUB_RUN_ID") else None)
        self.path = Path("runs") / started[:7] / f"{kind}-{run_id}-{attempt}.json"

    def save_state(self):
        json_write(STATE, dict(path=str(self.path), data=self.data))

    @classmethod
    def resume(cls):
        value = json.loads(STATE.read_text())
        journal = cls(value["data"]["kind"])
        journal.path = Path(value["path"])
        journal.data = value["data"]
        return journal

    def stage(self, name, function):
        step = dict(name=name, status="running", started=timestamp())
        self.data["stages"].append(step)
        self.save_state()
        try:
            result = function()
            step["status"] = "success"
            return result
        except Exception as error:
            step.update(status="failed", error=str(error)[-1800:])
            raise
        finally:
            step["finished"] = timestamp()
            self.save_state()

    def skipped(self, name, reason):
        self.data["stages"].append(dict(name=name, status="skipped", started=timestamp(), finished=timestamp(), reason=reason))
        self.save_state()

    def finish(self, status):
        self.data.update(status=status, finished=timestamp())
        self.save_state()
        json_write(self.root / self.path, self.data)


def compact_metadata(records, limit=40):
    records.sort(key=lambda r: r.get("started", ""), reverse=True)
    recent = records[:limit]
    return dict(checked_at=timestamp(), recent=recent, counts_scope="recent",
                last_success={kind: next((r for r in records if r.get("kind")==kind and r.get("status")=="success"),None) for kind in ("refresh","pages")},
                last_outcome={kind: next((r for r in records if r.get("kind")==kind and r.get("status")!="skipped"),None) for kind in ("refresh","pages")},
                counts={status: sum(r.get("status") == status for r in recent) for status in ("success", "failed", "skipped")},
                archive=f"https://github.com/{REPO}/tree/main/runs",
                live_url=f"https://raw.githubusercontent.com/{REPO}/main/runs/latest.json")


def pipeline_metadata(root=ROOT, limit=40):
    records = []
    for path in (root / "runs").glob("*/*.json"):
        try:
            record = json.loads(path.read_text())
            if "stages" in record:
                records.append(record)
        except (OSError, ValueError):
            continue
    return compact_metadata(records, limit)


def persist_summary(record):
    """Compare-and-swap the bounded reader feed, retaining concurrent run records."""
    with tempfile.TemporaryDirectory() as temporary:
        request = Path(temporary) / "summary.json"
        for attempt in range(4):
            result = subprocess.run(["gh", "api", f"repos/{REPO}/contents/runs/latest.json?ref=main"],
                                    text=True, capture_output=True)
            if result.returncode and "404" not in result.stderr:
                raise RuntimeError("Cannot read the existing run summary: "+result.stderr[-600:])
            previous = json.loads(result.stdout) if not result.returncode else None
            saved = json.loads(base64.b64decode(previous["content"])) if previous else {}
            records = saved.get("recent",[])
            for field in ("last_success","last_outcome"):
                for earlier in saved.get(field,{}).values():
                    if earlier and not any((r["kind"],r["run_id"],r["attempt"])==(earlier["kind"],earlier["run_id"],earlier["attempt"]) for r in records):
                        records.append(earlier)
            key = (record["kind"], record["run_id"], record["attempt"])
            records = [r for r in records if (r["kind"], r["run_id"], r["attempt"]) != key]
            summary = compact_metadata(records+[record])
            body = dict(message="Update recent pipeline outcomes", branch="main",
                        content=base64.b64encode((json.dumps(summary, ensure_ascii=False)+"\n").encode()).decode())
            if previous:
                body["sha"] = previous["sha"]
            json_write(request, body)
            try:
                command(["gh", "api", "--method", "PUT", f"repos/{REPO}/contents/runs/latest.json", "--input", str(request), "--silent"])
                json_write(ROOT / "runs/latest.json", summary)
                return
            except RuntimeError:
                if attempt == 3:
                    raise
                time.sleep(3)


def persist_file(relative, data):
    """Create one immutable blob using the Contents API, independent of local git state."""
    body = dict(message=f"Record {relative}", content=base64.b64encode(data).decode(), branch="main")
    with tempfile.TemporaryDirectory() as temporary:
        request = Path(temporary) / "request.json"
        json_write(request, body)
        for attempt in range(3):
            try:
                command(["gh", "api", "--method", "PUT", f"repos/{REPO}/contents/{relative}", "--input", str(request), "--silent"])
                return
            except RuntimeError:
                # A lost response may follow a successful write. Confirm the blob
                # before retrying without ever replacing an existing run record.
                try:
                    actual = command(["gh", "api", f"repos/{REPO}/contents/{relative}?ref=main", "--jq", ".sha"])
                    expected = hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
                    if actual == expected:
                        return
                except RuntimeError:
                    pass
                if attempt == 2:
                    raise
                time.sleep(3)


def publish_generated():
    command(["git", "config", "user.name", "github-actions[bot]"])
    command(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
    command(["git", "add", "--", *GENERATED])
    if not command(["git", "diff", "--cached", "--name-only"]):
        return
    command(["git", "commit", "-m", f"Publish market edition for run {os.environ.get('GITHUB_RUN_ID', 'local')}"])
    for attempt in range(3):
        command(["git", "fetch", "origin", "main"])
        try:
            command(["git", "rebase", "origin/main"])
        except RuntimeError:
            command(["git", "rebase", "--abort"])
            raise
        try:
            command(["git", "push", "origin", "HEAD:main"])
            return
        except RuntimeError:
            if attempt == 2:
                raise
            time.sleep(3)


def copy_verified(candidate, root=None):
    root = root or ROOT
    for name in GENERATED:
        source, target = candidate / name, root / name
        if source.is_dir():
            for path in source.rglob("*"):
                if path.is_file():
                    destination = target / path.relative_to(source)
                    if name == "editions":
                        immutable_write(destination, path.read_bytes())
                    else:
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(path, destination)
        elif source.exists():
            shutil.copy2(source, target)


def retain_candidate(candidate, journal, attempt):
    path = candidate / "dashboard/latest.json"
    if not path.exists():
        return
    relative = Path("runs/candidates") / journal.data["started"][:7] / f"{journal.data['run_id']}-{journal.data['attempt']}-{attempt}.json"
    immutable_write(ROOT / relative, path.read_bytes())
    journal.data.setdefault("candidates", []).append(str(relative))


def refresh(publish=False):
    journal = Journal("refresh")
    status = "failed"
    try:
        previous = journal.stage("load previous edition", lambda: json.loads((ROOT / "dashboard/latest.json").read_text()))
        now = datetime.now(ZONE)
        decision = slot_decision(previous, now, journal.data["event"])
        journal.data.update(target=decision, sources=source_freshness(previous, now), previous_edition=previous["created"])
        if not decision["due"]:
            journal.skipped("collection", "The current slot already has a collected edition.")
            journal.skipped("validation", "Collection was skipped.")
            journal.skipped("publication", "Collection was skipped.")
            status = "skipped"
            return
        with tempfile.TemporaryDirectory(prefix="market-candidate-") as directory:
            for attempt in (1, 2):
                candidate = Path(directory) / f"attempt-{attempt}"
                def ignored(path, names):
                    return [name for name in names if name in (".git", "__pycache__", "public") or
                            (Path(path).name == "runs" and name == "candidates")]
                shutil.copytree(ROOT, candidate, ignore=ignored)
                try:
                    journal.stage(f"collection {attempt}", lambda: command([sys.executable, "scripts/refresh.py"], candidate))
                    break
                except RuntimeError:
                    retain_candidate(candidate, journal, attempt)
                    if attempt == 2:
                        raise
            edition = json.loads((candidate / "dashboard/latest.json").read_text())
            journal.data.update(edition=edition["created"], sources=source_freshness(edition, datetime.now(ZONE)))
            try:
                journal.stage("financial validation", lambda: command([sys.executable, "scripts/verify.py"], candidate))
                journal.stage("regression tests", lambda: command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], candidate))
                journal.stage("reader validation", lambda: command(["node", "tests/test_dashboard.cjs"], candidate))
            except RuntimeError:
                retain_candidate(candidate, journal, attempt)
                raise
            journal.stage("promote verified files", lambda: copy_verified(candidate))
        if publish:
            journal.stage("repository publication", publish_generated)
            journal.stage("remote verification", lambda: command([sys.executable, "scripts/verify_remote.py"]))
        else:
            journal.skipped("repository publication", "Local validation requested.")
        status = "success"
    finally:
        completed = {s["name"] for s in journal.data["stages"]}
        for name in ("financial validation", "regression tests", "reader validation", "repository publication", "remote verification"):
            if name not in completed:
                journal.skipped(name, "An earlier stage failed." if status == "failed" else "This run did not require this stage.")
        journal.finish(status)
        if publish:
            for relative in journal.data.get("candidates", []):
                persist_file(relative, (ROOT / relative).read_bytes())
            persist_file(journal.path, (ROOT / journal.path).read_bytes())
            persist_summary(journal.data)


def read_url(url):
    request = Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "Market-Observatory/1.0"})
    with urlopen(request, timeout=15) as response:
        return response.read()


def site_manifest(directory):
    return {str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(directory.rglob("*")) if path.is_file() and path.name != "manifest.json"}


def pages_prepare():
    journal = Journal("pages")
    journal.data["edition"] = json.loads((ROOT / "dashboard/latest.json").read_text())["created"]
    journal.save_state()
    def prepare():
        command([sys.executable, "scripts/verify.py"])
        public = ROOT / "public"
        public.mkdir(exist_ok=True)
        shutil.copy2(ROOT / "dashboard/observatory.html", public / "index.html")
        shutil.copy2(ROOT / "dashboard/status.json", public / "status.json")
        command([sys.executable, "scripts/build_desk_designs.py", str(public / "design/index.html")])
        manifest = site_manifest(public)
        json_write(public / "manifest.json", manifest)
        try:
            served = json.loads(read_url(SITE_URL+"manifest.json?run="+journal.data["run_id"]))
        except (OSError, URLError, ValueError):
            served = None
        identical = served == manifest
        if identical:
            try:
                actual = read_url(SITE_URL+"?run="+journal.data["run_id"])
                identical = hashlib.sha256(actual).hexdigest() == manifest["index.html"]
            except (OSError, URLError):
                identical = False
        journal.data["needs_deploy"] = not identical
        if os.environ.get("GITHUB_OUTPUT"):
            with open(os.environ["GITHUB_OUTPUT"], "a") as output:
                output.write(f"deploy={str(not identical).lower()}\n")
    journal.stage("prepare and compare served edition", prepare)


def wait_artifact():
    journal = Journal.resume()
    def wait():
        for attempt in range(20):
            try:
                result = json.loads(command(["gh", "api", f"repos/{REPO}/actions/runs/{journal.data['run_id']}/artifacts"]))
                if any(a["name"] == "github-pages" and not a.get("expired") for a in result["artifacts"]):
                    return
            except RuntimeError:
                if attempt == 19:
                    raise
            time.sleep(3)
        raise RuntimeError("The uploaded github-pages artifact is still absent from the Actions API.")
    journal.stage("artifact visibility", wait)


def pages_verify():
    journal = Journal.resume()
    expected = (ROOT / "public/index.html").read_bytes()
    manifest = json.loads((ROOT / "public/manifest.json").read_text())
    def verify():
        for attempt in range(12):
            try:
                served = read_url(SITE_URL+"?edition="+journal.data["run_id"])
                served_manifest = json.loads(read_url(SITE_URL+"manifest.json?edition="+journal.data["run_id"]))
                if hashlib.sha256(served).digest() == hashlib.sha256(expected).digest() and served_manifest == manifest:
                    return
            except (OSError, URLError, ValueError):
                pass
            time.sleep(5)
        raise RuntimeError("The served dashboard does not match the published file.")
    journal.stage("served edition verification", verify)
    journal.data["verified"] = True
    journal.save_state()


def pages_finish(publish=False):
    journal = Journal.resume() if STATE.exists() else Journal("pages")
    try:
        jobs = json.loads(command(["gh", "api", f"repos/{REPO}/actions/runs/{journal.data['run_id']}/jobs?filter=latest"]))
        # These Action steps carry their actual runner timestamps, including a
        # failed first deploy followed by a successful bounded retry.
        for job in jobs["jobs"]:
            for step in job["steps"]:
                if step.get("conclusion") and step["name"] not in {r["name"] for r in journal.data["stages"]}:
                    journal.data["stages"].append(dict(name=step["name"], status=step["conclusion"],
                        started=step["started_at"], finished=step["completed_at"],
                        log_url=job["html_url"]+f"#step:{step['number']}:1"))
    except (RuntimeError, ValueError) as error:
        journal.data["audit_note"] = str(error)[-500:]
    skipped = journal.data.get("needs_deploy") is False
    status = "skipped" if skipped else "success" if journal.data.get("verified") else "failed"
    journal.finish(status)
    if publish:
        persist_file(journal.path, (ROOT / journal.path).read_bytes())
        persist_summary(journal.data)
    if status == "failed":
        raise RuntimeError("Pages publication failed. See the recorded stage results.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("refresh", "pages-prepare", "pages-wait", "pages-verify", "pages-finish"))
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if args.action == "refresh":
        refresh(args.publish)
    elif args.action == "pages-prepare":
        pages_prepare()
    elif args.action == "pages-wait":
        wait_artifact()
    elif args.action == "pages-verify":
        pages_verify()
    else:
        pages_finish(args.publish)
