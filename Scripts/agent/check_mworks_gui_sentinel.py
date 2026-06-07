"""Read-only MWORKS/Sysplorer GUI incident sentinel.

This script enumerates Windows top-level and child-window text with Win32 APIs.
It does not click, close, focus, move, restart, or authenticate any window.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import re
import sys
from ctypes import wintypes
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


CRASH_PATTERNS = [
    "MWORKS错误报告",
    "MWORKS 错误报告",
    "Sysplorer 遇到错误，需要关闭",
    "遇到错误，需要关闭",
    "错误报告",
    "发送错误报告",
]

LICENSE_STRONG_PATTERNS = [
    "L5104-B0",
    "软件尚未激活",
    "当前授权不允许变量方程数大于 300",
    "变量方程数大于 300",
    "未激活",
]

LICENSE_CONTEXT_PATTERNS = [
    "授权",
    "许可证",
    "登录",
    "登陆",
    "激活",
    "演示版",
    "demo",
    "Demo",
    "license",
    "License",
    "login",
    "Login",
    "activation",
    "Activation",
]

EDUCATION_PATTERNS = [
    "教育版",
]

DEMO_PATTERNS = [
    "演示版",
    "demo",
    "Demo",
]

LOGIN_ACTIVATION_PATTERNS = [
    "登录",
    "登陆",
    "激活",
    "login",
    "Login",
    "activation",
    "Activation",
]

AUTHORIZATION_FAILURE_PATTERNS = [
    "当前授权不允许变量方程数大于 300",
    "变量方程数大于 300",
    "授权不允许",
    "authorization failed",
    "Authorization failed",
]

LICENSE_DIALOG_PATTERNS = [
    "MWORKS License",
    "许可证",
    "License",
]

MWORKS_CONTEXT_PATTERNS = [
    "MWORKS",
    "Sysplorer",
    "Syslab",
    "Sysblock",
    "Modelica",
    "Quadrotor",
    "AWFF",
]

MWORKS_PROCESS_STEMS = {
    "mworks",
    "mw_browser_proxy",
    "mw_crash_handler",
    "mw_memory_monitor",
    "mwrsvc",
    "syslab",
    "syslab-mcp-server-win64",
    "sysplorer",
    "sysplorer-acp-server",
    "sysplorer_docsearch",
}

RESTART_PATTERNS = ["重启程序", "Restart", "restart"]
SEND_REPORT_PATTERNS = ["发送错误报告", "Send", "send report", "Send report"]
CONFIRM_PATTERNS = ["确定", "OK", "Ok"]
COPY_REPORT_PATH_PATTERNS = ["复制报告路径", "Copy"]

REPORT_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/][^\s\"'\u3002\uff0c,;]+MWORKS[\\/][^\s\"'\u3002\uff0c,;]*|"
    r"C:/Users/HP/Documents/MWORKS/log/[^\s\"'\u3002\uff0c,;]*)"
)


def now_cst() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _contains_any(text: str, patterns: list[str]) -> list[str]:
    folded = text.casefold()
    found: list[str] = []
    for pattern in patterns:
        if pattern.casefold() in folded:
            found.append(pattern)
    return found


def _combined_text(window: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("title", "class_name"):
        value = window.get(key)
        if value:
            parts.append(str(value))
    for child in window.get("children", []) or []:
        for key in ("text", "class_name"):
            value = child.get(key)
            if value:
                parts.append(str(value))
    return "\n".join(parts)


def _process_stem(window: dict[str, Any]) -> str:
    process_name = str(window.get("process_name") or "")
    if not process_name:
        process_path = str(window.get("process_path") or "")
        process_name = Path(process_path).name
    if process_name.casefold().endswith(".exe"):
        process_name = process_name[:-4]
    return process_name.casefold()


def _is_mworks_process(window: dict[str, Any]) -> bool:
    return _process_stem(window) in MWORKS_PROCESS_STEMS


def _window_ref(window: dict[str, Any]) -> dict[str, Any]:
    return {
        "hwnd": window.get("hwnd"),
        "process_id": window.get("process_id"),
        "process_name": window.get("process_name", ""),
        "process_path": window.get("process_path", ""),
        "title": window.get("title", ""),
        "class_name": window.get("class_name", ""),
        "visible": window.get("visible"),
        "enabled": window.get("enabled"),
        "rect": window.get("rect"),
    }


def classify_windows(windows: list[dict[str, Any]], screenshot_path: str | None = None) -> dict[str, Any]:
    matched_windows: list[dict[str, Any]] = []
    mworks_like_windows: list[dict[str, Any]] = []
    education_windows: list[dict[str, Any]] = []
    demo_windows: list[dict[str, Any]] = []
    login_activation_windows: list[dict[str, Any]] = []
    authorization_windows: list[dict[str, Any]] = []
    license_dialog_windows: list[dict[str, Any]] = []
    unknown_mworks_windows: list[dict[str, Any]] = []
    visible_unknown_mworks_windows: list[dict[str, Any]] = []
    hidden_unknown_mworks_windows: list[dict[str, Any]] = []
    all_crash_matches: list[str] = []
    all_license_matches: list[str] = []

    for window in windows:
        text = _combined_text(window)
        process_is_mworks = _is_mworks_process(window)
        crash_matches = _contains_any(text, CRASH_PATTERNS)
        strong_license_matches = _contains_any(text, LICENSE_STRONG_PATTERNS)
        education_matches = _contains_any(text, EDUCATION_PATTERNS)
        demo_matches = _contains_any(text, DEMO_PATTERNS)
        login_activation_matches = _contains_any(text, LOGIN_ACTIVATION_PATTERNS)
        authorization_matches = _contains_any(text, AUTHORIZATION_FAILURE_PATTERNS)
        license_dialog_matches = _contains_any(text, LICENSE_DIALOG_PATTERNS)
        context_license_matches = _contains_any(text, LICENSE_CONTEXT_PATTERNS)
        has_mworks_context = process_is_mworks and bool(
            _contains_any(
                text,
                MWORKS_CONTEXT_PATTERNS
                + CRASH_PATTERNS
                + LICENSE_CONTEXT_PATTERNS
                + LICENSE_STRONG_PATTERNS,
            )
        )
        license_dialog_is_relevant = has_mworks_context and bool(license_dialog_matches)
        license_matches = strong_license_matches + (
            demo_matches
            + login_activation_matches
            + authorization_matches
            + (license_dialog_matches if license_dialog_is_relevant else [])
            if has_mworks_context
            else []
        )

        if has_mworks_context:
            summary = {
                **_window_ref(window),
                "matched_education_patterns": education_matches,
                "matched_demo_patterns": demo_matches,
                "matched_login_activation_patterns": login_activation_matches,
                "matched_authorization_patterns": authorization_matches,
                "matched_license_dialog_patterns": license_dialog_matches if license_dialog_is_relevant else [],
                "matched_crash_patterns": crash_matches,
            }
            mworks_like_windows.append(summary)
            if education_matches:
                education_windows.append(summary)
            if demo_matches:
                demo_windows.append(summary)
            if strong_license_matches or login_activation_matches:
                login_activation_windows.append(summary)
            if authorization_matches:
                authorization_windows.append(summary)
            if license_dialog_is_relevant:
                license_dialog_windows.append(summary)
            if not (
                education_matches
                or demo_matches
                or strong_license_matches
                or login_activation_matches
                or authorization_matches
                or license_dialog_is_relevant
                or crash_matches
            ):
                unknown_mworks_windows.append(summary)
                if summary.get("visible"):
                    visible_unknown_mworks_windows.append(summary)
                else:
                    hidden_unknown_mworks_windows.append(summary)

        if crash_matches or license_matches:
            matched_windows.append(
                {
                    **_window_ref(window),
                    "matched_crash_patterns": crash_matches,
                    "matched_license_patterns": license_matches,
                    "matched_education_patterns": education_matches,
                    "matched_demo_patterns": demo_matches,
                    "matched_login_activation_patterns": login_activation_matches,
                    "matched_authorization_patterns": authorization_matches,
                    "matched_license_dialog_patterns": license_dialog_matches if license_dialog_is_relevant else [],
                    "text_sample": text[:1200],
                    "children": [
                        child
                        for child in (window.get("children", []) or [])
                        if child.get("text") or child.get("class_name")
                    ][:40],
                }
            )
            all_crash_matches.extend(crash_matches)
            all_license_matches.extend(license_matches)

    matched_text = "\n".join(match.get("text_sample", "") for match in matched_windows)
    report_paths = sorted(set(REPORT_PATH_RE.findall(matched_text)))
    restart_present = bool(_contains_any(matched_text, RESTART_PATTERNS))
    send_report_present = bool(_contains_any(matched_text, SEND_REPORT_PATTERNS))
    confirm_present = bool(_contains_any(matched_text, CONFIRM_PATTERNS))
    copy_report_path_present = bool(_contains_any(matched_text, COPY_REPORT_PATH_PATTERNS))

    if all_crash_matches:
        status = "incident_detected"
        error_kind = "gui_crash_report"
    elif all_license_matches:
        status = "incident_detected"
        error_kind = "license_or_login"
    else:
        status = "clean"
        error_kind = None

    mixed_license_state = bool(
        education_windows
        and (
            demo_windows
            or login_activation_windows
            or authorization_windows
            or license_dialog_windows
        )
    )
    blocking_window_count = len(
        {
            int(item["hwnd"])
            for item in (
                demo_windows
                + login_activation_windows
                + authorization_windows
                + license_dialog_windows
            )
            if item.get("hwnd") is not None
        }
    )
    if mixed_license_state and error_kind is None:
        status = "incident_detected"
        error_kind = "license_or_login"
    if visible_unknown_mworks_windows and error_kind is None:
        status = "incident_detected"
        error_kind = "license_or_login"
    if mworks_like_windows and not education_windows and error_kind is None:
        status = "incident_detected"
        error_kind = "license_or_login"

    if all_crash_matches:
        license_state_hint = "gui_error_report_blocked"
    elif mixed_license_state:
        license_state_hint = "mixed_education_and_demo_blocked"
    elif demo_windows:
        license_state_hint = "demo_blocked"
    elif login_activation_windows or license_dialog_windows:
        license_state_hint = "login_required"
    elif authorization_windows:
        license_state_hint = "authorization_failed"
    elif visible_unknown_mworks_windows:
        license_state_hint = "unknown_blocked"
    elif mworks_like_windows and not education_windows:
        license_state_hint = "unknown_blocked"
    elif education_windows and not blocking_window_count:
        license_state_hint = "education_window_observed_activation_unverified"
    elif mworks_like_windows:
        license_state_hint = "unknown_blocked"
    else:
        license_state_hint = "no_mworks_window_observed"

    return {
        "schema_version": "mosim.mworks_gui_sentinel.v1",
        "created_at": now_cst(),
        "sentinel": "win32_enumwindows_text",
        "status": status,
        "error_kind": error_kind,
        "matched_crash_patterns": sorted(set(all_crash_matches)),
        "matched_license_patterns": sorted(set(all_license_matches)),
        "matched_windows": matched_windows,
        "mworks_like_windows": mworks_like_windows,
        "education_windows": education_windows,
        "demo_windows": demo_windows,
        "login_activation_windows": login_activation_windows,
        "authorization_windows": authorization_windows,
        "license_dialog_windows": license_dialog_windows,
        "unknown_mworks_windows": unknown_mworks_windows,
        "visible_unknown_mworks_windows": visible_unknown_mworks_windows,
        "hidden_unknown_mworks_windows": hidden_unknown_mworks_windows,
        "target_window_count": len(mworks_like_windows),
        "education_window_count": len(education_windows),
        "demo_window_count": len(demo_windows),
        "login_activation_window_count": len(login_activation_windows),
        "authorization_window_count": len(authorization_windows),
        "license_dialog_window_count": len(license_dialog_windows),
        "unknown_mworks_window_count": len(unknown_mworks_windows),
        "visible_unknown_mworks_window_count": len(visible_unknown_mworks_windows),
        "hidden_unknown_mworks_window_count": len(hidden_unknown_mworks_windows),
        "mixed_license_state": mixed_license_state,
        "blocking_mworks_window_count": blocking_window_count,
        "license_state_hint": license_state_hint,
        "all_window_license_gate": "blocked" if status == "incident_detected" else "pass",
        "window_count": len(windows),
        "screenshot_path": screenshot_path,
        "mworks_report_path_or_visible_prefix": report_paths[0] if report_paths else None,
        "mworks_report_path_candidates": report_paths,
        "restart_button_present": restart_present,
        "send_report_button_present": send_report_present,
        "confirm_or_ok_button_present": confirm_present,
        "copy_report_path_button_present": copy_report_path_present,
        "will_click_or_close_any_window": False,
        "will_restart_program": False,
        "will_send_error_report": False,
        "next_safe_recovery_step": (
            "Stop active MWORKS/Sysplorer/Syslab MCP/model automation and return a blocker packet; "
            "PMO/user must decide whether to preserve, copy report path, close, or restart."
            if status == "incident_detected"
            else "Proceed only with the intended MWORKS step, then run this sentinel again before claiming unattended GUI safety."
        ),
        "claim_boundary": {
            "read_only_window_text_inventory": True,
            "not_hidden_window_screenshot": True,
            "not_computer_use_route": True,
            "windows_mcp_or_win32_route_required_for_mosim_mworks": True,
            "not_mworks_model_evidence": True,
            "does_not_read_external_mworks_log": True,
            "does_not_recover_license_or_login": True,
        },
        "windows": windows,
    }


def _get_window_text(user32: ctypes.WinDLL, hwnd: int) -> str:
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    return buffer.value


def _get_class_name(user32: ctypes.WinDLL, hwnd: int) -> str:
    buffer = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buffer, 256)
    return buffer.value


def _get_rect(user32: ctypes.WinDLL, hwnd: int) -> dict[str, int] | None:
    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return {
        "left": int(rect.left),
        "top": int(rect.top),
        "right": int(rect.right),
        "bottom": int(rect.bottom),
    }


def _get_process_info(user32: ctypes.WinDLL, kernel32: ctypes.WinDLL, hwnd: int) -> dict[str, Any]:
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process_id = int(pid.value)
    result: dict[str, Any] = {"process_id": process_id, "process_name": "", "process_path": ""}
    if process_id <= 0:
        return result

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
    if not handle:
        return result
    try:
        capacity = wintypes.DWORD(32768)
        buffer = ctypes.create_unicode_buffer(capacity.value)
        if kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(capacity)):
            process_path = buffer.value
            result["process_path"] = process_path
            result["process_name"] = Path(process_path).name
    finally:
        kernel32.CloseHandle(handle)
    return result


def enumerate_windows() -> tuple[list[dict[str, Any]], str | None]:
    if sys.platform != "win32":
        return [], f"unsupported_platform:{sys.platform}"

    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    except Exception as exc:  # pragma: no cover - platform guard
        return [], f"user32_unavailable:{exc}"

    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    windows: list[dict[str, Any]] = []

    enum_child_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def collect_children(parent_hwnd: int) -> list[dict[str, Any]]:
        children: list[dict[str, Any]] = []

        @enum_child_proc
        def child_callback(child_hwnd: int, _lparam: int) -> bool:
            text = _get_window_text(user32, child_hwnd)
            class_name = _get_class_name(user32, child_hwnd)
            if text or class_name:
                children.append(
                    {
                        "hwnd": int(child_hwnd),
                        "text": text,
                        "class_name": class_name,
                        "visible": bool(user32.IsWindowVisible(child_hwnd)),
                        "enabled": bool(user32.IsWindowEnabled(child_hwnd)),
                        "rect": _get_rect(user32, child_hwnd),
                    }
                )
            return True

        user32.EnumChildWindows(parent_hwnd, child_callback, 0)
        return children

    @enum_proc
    def callback(hwnd: int, _lparam: int) -> bool:
        title = _get_window_text(user32, hwnd)
        class_name = _get_class_name(user32, hwnd)
        children = collect_children(hwnd)
        process_info = _get_process_info(user32, kernel32, hwnd)
        if title or class_name or children:
            windows.append(
                {
                    "hwnd": int(hwnd),
                    **process_info,
                    "title": title,
                    "class_name": class_name,
                    "visible": bool(user32.IsWindowVisible(hwnd)),
                    "enabled": bool(user32.IsWindowEnabled(hwnd)),
                    "rect": _get_rect(user32, hwnd),
                    "children": children,
                }
            )
        return True

    ok = user32.EnumWindows(callback, 0)
    if not ok:
        err = ctypes.get_last_error()
        return windows, f"EnumWindows_failed:{err}"
    return windows, None


def load_fixture(path: Path | None, fixture_json: str | None) -> list[dict[str, Any]]:
    if path and fixture_json:
        raise SystemExit("Use either --fixture or --fixture-json, not both")
    if fixture_json:
        payload = json.loads(fixture_json)
    elif path:
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise SystemExit("fixture input is required")
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("windows"), list):
        return payload["windows"]
    raise SystemExit("fixture must be a window list or an object with windows=[...]")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="JSON evidence output path")
    parser.add_argument("--fixture", type=Path, help="Classify a fixture JSON instead of live windows")
    parser.add_argument("--fixture-json", help="Classify inline fixture JSON instead of live windows")
    parser.add_argument("--screenshot-path", help="Optional existing screenshot path reference")
    args = parser.parse_args(argv)

    if args.fixture or args.fixture_json:
        windows = load_fixture(args.fixture, args.fixture_json)
        payload = classify_windows(windows, screenshot_path=args.screenshot_path)
        payload["source"] = "fixture"
    else:
        windows, error = enumerate_windows()
        if error:
            payload = {
                "schema_version": "mosim.mworks_gui_sentinel.v1",
                "created_at": now_cst(),
                "sentinel": "win32_enumwindows_text",
                "source": "live_window_inventory",
                "status": "sentinel_unavailable",
                "error_kind": "gui_sentinel_unavailable",
                "unavailable_reason": error,
                "window_count": len(windows),
                "windows": windows,
                "will_click_or_close_any_window": False,
                "next_safe_recovery_step": "Do not claim unattended MWORKS GUI safety; use PMO-approved visible GUI inspection or restore a working sentinel surface.",
            }
        else:
            payload = classify_windows(windows, screenshot_path=args.screenshot_path)
            payload["source"] = "live_window_inventory"

    write_json(args.output, payload)
    if payload["status"] in {"incident_detected", "sentinel_unavailable"}:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
