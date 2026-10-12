from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.14.32"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


if read("VERSION").strip() != VERSION:
    raise SystemExit("VERSION must be " + VERSION)
if '__version__ = "1.14.32"' not in read("pt2vhf_aprs/__init__.py"):
    raise SystemExit("package version incorrect")

checks = {
    "pt2vhf_aprs/lan_access.py": [
        "def _firewall_script", "remoteip=localsubnet", "profile=any",
        "def note_remote_request", "last_remote_request()",
        "external_access_confirmed", "CREATE_NO_WINDOW",
    ],
    "pt2vhf_aprs/local_server.py": [
        "def lan_ipv4_candidates", '"lan_ip_candidates": lan_ipv4_candidates()',
        "def detect_lan_ipv4",
    ],
    "pt2vhf_aprs/web.py": [
        "note_remote_request(request.remote_addr", "/api/local-interface/remote-probe",
        "def api_allow_local_interface_firewall",
    ],
    "pt2vhf_aprs/diagnostics.py": [
        "def start_legacy_window_diagnostics",
        "win7_transient_window_seen",
    ],
    "windows_app.py": [
        "diag.start_legacy_window_diagnostics()", "if exit_code == 0:",
    ],
    "pt2vhf_aprs/static/js/app.js": [
        "if (scope !== 'lan') shareUrl = localUrl;",
        "access.external_access_confirmed", "remote_test_urls",
    ],
    "pt2vhf_aprs/templates/index.html": [
        "use somente em uma rede de confiança",
        'id="testLanAccessButton"',
    ],
    "tools/smoke_web_http.py": ["def main()", "/static/js/app.js", "/api/local-interface/remote-probe"],
    "tests/test_v1431_lan.py": [
        "test_firewall_script_is_single_elevated_operation_and_portable",
        "test_real_lan_bind_responds_at_actual_nic_address",
        "test_remote_evidence_requires_non_loopback_request",
    ],
    "tests/test_win7_firewall_popup.py": ["test_firewall_diagnostic_uses_hidden_console_and_cache"],
    "pt2vhf_aprs/version_notes.py": ['"1.14.32": {'],
    "CHANGELOG.md": ["## 1.14.32 - 2026-10-12"],
    "README.md": ["# PT2VHF APRS Client - v1.14.32"],
}
for path, markers in checks.items():
    content = read(path)
    for marker in markers:
        if marker not in content:
            raise SystemExit(f"{path} missing marker: {marker!r}")

if any(line.startswith("## Novo —") for line in read("BACKLOG.md").splitlines()):
    raise SystemExit("New untriaged backlog items remain")

print("v1.14.32 validation OK")
