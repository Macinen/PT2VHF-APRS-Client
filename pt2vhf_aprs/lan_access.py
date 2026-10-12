from __future__ import annotations

import ctypes
import os
import platform
import socket
import subprocess
import sys
import threading
import time
import re
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


def _firewall_rule_present(output: str, port: int) -> bool:
    """Parse localized netsh output conservatively; never accept an old port."""
    raw = str(output or "").lower()
    # Match exact TCP port, not e.g. 8080 as a substring of 18080.
    if not re.search(r"(?<![0-9])" + str(int(port)) + r"(?![0-9])", raw):
        return False
    # New rule intentionally follows the executable across Portable updates.
    return "tcp" in raw and "localsubnet" in raw.replace(" ", "")


def windows_firewall_rule_exists(port: int | None = None) -> bool | None:
    """Cache a hidden netsh probe; a local connection does not prove firewall access."""
    if os.name != "nt":
        return None
    key = (port, FIREWALL_RULE_NAME)
    now = time.monotonic()
    with _firewall_cache_lock:
        if _firewall_cache["key"] == key and now < float(_firewall_cache["until"]):
            return _firewall_cache["result"]
    try:
        result = subprocess.run(
            ["netsh", "advfirewall", "firewall", "show", "rule", f"name={FIREWALL_RULE_NAME}"],
            capture_output=True, text=True, errors="replace", timeout=8, check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        present = bool(result.returncode == 0) if port is None else (
            result.returncode == 0 and _firewall_rule_present(result.stdout, _valid_port(port)))
    except Exception:
        present = None
    with _firewall_cache_lock:
        _firewall_cache.update(key=key, until=time.monotonic() + FIREWALL_CHECK_CACHE_SECONDS,
                               result=present)
    return present


def _firewall_script(port: int) -> str:
    """One elevated operation, not two racing ShellExecuteW calls.

    Port-based rule survives renamed/moved Portable executables and upgrades.
    Access is deliberately restricted to the local subnet, including on Windows
    machines where the network profile is set to Public.
    """
    port = _valid_port(port)
    return (
        "@echo off\r\n"
        f'netsh advfirewall firewall delete rule name="{FIREWALL_RULE_NAME}" >nul 2>&1\r\n'
        f'netsh advfirewall firewall add rule name="{FIREWALL_RULE_NAME}" '
        f'dir=in action=allow protocol=TCP localport={port} profile=any '
        'remoteip=localsubnet enable=yes\r\n'
        "exit /b %errorlevel%\r\n"
    )


def request_windows_firewall_rule(port: Any) -> dict[str, Any]:
    """Ask UAC once; do not silently change Windows security policy.

    The elevated script replaces old rules and installs one local-subnet TCP
    rule for the *actual* server port. The immediate result means only that
    Windows accepted the request, never that the rule was installed.
    """
    value = _valid_port(port)
    if os.name != "nt":
        return {"ok": False, "supported": False, "error": "Ação disponível somente no Windows."}
    try:
        # Persist the helper in the same application data folder on Win7/Win11.
        # No shell interpolation of user-supplied values: only a validated port.
        from . import database as db
        script = db.DB_PATH.parent / "allow_web_lan_firewall.cmd"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_bytes(_firewall_script(value).encode("ascii"))
        _invalidate_firewall_cache()
        rc = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", os.environ.get("COMSPEC", "cmd.exe"),
            '/d /c ""' + str(script) + '""', None, 0
        )
        if int(rc) <= 32:
            raise OSError("O Windows não iniciou a autorização de firewall (UAC).")
        diag.log_event(
            "lan_firewall_rule_requested", rule=FIREWALL_RULE_NAME, port=value,
            profile="any", remoteip="localsubnet", portable_compatible=True,
        )
        return {
            "ok": True, "supported": True, "requested": True, "confirmed": False,
            "rule": FIREWALL_RULE_NAME, "port": value,
            "profile": "any", "remote_ip": "localsubnet",
            "message": "Autorize o UAC. Em seguida, use Testar LAN para verificar a regra."
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
