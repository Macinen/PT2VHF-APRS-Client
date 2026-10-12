from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.14.26"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


if read("VERSION").strip() != VERSION:
    raise SystemExit("VERSION must be 1.14.26")
if '__version__ = "1.14.26"' not in read("pt2vhf_aprs/__init__.py"):
    raise SystemExit("package version must be 1.14.26")

checks = {
    "windows_legacy_app.py": [
        'PT2VHF_WIN7_LEGACY"] = "1"',
        "PT2VHF_WEBVIEW_GUI",
    ],
    "requirements-windows7.txt": [
        "pywebview==4.4.1",
        "pythonnet==3.0.3",
        "pyinstaller==5.13.2",
    ],
    "windows/PT2VHF_APRS_Client_Win7_Legacy.spec": [
        'collect_submodules("webview")',
        'excludes=[]',
        'PT2VHF_APRS_Client_Win7_Legacy_Portable_x64',
    ],
    "windows_app.py": [
        'legacy = os.getenv("PT2VHF_WIN7_LEGACY") == "1"',
        'PT2VHF_WEBVIEW_GUI',
        "o navegador não será aberto automaticamente",
    ],
    "pt2vhf_aprs/updater.py": [
        "windows-legacy-portable",
        "windows-legacy-installer",
        "PT2VHF_APRS_Client_Win7_Legacy_Portable_x64",
        "PT2VHF_APRS_Client_Setup_Win7_Legacy_x64",
        "destination = current",
    ],
    "pt2vhf_aprs/local_server.py": [
        "addr.is_loopback",
        "addr.is_unspecified",
        "addr.is_link_local",
        "addr.is_private",
    ],
    "pt2vhf_aprs/lan_access.py": [
        "FIREWALL_RULE_NAME",
        "profile=private",
        "ShellExecuteW",
        "lan_diagnostics",
    ],
    "pt2vhf_aprs/web.py": [
        "lan_diagnostics(local_info)",
        '/api/local-interface/firewall/allow',
    ],
    "pt2vhf_aprs/templates/index.html": [
        'id="webAccessStatus"',
        'id="webAccessCopyButton"',
        'id="lanFirewallButton"',
        "i18n_v1426.js",
    ],
    "pt2vhf_aprs/static/js/app.js": [
        "async function openWebAccessUrl",
        "window.pywebview?.api?.open_external",
        "navigator.clipboard.writeText(url)",
        "/api/local-interface/firewall/allow",
    ],
    "pt2vhf_aprs/static/js/i18n_v1426.js": [
        "'de-DE':",
        "'it-IT':",
        "'ja-JP':",
        "'pl-PL':",
        "'nl-NL':",
        "'zh-CN':",
        "Autorizar no Firewall do Windows",
    ],
    "tests/test_v1426_release.py": [
        "test_v1426_win7_starts_as_desktop_app",
        "test_v1426_legacy_updater_assets_and_portable_in_place",
        "test_v1426_web_lan_opens_and_copies_separately",
        "test_v1426_lan_diagnostics_and_firewall_are_explicit",
    ],
    "CHANGELOG.md": ["## 1.14.26 - 2026-10-11"],
    "README.md": ["# PT2VHF APRS Client - v1.14.26"],
    "pt2vhf_aprs/version_notes.py": ['"1.14.26": {'],
    "docs/WINDOWS7.md": ["pywebview 4.4.1", "janela desktop", "Portable substitui o executável"],
}

for path, markers in checks.items():
    text = read(path)
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"{path} missing v1.14.26 marker: {marker}")

launcher = read("windows_legacy_app.py")
if 'sys.argv.append("--browser")' in launcher:
    raise SystemExit("Win7 Legacy must not force browser mode")

backlog = read("BACKLOG.md")
if any(line.startswith("## Novo —") for line in backlog.splitlines()):
    raise SystemExit("active backlog still contains Novo items")

print("v1.14.26 release validation OK")
