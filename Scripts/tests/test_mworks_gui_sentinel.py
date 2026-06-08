import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "agent" / "check_mworks_gui_sentinel.py"
WINDOW_MANAGER = ROOT / "Scripts" / "tools" / "manage_mworks_windows.ps1"


def run_fixture(tmp_path: Path, windows: list[dict]) -> dict:
    fixture = tmp_path / "fixture.json"
    output = tmp_path / "sentinel.json"
    fixture.write_text(json.dumps({"windows": windows}, ensure_ascii=False), encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--fixture", str(fixture), "--output", str(output)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(output.read_text(encoding="utf-8"))
    if payload["status"] == "clean":
        assert result.returncode == 0
    else:
        assert result.returncode == 2
    return payload


def run_window_manager_fixture(
    tmp_path: Path,
    windows: list[dict],
    mode: str,
    *extra_args: str,
) -> dict:
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    assert powershell, "PowerShell is required for manage_mworks_windows.ps1 fixture tests"
    fixture = tmp_path / "window_manager_fixture.json"
    output = tmp_path / "window_manager.json"
    fixture.write_text(json.dumps({"windows": windows}, ensure_ascii=False), encoding="utf-8")
    result = subprocess.run(
        [
            powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(WINDOW_MANAGER),
            "-Mode",
            mode,
            "-FixtureJson",
            str(fixture),
            "-OutJson",
            str(output),
            *extra_args,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode == 0, {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }
    return json.loads(output.read_text(encoding="utf-8"))


def test_detects_mworks_error_report_dialog_and_actions(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 100,
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [
                    {"text": "MWORKS错误报告", "class_name": "Static"},
                    {"text": "Sysplorer 遇到错误，需要关闭。", "class_name": "Static"},
                    {
                        "text": "C:/Users/HP/Documents/MWORKS/log/2026-06-06/2026-06-06T17...",
                        "class_name": "Edit",
                    },
                    {"text": "重启程序", "class_name": "Button"},
                    {"text": "发送错误报告", "class_name": "Button"},
                    {"text": "确定", "class_name": "Button"},
                ],
            }
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "gui_crash_report"
    assert "MWORKS错误报告" in payload["matched_crash_patterns"]
    assert payload["restart_button_present"] is True
    assert payload["send_report_button_present"] is True
    assert payload["confirm_or_ok_button_present"] is True
    assert payload["mworks_report_path_or_visible_prefix"].startswith(
        "C:/Users/HP/Documents/MWORKS/log/2026-06-06/"
    )
    assert payload["will_click_or_close_any_window"] is False


def test_window_manager_unauthorized_close_is_planned_only(tmp_path: Path) -> None:
    payload = run_window_manager_fixture(
        tmp_path,
        [
            {
                "hwnd": 501,
                "pid": 9001,
                "process": "mw_memory_monitor",
                "title": "Memory Warning",
                "class_name": "Dialog",
                "visible": True,
                "rect": {"left": 10, "top": 10, "right": 500, "bottom": 300},
            }
        ],
        "CloseSafeErrors",
    )
    assert payload["schema_version"] == "mosim.mworks_window_management.v2"
    assert payload["fixture_mode"] is True
    assert payload["action_count"] == 1
    action = payload["actions"][0]
    assert action["action"] == "close_safe_error"
    assert action["authorized"] is False
    assert action["executed"] is False
    assert action["api_return"] is None
    assert "-AuthorizedRequestId" in action["why_blocked"]
    assert action["no_main_window_targeted"] is True


def test_window_manager_cleanup_without_authorization_does_not_close(tmp_path: Path) -> None:
    payload = run_window_manager_fixture(
        tmp_path,
        [
            {
                "hwnd": 502,
                "pid": 9002,
                "process": "mw_memory_monitor",
                "title": "Memory Warning",
                "class_name": "Dialog",
                "visible": True,
                "rect": {"left": 10, "top": 10, "right": 500, "bottom": 300},
            }
        ],
        "Cleanup",
        "-AuthorizedRequestId",
        "COAGENTOPS-TEST",
    )
    assert payload["action_count"] == 1
    action = payload["actions"][0]
    assert action["action"] == "close_safe_error"
    assert action["authorized"] is False
    assert action["executed"] is False
    assert "-IncidentPacketPath" in action["why_blocked"]
    assert "-ExpectedHwnd or -ExpectedTitlePattern plus -ExpectedProcess" in action["why_blocked"]


def test_window_manager_authorized_close_only_for_expected_safe_error(tmp_path: Path) -> None:
    payload = run_window_manager_fixture(
        tmp_path,
        [
            {
                "hwnd": 601,
                "pid": 9101,
                "process": "mw_memory_monitor",
                "title": "Memory Warning",
                "class_name": "Dialog",
                "visible": True,
                "rect": {"left": 10, "top": 10, "right": 500, "bottom": 300},
            },
            {
                "hwnd": 602,
                "pid": 9102,
                "process": "mworks",
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "rect": {"left": 10, "top": 10, "right": 1200, "bottom": 900},
            },
            {
                "hwnd": 603,
                "pid": 9103,
                "process": "mworks",
                "title": "MWORKS License",
                "class_name": "Dialog",
                "visible": True,
                "rect": {"left": 20, "top": 20, "right": 700, "bottom": 380},
            },
            {
                "hwnd": 604,
                "pid": 9104,
                "process": "mw_crash_handler",
                "title": "MWORKS Error Report - Send Report",
                "class_name": "Dialog",
                "visible": True,
                "rect": {"left": 30, "top": 30, "right": 800, "bottom": 430},
            },
        ],
        "CloseSafeErrors",
        "-AuthorizedRequestId",
        "COAGENTOPS-MWORKS-WINDOW-MANAGEMENT-AUTH-GATE-REPAIR-20260608-006",
        "-ExpectedHwnd",
        "601",
        "-IncidentPacketPath",
        "Results/agent_packets/blockers/COAGENTOPS-TEST.json",
    )
    close_actions = [action for action in payload["actions"] if action["action"] == "close_safe_error"]
    assert len(close_actions) == 2
    safe_action = next(action for action in close_actions if action["hwnd"] == 601)
    report_action = next(action for action in close_actions if action["hwnd"] == 604)
    assert safe_action["authorized"] is True
    assert safe_action["matched_expected_target"] is True
    assert safe_action["no_main_window_targeted"] is True
    assert safe_action["executed"] is False
    assert report_action["authorized"] is False
    assert "protected" in report_action["why_blocked"]
    windows = {window["hwnd"]: window for window in payload["windows"]}
    assert windows[602]["main_window"] is True
    assert windows[603]["protected_window"] is True
    assert windows[604]["protected_window"] is True


def test_window_manager_minimize_helpers_does_not_require_close_authorization(tmp_path: Path) -> None:
    payload = run_window_manager_fixture(
        tmp_path,
        [
            {
                "hwnd": 701,
                "pid": 9201,
                "process": "mw_browser_proxy",
                "title": "MWORKS",
                "class_name": "Chrome_WidgetWin_0",
                "visible": True,
                "minimized": False,
                "rect": {"left": 100, "top": 100, "right": 900, "bottom": 700},
            },
            {
                "hwnd": 702,
                "pid": 9202,
                "process": "mworks",
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "rect": {"left": 10, "top": 10, "right": 1200, "bottom": 900},
            },
        ],
        "MinimizeHelpers",
    )
    assert payload["action_count"] == 1
    action = payload["actions"][0]
    assert action["action"] == "minimize_helper"
    assert action["authorized"] is True
    assert action["close_authorization_required"] is False
    assert action["no_main_window_targeted"] is True
    assert action["executed"] is False


def test_detects_license_or_login_incident(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 200,
                "title": "MWORKS License",
                "class_name": "Dialog",
                "visible": True,
                "children": [
                    {"text": "L5104-B0", "class_name": "Static"},
                    {"text": "软件尚未激活，请登录。", "class_name": "Static"},
                ],
            }
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "license_or_login"
    assert "L5104-B0" in payload["matched_license_patterns"]
    assert "软件尚未激活" in payload["matched_license_patterns"]
    assert payload["license_state_hint"] == "login_required"
    assert payload["all_window_license_gate"] == "blocked"


def test_mixed_education_and_demo_windows_block_all_mworks(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 210,
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [{"text": "QuadrotorModel", "class_name": "Static"}],
            },
            {
                "hwnd": 211,
                "title": "QuadrotorControllerBlocks - Sysplorer [演示版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [{"text": "Modelica package browser", "class_name": "Static"}],
            },
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "license_or_login"
    assert payload["mixed_license_state"] is True
    assert payload["target_window_count"] == 2
    assert payload["education_window_count"] == 1
    assert payload["demo_window_count"] == 1
    assert payload["blocking_mworks_window_count"] == 1
    assert payload["license_state_hint"] == "mixed_education_and_demo_blocked"
    assert payload["all_window_license_gate"] == "blocked"


def test_one_login_activation_window_blocks_even_with_clean_main_window(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 220,
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [{"text": "main window", "class_name": "Static"}],
            },
            {
                "hwnd": 221,
                "title": "MWORKS License",
                "class_name": "Dialog",
                "visible": True,
                "children": [
                    {"text": "软件尚未激活", "class_name": "Static"},
                    {"text": "请登录后继续使用", "class_name": "Static"},
                ],
            },
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "license_or_login"
    assert payload["mixed_license_state"] is True
    assert payload["login_activation_window_count"] == 1
    assert payload["license_dialog_window_count"] == 1
    assert payload["license_state_hint"] == "mixed_education_and_demo_blocked"


def test_clean_fixture_returns_clean(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 300,
                "title": "Codex",
                "class_name": "Chrome_WidgetWin_1",
                "visible": True,
                "children": [{"text": "normal editor window", "class_name": "Static"}],
            }
        ],
    )
    assert payload["status"] == "clean"
    assert payload["error_kind"] is None
    assert payload["matched_windows"] == []
    assert payload["target_window_count"] == 0
    assert payload["all_window_license_gate"] == "pass"


def test_unknown_mworks_window_blocks_instead_of_clean(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 310,
                "title": "Sysplorer",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [{"text": "QuadrotorModel", "class_name": "Static"}],
            }
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "license_or_login"
    assert payload["target_window_count"] == 1
    assert payload["unknown_mworks_window_count"] == 1
    assert payload["license_state_hint"] == "unknown_blocked"
    assert payload["all_window_license_gate"] == "blocked"


def test_unknown_mworks_windows_override_clean_education_hint(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 320,
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [{"text": "main window", "class_name": "Static"}],
            },
            {
                "hwnd": 321,
                "title": "MWORKS",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [{"text": "blank auxiliary pane may reveal more UI when maximized", "class_name": "Static"}],
            },
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "license_or_login"
    assert payload["education_window_count"] == 1
    assert payload["unknown_mworks_window_count"] == 1
    assert payload["license_state_hint"] == "unknown_blocked"
    assert payload["all_window_license_gate"] == "blocked"


def test_hidden_unknown_mworks_windows_do_not_override_clean_education_hint(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 330,
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "children": [{"text": "main window", "class_name": "Static"}],
            },
            {
                "hwnd": 331,
                "title": "MWORKS",
                "class_name": "Qt5152QWindowIcon",
                "visible": False,
                "children": [{"text": "hidden helper window", "class_name": "Static"}],
            },
        ],
    )
    assert payload["status"] == "clean"
    assert payload["error_kind"] is None
    assert payload["education_window_count"] == 1
    assert payload["unknown_mworks_window_count"] == 1
    assert payload["visible_unknown_mworks_window_count"] == 0
    assert payload["hidden_unknown_mworks_window_count"] == 1
    assert payload["license_state_hint"] == "education_window_observed_activation_unverified"
    assert payload["all_window_license_gate"] == "pass"


