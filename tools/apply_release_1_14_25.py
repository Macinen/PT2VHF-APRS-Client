from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.14.25"


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


if read("VERSION").strip() != VERSION:
    raise SystemExit("VERSION must be 1.14.25")

init_text = read("pt2vhf_aprs/__init__.py")
if '__version__ = "1.14.25"' not in init_text:
    raise SystemExit("package version must be 1.14.25")

checks = {
    "pt2vhf_aprs/database.py": [
        '"web_lan_enabled": 0',
        "web_lan_enabled INTEGER NOT NULL DEFAULT 0",
        'merged["web_lan_enabled"] = 1 if bool(merged["web_lan_enabled"]) else 0',
    ],
    "pt2vhf_aprs/local_server.py": [
        "def detect_lan_ipv4()",
        "def share_url(self)",
        '"share_url": handle.share_url',
        '"scope": handle.scope',
    ],
    "pt2vhf_aprs/templates/index.html": [
        'id="headerSendBeaconButton"',
        'class="btn secondary beacon-icon-button"',
        'id="webAccessStatus"',
        'name="web_lan_enabled"',
        "<strong>PY2FDG</strong>",
        "i18n_v1425.js",
    ],
    "pt2vhf_aprs/static/js/app.js": [
        "function updateWebAccessStatus",
        "navigator.clipboard.writeText(url)",
        "'de-DE': {",
        "'zh-CN': {",
        "return EXTRA_I18N[state.language]?.[pt] || pt;",
        ": EXTRA_I18N[state.language]?.[trimmed];",
    ],
    "pt2vhf_aprs/static/js/i18n_v1425.js": [
        "'de-DE':",
        "'it-IT':",
        "'ja-JP':",
        "'pl-PL':",
        "'nl-NL':",
        "'zh-CN':",
        "Permitir acesso Web pela rede local (LAN)",
    ],
    "pt2vhf_aprs/updater.py": [
        "windows-legacy-portable",
        "windows-legacy-installer",
        "PT2VHF_APRS_Client_Win7_Legacy_Portable_x64",
        "PT2VHF_APRS_Client_Setup_Win7_Legacy_x64",
    ],
    "requirements-windows7.txt": [
        "Flask==3.0.3",
        "waitress==3.0.0",
        "Pillow==10.4.0",
        "psutil==6.1.1",
        "pyinstaller==5.13.2",
    ],
    "windows_legacy_app.py": [
        'PT2VHF_WIN7_LEGACY"] = "1"',
        'sys.argv.append("--browser")',
    ],
    "windows/PT2VHF_APRS_Client_Win7_Legacy.spec": [
        'name="PT2VHF_APRS_Client_Win7_Legacy_Portable_x64"',
        'excludes=["webview", "clr", "pythonnet"]',
    ],
    "windows/installer_win7_legacy.iss": [
        "MinVersion=6.1sp1",
        "PT2VHF_APRS_Client_Setup_Win7_Legacy_x64",
    ],
    "windows/version_info.txt": [
        "filevers=(1, 14, 25, 0)",
        "prodvers=(1, 14, 25, 0)",
        "StringStruct('ProductVersion', '1.14.25')",
    ],
    ".github/workflows/build-production-current.yml": [
        "windows-win7-legacy:",
        "python-version: '3.8.10'",
        "apply_release_1_14_25.py",
    ],
    ".github/workflows/build-full-current.yml": [
        "windows-win7-legacy:",
        "python-version: '3.8.10'",
        "apply_release_1_14_25.py",
    ],
    "tests/test_v1425_release.py": [
        "test_v1425_lan_access_is_opt_in_and_runtime_has_safe_urls",
        "test_v1425_non_english_languages_do_not_silently_fall_back_to_english",
        "test_v1425_win7_legacy_assets_are_isolated",
    ],
    "CHANGELOG.md": [
        "## 1.14.25 - 2026-10-11",
        "Windows 7 Legacy",
        "Acesso Web LAN",
    ],
    "BACKLOG.md": [
        "## Implementado na v1.14.25 — Windows 7:",
        "## Implementado na v1.14.25 — Internacionalização:",
        "## Implementado na v1.14.25 — Barra superior:",
        "## Implementado na v1.14.25 — Menu superior:",
        "## Implementado na v1.14.25 — Sobre:",
    ],
    "docs/WINDOWS7.md": [
        "Windows 7 SP1 x64",
        "Python 3.8.10",
        "Windows Vista e Windows XP não são suportados",
    ],
}

for path, markers in checks.items():
    text = read(path)
    for marker in markers:
        if marker not in text:
            raise SystemExit("%s missing v1.14.25 marker: %s" % (path, marker))

html = read("pt2vhf_aprs/templates/index.html")
if 'id="themeQuickToggle"' in html:
    raise SystemExit("theme quick toggle must not remain in the top bar")

app = read("pt2vhf_aprs/static/js/app.js")
for forbidden in (
    "EXTRA_I18N[state.language]?.[pt] || en",
    "EXTRA_I18N[state.language]?.[trimmed] || EN_TEXT",
    "EXTRA_I18N[state.language]?.[original] || EN_TEXT",
):
    if forbidden in app:
        raise SystemExit("silent English fallback regression: %s" % forbidden)

print("v1.14.25 release validation OK")
