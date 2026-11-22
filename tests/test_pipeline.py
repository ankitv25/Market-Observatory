import base64
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import pipeline


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory()
        self.root=Path(self.temporary.name)/"repo"
        self.root.mkdir()
        self.state=Path(self.temporary.name)/"state.json"
        self.edition={"created":"2026-11-20T07:00:00-05:00","markets":[]}
        pipeline.json_write(self.root/"dashboard/latest.json",self.edition)
        (self.root/"README.md").write_text("old verified reader")
        self.patches=[patch.object(pipeline,"ROOT",self.root),patch.object(pipeline,"STATE",self.state),
                      patch.dict(pipeline.os.environ,{"GITHUB_EVENT_NAME":"workflow_dispatch","GITHUB_RUN_ID":"987","GITHUB_RUN_ATTEMPT":"1"})]
        for item in self.patches:item.start()

    def tearDown(self):
        for item in reversed(self.patches):item.stop()
        self.temporary.cleanup()

    def collect(self,args,cwd=None):
        if args[1:]==["scripts/refresh.py"]:
            self.assertTrue((cwd/"runs/2026-11/existing.json").exists())
            fresh=dict(self.edition,created="2026-11-20T16:31:00-05:00")
            pipeline.json_write(cwd/"dashboard/latest.json",fresh)
            pipeline.json_write(cwd/"editions/2026-11/new.json",fresh)
            (cwd/"README.md").write_text("new verified reader")
        return ""

    def seed_history(self):
        pipeline.json_write(self.root/"runs/2026-11/existing.json",{"started":"2026-11-20T05:00:00-05:00","status":"skipped","stages":[]})

    def test_invalid_candidate_keeps_published_files_and_retains_evidence(self):
        self.seed_history()
        def fail(args,cwd=None):
            if "scripts/verify.py" in args:raise RuntimeError("invalid Treasury date")
            return self.collect(args,cwd)
        with patch.object(pipeline,"command",side_effect=fail):
            with self.assertRaisesRegex(RuntimeError,"Treasury"):
                pipeline.refresh()
        self.assertEqual((self.root/"README.md").read_text(),"old verified reader")
        self.assertEqual(json.loads((self.root/"dashboard/latest.json").read_text()),self.edition)
        evidence=list((self.root/"runs/candidates").glob("*/*.json"))
        self.assertEqual(len(evidence),1)
        self.assertIn("16:31",json.loads(evidence[0].read_text())["created"])
        audit=json.loads(self.state.read_text())["data"]
        self.assertEqual(audit["status"],"failed")
        self.assertTrue(any(s.get("error")=="invalid Treasury date" for s in audit["stages"]))

    def test_retry_uses_clean_candidate_and_promotes_only_verified_output(self):
        self.seed_history()
        calls=0
        def retry(args,cwd=None):
            nonlocal calls
            if args[1:]==["scripts/refresh.py"]:
                calls+=1
                if calls==1:
                    pipeline.json_write(cwd/"editions/2026-11/rejected.json",{"bad":True})
                    raise RuntimeError("temporary transport error")
                self.assertFalse((cwd/"editions/2026-11/rejected.json").exists())
            return self.collect(args,cwd)
        with patch.object(pipeline,"command",side_effect=retry):
            pipeline.refresh()
        self.assertEqual(calls,2)
        self.assertEqual((self.root/"README.md").read_text(),"new verified reader")
        self.assertFalse((self.root/"editions/2026-11/rejected.json").exists())
        audit=json.loads(self.state.read_text())["data"]
        self.assertEqual(audit["status"],"success")
        self.assertEqual([s["status"] for s in audit["stages"] if s["name"].startswith("collection")],["failed","success"])

    def test_skipped_run_persists_without_collection(self):
        with patch.object(pipeline,"slot_decision",return_value={"due":False}),patch.object(pipeline,"command") as execute:
            pipeline.refresh()
        execute.assert_not_called()
        audit=json.loads(self.state.read_text())["data"]
        self.assertEqual(audit["status"],"skipped")
        self.assertTrue(list((self.root/"runs").glob("*/*.json")))

    def test_edition_archive_is_immutable(self):
        path=self.root/"editions/2026-11/edition.json"
        pipeline.immutable_write(path,b"original")
        pipeline.immutable_write(path,b"original")
        with self.assertRaisesRegex(ValueError,"immutable"):
            pipeline.immutable_write(path,b"changed")
        self.assertEqual(path.read_bytes(),b"original")

    def test_manifest_detects_content_changes_without_timestamp_churn(self):
        public=self.root/"public";public.mkdir()
        (public/"index.html").write_text("same")
        original=pipeline.site_manifest(public)
        pipeline.json_write(public/"manifest.json",original)
        self.assertEqual(original,pipeline.site_manifest(public))
        (public/"index.html").write_text("new")
        self.assertNotEqual(original,pipeline.site_manifest(public))

    def test_summary_conflict_merges_concurrent_records(self):
        def record(run):return dict(kind="refresh",run_id=run,attempt="1",started="2026-11-20T07:00:00-05:00",status="success")
        def response(records,sha):
            data={"sha":sha,"content":base64.b64encode(json.dumps({"recent":records}).encode()).decode()}
            return subprocess.CompletedProcess([],0,json.dumps(data),"")
        bodies=[]
        def update(args,cwd=None):
            bodies.append(json.loads(Path(args[args.index("--input")+1]).read_text()))
            if len(bodies)==1:raise RuntimeError("409 conflict")
            return ""
        with patch.object(pipeline.subprocess,"run",side_effect=[response([record("one")],"a"),response([record("two"),record("one")],"b")]),patch.object(pipeline,"command",side_effect=update),patch.object(pipeline.time,"sleep"):
            pipeline.persist_summary(record("ours"))
        payload=json.loads(base64.b64decode(bodies[-1]["content"]))
        self.assertEqual({r["run_id"] for r in payload["recent"]},{"one","two","ours"})
        self.assertEqual(bodies[-1]["sha"],"b")

    def test_last_success_survives_the_recent_record_limit(self):
        records=[dict(kind="refresh",run_id="good",attempt="1",started="2026-11-20T07:00:00-05:00",status="success")]
        records += [dict(kind="refresh",run_id=str(i),attempt="1",started=f"2026-11-21T07:{i:02}:00-05:00",status="skipped") for i in range(50)]
        result=pipeline.compact_metadata(records)
        self.assertEqual(len(result["recent"]),40)
        self.assertEqual(result["last_success"]["refresh"]["run_id"],"good")
        self.assertEqual(result["last_outcome"]["refresh"]["run_id"],"good")

    def test_metadata_bounds_recent_records(self):
        for i in range(50):
            pipeline.json_write(self.root/f"runs/2026-11/run-{i}.json",dict(stages=[],started=f"2026-11-20T07:{i:02}:00-05:00",status="success"))
        data=pipeline.pipeline_metadata(self.root)
        self.assertEqual(len(data["recent"]),40)
        self.assertEqual(data["counts"]["success"],40)
        self.assertIn("runs/latest.json",data["live_url"])

    def test_identical_served_edition_skips_deployment_but_checks_actual_html(self):
        (self.root/"dashboard/observatory.html").write_text("published dashboard")
        pipeline.json_write(self.root/"dashboard/status.json",{"created":self.edition["created"]})
        def build(args,cwd=None):
            if "scripts/build_desk_designs.py" in args:
                output=Path(args[-1]);output.parent.mkdir(parents=True,exist_ok=True)
                output.write_text("design")
            return ""
        def served(url):
            if "manifest.json" in url:
                return json.dumps(pipeline.site_manifest(self.root/"public")).encode()
            return b"published dashboard"
        with patch.object(pipeline,"command",side_effect=build),patch.object(pipeline,"read_url",side_effect=served) as fetch:
            pipeline.pages_prepare()
        self.assertFalse(json.loads(self.state.read_text())["data"]["needs_deploy"])
        self.assertEqual(fetch.call_count,2)
        with patch.object(pipeline,"command",return_value='{"jobs":[]}'):
            pipeline.pages_finish()
        self.assertEqual(json.loads(self.state.read_text())["data"]["status"],"skipped")

    def test_artifact_visibility_race_is_retried(self):
        journal=pipeline.Journal("pages");journal.save_state()
        with patch.object(pipeline,"command",side_effect=['{"artifacts":[]}','{"artifacts":[{"name":"github-pages","expired":false}]}']) as query,patch.object(pipeline.time,"sleep"):
            pipeline.wait_artifact()
        self.assertEqual(query.call_count,2)
        self.assertEqual(json.loads(self.state.read_text())["data"]["stages"][-1]["status"],"success")


if __name__ == "__main__":
    unittest.main()
