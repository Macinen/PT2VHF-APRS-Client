from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.14.27"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


if read("VERSION").strip() != VERSION:
    raise SystemExit("VERSION must be 1.14.27")
if '__version__ = "1.14.27"' not in read("pt2vhf_aprs/__init__.py"):
    raise SystemExit("package version must be 1.14.27")

checks = {
    "windows_legacy_app.py": [
        'PT2VHF_WIN7_LEGACY"] = "1"',
        "--write-version",
        "target.write_text(__version__",
    ],
    "requirements-windows7.txt": [
        "pyinstaller==5.13.2",
        "Flask==3.0.3",
        "waitress==3.0.0",
    ],
    "windows/PT2VHF_APRS_Client_Win7_Legacy.spec": [
        'hiddenimports = collect_submodules("aprslib")',
        'excludes=["webview", "clr", "pythonnet"]',
        "PT2VHF_APRS_Client_Win7_Legacy_Portable_x64",
    ],
    "windows_app.py": [
        "def _run_legacy_app_shell",
        "def _find_legacy_app_browser",
        "--app=",
        "win7_legacy_shell_started",
        "win7_legacy_shell_fallback_browser",
    ],
    "windows/installer_win7_legacy.iss": [
        '#define MyAppVersion "1.14.27"',
        'dist-win7\\PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_v{#MyAppVersion}.exe',
        "PT2VHF_APRS_Client_Win7_Legacy*.exe",
    ],
    ".github/workflows/build-production-current.yml": [
        "Remove-Item -Recurse -Force build, dist, dist-win7",
        "portable-version.txt",
        "installed-version.txt",
        "smoke-install",
        "Setup instalou versão",
    ],
    ".github/workflows/build-full-current.yml": [
        "Remove-Item -Recurse -Force build, dist, dist-win7",
        "portable-version.txt",
        "installed-version.txt",
        "smoke-install",
    ],
    "pt2vhf_aprs/updater.py": [
        "windows-legacy-portable",
        "windows-legacy-installer",
        "PT2VHF_APRS_Client_Win7_Legacy_Portable_x64",
        "PT2VHF_APRS_Client_Setup_Win7_Legacy_x64",
        "destination = current",
    ],
    "tests/test_v1427_release.py": [
        "test_v1427_win7_shell_avoids_unstable_webview_stack",
        "test_v1427_setup_uses_fresh_versioned_portable_and_kills_old_legacy",
        "test_v1427_workflow_cleans_and_probes_both_portable_and_setup",
    ],
    "CHANGELOG.md": ["## 1.14.27 - 2026-10-11"],
    "README.md": ["# PT2VHF APRS Client - v1.14.27"],
    "pt2vhf_aprs/version_notes.py": ['"1.14.27": {'],
    "docs/WINDOWS7.md": ["modo app", "--write-version", "sem pywebview/pythonnet"],
}

for path, markers in checks.items():
    text = read(path)
    for marker in markers:
        if marker not in text:
            raise SystemExit(f"{path} missing v1.14.27 marker: {marker}")

requirements = read("requirements-windows7.txt").lower()
if "pywebview" in requirements or "pythonnet" in requirements:
    raise SystemExit("Win7 Legacy must not package pywebview/pythonnet in v1.14.27")

launcher = read("windows_legacy_app.py")
if 'sys.argv.append("--browser")' in launcher:
    raise SystemExit("Win7 Legacy must not force browser mode")

backlog = read("BACKLOG.md")
if any(line.startswith("## Novo —") for line in backlog.splitlines()):
    raise SystemExit("active backlog still contains Novo items")

print("v1.14.27 release validation OK")
