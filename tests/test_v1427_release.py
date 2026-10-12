from __future__ import annotations

from pathlib import Path

from pt2vhf_aprs import updater


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v1427_win7_shell_avoids_unstable_webview_stack():
    req = read("requirements-windows7.txt").lower()
    spec = read("windows/PT2VHF_APRS_Client_Win7_Legacy.spec")
    launcher = read("windows_legacy_app.py")
    app = read("windows_app.py")
    assert "pywebview" not in req
    assert "pythonnet" not in req
    assert 'excludes=["webview", "clr", "pythonnet"]' in spec
    assert 'PT2VHF_WIN7_LEGACY"] = "1"' in launcher
    assert "--write-version" in launcher
    assert "def _run_legacy_app_shell" in app
    assert "def _find_legacy_app_browser" in app
    assert "--app=" in app
    assert "win7_legacy_shell_fallback_browser" in app


def test_v1427_setup_uses_fresh_versioned_portable_and_kills_old_legacy():
    installer = read("windows/installer_win7_legacy.iss")
    assert 'Source: "..\\dist-win7\\PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_v{#MyAppVersion}.exe"' in installer
    assert 'DestName: "{#MyAppExeName}"' in installer
    assert 'PT2VHF_APRS_Client_Win7_Legacy*.exe' in installer
    assert "Sleep(900)" in installer


def test_v1427_workflow_cleans_and_probes_both_portable_and_setup():
    for path in (".github/workflows/build-production-current.yml", ".github/workflows/build-full-current.yml"):
        workflow = read(path)
        assert "Remove-Item -Recurse -Force build, dist, dist-win7" in workflow
        assert "--write-version" in workflow
        assert "portable-version.txt" in workflow
        assert "installed-version.txt" in workflow
        assert "smoke-install" in workflow
        assert "Setup instalou versão" in workflow


def test_v1427_legacy_updater_assets_remain_isolated(monkeypatch):
    monkeypatch.setattr(updater, "_machine", lambda: "x86_64")
    monkeypatch.setattr(updater, "current_update_mode", lambda: "windows-legacy-portable")
    assert updater.desired_asset_name("1.14.27") == "PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_v1.14.27.exe"
    monkeypatch.setattr(updater, "current_update_mode", lambda: "windows-legacy-installer")
    assert updater.desired_asset_name("1.14.27") == "PT2VHF_APRS_Client_Setup_Win7_Legacy_x64_v1.14.27.exe"


def test_v1427_release_metadata_and_backlog():
    assert read("VERSION").strip() == "1.14.27"
    assert '__version__ = "1.14.27"' in read("pt2vhf_aprs/__init__.py")
    assert "## 1.14.27 - 2026-10-11" in read("CHANGELOG.md")
    assert '"1.14.27": {' in read("pt2vhf_aprs/version_notes.py")
    assert not any(line.startswith("## Novo —") for line in read("BACKLOG.md").splitlines())
