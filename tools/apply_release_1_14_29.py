from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.14.29"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


if read("VERSION").strip() != VERSION:
    raise SystemExit("VERSION must be 1.14.29")
if '__version__ = "1.14.29"' not in read("pt2vhf_aprs/__init__.py"):
    raise SystemExit("package version must be 1.14.29")

checks = {
    "pt2vhf_aprs/local_server.py": [
        "def lan_host",
        "return detect_lan_ipv4()",
        "def display_url",
        '"display_url": handle.display_url',
        '"lan_ip": handle.lan_host',
        '"scope": handle.scope',
    ],
    "pt2vhf_aprs/static/js/app.js": [
        "localInfo.display_url || localInfo.share_url",
        "if (lanHost && localPort)",
        "shareUrl = `http://${lanHost}:${localPort}`",
        "lanHost ? ui('Web:', 'Web:')",
    ],
    "tests/test_v1429_release.py": [
        "test_v1429_local_bind_still_publishes_real_lan_ip",
        "test_v1429_lan_bind_publishes_shareable_real_lan_url",
        "test_v1429_frontend_uses_display_url_or_lan_ip_even_when_scope_local",
    ],
    "CHANGELOG.md": ["## 1.14.29 - 2026-10-11"],
    "README.md": ["# PT2VHF APRS Client - v1.14.29"],
    "pt2vhf_aprs/version_notes.py": ['"1.14.29": {'],
}

for path, markers in checks.items():
    text = read(path)
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"{path} missing v1.14.29 marker: {marker}")

backlog = read("BACKLOG.md")
if any(line.startswith("## Novo —") for line in backlog.splitlines()):
    raise SystemExit("active backlog still contains Novo items")

print("v1.14.29 release validation OK")
