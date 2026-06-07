#!/usr/bin/env python3
"""Check MoSim WeChat gateway health without spamming WeChat.

Default mode is local-only: inspect cc-connect runtime state and write a JSON
snapshot. Use --send-canary only for an explicit low-frequency outbound test.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GATEWAY = ROOT / "CoAgent" / "gateway" / "cc_connect_weixin.py"
EMAIL_ALERT = ROOT / "Scripts" / "agent" / "send_gateway_email_alert.py"
CC_BIN = ROOT / "Results" / "tmp" / "cc-connect-node" / "node_modules" / "cc-connect" / "bin" / "cc-connect"
WSL_DATA_DIR = "/home/linux/.cache/mosim/coagent/cc-connect-weixin/data"
PROJECT = "MoSim｜微信通知网关"
OUT_DIR = ROOT / "Results" / "coagent_gateway" / "health"
WSL_DISTRO = "Ubuntu-22.04"
HEALTHY_LATEST = OUT_DIR / "gateway_healthy_latest.json"
UNHEALTHY_LATEST = OUT_DIR / "gateway_unhealthy_latest.json"
OUTBOUND_LATEST = OUT_DIR / "gateway_outbound_latest.json"
OUTBOUND_UNHEALTHY_LATEST = OUT_DIR / "gateway_outbound_unhealthy_latest.json"
EMAIL_INCIDENT_STATE = OUT_DIR / "gateway_email_intervention_state.json"
DEFAULT_CONFIG = ROOT / "Results" / "tmp" / "cc-connect-weixin-smoke" / "config-wsl-runtime.toml"
RUNTIME_DIR = ROOT / "Results" / "tmp" / "cc-connect-weixin-smoke"


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
    socket_path = data_dir / "run" / "api.sock"
    if not socket_path.exists():
        return {"ok": False, "socket_exists": False, "error": "api_socket_missing"}
    if sys.platform.startswith("win"):
        script = (
            "import socket, sys\n"
            "p = sys.argv[1]\n"
            "s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)\n"
            f"s.settimeout({max(1, timeout)!r})\n"
            "try:\n"
            "    s.connect(p)\n"
            "    print('connect_ok')\n"
            "except Exception as exc:\n"
            "    print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr)\n"
            "    raise SystemExit(1)\n"
            "finally:\n"
            "    s.close()\n"
        )
        command = [
            "wsl.exe",
            "-d",
            WSL_DISTRO,
            "--",
            "python3",
            "-c",
            script,
            to_wsl_path(socket_path),
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
                timeout=timeout + 2,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"ok": False, "socket_exists": True, "error": f"{type(exc).__name__}: {exc}"}
        return {
            "ok": completed.returncode == 0,
            "socket_exists": True,
            "returncode": completed.returncode,
            "stdout_tail": (completed.stdout or "")[-500:],
            "stderr_tail": (completed.stderr or "")[-500:],
        }
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(max(1, timeout))
    try:
        sock.connect(str(socket_path))
    except OSError as exc:
        return {"ok": False, "socket_exists": True, "error": f"{type(exc).__name__}: {exc}"}
    finally:
        sock.close()
    return {"ok": True, "socket_exists": True}


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


def recover_api_socket(data_dir: Path, config: Path, timeout: int = 20) -> dict[str, object]:
    """One bounded local runtime recovery for stale/missing cc-connect API sockets."""
    if not sys.platform.startswith("win"):
        return {"attempted": False, "reason": "windows_wsl_runtime_expected"}
    if not CC_BIN.exists():
        return {"attempted": False, "reason": "cc_bin_missing", "cc_bin": str(CC_BIN)}
    if not config.exists():
        return {"attempted": False, "reason": "config_missing", "config": str(config)}
    stamp = now_stamp()
    log_path = RUNTIME_DIR / f"health-recover-{stamp}.log"
    lock_path = RUNTIME_DIR / ".config-wsl-runtime.toml.lock"
    socket_path = data_dir / "run" / "api.sock"
    script = (
        "import os, signal, subprocess, sys\n"
        "lock, sock, bin_path, cfg, log = sys.argv[1:6]\n"
        "pid = ''\n"
        "try:\n"
        "    with open(lock, 'r', encoding='utf-8', errors='replace') as handle:\n"
        "        pid = handle.read().strip()\n"
        "except OSError:\n"
        "    pass\n"
        "if pid:\n"
        "    try:\n"
        "        os.kill(int(pid), 0)\n"
        "    except (OSError, ValueError):\n"
        "        pass\n"
        "    else:\n"
        "        print(f'active_lock_pid={pid}', file=sys.stderr)\n"
        "        raise SystemExit(3)\n"
        "for path in (lock, sock):\n"
        "    try:\n"
        "        os.unlink(path)\n"
        "    except FileNotFoundError:\n"
        "        pass\n"
        "os.makedirs(os.path.dirname(log), exist_ok=True)\n"
        "log_handle = open(log, 'ab', buffering=0)\n"
        "proc = subprocess.Popen(\n"
        "    [bin_path, '--config', cfg],\n"
        "    cwd='/mnt/c/Users/HP/Desktop/MoSim',\n"
        "    stdin=subprocess.DEVNULL,\n"
        "    stdout=log_handle,\n"
        "    stderr=subprocess.STDOUT,\n"
        "    start_new_session=True,\n"
        ")\n"
        "print(proc.pid)\n"
    )
    command = [
        "wsl.exe",
        "-d",
        WSL_DISTRO,
        "--",
        "python3",
        "-c",
        script,
        to_wsl_path(lock_path),
        to_wsl_path(socket_path),
        to_wsl_path(CC_BIN),
        to_wsl_path(config),
        to_wsl_path(log_path),
    ]
    try:
        started = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"attempted": True, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
    result: dict[str, object] = {
        "attempted": True,
        "start_returncode": started.returncode,
        "stdout_tail": (started.stdout or "")[-500:],
        "stderr_tail": (started.stderr or "")[-500:],
        "log_path": str(log_path),
    }
    if started.returncode != 0:
        result["ok"] = False
        return result
    deadline = time.monotonic() + max(1, timeout)
    probe: dict[str, object] = {}
    while time.monotonic() < deadline:
        probe = probe_api_socket(data_dir, timeout=3)
        if probe.get("ok"):
            result["ok"] = True
            result["api_socket_probe"] = probe
            return result
        time.sleep(0.5)
    result["ok"] = False
    result["api_socket_probe"] = probe
    try:
        result["log_tail"] = log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
    except OSError:
        pass
    return result


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def close_email_incidents(reason: str) -> None:
    state = read_json(EMAIL_INCIDENT_STATE)
    open_items = state.get("open")
    if not isinstance(open_items, dict) or not open_items:
        return
    state["last_closed_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
    state["last_closed_reason"] = reason
    state["closed"] = open_items
    state["open"] = {}
    write_json(EMAIL_INCIDENT_STATE, state)


def email_incident_is_open(key: str) -> bool:
    state = read_json(EMAIL_INCIDENT_STATE)
    open_items = state.get("open")
    return isinstance(open_items, dict) and key in open_items


def mark_email_incident_open(key: str, status_path: Path, email_result: dict[str, object]) -> None:
    state = read_json(EMAIL_INCIDENT_STATE)
    open_items = state.get("open")
    if not isinstance(open_items, dict):
        open_items = {}
    open_items[key] = {
        "opened_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status_path": str(status_path),
        "email_result": email_result,
    }
    state["open"] = open_items
    write_json(EMAIL_INCIDENT_STATE, state)


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


def classify_canary_failure(send_canary: dict[str, object]) -> str:
    text = f"{send_canary.get('stdout_tail', '')}\n{send_canary.get('stderr_tail', '')}".lower()
    if "ret=-2" in text:
        return "weixin_ret_minus_2"
    if "context_token" in text:
        return "context_token"
    if "no active session" in text:
        return "active_session"
    if "api.sock" in text or "connection refused" in text:
        return "api_socket"
    return "weixin_outbound"


def canary_minimal_action(kind: str) -> str:
    if kind == "weixin_ret_minus_2":
        return "请在 MoSim｜微信通知网关 微信聊天里发一条普通文字消息；若下一次 canary 仍失败，再重新扫码 QR。"
    if kind in {"context_token", "active_session"}:
        return minimal_user_action(kind)
    if kind == "api_socket":
        return minimal_user_action(kind)
    return "查看 gateway_outbound_unhealthy_latest.json；不要循环重试 canary。"


def write_outbound_status(result: dict[str, object], out_path: Path) -> None:
    send_canary = result.get("send_canary")
    if not isinstance(send_canary, dict):
        return
    ok = bool(send_canary.get("ok"))
    kind = "" if ok else classify_canary_failure(send_canary)
    payload = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "healthy" if ok else "unhealthy",
        "latest_snapshot": str(out_path),
        "failure_kind": kind,
        "send_canary": send_canary,
        "send_canary_packet": result.get("send_canary_packet"),
        "minimal_user_action": "无需处理。" if ok else canary_minimal_action(kind),
        "note": "This file records real end-to-end Weixin outbound canary state. Local health snapshots must not overwrite it.",
    }
    write_json(OUTBOUND_LATEST, payload)
    if not ok:
        payload["windows_notification"] = send_windows_notification(payload)
        write_json(OUTBOUND_UNHEALTHY_LATEST, payload)
        payload["email_alert"] = send_email_alert(OUTBOUND_UNHEALTHY_LATEST, kind)
        write_json(OUTBOUND_UNHEALTHY_LATEST, payload)
    else:
        close_email_incidents("outbound_canary_recovered")


def write_latest_status(result: dict[str, object], out_path: Path) -> None:
    local = result.get("local", {})
    if not isinstance(local, dict):
        local = {}
    ok_local = bool(local.get("ok_local"))
    send_canary = result.get("send_canary")
    canary_failed = isinstance(send_canary, dict) and not bool(send_canary.get("ok"))
    payload = {
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "healthy" if ok_local and not canary_failed else "unhealthy",
        "latest_snapshot": str(out_path),
        "local": local,
        "send_canary": send_canary,
        "wechat_notification_attempted": False,
        "wechat_notification_reason": "local health failures must be reported by files/local OS notification because WeChat may be the broken channel",
    }
    if ok_local and not canary_failed:
        payload["failure_kind"] = ""
        payload["minimal_user_action"] = "无需处理。"
        write_json(HEALTHY_LATEST, payload)
        return
    failure_kind = classify_local_failure(local) if not ok_local else "weixin_outbound"
    payload["failure_kind"] = failure_kind
    if failure_kind == "weixin_outbound":
        payload["minimal_user_action"] = "请在 MoSim｜微信通知网关 微信聊天里发一条普通文字消息，然后只重试一次 canary。"
    else:
        payload["minimal_user_action"] = minimal_user_action(failure_kind)
    payload["windows_notification"] = send_windows_notification(payload)
    write_json(UNHEALTHY_LATEST, payload)
    payload["email_alert"] = send_email_alert(UNHEALTHY_LATEST, failure_kind)
    write_json(UNHEALTHY_LATEST, payload)


def send_email_alert(status_path: Path, cooldown_key: str) -> dict[str, object]:
    if os.environ.get("MOSIM_GATEWAY_EMAIL_ALERT", "1") == "0":
        return {"attempted": False, "reason": "disabled_by_MOSIM_GATEWAY_EMAIL_ALERT"}
    incident_key = f"weixin-gateway:{cooldown_key}"
    if email_incident_is_open(incident_key):
        return {"attempted": False, "reason": "already_sent_for_open_incident", "incident_key": incident_key}
    command = [
        sys.executable,
        str(EMAIL_ALERT),
        "--status-json",
        str(status_path),
        "--cooldown-key",
        incident_key,
        "--cooldown-minutes",
        "0",
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
            timeout=30,
            check=False,
        )
    except Exception as exc:
        return {"attempted": True, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
    result = {
        "attempted": True,
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout_tail": (completed.stdout or "")[-1000:],
        "stderr_tail": (completed.stderr or "")[-1000:],
    }
    if result["ok"]:
        mark_email_incident_open(incident_key, status_path, result)
    return result


def send_windows_notification(payload: dict[str, object]) -> dict[str, object]:
    if not sys.platform.startswith("win"):
        return {"attempted": False, "reason": "not_windows"}
    if os.environ.get("MOSIM_WEIXIN_HEALTH_TOAST", "1") == "0":
        return {"attempted": False, "reason": "disabled_by_MOSIM_WEIXIN_HEALTH_TOAST"}
    title = "MoSim Weixin gateway unhealthy"
    message = f"{payload.get('failure_kind')}: {payload.get('minimal_user_action')}"
    ps_title = title.replace("'", "''")
    ps_message = message.replace("'", "''")
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
            f"$texts.Item(0).AppendChild($xml.CreateTextNode('{ps_title}')) > $null;"
            f"$texts.Item(1).AppendChild($xml.CreateTextNode('{ps_message}')) > $null;"
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
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--recover-api-socket", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    stamp = now_stamp()
    result: dict[str, object] = {"local": inspect_state(args.data_dir), "send_canary": None}
    if (
        args.recover_api_socket
        and not bool(result["local"].get("ok_local"))
        and classify_local_failure(result["local"]) == "api_socket"
    ):
        result["local_recovery"] = recover_api_socket(args.data_dir, args.config, timeout=min(args.timeout, 30))
        result["local_after_recovery"] = inspect_state(args.data_dir)
        if bool(result["local_after_recovery"].get("ok_local")):
            result["local"] = result["local_after_recovery"]
    if args.send_canary:
        packet_path = args.out_dir / f"weixin_gateway_health_canary_{stamp}.json"
        make_canary_packet(packet_path)
        result["send_canary_packet"] = str(packet_path)
        result["send_canary"] = send_canary(packet_path, args.timeout)

    out_path = args.out_dir / f"weixin_gateway_health_{stamp}.json"
    write_json(out_path, result)
    write_latest_status(result, out_path)
    write_outbound_status(result, out_path)
    ok_local = bool(result["local"].get("ok_local"))
    canary_ok = not args.send_canary or (isinstance(result["send_canary"], dict) and bool(result["send_canary"].get("ok")))
    ok = ok_local and canary_ok
    print(json.dumps({"ok": ok, "ok_local": ok_local, "path": str(out_path), "send_canary": result["send_canary"]}, ensure_ascii=False))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
