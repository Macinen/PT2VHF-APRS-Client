from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from pt2vhf_aprs import database as db, retention, lan_access
import windows_app


def test_retention_preserves_historical_links_when_station_expires(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "retention.db")
    db.init_db()
    retention.ensure_schema()
    old = "2024-01-01T00:00:00+00:00"
    with db.connection() as conn:
        conn.execute("""INSERT INTO stations(callsign,last_heard,symbol)
                        VALUES('PT2OLD',?,'>')""", (old,))
        conn.execute("""INSERT INTO topology_edges
                        (source,target,kind,first_seen,last_seen)
                        VALUES('PT2OLD','PT2NEXT','rf',?,?)""", (old, old))
        conn.execute("""INSERT INTO messages
                        (direction,from_call,to_call,message,message_type,status,timestamp)
                        VALUES('in','PT2OLD','PT2NEXT','teste','message','received',?)""", (old,))
        conn.execute("""INSERT INTO messages
                        (direction,from_call,to_call,message,message_type,status,timestamp)
                        VALUES('in','BLN1','PT2NEXT','boletim','bulletin','received',?)""", (old,))
        conn.execute("""INSERT INTO messages
                        (direction,from_call,to_call,message,message_type,status,timestamp)
                        VALUES('in','PT2OLD','CQ','grupo','group','received',?)""", (old,))
    retention.save_policy({
        "stations": 1, "rf_links": 0, "messages": 1,
        "bulletins": 1, "groups": 1,
    }, enabled=True)
    result = retention.apply_retention(batch_size=100, max_batches=16)
    assert result["ok"]
    with db.connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM stations WHERE callsign='PT2OLD'").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM topology_edges WHERE source='PT2OLD'").fetchone()[0] == 1
        assert conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 0


def test_retention_never_expires_rf_link_when_permanent(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "permanent.db")
    db.init_db()
    retention.ensure_schema()
    with db.connection() as conn:
        conn.execute("""INSERT INTO topology_edges
                        (source,target,kind,first_seen,last_seen)
                        VALUES('P1','P2','rf','2020-01-01','2020-01-01')""")
    retention.save_policy({"rf_links": 0}, enabled=True)
    retention.apply_retention()
    with db.connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM topology_edges").fetchone()[0] == 1


def test_lan_diagnostics_requires_real_ip_socket_probe(monkeypatch):
    calls = []
    monkeypatch.setattr(lan_access, "tcp_listening",
                        lambda port, host="127.0.0.1": calls.append(host) or host == "192.168.50.2")
    monkeypatch.setattr(lan_access, "windows_firewall_rule_exists", lambda: None)
    runtime = {"bind_host": "0.0.0.0", "scope": "lan", "port": 8080,
               "lan_ip": "192.168.50.2", "share_url": "http://192.168.50.2:8080"}
    status = lan_access.lan_diagnostics(runtime, True)
    assert status["listening_lan"] is True
    assert "192.168.50.2" in calls
    assert status["external_access_confirmed"] is False
    runtime.update(bind_host="127.0.0.1", scope="local")
    status = lan_access.lan_diagnostics(runtime, True)
    assert status["state"] == "restart-required"


def test_win7_chromium_handoff_zero_does_not_trigger_fallback(monkeypatch, tmp_path):
    class P:
        pid = 123
        returncode = 0
        def poll(self):
            return 0
    events = []
    monkeypatch.setattr(windows_app.db, "DB_PATH", tmp_path / "client.db")
    monkeypatch.setattr(windows_app, "_find_legacy_app_browser",
                        lambda: tmp_path / "chrome.exe")
    monkeypatch.setattr(windows_app, "_current_url", lambda: "http://127.0.0.1:8080")
    monkeypatch.setattr(windows_app.subprocess, "Popen", lambda *a, **kw: P())
    monkeypatch.setattr(windows_app.time, "sleep", lambda *args: None)
    monkeypatch.setattr(windows_app.diag, "log_event",
                        lambda event, **kw: events.append(event))
    monkeypatch.setattr(windows_app.webbrowser, "open",
                        lambda *a, **kw: (_ for _ in ()).throw(AssertionError("fallback")))
    assert windows_app._launch_legacy_app_window()
    assert "win7_legacy_shell_handoff" in events


def test_config_retention_and_lan_controls_exist():
    root = Path(__file__).resolve().parents[1]
    html = (root / "pt2vhf_aprs/templates/index.html").read_text(encoding="utf-8")
    js = (root / "pt2vhf_aprs/static/js/app.js").read_text(encoding="utf-8")
    for value in ("retentionPolicyGrid", "retentionEnabled", "saveRetentionPolicy",
                  "applyRetentionNow", "testLanAccessButton"):
        assert value in html and value in js
