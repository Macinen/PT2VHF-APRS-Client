from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.14.30"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


assert read("VERSION").strip() == VERSION
assert '__version__ = "1.14.30"' in read("pt2vhf_aprs/__init__.py")

checks = {
    "pt2vhf_aprs/retention.py": [
        "DEFAULT_DAYS =", "def ensure_schema", "def apply_retention",
        "def start_worker", "def save_policy", "topology_edges",
        "def _delete_batch", "PERIODS =",
    ],
    "pt2vhf_aprs/web.py": [
        '"/api/local-interface/test"', '"/api/retention"',
        '"/api/retention/apply"', '"/api/retention/reset"',
        "retention.start_worker()", "lan_diagnostics(local_info,",
    ],
    "pt2vhf_aprs/lan_access.py": [
        "def tcp_listening(", "def lan_diagnostics(",
        "listening_lan", "restart-required", "remoteip=localsubnet",
        "actual_bind_host", "external_access_confirmed",
    ],
    "windows_app.py": ["if exit_code == 0:", "win7_legacy_shell_handoff"],
    "pt2vhf_aprs/templates/index.html": [
        "retentionPolicyGrid", "retentionEnabled", "applyRetentionNow",
        "testLanAccessButton",
    ],
    "pt2vhf_aprs/static/js/app.js": [
        "function buildRetentionSelectors", "async function loadRetentionInfo",
        "saveRetentionPolicy", "testLanAccessButton",
    ],
    "tests/test_v1430_release.py": [
        "test_retention_preserves_historical_links_when_station_expires",
        "test_lan_diagnostics_requires_real_ip_socket_probe",
        "test_win7_chromium_handoff_zero_does_not_trigger_fallback",
    ],
    "CHANGELOG.md": ["## 1.14.30 - 2026-10-12"],
    "README.md": ["# PT2VHF APRS Client - v1.14.30"],
    "pt2vhf_aprs/version_notes.py": ['"1.14.30": {'],
}
for path, markers in checks.items():
    content = read(path)
    for marker in markers:
        if marker not in content:
            raise SystemExit("{}: missing {}".format(path, marker))

backlog = read("BACKLOG.md")
if any(line.startswith("## Novo —") for line in backlog.splitlines()):
    raise SystemExit("Active untriaged backlog item")
print("v1.14.30 release validation OK")
