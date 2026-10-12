from __future__ import annotations

from pathlib import Path

from pt2vhf_aprs import updater


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v1426_win7_starts_as_desktop_app():
    launcher = read("windows_legacy_app.py")
    requirements = read("requirements-windows7.txt")
    spec = read("windows/PT2VHF_APRS_Client_Win7_Legacy.spec")
    windows_app = read("windows_app.py")
    assert 'PT2VHF_WIN7_LEGACY"] = "1"' in launcher
    assert 'PT2VHF_WEBVIEW_GUI' in launcher
    assert 'sys.argv.append("--browser")' not in launcher
    assert "pywebview==4.4.1" in requirements
    assert "pythonnet==3.0.3" in requirements
    assert 'collect_submodules("webview")' in spec
    assert 'excludes=[]' in spec
    assert 'legacy = os.getenv("PT2VHF_WIN7_LEGACY") == "1"' in windows_app
    assert "o navegador não será aberto automaticamente" in windows_app


def test_v1426_legacy_updater_assets_and_portable_in_place(monkeypatch):
    monkeypatch.setattr(updater, "_machine", lambda: "x86_64")
    monkeypatch.setattr(updater, "current_update_mode", lambda: "windows-legacy-portable")
    assert updater.desired_asset_name("1.14.26") == "PT2VHF_APRS_Client_Win7_Legacy_Portable_x64_v1.14.26.exe"
    monkeypatch.setattr(updater, "current_update_mode", lambda: "windows-legacy-installer")
    assert updater.desired_asset_name("1.14.26") == "PT2VHF_APRS_Client_Setup_Win7_Legacy_x64_v1.14.26.exe"
    source = read("pt2vhf_aprs/updater.py")
    assert 'mode in {"windows-legacy-portable", "windows-legacy-installer"}' in source
    assert "destination = current" in source


def test_v1426_web_lan_opens_and_copies_separately():
    html = read("pt2vhf_aprs/templates/index.html")
    js = read("pt2vhf_aprs/static/js/app.js")
    assert 'id="webAccessStatus"' in html
    assert 'id="webAccessCopyButton"' in html
    assert "async function openWebAccessUrl" in js
    assert "window.pywebview?.api?.open_external" in js
    assert "navigator.clipboard.writeText(url)" in js


def test_v1426_lan_diagnostics_and_firewall_are_explicit():
    web = read("pt2vhf_aprs/web.py")
    module = read("pt2vhf_aprs/lan_access.py")
    html = read("pt2vhf_aprs/templates/index.html")
    assert '/api/local-interface/firewall/allow' in web
    assert "lan_diagnostics(local_info)" in web
    assert 'id="lanFirewallButton"' in html
    assert "profile=private" in module
    assert 'ShellExecuteW(None, "runas", "netsh.exe"' in module
    assert "UPnP" not in module


def test_v1426_lan_ip_detection_rejects_loopback_and_link_local():
    source = read("pt2vhf_aprs/local_server.py")
    assert "addr.is_loopback" in source
    assert "addr.is_unspecified" in source
    assert "addr.is_link_local" in source
    assert "is_private" in source


def test_v1426_i18n_patch_covers_all_extra_locales():
    patch = read("pt2vhf_aprs/static/js/i18n_v1426.js")
    for locale in ("es", "fr", "de-DE", "it-IT", "ja-JP", "pl-PL", "nl-NL", "zh-CN"):
        assert f"'{locale}':" in patch or f"{locale}:" in patch
    assert "Autorizar no Firewall do Windows" in patch
    assert "Abrir endereço LAN no navegador padrão" in patch


def test_v1426_release_metadata():
    assert read("VERSION").strip() == "1.14.26"
    assert '__version__ = "1.14.26"' in read("pt2vhf_aprs/__init__.py")
    assert "## 1.14.26 - 2026-10-11" in read("CHANGELOG.md")
    assert '"1.14.26": {' in read("pt2vhf_aprs/version_notes.py")
    assert not any(line.startswith("## Novo —") for line in read("BACKLOG.md").splitlines())
