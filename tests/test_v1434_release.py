"""Regression tests for Windows Portable, notification tray and scheduled UX."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from pt2vhf_aprs import updater

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_portable_updater_has_retries_rollback_and_health_gate(tmp_path, monkeypatch):
    monkeypatch.setattr(updater, "UPDATE_DIR", tmp_path)
    monkeypatch.setattr(updater, "PENDING_FILE", tmp_path / "pending_update.json")
    monkeypatch.setattr(updater, "APPLY_LOG", tmp_path / "update_apply.log")
    monkeypatch.setattr(updater, "UPDATE_LOCK_FILE", tmp_path / "update.lock")
    monkeypatch.setattr(updater, "HELPER_READY_FILE", tmp_path / "helper_ready")

    previous = tmp_path / "PT2VHF_APRS_Client_Portable_x64_v1.14.33.exe"
    previous.write_bytes(b"old")
    downloaded = tmp_path / "PT2VHF_APRS_Client_Portable_x64_v1.14.34.exe"
    downloaded.write_bytes(b"replacement")

    helper = updater._write_windows_cmd_helper({
        "path": str(downloaded),
        "current_executable": str(previous),
        "mode": "windows-portable",
        "pid": 7654,
        "version": "1.14.34",
    })
    script = helper.read_text(encoding="utf-8")
    assert "oldpid=7654" in script
    assert "setlocal DisableDelayedExpansion" in script
    assert ":backup_retry" in script
    assert 'copy /Y "%current%" "%backup%"' in script
    assert ":portable_retry" in script
    assert 'move /Y "%downloaded%" "%destination%"' in script
    assert 'if not errorlevel 1 goto portable_installed' in script
    assert "executable still locked; retry" in script
    assert "PT2VHF_UPDATE_READY_MARKER" in script
    assert 'if exist "%marker%" goto portable_healthy' in script
    assert ":rollback_retry" in script
    assert "previous portable restored" in script
    assert "new portable backend confirmed healthy" in script
    assert script.index(":portable_installed") < script.index(":wait_new_instance")
    # No assumptions about the older distributed v1.14.31 helper.
    assert "portable update installed" in script


def test_windows_tray_badge_and_ready_signal_are_independent():
    source = read("windows_app.py")
    assert "def _make_tray_image()" in source
    assert 'd.text((x, y), "APRS"' in source
    assert "tray_icon_generation_failed" in source
    assert "tray_icon_resource_failed" in source
    assert "source=\"drawn_aprs_badge\"" in source
    assert "def _mark_updated_instance_ready()" in source
    assert '"embedded_window_create_failed"' in source
    assert 'netfx_failure=netfx_failure' in source
    assert 'if os.name == "nt" and not netfx_failure' in source
    assert "update_ready.flag" in source
    assert "update_relaunch_confirmed" in source
    assert source.index("if not _wait_for_server():") < source.index("_mark_updated_instance_ready()",
                      source.index("def main()"))


def test_scheduled_messages_modal_retains_service_independence():
    html = read("pt2vhf_aprs/templates/index.html")
    js = read("pt2vhf_aprs/static/js/app.js")
    css = read("pt2vhf_aprs/static/css/app.css")
    assert 'id="scheduledMessagesPanel" class="scheduled-messages-panel hidden" role="dialog" aria-modal="true"' in html
    assert 'id="scheduledMessageForm" class="scheduled-editor hidden"' in html
    assert 'id="scheduledRecipientGroupsEditor" class="recipient-groups-card hidden"' in html
    assert 'id="manageRecipientGroupsButton"' in html
    assert "document.body.appendChild(scheduledDialog)" in js
    assert "function confirmScheduleDiscard()" in js
    assert "function closeScheduledModal()" in js
    assert "function showScheduledEditor()" in js
    assert "event.key === 'Escape'" in js
    assert "scheduledFocusBeforeOpen" in js
    assert "document.body.classList.remove('scheduled-modal-open')" in js
    assert ".scheduled-messages-panel {" in css
    assert "position: fixed" in css
    assert "scheduled-modal-open" in css
    # Preserved message scheduler endpoints, unaffected by UI closing.
    assert "/api/messages/scheduled" in js
    assert 'state.scheduledPanelOpen = false' in js


def test_packaged_windows_sources_must_have_icon_and_python_tray():
    modern = read("windows/PT2VHF_APRS_Client.spec")
    portable = read("windows/PT2VHF_APRS_Client_Portable.spec")
    for script in (modern, portable):
        assert "app_icon.ico" in script
        assert "'windows'" in script
    assert "__version__ = \"1.14.34\"" in read("pt2vhf_aprs/__init__.py")
