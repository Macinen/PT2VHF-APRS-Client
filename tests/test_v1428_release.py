from __future__ import annotations

from pathlib import Path

from pt2vhf_aprs import local_server


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v1428_header_is_passive_and_has_no_copy_button_or_literal_newline():
    html = read("pt2vhf_aprs/templates/index.html")
    js = read("pt2vhf_aprs/static/js/app.js")
    css = read("pt2vhf_aprs/static/css/app.css")

    assert '<div id="webAccessStatus" class="web-access-status"' in html
    assert 'id="webAccessCopyButton"' not in html
    assert "\\n    <button id=\"webAccessCopyButton\"" not in html
    assert "webAccessCopyButton" not in js
    assert "openWebAccessUrl" not in js
    assert "navigator.clipboard.writeText(url)" not in js
    assert ".web-access-copy" not in css


def test_v1428_lan_runtime_publishes_real_host_and_share_url(monkeypatch):
    monkeypatch.setattr(local_server, "detect_lan_ipv4", lambda: "192.168.10.2")
    handle = local_server.LocalServerHandle(
        server=object(),
        server_kind="test",
        host="0.0.0.0",
        port=8080,
        start_port=8080,
    )
    assert handle.local_host == "127.0.0.1"
    assert handle.lan_host == "192.168.10.2"
    assert handle.share_url == "http://192.168.10.2:8080"
    assert handle.scope == "lan"

    local_server._set_runtime(handle)
    info = local_server.runtime_info()
    assert info["bind_host"] == "0.0.0.0"
    assert info["host"] == "127.0.0.1"
    assert info["display_host"] == "192.168.10.2"
    assert info["lan_ip"] == "192.168.10.2"
    assert info["share_url"] == "http://192.168.10.2:8080"
    assert info["scope"] == "lan"


def test_v1428_frontend_prioritizes_lan_host_over_loopback():
    js = read("pt2vhf_aprs/static/js/app.js")
    assert "const lanHost = String(localInfo.lan_ip || localInfo.lan_host || '').trim();" in js
    assert "lanHost && localPort" in js
    assert "if (scope === 'lan') shareUrl = lanCandidate;" in js
    assert "if (scope !== 'lan') shareUrl = localUrl;" in js


def test_v1428_browser_opening_is_controlled_by_configuration():
    html = read("pt2vhf_aprs/templates/index.html")
    app = read("windows_app.py")
    assert 'name="open_browser_on_start"' in html
    assert "Abrir também no navegador ao iniciar" in html
    assert 'db.get_config().get("open_browser_on_start")' in app
    assert "_open_browser()" in app


def test_v1428_release_metadata_and_backlog():
    assert tuple(map(int, read("VERSION").strip().split("."))) >= (1, 14, 28)
    assert '"1.14.28": {' in read("pt2vhf_aprs/version_notes.py")
    assert "## 1.14.28 - 2026-10-11" in read("CHANGELOG.md")
    assert '"1.14.28": {' in read("pt2vhf_aprs/version_notes.py")
    assert not any(line.startswith("## Novo —") for line in read("BACKLOG.md").splitlines())
