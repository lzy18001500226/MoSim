#!/usr/bin/env python3
"""Run arbitrary long-duration sensitivity profiles through existing FormalRunners.

The frozen seven-scenario A/B runner intentionally accepts exactly seven named
profiles.  This entry point preserves that runner and its evidence helpers, but
uses ``profile_id`` as the case key so a single scenario can be evaluated at
multiple disturbance strengths.  It never changes Plant or controller source.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import io
import json
import math
import re
import shutil
import subprocess
import sys
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LEGACY_RUNNER = ROOT / "Scripts" / "mworks" / "run_seven_scenario_ab.py"
MCP_RUNNER = ROOT / "Scripts" / "mworks" / "run_sysplorer_mcp_smoke.py"
SENTINEL_SCRIPT = ROOT / "Scripts" / "agent" / "check_mworks_gui_sentinel.py"
CAPTURE_SCRIPT = ROOT / "Scripts" / "tools" / "capture_window_background.ps1"
DEFAULT_CONTRACT = ROOT / "Config" / "control_platform" / "seven_scenario_injection_contract_v2.json"
# This is the client-side MCP wait bound, not a Modelica solver setting.  A
# 50 s formal run can legitimately take longer than the old 120 s transport
# timeout while the MWORKS worker stays responsive.
DEFAULT_TIMEOUT_S = 360.0
EVIDENCE_LEVEL = "formal_mworks_sensitivity_long_duration_v1"
SENSITIVITY_SCENARIOS = frozenset({
    "motor_efficiency_fault",
    "wind_disturbance",
    "parameter_mismatch",
})
REQUIRED_OVERRIDE_KEYS = (
    "gust_force",
    "gust_start_s",
    "gust_duration_s",
    "mass_scale",
    "inertia_scale",
    "rotor_effectiveness",
    "fault_start_s",
    "fault_rotor_index",
    "fault_rotor_effectiveness",
)


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


LEGACY = load_module(LEGACY_RUNNER, "mosim_sensitivity_legacy_runner")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_project_path(path: Path) -> Path:
    resolved = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"Path must remain under the project root: {resolved}") from exc
    return resolved


def project_relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def optional_project_path(value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return resolve_project_path(Path(value))
    except (OSError, ValueError):
        return None


def mcp_tool_response_payload(event: dict[str, Any]) -> dict[str, Any] | None:
    result = event.get("result")
    if not isinstance(result, dict):
        return None
    for candidate in (
        result.get("structuredContent", {}).get("result") if isinstance(result.get("structuredContent"), dict) else None,
        *(
            item.get("text")
            for item in result.get("content", [])
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        ),
    ):
        if isinstance(candidate, dict):
            return candidate
        if isinstance(candidate, str):
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return None


def infer_check_model_status(mcp_log: Path, model_name: str) -> str:
    """Classify a completed CheckModel request from an existing JSONL MCP log."""
    if not mcp_log.is_file():
        return "not_observed"
    request_ids: set[str] = set()
    for line in mcp_log.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("direction") == "request":
            params = event.get("params") if isinstance(event.get("params"), dict) else {}
            arguments = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
            if params.get("name") == "check_model" and arguments.get("model_name") == model_name:
                request_ids.add(str(event.get("id")))
            continue
        if event.get("direction") != "response" or str(event.get("id")) not in request_ids:
            continue
        payload = mcp_tool_response_payload(event)
        return "passed" if isinstance(payload, dict) and payload.get("ok") is True else "failed"
    return "not_observed"


def finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def require_vector(value: Any, size: int, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(f"{label} must be an array of {size} numeric values")
    return [finite_number(item, f"{label}[{index}]") for index, item in enumerate(value)]


def validate_profile(profile: Any) -> dict[str, Any]:
    if not isinstance(profile, dict):
        raise ValueError("Each profile must be an object")
    profile_id = profile.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ValueError("Each profile requires a nonempty profile_id")
    scenario = profile.get("scenario_id")
    if scenario not in SENSITIVITY_SCENARIOS:
        raise ValueError(f"Unsupported sensitivity scenario_id for {profile_id}: {scenario!r}")
    if not isinstance(profile.get("trajectory_class"), str):
        raise ValueError(f"{profile_id} requires trajectory_class")
    if abs(finite_number(profile.get("duration_s"), f"{profile_id}.duration_s") - 50.0) > 1e-9:
        raise ValueError(f"{profile_id} must use the 50 s long-duration contract")
    trajectory = profile.get("trajectory_parameter_overrides")
    if not isinstance(trajectory, dict):
        raise ValueError(f"{profile_id}.trajectory_parameter_overrides must be an object")
    overrides = profile.get("runner_parameter_overrides")
    if not isinstance(overrides, dict):
        raise ValueError(f"{profile_id}.runner_parameter_overrides must be an object")
    missing = [key for key in REQUIRED_OVERRIDE_KEYS if key not in overrides]
    if missing:
        raise ValueError(f"{profile_id} is missing runner overrides: {', '.join(missing)}")
    if "time_varying_rotor_effectiveness" in overrides or "time_varying_rotor_effectiveness" in profile:
        raise ValueError(f"{profile_id} requests unsupported short-duration time-varying rotor effectiveness")
    require_vector(overrides["gust_force"], 3, f"{profile_id}.gust_force")
    require_vector(overrides["inertia_scale"], 3, f"{profile_id}.inertia_scale")
    require_vector(overrides["rotor_effectiveness"], 4, f"{profile_id}.rotor_effectiveness")
    finite_number(overrides["mass_scale"], f"{profile_id}.mass_scale")
    finite_number(overrides["fault_start_s"], f"{profile_id}.fault_start_s")
    finite_number(overrides["fault_rotor_effectiveness"], f"{profile_id}.fault_rotor_effectiveness")

    if scenario == "motor_efficiency_fault":
        if profile["trajectory_class"] != "MoSimQuadrotorModel.Guidance.Trajectories.Figure8":
            raise ValueError(f"{profile_id} must use Figure8")
        if abs(finite_number(overrides["fault_start_s"], f"{profile_id}.fault_start_s") - 15.0) > 1e-9:
            raise ValueError(f"{profile_id} must start the sustained fault at 15 s")
    elif scenario == "wind_disturbance":
        if profile["trajectory_class"] != "MoSimQuadrotorModel.Guidance.Trajectories.Figure8":
            raise ValueError(f"{profile_id} must use Figure8")
        if abs(finite_number(overrides["gust_start_s"], f"{profile_id}.gust_start_s") - 15.0) > 1e-9:
            raise ValueError(f"{profile_id} must start the sustained gust at 15 s")
        if abs(finite_number(overrides["gust_duration_s"], f"{profile_id}.gust_duration_s") - 35.0) > 1e-9:
            raise ValueError(f"{profile_id} must sustain the gust through 50 s")
    else:
        if profile["trajectory_class"] != "MoSimQuadrotorModel.Guidance.Trajectories.SpiralAscent":
            raise ValueError(f"{profile_id} must use SpiralAscent")
        mass_scale = finite_number(overrides["mass_scale"], f"{profile_id}.mass_scale")
        if any(abs(value - mass_scale) > 1e-9 for value in require_vector(overrides["inertia_scale"], 3, f"{profile_id}.inertia_scale")):
            raise ValueError(f"{profile_id} requires synchronized mass and inertia scales")
    return profile


def read_profiles(profile_path: Path) -> tuple[dict[str, Any], str]:
    document = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"Profile document must be an object: {profile_path}")
    if document.get("schema") != "mosim.seven_scenario_experiment_profiles.v2":
        raise ValueError("Sensitivity profile document has the wrong schema")
    profiles = document.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("Sensitivity profile document must contain one or more profiles")
    ids: set[str] = set()
    for profile in profiles:
        validated = validate_profile(profile)
        profile_id = str(validated["profile_id"])
        if profile_id in ids:
            raise ValueError(f"Duplicate profile_id: {profile_id}")
        ids.add(profile_id)
    return document, sha256_path(profile_path)


def expected_profile_strengths(document: dict[str, Any]) -> list[float]:
    """Return the configured gradient without imposing a seven-profile shape."""
    values: list[float] = []
    for profile in document["profiles"]:
        overrides = profile["runner_parameter_overrides"]
        scenario = profile["scenario_id"]
        if scenario == "motor_efficiency_fault":
            values.append(float(overrides["fault_rotor_effectiveness"]))
        elif scenario == "wind_disturbance":
            values.append(float(overrides["gust_force"][0]))
        else:
            values.append(float(overrides["mass_scale"]))
    return values


@dataclass(frozen=True)
class SensitivityCase:
    controller_id: str
    profile: dict[str, Any]
    result_root: Path

    @property
    def controller(self) -> dict[str, str]:
        return LEGACY.CONTROLLERS[self.controller_id]

    @property
    def scenario_id(self) -> str:
        return str(self.profile["scenario_id"])

    @property
    def profile_id(self) -> str:
        return str(self.profile["profile_id"])

    @property
    def model_name(self) -> str:
        return f"Sensitivity{self.controller['model_slug']}_{LEGACY.camel_case(self.profile_id)}"

    @property
    def output_dir(self) -> Path:
        return self.result_root / self.controller_id / self.profile_id


def selected_cases(document: dict[str, Any], controllers: list[str], result_root: Path) -> list[SensitivityCase]:
    allowed = document.get("formal_runner_binding", {}).get("allowed_runner_classes", [])
    if not isinstance(allowed, list):
        raise ValueError("formal_runner_binding.allowed_runner_classes must be an array")
    unsupported = [
        controller_id for controller_id in controllers
        if LEGACY.CONTROLLERS[controller_id]["runner_class"] not in allowed
    ]
    if unsupported:
        raise ValueError(f"Selected controller(s) are not allowed by this profile: {unsupported}")
    return [
        SensitivityCase(controller_id, profile, result_root)
        for controller_id in controllers
        for profile in document["profiles"]
    ]


def harness_path(case: SensitivityCase) -> Path:
    return case.output_dir / "harness" / f"{case.model_name}.mo"


def stage_harness(case: SensitivityCase) -> Path:
    path = harness_path(case)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(LEGACY.render_harness(case), encoding="utf-8", newline="\n")
    return path


def build_command(case: SensitivityCase, harness: Path, native_result_dir: Path, timeout_s: float) -> list[str]:
    command = LEGACY.runner_arguments(case, harness, EVIDENCE_LEVEL, native_result_dir)
    command = [argument for argument in command if argument != "--gui-reset-windows"]
    timeout_index = command.index("--simulation-timeout-s") + 1
    command[timeout_index] = f"{timeout_s:g}"
    # Retain the native Result.msr, but do not open a plot/animation window for
    # each of the 24 cases. Background captures record the reusable main window.
    command.append("--no-gui-open")
    return command


def write_run_config(
    case: SensitivityCase,
    *,
    profile_path: Path,
    profile_hash: str,
    contract_path: Path,
    contract_hash: str,
    harness: Path,
    native_result_dir: Path,
    command: list[str],
) -> Path:
    path = case.output_dir / "RUN_CONFIG.json"
    write_json(path, {
        "schema": "mosim.sensitivity_run_config.v1",
        "generated_at": utc_now(),
        "controller_id": case.controller_id,
        "runner_class": case.controller["runner_class"],
        "scenario_id": case.scenario_id,
        "profile_id": case.profile_id,
        "profile": case.profile,
        "profile_document": project_relative(profile_path),
        "profile_sha256": profile_hash,
        "injection_contract_document": project_relative(contract_path),
        "injection_contract_sha256": contract_hash,
        "harness": project_relative(harness),
        "native_result_directory": project_relative(native_result_dir),
        "command": command,
        "source": "MWORKS_MCP",
        "claim_boundary": "This configuration binds an existing FormalRunner to a profile. It does not alter Plant source, controller gains, or runtime deployment behavior."
    })
    return path


def process_snapshot() -> dict[str, Any]:
    script = (
        "$rows = @(Get-Process -ErrorAction SilentlyContinue | Where-Object "
        "{ $_.ProcessName -match '^(mworks|sysplorer|mw_browser_proxy|mw_crash_handler|syslab)$' } | "
        "Select-Object Id,ProcessName,StartTime,Path); $rows | ConvertTo-Json -Depth 3 -Compress"
    )
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", script],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    rows: list[dict[str, Any]] = []
    if completed.returncode == 0 and completed.stdout.strip():
        try:
            parsed = json.loads(completed.stdout)
            rows = parsed if isinstance(parsed, list) else [parsed]
            rows = [row for row in rows if isinstance(row, dict)]
        except json.JSONDecodeError:
            pass
    return {
        "captured_at": utc_now(),
        "exit_code": completed.returncode,
        "count": len(rows),
        "processes": rows,
        "stderr": completed.stderr.strip(),
    }


def mworks_process_ids(snapshot: dict[str, Any]) -> set[int]:
    return {
        int(row["Id"])
        for row in snapshot.get("processes", [])
        if isinstance(row, dict)
        and str(row.get("ProcessName") or "").casefold() == "mworks"
        and isinstance(row.get("Id"), int)
    }


def mworks_pid_for_port(port: Any) -> int | None:
    if not isinstance(port, int) or port <= 0:
        return None
    command = (
        "$connection = Get-NetTCPConnection -LocalPort "
        f"{port} -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; "
        "if ($connection) { $connection.OwningProcess }"
    )
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=15,
        check=False,
    )
    try:
        return int(completed.stdout.strip())
    except ValueError:
        return None


def classify_session_binding(
    *,
    mworks_pid: int | None,
    before_mworks_pids: set[int],
    allowed_existing_mworks_pids: set[int],
) -> dict[str, Any]:
    if not isinstance(mworks_pid, int) or mworks_pid <= 0:
        return {
            "blocked": True,
            "blocker_kind": "gui_or_sentinel_unavailable",
            "observation": "The batch MCP health response did not resolve a dedicated MWORKS process ID; no window capture or model call will be attempted against an ambiguous session.",
        }
    if mworks_pid in before_mworks_pids and mworks_pid not in allowed_existing_mworks_pids:
        return {
            "blocked": True,
            "blocker_kind": "ambiguous_existing_mworks_session",
            "observation": f"The batch MCP client resolved pre-existing MWORKS PID {mworks_pid}, which was not explicitly authorized for this batch.",
        }
    return {
        "blocked": False,
        "ownership": "explicitly_authorized_existing_session" if mworks_pid in before_mworks_pids else "batch_started_dedicated_session",
        "mworks_pid": mworks_pid,
        "observation": f"The batch MCP client is bound to MWORKS PID {mworks_pid} without selecting an unapproved pre-existing session.",
    }


def run_sentinel(output_path: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(SENTINEL_SCRIPT), "--output", str(output_path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    payload: dict[str, Any] = {}
    if output_path.is_file():
        try:
            parsed = json.loads(output_path.read_text(encoding="utf-8"))
            payload = parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            payload = {}
    return {
        "command": [sys.executable, str(SENTINEL_SCRIPT), "--output", str(output_path)],
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "output": project_relative(output_path) if output_path.is_file() else None,
        "payload": payload,
    }


def build_capture_command(output_dir: Path, *, maximize: bool, mworks_pid: int) -> list[str]:
    command = [
        "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(CAPTURE_SCRIPT),
        "-TitleRegex", "Sysplorer|MWORKS",
        "-ProcessRegex", "^(mworks|sysplorer)$",
        "-ProcessId", str(mworks_pid),
        "-OutDir", str(output_dir),
        "-RestoreMinimized",
        "-MinimizeAfter",
    ]
    if maximize:
        command.extend(["-Maximize", "-MaximizeWaitMs", "500"])
    return command


def capture_mworks_window(output_dir: Path, *, maximize: bool, mworks_pid: int) -> dict[str, Any]:
    command = build_capture_command(output_dir, maximize=maximize, mworks_pid=mworks_pid)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    manifest_path = output_dir / "capture_manifest.json"
    rows: list[dict[str, Any]] = []
    if manifest_path.is_file():
        try:
            parsed = json.loads(manifest_path.read_text(encoding="utf-8"))
            rows = [row for row in parsed if isinstance(row, dict)] if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            rows = []
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "manifest": project_relative(manifest_path) if manifest_path.is_file() else None,
        "captured_windows": rows,
    }


def select_result_window(capture: dict[str, Any], *, model_name: str) -> dict[str, Any]:
    """Bind result-window evidence to the runner and MWORKS process used for one case."""
    captured_windows = [
        row for row in capture.get("captured_windows", [])
        if isinstance(row, dict)
        and bool(row.get("path"))
        and not bool(row.get("helper_window"))
    ]
    matching_model = [
        row for row in captured_windows
        if model_name.casefold() in str(row.get("title") or "").casefold()
    ]
    result_candidates = [
        row for row in matching_model
        if re.search(r"plot|result|curve|chart|曲线|结果", str(row.get("title") or ""), re.IGNORECASE)
    ]
    selected = result_candidates[0] if result_candidates else (
        matching_model[0] if matching_model else None
    )
    return {
        "schema": "mosim.native_result_window_capture.v1",
        "captured_at": utc_now(),
        "capture_exit_code": capture.get("exit_code"),
        "capture_manifest": capture.get("manifest"),
        "capture_command": capture.get("command"),
        "captured_windows": captured_windows,
        "selected_result_window": selected,
        "valid_native_result_window_capture": selected is not None,
        "capture_kind": (
            "model_bound_result_window" if result_candidates else
            "model_bound_main_window_fallback" if selected else
            "missing"
        ),
        "selection_observation": (
            f"Selected a PID-bound result-window candidate for {model_name}."
            if result_candidates else
            f"Only a PID-bound model window was available for {model_name}; visual curve review remains required."
            if selected else
            f"No PID-bound window title matched {model_name}."
        ),
        "visual_curve_review_required": bool(selected and not result_candidates),
    }


def capture_result_window(case: SensitivityCase, *, mworks_pid: int) -> dict[str, Any]:
    capture = capture_mworks_window(case.output_dir / "screenshots", maximize=False, mworks_pid=mworks_pid)
    output = select_result_window(capture, model_name=case.model_name)
    write_json(case.output_dir / "logs" / "screenshot_manifest.json", output)
    return output


def capture_titles(capture: dict[str, Any]) -> list[str]:
    return [str(row.get("title") or "") for row in capture.get("captured_windows", []) if isinstance(row, dict)]


def classify_window_evidence(sentinel: dict[str, Any], capture: dict[str, Any]) -> dict[str, Any]:
    titles = capture_titles(capture)
    if capture.get("exit_code") != 0 or not isinstance(capture.get("captured_windows"), list):
        return {
            "blocked": True,
            "blocker_kind": "gui_capture_unavailable",
            "license_state": "sentinel_unavailable_blocked",
            "observation": "The background-capture tool did not produce a readable MWORKS/Sysplorer manifest.",
            "titles": titles,
        }
    if not titles:
        return {
            "blocked": True,
            "blocker_kind": "gui_or_sentinel_unavailable",
            "license_state": "unknown_blocked",
            "observation": "No MWORKS/Sysplorer main-window capture was available after the bounded session start.",
            "titles": titles,
        }
    combined = "\n".join(titles).casefold()
    marker_groups = {
        "demo": ("演示版", "demo"),
        "login_or_activation": ("登录", "登陆", "激活", "login", "activation", "软件尚未激活", "l5104-b0"),
        "authorization": ("授权不允许", "authorization failed", "变量方程数大于 300"),
        "gui_error": ("错误报告", "发送错误报告", "遇到错误，需要关闭"),
    }
    matches = {
        kind: [marker for marker in markers if marker.casefold() in combined]
        for kind, markers in marker_groups.items()
    }
    matches = {kind: found for kind, found in matches.items() if found}
    if matches:
        return {
            "blocked": True,
            "blocker_kind": "license_or_login" if set(matches).intersection({"demo", "login_or_activation", "authorization"}) else "gui_error",
            "license_state": next(iter(matches)),
            "observation": f"Captured MWORKS/Sysplorer title marker(s): {matches}.",
            "titles": titles,
            "markers": matches,
        }
    sentinel_payload = sentinel.get("payload") if isinstance(sentinel.get("payload"), dict) else {}
    sentinel_status = sentinel_payload.get("status")
    education_marker = "教育版" in combined
    return {
        "blocked": False,
        "license_state": (
            "education_edition_marker_with_current_session_health" if education_marker
            else "current_session_health_no_blocking_window_marker"
        ),
        "observation": (
            "Background capture found MWORKS/Sysplorer main window(s): " + "; ".join(titles)
            + ". No demo/login/activation/authorization/error-report marker was visible. "
            + ("[教育版] is treated as an edition marker, not a permanent-activation claim. " if education_marker else "")
            + f"Sentinel status was {sentinel_status!r}; any non-MWORKS explorer title match is not used as a GUI blocker."
        ),
        "titles": titles,
        "sentinel_status": sentinel_status,
        "education_title_is_edition_marker_only": education_marker,
    }


class SensitivityBatchSession:
    """One session for the full batch; default close leaves Sysplorer reusable."""

    def __init__(self, result_root: Path) -> None:
        self.module = load_module(MCP_RUNNER, "mosim_sensitivity_mcp_runner")
        self.result_root = result_root
        self.session_log = result_root / "batch_session_mcp.jsonl"
        wrapper = self.module.resolve_wrapper(None)
        self.client = self.module.JsonlMcpClient(self.module.wrapper_command(wrapper), self.session_log)
        self.health = self.module.initialize_mcp_client(self.client)
        startup = self.health.get("sysplorer_startup") if isinstance(self.health.get("sysplorer_startup"), dict) else {}
        port = startup.get("dedicated_sysplorer_port")
        self.dedicated_sysplorer_port = port if isinstance(port, int) and port > 0 else None
        self.mworks_pid = mworks_pid_for_port(self.dedicated_sysplorer_port)
        self.last_run: dict[str, Any] = {}
        self.closed = False

    def run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        args = self.module.parse_args(command[2:])
        args.simulate_ex_options = self.module.parse_simulate_ex_options(args.simulate_ex_options_json)
        args.metrics_context = self.module.parse_metrics_context(args.metrics_context_json)
        if args.metrics_csv is None:
            args.metrics_csv = args.metrics_json.with_suffix(".csv")
        active_log, final_log = self.module.prepare_log_output(args.log_output)
        self.client.set_log_path(active_log)
        stdout = io.StringIO()
        stderr = io.StringIO()
        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result = self.module.run_mcp_simulation(
                    args,
                    self.client,
                    active_log_output=active_log,
                    final_log_output=final_log,
                )
            self.last_run = {"ok": True, "result": result}
            return subprocess.CompletedProcess(command, 0, stdout.getvalue(), stderr.getvalue())
        except Exception as exc:
            traceback.print_exc(file=stderr)
            self.last_run = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
            return subprocess.CompletedProcess(command, 1, stdout.getvalue(), stderr.getvalue())

    def close(self, *, shutdown_session: bool) -> None:
        if self.closed:
            return
        shutdown: dict[str, Any] | str = "not_requested_session_left_reusable"
        if shutdown_session:
            try:
                self.client.set_log_path(self.session_log)
                shutdown = self.client.call_tool("session_manager", {"action": "shutdown"}, timeout_s=60)
            except Exception as exc:
                shutdown = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        write_json(self.result_root / "batch_session_close.json", {
            "schema": "mosim.sensitivity_batch_session_close.v1",
            "recorded_at": utc_now(),
            "session_manager_shutdown": shutdown,
            "health": self.health,
        })
        self.client.close()
        self.closed = True


def validate_numerical_closure(case: SensitivityCase, rows: list[dict[str, float]]) -> dict[str, Any]:
    if not rows:
        return {"passed": False, "reasons": ["raw CSV has no rows"]}
    core_columns = LEGACY.CORE_COLUMNS
    finite = all(math.isfinite(row[column]) for row in rows for column in core_columns)
    errors = [
        math.sqrt(
            (row["x"] - row["x_ref"]) ** 2
            + (row["y"] - row["y_ref"]) ** 2
            + (row["z"] - row["z_ref"]) ** 2
        )
        for row in rows
    ]
    terminal_time = rows[-1]["time"]
    terminal_error = errors[-1] if errors else float("nan")
    maximum_error = max(errors) if errors else float("nan")
    reasons: list[str] = []
    if not finite:
        reasons.append("core tracking signals contain NaN or Inf")
    if not math.isfinite(terminal_time) or terminal_time < 49.995:
        reasons.append(f"simulation ended at {terminal_time:g}s before 50s")
    if not math.isfinite(terminal_error) or terminal_error >= 5.0:
        reasons.append(f"terminal position error {terminal_error:g}m is not below 5m")
    if not math.isfinite(maximum_error) or maximum_error >= 10.0:
        reasons.append(f"maximum position error {maximum_error:g}m is not below 10m")
    return {
        "passed": not reasons,
        "row_count": len(rows),
        "terminal_time_s": terminal_time,
        "terminal_position_error_m": terminal_error,
        "maximum_position_error_m": maximum_error,
        "reasons": reasons,
        "acceptance_gate": {
            "required_stop_time_s": 50.0,
            "terminal_position_error_m_lt": 5.0,
            "maximum_position_error_m_lt": 10.0,
        },
    }


def run_case(
    case: SensitivityCase,
    *,
    profile_path: Path,
    profile_hash: str,
    contract_path: Path,
    contract_hash: str,
    session: SensitivityBatchSession | None,
    mworks_pid: int | None,
    dry_run: bool,
    overwrite: bool,
    timeout_s: float,
    license_state: str,
) -> dict[str, Any]:
    record_path = case.output_dir / "SENSITIVITY_RUN_RECORD.json"
    if record_path.is_file() and not overwrite:
        try:
            existing = json.loads(record_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {"status": "invalid_existing_record"}
        return {"skipped": True, "record": existing}
    if overwrite and case.output_dir.exists():
        shutil.rmtree(case.output_dir)
    harness = stage_harness(case)
    native_result_dir = LEGACY.next_native_result_dir(case)
    command = build_command(case, harness, native_result_dir, timeout_s)
    run_config = write_run_config(
        case,
        profile_path=profile_path,
        profile_hash=profile_hash,
        contract_path=contract_path,
        contract_hash=contract_hash,
        harness=harness,
        native_result_dir=native_result_dir,
        command=command,
    )
    if dry_run:
        return {"skipped": False, "dry_run": True, "run_config": project_relative(run_config)}

    process: subprocess.CompletedProcess[str] | None = None
    numerical: dict[str, Any] | None = None
    injection: dict[str, Any] | None = None
    screenshot: dict[str, Any] | None = None
    error: str | None = None
    check_model_status = "not_completed"
    session_result: dict[str, Any] | None = None
    try:
        if session is None:
            raise RuntimeError("Live MWORKS session is unavailable")
        if not isinstance(mworks_pid, int) or mworks_pid <= 0:
            raise RuntimeError("Live MWORKS session does not have a resolved PID-bound capture target")
        process = session.run(command)
        session_result = dict(session.last_run)
        LEGACY.save_process_output(case.output_dir, process)
        logged_check = infer_check_model_status(
            case.output_dir / "logs" / "sysplorer_mcp.jsonl",
            case.model_name,
        )
        check_model_status = (
            logged_check
            if logged_check != "not_observed"
            else ("passed" if session.last_run.get("ok") else "failed_or_not_reached")
        )
        raw = case.output_dir / "raw" / "result.csv"
        if raw.is_file():
            rows = LEGACY.read_csv_rows(raw)
            numerical = validate_numerical_closure(case, rows)
            injection = LEGACY.validate_injection(case, rows)
        python_metrics = case.output_dir / "metrics" / "metrics.python.json"
        if python_metrics.is_file():
            shutil.copyfile(python_metrics, case.output_dir / "metrics" / "METRICS.json")
        screenshot = capture_result_window(case, mworks_pid=mworks_pid)
        if process.returncode != 0:
            error = session.last_run.get("error") or "MWORKS runner returned a nonzero exit code"
        elif not raw.is_file():
            error = "MWORKS runner reported success but did not write raw CSV"
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    raw = case.output_dir / "raw" / "result.csv"
    metrics = case.output_dir / "metrics" / "METRICS.json"
    native_result = native_result_dir / case.model_name / "Result.msr"
    failure_reasons: list[str] = []
    if check_model_status != "passed":
        failure_reasons.append("CheckModel did not complete successfully before simulation")
    if process is None or process.returncode != 0:
        failure_reasons.append("MWORKS runner returned a nonzero exit code")
    if error:
        failure_reasons.append(error)
    if numerical and not numerical.get("passed"):
        failure_reasons.extend(str(reason) for reason in numerical.get("reasons", []))
    if injection and injection.get("status") != "passed":
        failure_reasons.append(f"Plant injection self-check status={injection.get('status')}")
    if not raw.is_file():
        failure_reasons.append("raw CSV is missing")
    if not metrics.is_file():
        failure_reasons.append("metrics JSON is missing")
    result_binding = describe_result_binding(
        raw=raw,
        metrics=metrics,
        native_result=native_result,
        session_result=session_result,
    )
    record = {
        "schema": "mosim.sensitivity_run_record.v1",
        "recorded_at": utc_now(),
        "status": "passed" if not failure_reasons else "failed",
        "failure_reasons": failure_reasons,
        "controller_id": case.controller_id,
        "runner_class": case.controller["runner_class"],
        "scenario_id": case.scenario_id,
        "profile_id": case.profile_id,
        "profile": case.profile,
        "source": "MWORKS_MCP",
        "evidence_level": EVIDENCE_LEVEL,
        "check_model_status": check_model_status,
        "license_state": license_state,
        "execution": {
            "solver_algorithm": "Dassl",
            "solver_tolerance": 0.0001,
            "result_interval_s": 0.01,
            "simulation_timeout_s": timeout_s,
            "runner_command_exit_code": process.returncode if process else None,
        },
        "profile_document": project_relative(profile_path),
        "profile_sha256": profile_hash,
        "injection_contract_document": project_relative(contract_path),
        "injection_contract_sha256": contract_hash,
        "hashes": {
            "harness_sha256": sha256_path(harness) if harness.is_file() else None,
            "runner_source_sha256": sha256_path(
                ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "Formal"
                / ("OfficialPidFormalRunner.mo" if case.controller_id == "official_pid" else "Px4CtrlFormalRunner.mo")
            ),
            "plant_source_sha256": sha256_path(LEGACY.PLANT_PATH),
            "raw_csv_sha256": sha256_path(raw) if raw.is_file() else None,
        },
        "numerical_closure": numerical,
        "injection_self_check": injection,
        "session_result": session_result,
        "result_binding": result_binding,
        "mworks_phase_screenshots": screenshot,
        "artifacts": {
            "run_config": project_relative(run_config),
            "harness": project_relative(harness),
            "raw_csv": project_relative(raw) if raw.is_file() else None,
            "metrics_json": project_relative(metrics) if metrics.is_file() else None,
            "native_result": project_relative(native_result) if native_result.is_file() else None,
            "mcp_log": project_relative(case.output_dir / "logs" / "sysplorer_mcp.jsonl")
            if (case.output_dir / "logs" / "sysplorer_mcp.jsonl").is_file() else None,
            "result_window_capture": screenshot.get("selected_result_window", {}).get("path")
            if isinstance(screenshot, dict) and isinstance(screenshot.get("selected_result_window"), dict) else None,
        },
        "claim_boundary": "One profile/controller MWORKS formal-run result only. It is not a controller retune, Plant-source change, PX4/Gazebo/ROS runtime result, or deployment claim.",
    }
    write_json(record_path, record)
    return {"skipped": False, "record": record}


def describe_result_binding(
    *,
    raw: Path,
    metrics: Path,
    native_result: Path,
    session_result: dict[str, Any] | None,
) -> dict[str, Any]:
    result = session_result.get("result") if isinstance(session_result, dict) else None
    result = result if isinstance(result, dict) else {}
    requested_locator = result.get("native_result")
    if native_result.is_file():
        status = "native_msr_present"
        primary_evidence = "native_msr_raw_csv_metrics"
    elif raw.is_file() and metrics.is_file():
        status = "native_msr_not_materialized_raw_result_api_exported"
        primary_evidence = "raw_csv_metrics_exported_by_mworks_result_api"
    else:
        status = "result_binding_incomplete"
        primary_evidence = "none"
    return {
        "status": status,
        "primary_result_evidence": primary_evidence,
        "requested_native_result_locator": requested_locator,
        "native_result_file": project_relative(native_result) if native_result.is_file() else None,
        "raw_csv_present": raw.is_file(),
        "metrics_json_present": metrics.is_file(),
        "claim_boundary": (
            "A missing Result.msr does not invalidate a completed MWORKS result-API CSV/metrics export. "
            "The record does not claim the requested native MSR path was materialized."
        ),
    }


def reconcile_existing_record(record_path: Path) -> dict[str, Any]:
    record = json.loads(record_path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"Record must be an object: {record_path}")
    status_before = str(record.get("status"))
    check_model_status_before = record.get("check_model_status")
    artifacts = record.get("artifacts") if isinstance(record.get("artifacts"), dict) else {}
    raw = optional_project_path(artifacts.get("raw_csv")) or (record_path.parent / "raw" / "result.csv")
    metrics = optional_project_path(artifacts.get("metrics_json")) or (record_path.parent / "metrics" / "METRICS.json")
    session_result = record.get("session_result") if isinstance(record.get("session_result"), dict) else None
    requested_locator = None
    if isinstance(session_result, dict) and isinstance(session_result.get("result"), dict):
        requested_locator = session_result["result"].get("native_result")
    native_result = optional_project_path(requested_locator)
    if native_result is None:
        native_result = record_path.parent / "native_result" / "Result.msr"
    binding = describe_result_binding(
        raw=raw,
        metrics=metrics,
        native_result=native_result,
        session_result=session_result,
    )
    reasons = [str(reason) for reason in record.get("failure_reasons", [])]
    harness = optional_project_path(artifacts.get("harness"))
    logged_check = infer_check_model_status(
        optional_project_path(artifacts.get("mcp_log")) or (record_path.parent / "logs" / "sysplorer_mcp.jsonl"),
        harness.stem if harness is not None else "",
    )
    if logged_check == "passed":
        record["check_model_status"] = "passed"
        reasons = [reason for reason in reasons if reason != "CheckModel did not complete successfully before simulation"]
    removed = False
    if binding["status"] != "result_binding_incomplete":
        original_count = len(reasons)
        reasons = [reason for reason in reasons if reason != "native Result.msr is missing"]
        removed = len(reasons) != original_count
    changed = (
        record.get("result_binding") != binding
        or record.get("failure_reasons") != reasons
        or record.get("check_model_status") != check_model_status_before
    )
    if not changed:
        return {
            "changed": False,
            "path": project_relative(record_path),
            "status_before": status_before,
            "status_after": status_before,
            "result_binding": binding["status"],
        }
    record["failure_reasons"] = reasons
    record["status"] = "passed" if not reasons else "failed"
    record["result_binding"] = binding
    artifacts["native_result"] = project_relative(native_result) if native_result.is_file() else None
    record["artifacts"] = artifacts
    record["static_reconciliation"] = {
        "reconciled_at": utc_now(),
        "removed_native_msr_only_failure": removed,
        "rule": "Raw CSV plus METRICS.json exported from MWORKS result APIs is sufficient result evidence when the requested native Result.msr was not materialized.",
        "claim_boundary": "This changes only evidence classification. It does not rerun, tune, or alter a controller, Plant, solver, or MWORKS session.",
        "check_model_log_status": logged_check,
    }
    write_json(record_path, record)
    return {
        "changed": True,
        "path": project_relative(record_path),
        "status_before": status_before,
        "status_after": record["status"],
        "removed_native_msr_only_failure": removed,
        "result_binding": binding["status"],
    }


def persisted_records(result_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(result_root.glob("*/*/SENSITIVITY_RUN_RECORD.json")):
        try:
            parsed = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            records.append(parsed)
    return records


def write_matrix(result_root: Path, *, profile_path: Path, profile_hash: str, contract_path: Path, contract_hash: str) -> Path:
    rows: list[dict[str, Any]] = []
    for record in persisted_records(result_root):
        numerical = record.get("numerical_closure") if isinstance(record.get("numerical_closure"), dict) else {}
        profile = record.get("profile") if isinstance(record.get("profile"), dict) else {}
        overrides = profile.get("runner_parameter_overrides") if isinstance(profile.get("runner_parameter_overrides"), dict) else {}
        rows.append({
            "controller_id": record.get("controller_id"),
            "scenario_id": record.get("scenario_id"),
            "profile_id": record.get("profile_id"),
            "status": record.get("status"),
            "fault_rotor_effectiveness": overrides.get("fault_rotor_effectiveness"),
            "gust_force_x_N": (overrides.get("gust_force") or [None])[0],
            "mass_scale": overrides.get("mass_scale"),
            "terminal_time_s": numerical.get("terminal_time_s"),
            "terminal_position_error_m": numerical.get("terminal_position_error_m"),
            "maximum_position_error_m": numerical.get("maximum_position_error_m"),
            "injection_status": (record.get("injection_self_check") or {}).get("status"),
        })
    payload = {
        "schema": "mosim.sensitivity_batch_matrix.v1",
        "generated_at": utc_now(),
        "profile_document": project_relative(profile_path),
        "profile_sha256": profile_hash,
        "injection_contract_document": project_relative(contract_path),
        "injection_contract_sha256": contract_hash,
        "row_count": len(rows),
        "passed_count": sum(row["status"] == "passed" for row in rows),
        "failed_count": sum(row["status"] == "failed" for row in rows),
        "rows": rows,
    }
    path = result_root / "SENSITIVITY_BATCH_MATRIX.json"
    write_json(path, payload)
    with path.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["controller_id", "scenario_id", "profile_id", "status"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_batch_status(
    result_root: Path,
    *,
    matrix_path: Path,
    reconciliation_only: bool = False,
) -> Path:
    records = persisted_records(result_root)
    payload = {
        "schema": "mosim.sensitivity_batch_status.v1",
        "recorded_at": utc_now(),
        "status": "completed_with_negative_evidence" if any(record.get("status") == "failed" for record in records) else "completed",
        "attempted_cases": len(records),
        "passed_cases": sum(record.get("status") == "passed" for record in records),
        "failed_cases": sum(record.get("status") == "failed" for record in records),
        "matrix": project_relative(matrix_path),
        "live_mworks_touched": True,
        "mworks_window_evidence_touched": True,
        "will_not_click_activation_login": True,
        "claim_boundary": "This batch is 24 planned long-duration MWORKS sensitivity cases only; no recovery-time, source-tuning, PX4/Gazebo/ROS, or deployment conclusion is made here.",
    }
    if reconciliation_only:
        payload["reconciliation_live_mworks_touched"] = False
        payload["status_rebuilt_from_existing_records"] = True
    path = result_root / "SENSITIVITY_BATCH_STATUS.json"
    write_json(path, payload)
    return path


def reconcile_existing_records(result_root: Path, cases: list[SensitivityCase]) -> Path:
    changes: list[dict[str, Any]] = []
    missing: list[str] = []
    for case in cases:
        record_path = case.output_dir / "SENSITIVITY_RUN_RECORD.json"
        if not record_path.is_file():
            missing.append(project_relative(record_path))
            continue
        changes.append(reconcile_existing_record(record_path))
    path = result_root / "SENSITIVITY_BATCH_RECONCILIATION.json"
    write_json(path, {
        "schema": "mosim.sensitivity_batch_reconciliation.v1",
        "reconciled_at": utc_now(),
        "status": "completed",
        "reconciliation_live_mworks_touched": False,
        "records_examined": len(changes),
        "records_changed": sum(bool(change.get("changed")) for change in changes),
        "missing_records": missing,
        "changes": changes,
        "claim_boundary": "This is a static evidence-contract reconciliation only. It does not rerun or modify MWORKS, Modelica source, controller gains, Plant, or solver settings.",
    })
    return path


def write_batch_plan(
    result_root: Path,
    cases: list[SensitivityCase],
    *,
    profile_path: Path,
    profile_hash: str,
    contract_path: Path,
    contract_hash: str,
    dry_run: bool,
) -> Path:
    path = result_root / "SENSITIVITY_BATCH_PLAN.json"
    write_json(path, {
        "schema": "mosim.sensitivity_batch_plan.v1",
        "generated_at": utc_now(),
        "status": "dry_run" if dry_run else "execution_started",
        "profile_document": project_relative(profile_path),
        "profile_sha256": profile_hash,
        "injection_contract_document": project_relative(contract_path),
        "injection_contract_sha256": contract_hash,
        "case_count": len(cases),
        "cases": [
            {
                "controller_id": case.controller_id,
                "scenario_id": case.scenario_id,
                "profile_id": case.profile_id,
                "model_name": case.model_name,
                "output_dir": project_relative(case.output_dir),
            }
            for case in cases
        ],
        "runner_shape": "Arbitrary number of unique profile_id entries; no len(profiles)==7 requirement.",
        "live_mworks_touched": not dry_run,
        "claim_boundary": "This plan declares only long-duration sensitivity cases. It does not authorize short-duration recovery experiments or source changes."
    })
    return path


def has_gui_blocker(capture: dict[str, Any]) -> bool:
    combined = "\n".join(capture_titles(capture)).casefold()
    return any(marker in combined for marker in (
        "演示版", "demo", "登录", "登陆", "激活", "license", "authorization failed",
        "授权不允许", "错误报告", "发送错误报告", "遇到错误，需要关闭",
    ))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True, help="Sensitivity profile JSON with any nonzero number of profiles.")
    parser.add_argument("--controllers", nargs="+", required=True, choices=sorted(LEGACY.CONTROLLERS))
    parser.add_argument("--output", type=Path, required=True, help="Result root for this one profile document.")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--dry-run", action="store_true", help="Render per-profile harness/config evidence without invoking MWORKS.")
    parser.add_argument("--overwrite", action="store_true", help="Replace only exact existing profile/controller evidence leaves.")
    parser.add_argument("--reconcile-existing", action="store_true", help="Reclassify existing raw-result records without invoking MWORKS.")
    parser.add_argument("--case-timeout-s", type=float, default=DEFAULT_TIMEOUT_S, help="MCP wait bound only; it does not modify solver settings.")
    parser.add_argument(
        "--allow-existing-mworks-pid",
        action="append",
        type=int,
        default=[],
        help="Explicitly authorize one pre-existing MWORKS PID for this batch; otherwise the MCP client must start its own session.",
    )
    parser.add_argument("--shutdown-session", action="store_true", help="Explicitly close the MWORKS session at batch end; default leaves it reusable.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.case_timeout_s <= 0:
        raise ValueError("--case-timeout-s must be positive")
    profile_path = resolve_project_path(args.profile)
    contract_path = resolve_project_path(args.contract)
    result_root = resolve_project_path(args.output)
    document, profile_hash = read_profiles(profile_path)
    _, contract_hash = LEGACY.read_contract(contract_path)
    cases = selected_cases(document, args.controllers, result_root)
    if not cases:
        raise ValueError("No sensitivity cases selected")
    if args.reconcile_existing:
        if args.dry_run or args.overwrite:
            raise ValueError("--reconcile-existing cannot be combined with --dry-run or --overwrite")
        reconciliation_path = reconcile_existing_records(result_root, cases)
        matrix_path = write_matrix(result_root, profile_path=profile_path, profile_hash=profile_hash, contract_path=contract_path, contract_hash=contract_hash)
        write_batch_status(result_root, matrix_path=matrix_path, reconciliation_only=True)
        print(project_relative(reconciliation_path))
        return 0
    write_batch_plan(
        result_root, cases,
        profile_path=profile_path,
        profile_hash=profile_hash,
        contract_path=contract_path,
        contract_hash=contract_hash,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        for case in cases:
            run_case(
                case,
                profile_path=profile_path,
                profile_hash=profile_hash,
                contract_path=contract_path,
                contract_hash=contract_hash,
                session=None,
                mworks_pid=None,
                dry_run=True,
                overwrite=args.overwrite,
                timeout_s=args.case_timeout_s,
                license_state="not_applicable_static_dry_run",
            )
        write_matrix(result_root, profile_path=profile_path, profile_hash=profile_hash, contract_path=contract_path, contract_hash=contract_hash)
        return 0

    before_start = process_snapshot()
    before_mworks_pids = mworks_process_ids(before_start)
    write_json(result_root / "process_snapshot_before_session.json", before_start)
    session: SensitivityBatchSession | None = None
    try:
        session = SensitivityBatchSession(result_root)
        after_start = process_snapshot()
        write_json(result_root / "process_snapshot_after_session_start.json", after_start)
        sentinel = run_sentinel(result_root / "preflight" / "gui_sentinel_after_start.json")
        session_binding = classify_session_binding(
            mworks_pid=session.mworks_pid,
            before_mworks_pids=before_mworks_pids,
            allowed_existing_mworks_pids=set(args.allow_existing_mworks_pid),
        )
        if session_binding["blocked"]:
            capture = {
                "command": [],
                "exit_code": 1,
                "stdout": "",
                "stderr": session_binding["observation"],
                "manifest": None,
                "captured_windows": [],
            }
            classification = {
                "blocked": True,
                "blocker_kind": session_binding["blocker_kind"],
                "license_state": "unknown_blocked",
                "observation": session_binding["observation"],
                "titles": [],
            }
        else:
            capture = capture_mworks_window(
                result_root / "preflight" / "background_capture_after_start",
                maximize=True,
                mworks_pid=session.mworks_pid,
            )
            classification = classify_window_evidence(sentinel, capture)
        preflight = {
            "schema": "mosim.sensitivity_mworks_preflight.v1",
            "recorded_at": utc_now(),
            "before_session_processes": before_start,
            "after_session_start_processes": after_start,
            "activation_sentinel_before": sentinel,
            "background_screenshot_before": capture,
            "gui_sentinel_before": sentinel.get("output"),
            "activation_state_observation": classification["observation"],
            "license_state": classification["license_state"],
            "will_not_click_activation_login": True,
            "live_mworks_touched": True,
            "mworks_window_evidence_touched": True,
            "mworks_window_policy": "one_user_authorized_new_session_then_reuse_for_serial_sensitivity_batch",
            "session_health": session.health,
            "session_binding": {
                **session_binding,
                "dedicated_sysplorer_port": session.dedicated_sysplorer_port,
            },
            "classification": classification,
        }
        write_json(result_root / "MWORKS_PREFLIGHT.json", preflight)
        if classification["blocked"]:
            write_json(result_root / "LIVE_PREFLIGHT_BLOCKER.json", {
                **preflight,
                "status": "blocked",
                "blocker_kind": classification["blocker_kind"],
                "minimal_user_action": "Restore a clean reusable MWORKS/Sysplorer window without demo/login/license/error UI, then rerun this batch without source changes.",
            })
            return 2

        for index, case in enumerate(cases, start=1):
            print(f"[{index}/{len(cases)}] {case.controller_id}/{case.profile_id}", flush=True)
            run_case(
                case,
                profile_path=profile_path,
                profile_hash=profile_hash,
                contract_path=contract_path,
                contract_hash=contract_hash,
                session=session,
                mworks_pid=session.mworks_pid,
                dry_run=False,
                overwrite=args.overwrite,
                timeout_s=args.case_timeout_s,
                license_state=classification["license_state"],
            )
            post_case_capture = capture_mworks_window(
                case.output_dir / "screenshots" / "post_case",
                maximize=False,
                mworks_pid=session.mworks_pid,
            )
            write_json(case.output_dir / "logs" / "post_case_window_capture.json", post_case_capture)
            if has_gui_blocker(post_case_capture):
                write_json(result_root / "BATCH_STOPPED_GUI_BLOCKER.json", {
                    "status": "blocked",
                    "recorded_at": utc_now(),
                    "case": {"controller_id": case.controller_id, "profile_id": case.profile_id},
                    "blocker_kind": "license_or_login_or_gui_error",
                    "capture": post_case_capture,
                    "will_not_click_activation_login": True,
                    "live_mworks_touched": True,
                })
                return 2
    finally:
        if session is not None:
            session.close(shutdown_session=args.shutdown_session)
        after_finish = process_snapshot()
        write_json(result_root / "process_snapshot_after_batch.json", after_finish)
    matrix_path = write_matrix(result_root, profile_path=profile_path, profile_hash=profile_hash, contract_path=contract_path, contract_hash=contract_hash)
    write_batch_status(result_root, matrix_path=matrix_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
