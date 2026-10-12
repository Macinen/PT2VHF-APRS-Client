from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.14.28"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


if read("VERSION").strip() != VERSION:
    raise SystemExit("VERSION must be 1.14.28")
if '__version__ = "1.14.28"' not in read("pt2vhf_aprs/__init__.py"):
    raise SystemExit("package version must be 1.14.28")

checks = {
    "pt2vhf_aprs/templates/index.html": [
        '<div id="webAccessStatus" class="web-access-status"',
        'id="webAccessUrl"',
        'name="open_browser_on_start"',
        'name="web_lan_enabled"',
    ],
    "pt2vhf_aprs/static/js/app.js": [
        "function updateWebAccessStatus",
        "localInfo.lan_ip",
        "reportedScope === 'lan' && lanHost && localPort",
        "127\\.|0\\.0\\.0\\.0",
    ],
    "pt2vhf_aprs/local_server.py": [
        '"display_host": handle.lan_host or handle.local_host',
        '"lan_ip": handle.lan_host',
        '"share_url": handle.share_url',
        '"scope": handle.scope',
    ],
    "windows_app.py": [
        'db.get_config().get("open_browser_on_start")',
        "_open_browser()",
    ],
    "tests/test_v1428_release.py": [
        "test_v1428_header_is_passive_and_has_no_copy_button_or_literal_newline",
        "test_v1428_lan_runtime_publishes_real_host_and_share_url",
        "test_v1428_frontend_prioritizes_lan_host_over_loopback",
    ],
    "CHANGELOG.md": ["## 1.14.28 - 2026-10-11"],
    "README.md": ["# PT2VHF APRS Client - v1.14.28"],
    "pt2vhf_aprs/version_notes.py": ['"1.14.28": {'],
}

for path, markers in checks.items():
    text = read(path)
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"{path} missing v1.14.28 marker: {marker}")

html = read("pt2vhf_aprs/templates/index.html")
js = read("pt2vhf_aprs/static/js/app.js")
css = read("pt2vhf_aprs/static/css/app.css")
if 'webAccessCopyButton' in html or 'webAccessCopyButton' in js:
    raise SystemExit("copy button must not exist in v1.14.28")
if "\\n    <button" in html:
    raise SystemExit("literal newline escape remains in header markup")
if "openWebAccessUrl" in js or "navigator.clipboard.writeText(url)" in js:
    raise SystemExit("header web address must not be interactive")
if ".web-access-copy" in css:
    raise SystemExit("obsolete copy-button CSS remains")

backlog = read("BACKLOG.md")
if any(line.startswith("## Novo —") for line in backlog.splitlines()):
    raise SystemExit("active backlog still contains Novo items")

print("v1.14.28 release validation OK")
