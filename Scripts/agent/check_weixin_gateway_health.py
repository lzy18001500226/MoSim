#!/usr/bin/env python3
"""Check MoSim WeChat gateway health without spamming WeChat.

Default mode is local-only: inspect cc-connect runtime state and write a JSON
snapshot. Use --send-canary only for an explicit low-frequency outbound test.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATEWAY = ROOT / "CoAgent" / "gateway" / "cc_connect_weixin.py"
CC_BIN = ROOT / "Results" / "tmp" / "cc-connect-node" / "node_modules" / "cc-connect" / "bin" / "cc-connect"
WSL_DATA_DIR = "/home/linux/.cache/mosim/coagent/cc-connect-weixin/data"
PROJECT = "MoSim｜微信通知网关"
OUT_DIR = ROOT / "Results" / "coagent_gateway" / "health"
WSL_DISTRO = "Ubuntu-22.04"
HEALTHY_LATEST = OUT_DIR / "gateway_healthy_latest.json"
UNHEALTHY_LATEST = OUT_DIR / "gateway_unhealthy_latest.json"


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def default_data_dir() -> Path:
    if sys.platform.startswith("win"):
        return Path(r"\\wsl.localhost\Ubuntu-22.04\home\linux\.cache\mosim\coagent\cc-connect-weixin\data")
    return Path(WSL_DATA_DIR)


def to_wsl_path(path: Path) -> str:
    text = str(path)
    if text.startswith("\\\\wsl.localhost\\") or text.startswith("\\\\wsl$\\"):
        parts = text.split("\\")
        if len(parts) >= 5:
            return "/" + "/".join(parts[4:])
    drive = path.drive.rstrip(":").lower()
    if drive:
        rest = text[len(path.drive) :].replace("\\", "/").lstrip("/")
        return f"/mnt/{drive}/{rest}"
    return text.replace("\\", "/")


def probe_api_socket(data_dir: Path, timeout: int = 8) -> dict[str, object]:
    if sys.platform.startswith("win"):
        command = [
            "wsl.exe",
            "-d",
            WSL_DISTRO,
            "--",
            to_wsl_path(CC_BIN),
            "sessions",
            "list",
            "--data-dir",
            to_wsl_path(data_dir),
        ]
    else:
        command = [str(CC_BIN), "sessions", "list", "--data-dir", str(data_dir)]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-500:],
        "stderr_tail": (completed.stderr or "")[-500:],
    }


def inspect_state(data_dir: Path) -> dict[str, object]:
    sessions_dir = data_dir / "sessions"
    socket_path = data_dir / "run" / "api.sock"
    api_probe = probe_api_socket(data_dir)
    project_sessions = sorted(sessions_dir.glob(f"{PROJECT}_*.json")) if sessions_dir.exists() else []
    all_sessions = sorted(sessions_dir.glob("*.json")) if sessions_dir.exists() else []
    active_session = ""
    active_source = ""
    for path in project_sessions + [p for p in all_sessions if p not in project_sessions]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        active = payload.get("active_session") or {}
        if isinstance(active, dict):
            active_session = str(active.get("key") or "")
            if not active_session and active:
                active_session = str(next(iter(active.keys())))
        elif active:
            active_session = str(active)
        if active_session:
            active_source = str(path)
            break
    context_root = data_dir / "weixin" / PROJECT
    context_files = sorted(context_root.glob("*/context_tokens.json")) if context_root.exists() else []
    ok_local = data_dir.exists() and socket_path.exists() and bool(api_probe["ok"]) and bool(active_session) and bool(context_files)
    return {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "project": PROJECT,
        "data_dir": str(data_dir),
        "data_dir_exists": data_dir.exists(),
        "api_socket_exists": socket_path.exists(),
        "api_socket_connectable": bool(api_probe["ok"]),
        "api_socket_probe": api_probe,
        "project_session_files": len(project_sessions),
        "all_session_files": len(all_sessions),
        "active_session_present": bool(active_session),
        "active_session_key_type": "platform" if ":" in active_session else ("alias_or_empty" if active_session else "missing"),
        "active_session_source": active_source,
        "context_token_files": len(context_files),
        "ok_local": ok_local,
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def classify_local_failure(local: dict[str, object]) -> str:
    if not local.get("data_dir_exists"):
        return "data_dir"
    if not local.get("api_socket_exists"):
        return "api_socket"
    if not local.get("api_socket_connectable"):
        return "api_socket"
    if int(local.get("project_session_files") or 0) <= 0:
        return "session"
    if not local.get("active_session_present"):
        return "active_session"
    if local.get("active_session_key_type") != "platform":
        return "active_session"
    if int(local.get("context_token_files") or 0) <= 0:
        return "context_token"
    return "unknown"


def minimal_user_action(kind: str) -> str:
    if kind in {"active_session", "context_token"}:
        return "请在 MoSim｜微信通知网关 微信聊天里发一条普通文字消息，然后重试一次 canary。"
    if kind == "session":
        return "请确认 cc-connect Weixin 项目会话 MoSim｜微信通知网关 存在；如不存在，重新扫码 QR。"
    if kind == "api_socket":
        return "无需先操作微信；先检查或重启 cc-connect 后台进程。"
    if kind == "data_dir":
        return "无需先操作微信；先检查 WSL 数据目录和 Ubuntu-22.04 可访问性。"
    return "先查看 gateway_unhealthy_latest.json 中的 failure_kind 和 api_socket_probe。"


def write_latest_status(result: dict[str, object], out_path: Path) -> None:
    local = result.get("local", {})
    if not isinstance(local, dict):
        local = {}
    ok_local = bool(local.get("ok_local"))
    payload = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "healthy" if ok_local else "unhealthy",
        "latest_snapshot": str(out_path),
        "local": local,
        "send_canary": result.get("send_canary"),
        "wechat_notification_attempted": False,
        "wechat_notification_reason": "local health failures must be reported by files/local OS notification because WeChat may be the broken channel",
    }
    if ok_local:
        payload["failure_kind"] = ""
        payload["minimal_user_action"] = "无需处理。"
        write_json(HEALTHY_LATEST, payload)
        return
    failure_kind = classify_local_failure(local)
    payload["failure_kind"] = failure_kind
    payload["minimal_user_action"] = minimal_user_action(failure_kind)
    payload["windows_notification"] = send_windows_notification(payload)
    write_json(UNHEALTHY_LATEST, payload)


def send_windows_notification(payload: dict[str, object]) -> dict[str, object]:
    if not sys.platform.startswith("win"):
        return {"attempted": False, "reason": "not_windows"}
    if os.environ.get("MOSIM_WEIXIN_HEALTH_TOAST", "1") == "0":
        return {"attempted": False, "reason": "disabled_by_MOSIM_WEIXIN_HEALTH_TOAST"}
    title = "MoSim Weixin gateway unhealthy"
    message = f"{payload.get('failure_kind')}: {payload.get('minimal_user_action')}"
    command = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        (
            "$ErrorActionPreference='Stop';"
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null;"
            "$template=[Windows.UI.Notifications.ToastTemplateType]::ToastText02;"
            "$xml=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template);"
            "$texts=$xml.GetElementsByTagName('text');"
            f"$texts.Item(0).AppendChild($xml.CreateTextNode(@'{title}'@)) > $null;"
            f"$texts.Item(1).AppendChild($xml.CreateTextNode(@'{message}'@)) > $null;"
            "$toast=[Windows.UI.Notifications.ToastNotification]::new($xml);"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('MoSim.WeixinGateway').Show($toast);"
        ),
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
    except Exception as exc:
        return {"attempted": True, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "attempted": True,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stderr_tail": (completed.stderr or "")[-500:],
    }


def make_canary_packet(path: Path) -> None:
    payload = {
        "template_type": "completion_notification",
        "task_id": "WEIXIN-GATEWAY-HEALTH-CANARY",
        "canonical_status": "completed",
        "owner": "MoSim｜微信网关运维",
        "summary": "微信通知链路定时探活 canary。收到此消息说明 cc-connect outbound send 当前可用。",
        "evidence_paths": [str(path.relative_to(ROOT)).replace("\\", "/")],
        "next_recommended_action": "无需处理；若频率过高，请降低计划任务频率。",
        "dedupe_key": f"weixin-gateway-health-canary:{now_stamp()}",
    }
    write_json(path, payload)


def send_canary(packet_path: Path, timeout: int) -> dict[str, object]:
    command = [
        sys.executable,
        str(GATEWAY),
        "notify",
        "--packet",
        str(packet_path),
        "--send",
        "--force",
        "--timeout",
        str(timeout),
        "--data-dir",
        str(default_data_dir()),
        "--omit-message-in-audit",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=max(timeout + 10, 20),
    )
    return {
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
        "ok": completed.returncode == 0 and '"ok": true' in completed.stdout.lower(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send-canary", action="store_true", help="send one real WeChat canary message")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--data-dir", type=Path, default=default_data_dir())
    args = parser.parse_args()

    stamp = now_stamp()
    result: dict[str, object] = {"local": inspect_state(args.data_dir), "send_canary": None}
    if args.send_canary:
        packet_path = args.out_dir / f"weixin_gateway_health_canary_{stamp}.json"
        make_canary_packet(packet_path)
        result["send_canary_packet"] = str(packet_path)
        result["send_canary"] = send_canary(packet_path, args.timeout)

    out_path = args.out_dir / f"weixin_gateway_health_{stamp}.json"
    write_json(out_path, result)
    write_latest_status(result, out_path)
    print(json.dumps({"ok": bool(result["local"].get("ok_local")), "path": str(out_path), "send_canary": result["send_canary"]}, ensure_ascii=False))
    return 0 if result["local"].get("ok_local") else 2


if __name__ == "__main__":
    raise SystemExit(main())
