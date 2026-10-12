"""Fail fast on incomplete v1.14.33 cross-platform release metadata."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(filename):
    return (ROOT / filename).read_text(encoding="utf-8")


assert read("VERSION").strip() == "1.14.33"
assert '__version__ = "1.14.33"' in read("pt2vhf_aprs/__init__.py")
assert "filevers=(1, 14, 33, 0)" in read("windows/version_info.txt")
assert "## 1.14.33 - 2026-10-12" in read("CHANGELOG.md")
assert '"1.14.33": {' in read("pt2vhf_aprs/version_notes.py")
assert "# PT2VHF APRS Client - v1.14.33" in read("README.md")
for path in (".github/workflows/build-production-current.yml", ".github/workflows/build-full-current.yml"):
    assert "tools/apply_release_1_14_33.py" in read(path)
for path, marker in {
    "pt2vhf_aprs/database.py": '"web_lan_enabled": 1',
    "windows_app.py": "read_runtime_browser_url",
    "pt2vhf_aprs/local_server.py": "def read_runtime_browser_url(",
    "pt2vhf_aprs/lan_access.py": "def mark_remote_web_presence(",
    "pt2vhf_aprs/web.py": '@app.post("/api/local-interface/presence")',
    "pt2vhf_aprs/static/js/app.js": "sendWebPresence(true)",
    "pt2vhf_aprs/static/css/app.css": ".web-access-status.remote-active",
    "pt2vhf_aprs/static/js/v190.js": "settingsForm.insertBefore(card,retentionCard)",
    "windows/make_icon.py": 'text = "APRS"',
    "tests/test_v1433_release.py": "test_windows_ico_has_real_per_size_aprs_variants",
}.items():
    assert marker in read(path), "{} missing {}".format(path, marker)
if any(s.startswith("## Novo —") for s in read("BACKLOG.md").splitlines()):
    raise SystemExit("Untriaged backlog entry.")
print("v1.14.33 release validation OK")
