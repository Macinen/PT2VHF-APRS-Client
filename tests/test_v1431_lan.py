"""Regressão v1.14.31: LAN Win7/Win11 e diagnóstico de acesso remoto."""
from __future__ import annotations

import os
import socket
from pathlib import Path
from types import SimpleNamespace

import pytest
from pt2vhf_aprs import lan_access, local_server, database as db


def test_firewall_script_is_single_elevated_operation_and_portable():
    script = lan_access._firewall_script(8080)
    assert "delete rule" in script
    assert "add rule" in script
    assert script.index("delete rule") < script.index("add rule")
    assert "localport=8080" in script
    assert "profile=any" in script
    assert "remoteip=localsubnet" in script
    assert "program=" not in script
    assert "exit /b %errorlevel%" in script
    with pytest.raises(ValueError):
        lan_access._firewall_script(65536)


def test_firewall_request_uses_one_uac_not_two(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "app.db")
    monkeypatch.setattr(lan_access, "os", SimpleNamespace(name="nt", environ={"COMSPEC":"cmd.exe"}))
    calls = []
    fake_shell32 = SimpleNamespace(ShellExecuteW=lambda *args: calls.append(args) or 33)
    monkeypatch.setattr(lan_access.ctypes, "windll", SimpleNamespace(shell32=fake_shell32), raising=False)
    monkeypatch.setattr(lan_access.diag, "log_event", lambda *args, **kw: None)
    result = lan_access.request_windows_firewall_rule(8080)
    assert result["requested"] is True
    assert result["confirmed"] is False  # UAC request is NOT confirmed installation
    assert len(calls) == 1
    assert calls[0][1] == "runas"
    helper = tmp_path / "allow_web_lan_firewall.cmd"
    assert helper.is_file()
    assert b"remoteip=localsubnet" in helper.read_bytes()


def test_remote_evidence_requires_non_loopback_request(monkeypatch):
    with lan_access._last_remote_lock:
        lan_access._last_remote.update(address="", path="", at="", when=0)
    lan_access.note_remote_request("127.0.0.1", "/api/status")
    assert lan_access.last_remote_request()["confirmed"] is False
    lan_access.note_remote_request("::1", "/api/status")
    assert lan_access.last_remote_request()["confirmed"] is False
    lan_access.note_remote_request("192.168.44.9", "/api/local-interface/remote-probe")
    last = lan_access.last_remote_request()
    assert last["confirmed"] is True
    assert last["address"] == "192.168.44.9"
    with lan_access._last_remote_lock:
        lan_access._last_remote.update(address="", path="", at="", when=0)


def test_real_lan_bind_responds_at_actual_nic_address():
    ip = local_server.detect_lan_ipv4()
    if not ip:
        pytest.skip("Runner has no real IPv4 LAN interface")
    def app(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"pt2vhf-lan-ok"]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as free:
        free.bind(("127.0.0.1", 0))
        candidate = free.getsockname()[1]
    handle = local_server.start_local_server(app, host="0.0.0.0",
                                              start_port=candidate, attempts=30)
    try:
        assert handle.wait_ready(5)
        assert handle.scope == "lan"
        with socket.create_connection((ip, handle.port), timeout=2) as sock:
            sock.sendall(b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n")
            reply = sock.recv(4096)
        assert b"200 OK" in reply
    finally:
        handle.close()


def test_accessible_address_reports_only_when_lan_bound():
    src = (Path(__file__).resolve().parents[1] /
           "pt2vhf_aprs/static/js/app.js").read_text(encoding="utf-8")
    assert "if (scope !== 'lan') shareUrl = localUrl;" in src
    assert "if (scope === 'lan') shareUrl = lanCandidate;" in src
    assert "access.external_access_confirmed" in src
    assert "remote_test_urls" in src


def test_win7_popup_probe_logs_child_windows_only():
    src = (Path(__file__).resolve().parents[1] /
           "pt2vhf_aprs/diagnostics.py").read_text(encoding="utf-8")
    assert 'os.getenv("PT2VHF_WIN7_LEGACY") != "1"' in src
    assert "pt2vhf-win7-window-diagnostics" in src
    assert "if value not in child_pids:" in src
