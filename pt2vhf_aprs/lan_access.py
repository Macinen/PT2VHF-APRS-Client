from __future__ import annotations

import ctypes
import os
import platform
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from . import diagnostics as diag

FIREWALL_RULE_NAME = "PT2VHF APRS Client Web LAN"

# /api/status atualiza a cada 3 s. Evite abrir netsh em cada consulta.
FIREWALL_CHECK_CACHE_SECONDS = 60.0
_firewall_cache_lock = threading.Lock()
_firewall_cache: dict[str, Any] = {"key": None, "until": 0.0, "result": None}


def _invalidate_firewall_cache() -> None:
    with _firewall_cache_lock:
        _firewall_cache["until"] = 0.0




def _valid_port(port: Any) -> int:
    value = int(port or 0)
    if not 1 <= value <= 65535:
        raise ValueError("Porta TCP inválida.")
    return value


def tcp_listening(port: Any, host: str = "127.0.0.1") -> bool:
    """Check a concrete socket, never infer LAN reachability from loopback."""
    value = _valid_port(port)
    try:
        with socket.create_connection((host, value), timeout=0.45):
            return True
    except OSError:
        return False


def windows_firewall_rule_exists(port: int | None = None) -> bool | None:
    """Consult the firewall without showing a console window or polling netsh
    at the same frequency as /api/status (every ~3 s).
    """
    if os.name != "nt":
        return None
    executable = str(Path(sys.executable).resolve())
    key = (port, executable.lower())
    now = time.monotonic()
    with _firewall_cache_lock:
        if _firewall_cache["key"] == key and now < float(_firewall_cache["until"]):
            return _firewall_cache["result"]
    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"name={FIREWALL_RULE_NAME}"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
            # GUI executables made with PyInstaller --noconsole must never
            # spawn a visible console for periodic diagnostic commands.
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        output = result.stdout.lower()
        rule_exists = result.returncode == 0
        if port is not None and str(_valid_port(port)) not in output:
            rule_exists = False
        if executable.lower() not in output:
            rule_exists = False
    except Exception:
        rule_exists = None
    with _firewall_cache_lock:
        _firewall_cache.update(key=key, until=time.monotonic() + FIREWALL_CHECK_CACHE_SECONDS,
                               result=rule_exists)
    return rule_exists


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
        f'program="{exe}" remoteip=localsubnet enable=yes'
    )

    _invalidate_firewall_cache()
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


def lan_diagnostics(runtime: dict[str, Any],
                    configured_enabled: bool | None = None) -> dict[str, Any]:
    """Local LAN-bind probe. External reachability needs a second-device test."""
    port = int(runtime.get("port") or 0)
    scope = str(runtime.get("scope") or "local")
    bind_host = str(runtime.get("bind_host") or "127.0.0.1")
    lan_ip = str(runtime.get("lan_ip") or "")
    listening_local = tcp_listening(port) if port else False
    listening_lan = tcp_listening(port, lan_ip) if port and lan_ip else False
    firewall = windows_firewall_rule_exists(port) if scope == "lan" and port else None
    expected_lan = bool(configured_enabled) if configured_enabled is not None else (scope == "lan")
    mismatch = expected_lan != (scope == "lan")

    if mismatch:
        state = "restart-required"
        message = "Configuração LAN alterada. Reinicie o aplicativo para aplicar o bind."
    elif scope != "lan" or bind_host.startswith("127."):
        state = "local-only"
        message = "Servidor restrito a localhost. Habilite LAN nas Configurações e reinicie."
    elif not lan_ip:
        state = "no-lan-address"
        message = "Não foi possível detectar o IPv4 LAN."
    elif not listening_local or not listening_lan:
        state = "lan-bind-failed"
        message = "Servidor não responde no IPv4 LAN. Verifique bind e porta."
    elif os.name == "nt" and firewall is False:
        state = "firewall-not-confirmed"
        message = "Bind LAN funcionando; regra de firewall não confirmada."
    else:
        state = "lan-bind-confirmed"
        message = "Bind LAN confirmado no host. Teste a URL em outro dispositivo; firewall pode bloquear."

    return {
        "state": state, "message": message, "platform": platform.system(),
        "scope": scope, "configured_web_lan_enabled": expected_lan,
        "requested_bind_host": "0.0.0.0" if expected_lan else "127.0.0.1",
        "actual_bind_host": bind_host, "bind_host": bind_host,
        "display_host": str(runtime.get("display_host") or ""),
        "lan_ip": lan_ip, "port": port,
        "share_url": str(runtime.get("share_url") or ""),
        "listening": listening_local, "listening_lan": listening_lan,
        "external_access_confirmed": False, "restart_required": mismatch,
        "windows_firewall_rule": firewall,
        "firewall_rule_name": FIREWALL_RULE_NAME if os.name == "nt" else "",
    }
