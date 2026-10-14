"""Smoke-check the generated application tracker UI and JavaScript."""
from pathlib import Path
import re
import subprocess
import tempfile

html = (Path(__file__).resolve().parents[1] / "_site" / "index.html").read_text(encoding="utf-8")
assert 'id="exportTracker"' in html, "Missing application tracker export button"
scripts = re.findall(r"<script(?:\s[^>]*)?>([\s\S]*?)</script>", html)
assert scripts, "No JavaScript found in generated page"
js = scripts[-1]
for marker in (
    "TRACKER_COLUMNS",
    "Application Status",
    "Private Notes",
    "Job posting URL",
    "Follow-up date",
    "currentRows=rows",
    "String.fromCharCode(0xFEFF)",
):
    assert marker in js, f"Missing CSV export feature: {marker}"

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "index.js"
    path.write_text(js, encoding="utf-8")
    subprocess.run(["node", "--check", str(path)], check=True)

print("Application tracker export smoke check passed.")
