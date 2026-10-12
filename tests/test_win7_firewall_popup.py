"""Regressão: netsh não pode abrir console a cada /api/status no Win7."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

from pt2vhf_aprs import lan_access


def test_firewall_diagnostic_uses_hidden_console_and_cache(monkeypatch):
    monkeypatch.setattr(lan_access, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)
    lan_access._invalidate_firewall_cache()
    calls = []
    exe = str(Path(sys.executable).resolve())

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0, stdout=f"Porta local: 8080\nProtocolo: TCP\nIP Remoto: LocalSubnet\n")

    monkeypatch.setattr(lan_access.subprocess, "run", fake_run)
    assert lan_access.windows_firewall_rule_exists(8080) is True
    assert lan_access.windows_firewall_rule_exists(8080) is True
    assert len(calls) == 1, "refresh de /api/status não deve iniciar netsh novamente"
    assert calls[0][1]["creationflags"] == 0x08000000
    assert calls[0][1]["capture_output"] is True
    assert calls[0][1]["timeout"] == 8

    lan_access._invalidate_firewall_cache()
    assert lan_access.windows_firewall_rule_exists(8080) is True
    assert len(calls) == 2


def test_firewall_probe_cache_does_not_cross_port_changes(monkeypatch):
    monkeypatch.setattr(lan_access, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(subprocess, "CREATE_NO_WINDOW", 0x08000000, raising=False)
    lan_access._invalidate_firewall_cache()
    exe = str(Path(sys.executable).resolve())
    calls = []
    def fake_run(args, **kwargs):
        calls.append(1)
        return SimpleNamespace(returncode=0, stdout=f"LocalPort: 8080\nProtocol: TCP\nRemoteIP: LocalSubnet\n")
    monkeypatch.setattr(lan_access.subprocess, "run", fake_run)
    assert lan_access.windows_firewall_rule_exists(8080) is True
    assert lan_access.windows_firewall_rule_exists(8081) is False
    assert len(calls) == 2
