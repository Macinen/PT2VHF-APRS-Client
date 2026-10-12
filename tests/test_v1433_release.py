"""Regressões Web/Windows v1.14.33: configurações, presença e alertas."""
from __future__ import annotations

import json
from pathlib import Path

from pt2vhf_aprs import database as db, lan_access, local_server

ROOT = Path(__file__).resolve().parents[1]


def src(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_lan_default_enabled_without_automatic_extra_browser():
    assert db.DEFAULT_CONFIG["web_lan_enabled"] == 1
    assert db.DEFAULT_CONFIG["open_browser_on_start"] == 0
    source = src("pt2vhf_aprs/database.py")
    assert "web_lan_enabled INTEGER NOT NULL DEFAULT 1" in source
    assert "ALTER TABLE config ADD COLUMN web_lan_enabled INTEGER NOT NULL DEFAULT 1" in source
    assert "UPDATE config SET web_lan_enabled=1" not in source


def test_browser_prefers_active_lan_with_safe_fallback(tmp_path, monkeypatch):
    runtime = tmp_path / "runtime.json"
    monkeypatch.setattr(local_server, "runtime_file_for", lambda _: runtime)
    monkeypatch.setattr(local_server, "read_runtime_url", lambda _: "http://127.0.0.1:8808")

    class Socket:
        def __enter__(self): return self
        def __exit__(self, *_args): return None

    calls = []
    def connection(addr, timeout=0):
        calls.append(addr)
        return Socket()

    monkeypatch.setattr(local_server.socket, "create_connection", connection)
    runtime.write_text(json.dumps({"scope": "lan", "port": 8808, "lan_ip": "192.168.5.21"}))
    assert local_server.read_runtime_browser_url(tmp_path) == "http://192.168.5.21:8808"
    assert calls[-1] == ("192.168.5.21", 8808)
    runtime.write_text(json.dumps({"scope": "local", "port": 8808, "lan_ip": "192.168.5.21"}))
    assert local_server.read_runtime_browser_url(tmp_path) == "http://127.0.0.1:8808"
    runtime.write_text(json.dumps({"scope": "lan", "port": 8808, "lan_ip": "invalid"}))
    assert local_server.read_runtime_browser_url(tmp_path) == "http://127.0.0.1:8808"


def test_remote_web_presence_requires_valid_guest_and_expires():
    with lan_access._web_presence_lock:
        lan_access._web_presence.clear()
    hosts = ["192.168.5.21"]
    try:
        assert not lan_access.mark_remote_web_presence("127.0.0.1", "browser123", True, hosts)
        assert not lan_access.mark_remote_web_presence("192.168.5.21", "browser123", True, hosts)
        assert not lan_access.mark_remote_web_presence("192.168.5.60", "short", True, hosts)
        assert not lan_access.remote_web_presence()["remote_web_active"]
        assert lan_access.mark_remote_web_presence("192.168.5.60", "browser123", True, hosts)
        assert lan_access.remote_web_presence()["remote_web_active_count"] == 1
        with lan_access._web_presence_lock:
            lan_access._web_presence["192.168.5.60:browser123"] -= 120
        assert not lan_access.remote_web_presence()["remote_web_active"]
        assert lan_access.mark_remote_web_presence("192.168.5.60", "browser123", True, hosts)
        assert lan_access.mark_remote_web_presence("192.168.5.60", "browser123", False, hosts)
        assert not lan_access.remote_web_presence()["remote_web_active"]
    finally:
        with lan_access._web_presence_lock:
            lan_access._web_presence.clear()


def test_web_presence_and_visible_alert_control():
    web = src("pt2vhf_aprs/web.py")
    js = src("pt2vhf_aprs/static/js/app.js")
    css = src("pt2vhf_aprs/static/css/app.css")
    alert_js = src("pt2vhf_aprs/static/js/v190.js")
    assert '@app.post("/api/local-interface/presence")' in web
    assert "sendWebPresence(true)" in js
    assert "header.classList.toggle('remote-active', remoteActive)" in js
    assert "remote_web_active" in js
    assert ".web-access-status.remote-active" in css
    assert "background: #ffa726" in css
    assert "color: #000" in css
    assert "Desmarque Estação apareceu para silenciar" in alert_js
    assert "settingsForm.insertBefore(card,retentionCard)" in alert_js
    assert "data-v190-alert" in alert_js
    assert "station_appeared" in alert_js


def test_windows_ico_has_real_per_size_aprs_variants(tmp_path, monkeypatch):
    from PIL import Image
    from windows import make_icon as icon
    assert icon.SIZES == (16, 24, 32, 48, 64, 128, 256)
    monkeypatch.setattr(icon, "OUTPUT", tmp_path / "test.ico")
    icon.main()
    with Image.open(icon.OUTPUT) as result:
        assert set(icon.SIZES).issubset({size[0] for size in result.ico.sizes()})
        for size in icon.SIZES:
            frame = result.ico.getimage((size, size))
            assert frame.mode == "RGBA"
            assert frame.getbbox() is not None
    app = src("windows_app.py")
    assert "src.ico.getimage(preferred)" in app