def test_minimized_offscreen_unknown_mworks_windows_do_not_block(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 340,
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "rect": {"left": 10, "top": 10, "right": 1200, "bottom": 900},
                "children": [{"text": "main window", "class_name": "Static"}],
            },
            {
                "hwnd": 341,
                "title": "MWORKS",
                "class_name": "Qt5152QWindowIcon",
                "process_name": "mw_browser_proxy.exe",
                "visible": True,
                "rect": {"left": -25600, "top": -25600, "right": -25441, "bottom": -25573},
                "children": [{"text": "blank browser proxy helper", "class_name": "Static"}],
            },
        ],
    )
    assert payload["status"] == "clean"
    assert payload["error_kind"] is None
    assert payload["helper_mworks_window_count"] == 1
    assert payload["unknown_mworks_window_count"] == 0
    assert payload["visible_unknown_mworks_window_count"] == 0
    assert payload["minimized_or_offscreen_unknown_mworks_window_count"] == 0
    assert payload["license_state_hint"] == "education_window_observed_activation_unverified"
    assert payload["all_window_license_gate"] == "pass"


def test_onscreen_unknown_mworks_windows_still_block(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 350,
                "title": "Sysplorer [教育版]",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "rect": {"left": 10, "top": 10, "right": 1200, "bottom": 900},
                "children": [{"text": "main window", "class_name": "Static"}],
            },
            {
                "hwnd": 351,
                "title": "MWORKS",
                "class_name": "Qt5152QWindowIcon",
                "visible": True,
                "rect": {"left": 200, "top": 200, "right": 900, "bottom": 700},
                "children": [{"text": "unknown on-screen MWORKS pane", "class_name": "Static"}],
            },
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "license_or_login"
    assert payload["unknown_mworks_window_count"] == 1
    assert payload["visible_unknown_mworks_window_count"] == 1
    assert payload["minimized_or_offscreen_unknown_mworks_window_count"] == 0
    assert payload["license_state_hint"] == "unknown_blocked"
    assert payload["all_window_license_gate"] == "blocked"


def test_crash_precedence_over_license_words(tmp_path: Path) -> None:
    payload = run_fixture(
        tmp_path,
        [
            {
                "hwnd": 400,
                "title": "MWORKS错误报告",
                "class_name": "Dialog",
                "visible": True,
                "children": [
                    {"text": "Sysplorer 遇到错误，需要关闭。", "class_name": "Static"},
                    {"text": "错误报告不包含任何隐私信息。", "class_name": "Static"},
                ],
            }
        ],
    )
    assert payload["status"] == "incident_detected"
    assert payload["error_kind"] == "gui_crash_report"
