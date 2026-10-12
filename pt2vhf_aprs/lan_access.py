from __future__ import annotations

import ctypes
import os
import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import diagnostics as diag

FIREWALL_RULE_NAME = "PT2VHF APRS Client Web LAN"


def _valid_port(port: Any) -> int:
    value = int(port or 0)
    if not 1 <= value <= 65535:
        raise ValueError("Porta TCP inválida.")
    return value


def tcp_listening(port: Any) -> bool:
    value = _valid_port(port)
    try:
        with socket.create_connection(("127.0.0.1", value), timeout=0.35):
            return True
    except OSError:
        return False


def windows_firewall_rule_exists() -> bool | None:
    if os.name != "nt":
        return None
    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"name={FIREWALL_RULE_NAME}"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return None


def request_windows_firewall_rule(port: Any) -> dict[str, Any]:
    """Request an elevated, Private-profile inbound TCP rule.

    Elevation is always interactive through the Windows UAC prompt. We never
    disable the firewall or modify global profiles.
    """
    value = _valid_port(port)
    if os.name != "nt":
        return {"ok": False, "supported": False, "error": "Ação disponível somente no Windows."}

    exe = Path(sys.executable).resolve()
    delete_args = f'advfirewall firewall delete rule name="{FIREWALL_RULE_NAME}"'
    add_args = (
        f'advfirewall firewall add rule name="{FIREWALL_RULE_NAME}" '
        f'dir=in action=allow protocol=TCP localport={value} profile=private '
        f'program="{exe}" enable=yes'
    )

    try:
        # Delete old rule first so a port change does not leave stale exposure.
        ctypes.windll.shell32.ShellExecuteW(None, "runas", "netsh.exe", delete_args, None, 0)
        rc = ctypes.windll.shell32.ShellExecuteW(None, "runas", "netsh.exe", add_args, None, 1)
        if int(rc) <= 32:
            raise OSError("O Windows recusou a solicitação de elevação do firewall.")
        diag.log_event(
            "lan_firewall_rule_requested",
            rule=FIREWALL_RULE_NAME,
            port=value,
            profile="private",
            executable=str(exe),
        )
        return {
            "ok": True,
            "supported": True,
            "requested": True,
            "rule": FIREWALL_RULE_NAME,
            "port": value,
            "profile": "private",
        }
    except Exception as exc:
        diag.log_event("lan_firewall_rule_failed", port=value, error=str(exc))
        return {"ok": False, "supported": True, "error": str(exc), "port": value}


def lan_diagnostics(runtime: dict[str, Any]) -> dict[str, Any]:
    port = int(runtime.get("port") or 0)
    scope = str(runtime.get("scope") or "local")
    lan_ip = str(runtime.get("lan_ip") or "")
    listening = tcp_listening(port) if port else False
    firewall = windows_firewall_rule_exists() if scope == "lan" else None

    if scope != "lan":
        state = "local-only"
        message = "Acesso restrito à própria máquina."
    elif not lan_ip:
        state = "no-lan-address"
        message = "O endereço IPv4 da rede local não pôde ser determinado."
    elif not listening:
        state = "not-listening"
        message = "A porta publicada não está em escuta."
    elif os.name == "nt" and firewall is False:
        state = "firewall-not-confirmed"
        message = "Servidor ativo; regra do Windows Firewall não confirmada."
    else:
        state = "lan-ready"
        message = "Servidor em escuta na LAN."

    return {
        "state": state,
        "message": message,
        "platform": platform.system(),
        "scope": scope,
        "bind_host": str(runtime.get("bind_host") or ""),
        "display_host": str(runtime.get("display_host") or ""),
        "lan_ip": lan_ip,
        "port": port,
        "share_url": str(runtime.get("share_url") or ""),
        "listening": listening,
        "windows_firewall_rule": firewall,
        "firewall_rule_name": FIREWALL_RULE_NAME if os.name == "nt" else "",
    }
