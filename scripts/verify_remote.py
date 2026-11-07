"""Read the published branch back through the GitHub API and verify its blobs."""
import hashlib
import os
from pathlib import Path
import subprocess

repo = os.environ["GITHUB_REPOSITORY"]
for name in ["README.md", "dashboard/latest.json", "assets/banner.svg", "CADENCE.md"]:
    remote = subprocess.check_output(
        ["gh", "api", f"repos/{repo}/contents/{name}?ref=main", "--jq", ".sha"], text=True
    ).strip()
    data = Path(name).read_bytes()
    expected = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if remote != expected:
        raise SystemExit(f"Published file differs from compiled edition: {name}")
    print(f"Verified {name} at {remote}")
