import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "agent" / "check_mworks_gui_sentinel.py"


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
