#!/usr/bin/env python3
"""
Basic project QA check for the A8 quadrotor control project.

Usage:
    python scripts/qa_check.py

This script checks the project entry points, key documents, converted MWORKS
knowledge base, official quadrotor case, and MCP wrapper scripts. It does not
validate MWORKS models.
"""

from __future__ import annotations

from pathlib import Path
import csv
import os
import subprocess
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - checked at runtime for local setup
    yaml = None


REQUIRED_DIRS = [
    "scripts",
    "docs",
    "docs/index",
    "docs/mworks/converted",
    "QuadrotorModel",
    "workflows",
]

RECOMMENDED_DIRS = [
    "controllers",
    "planners",
    "scenarios",
    "tests",
    "results",
]

OPTIONAL_NONEMPTY_DIRS = [
    "controllers",
    "planners",
    "scenarios",
    "tests",
    "results",
]

REQUIRED_DOCS = [
    "README.md",
    "AGENTS.md",
]

RECOMMENDED_DOCS = [
    "docs/user_manual.md",
    "docs/simulation_report.md",
    "docs/index/doc_index.md",
    "docs/index/api_index.md",
    "docs/index/variable_mapping.md",
    "docs/index/workflow_index.md",
    "workflows/run_simulation.md",
    "workflows/read_results.md",
    "workflows/calc_metrics.md",
    "workflows/pre_submit_check.md",
]

RECOMMENDED_SCRIPTS = [
    "scripts/generate_reference.py",
    "scripts/check_reference_outputs.py",
    "scripts/extract_mcp_timeseries.py",
    "scripts/calc_metrics.py",
    "scripts/plot_results.py",
    "scripts/generate_replay_html.py",
    "scripts/summarize_experiments.py",
    "scripts/generate_planning_reference.py",
    "scripts/generate_obstacle_planning_reference.py",
    "scripts/generate_formation_reference.py",
    "scripts/generate_fault_scenario.py",
    "scripts/generate_disturbance_mode_demo.py",
    "scripts/generate_mass_adaptation_demo.py",
    "scripts/generate_safety_filter_demo.py",
    "scripts/generate_fault_reallocation_demo.py",
]

RECOMMENDED_TESTS = [
    "tests/test_metrics.py",
    "tests/test_summary.py",
    "tests/test_planning_reference.py",
    "tests/test_obstacle_planning.py",
    "tests/test_formation_reference.py",
    "tests/test_fault_scenario.py",
    "tests/test_disturbance_mode_demo.py",
    "tests/test_mass_adaptation_demo.py",
    "tests/test_safety_filter_demo.py",
    "tests/test_fault_reallocation_demo.py",
]

OFFICIAL_MODELS = [
    "QuadrotorModel.Examples.Example1",
    "QuadrotorModel.Examples.Example2",
    "QuadrotorModel.Examples.Example3",
]

OFFICIAL_SCENARIOS = [
    "scenarios/official/example1_pid_baseline.yaml",
    "scenarios/official/example2_pid_baseline.yaml",
    "scenarios/official/example3_pid_baseline.yaml",
]

CONTROLLER_CONFIGS = {
    "pid_baseline": "controllers/pid/baseline.yaml",
    "improved_pid": "controllers/improved_pid/default.yaml",
    "nmpc_indi_l1": "controllers/nmpc_indi_l1/default.yaml",
}

PLANNER_CONFIGS = [
    "planners/waypoint/default.yaml",
]

REQUIRED_SCENARIO_KEYS = [
    "experiment_id",
    "scene_id",
    "controller_id",
    "model",
    "simulation",
    "reference",
    "result",
]

REQUIRED_SIMULATION_KEYS = [
    "start_time_s",
    "stop_time_s",
    "step_size_s",
]

REQUIRED_RESULT_KEYS = [
    "raw_file",
    "metrics_file",
]

REQUIRED_CONTROLLER_INTERFACE_KEYS = [
    "replacement_component",
    "inputs",
    "outputs",
    "required_result_variables",
]

OFFICIAL_REPLACEMENT_COMPONENT = "controller3_2"

OFFICIAL_FULL_RESULT_EXPECTATIONS = {
    "results/raw/official_example1_pid_baseline.csv": 50.0,
    "results/raw/official_example2_pid_baseline.csv": 50.0,
    "results/raw/official_example3_pid_baseline.csv": 120.0,
}

OFFICIAL_REFERENCE_OUTPUTS = [
    "results/raw/reference_official_example1.csv",
    "results/raw/reference_official_example2.csv",
    "results/raw/reference_official_example3.csv",
    "results/replay/reference_official_example1.json",
    "results/replay/reference_official_example2.json",
    "results/replay/reference_official_example3.json",
    "results/replay_html/reference_official_example1.html",
    "results/replay_html/reference_official_example2.html",
    "results/replay_html/reference_official_example3.html",
]

SMOKE_RESULT_OUTPUTS = [
    "results/raw/smoke_official_example1_pid_baseline.csv",
    "results/metrics/smoke_official_example1_pid_baseline.json",
    "results/metrics/smoke_official_example1_pid_baseline.csv",
]

DISTURBANCE_OUTPUTS = [
    "results/raw/wind_nmpc_indi_l1.csv",
    "results/metrics/wind_nmpc_indi_l1.json",
    "results/logs/wind_nmpc_indi_l1_events.jsonl",
    "results/replay/wind_nmpc_indi_l1.json",
    "results/replay_html/wind_nmpc_indi_l1.html",
    "results/raw/reference_delivery_mass_change.csv",
    "results/raw/delivery_mass_change.csv",
    "results/metrics/delivery_mass_change.json",
    "results/logs/delivery_mass_change_events.jsonl",
    "results/replay/delivery_mass_change.json",
    "results/replay_html/delivery_mass_change.html",
]

PLANNING_OUTPUTS = [
    "results/raw/reference_planning_trackable_waypoint.csv",
    "results/metrics/trackability_planning_trackable_waypoint.json",
    "results/replay/planning_trackable_waypoint.json",
    "results/replay_html/planning_trackable_waypoint.html",
    "results/raw/path_planning_obstacle_corridor.csv",
    "results/raw/reference_planning_obstacle_corridor.csv",
    "results/metrics/planning_obstacle_corridor.json",
    "results/replay/planning_obstacle_corridor.json",
    "results/replay_html/planning_obstacle_corridor.html",
]

FORMATION_OUTPUTS = [
    "results/raw/reference_formation_triangle_switch.csv",
    "results/metrics/formation_triangle_switch.json",
    "results/replay/formation_triangle_switch.json",
    "results/replay_html/formation_triangle_switch.html",
]

FAULT_OUTPUTS = [
    "results/raw/fault_motor_return_reference.csv",
    "results/metrics/fault_motor_return.json",
    "results/logs/fault_motor_return_events.jsonl",
    "results/replay/fault_motor_return.json",
    "results/replay_html/fault_motor_return.html",
    "results/raw/reference_fault_reallocation_compare.csv",
    "results/raw/fault_reallocation_compare.csv",
    "results/metrics/fault_reallocation_compare.json",
    "results/logs/fault_reallocation_compare_events.jsonl",
    "results/replay/fault_reallocation_compare.json",
    "results/replay_html/fault_reallocation_compare.html",
]

SAFETY_OUTPUTS = [
    "results/raw/reference_safety_filter_guard.csv",
    "results/raw/safety_filter_guard.csv",
    "results/metrics/safety_filter_guard.json",
    "results/logs/safety_filter_guard_events.jsonl",
    "results/replay/safety_filter_guard.json",
    "results/replay_html/safety_filter_guard.html",
]

OFFICIAL_RESULT_VARIABLE_CANDIDATES = [
    "sensors1_1.PosMea",
    "sensors1_1.AngleMea",
    "climbePath.position_command",
    "controller3_2.y",
    "controller3_2.y1",
    "controller3_2.y2",
    "controller3_2.y3",
    "speedSensor[4]",
]

WRAPPER_SCRIPTS = {
    "syslab_mcp.sh": [
        "~/mcp-wrappers/syslab_mcp.sh",
        "/home/linux/mcp-wrappers/syslab_mcp.sh",
    ],
    "sysplorer_mcp.sh": [
        "~/mcp-wrappers/sysplorer_mcp.sh",
        "/home/linux/mcp-wrappers/sysplorer_mcp.sh",
    ],
    "filesystem_mcp.sh": [
        "~/mcp-wrappers/filesystem_mcp.sh",
        "/home/linux/mcp-wrappers/filesystem_mcp.sh",
    ],
}


def check_path(path: Path, required: bool = True) -> bool:
    if path.exists():
        print(f"[OK] {path}")
        return True

    label = "FAIL" if required else "WARN"
    print(f"[{label}] Missing: {path}")
    return not required


def has_real_content(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    for item in path.rglob("*"):
        if item.is_file() and item.name != ".gitkeep":
            return True
    return False


def is_windows() -> bool:
    return os.name == "nt"


def check_wsl_file(path: str) -> tuple[bool, bool]:
    """Return (exists, executable) for a WSL path when running from Windows."""
    if not is_windows() or not path.startswith("/"):
        return False, False

    try:
        exists = subprocess.run(
            ["wsl.exe", "test", "-f", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode == 0
        executable = subprocess.run(
            ["wsl.exe", "test", "-x", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode == 0
    except FileNotFoundError:
        return False, False

    return exists, executable


def check_dirs(root: Path) -> bool:
    print("\n== Required directories ==")
    ok = True
    for item in REQUIRED_DIRS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Recommended directories ==")
    for item in RECOMMENDED_DIRS:
        ok = check_path(root / item, required=False) and ok

    print("\n== Optional implementation directories ==")
    for item in OPTIONAL_NONEMPTY_DIRS:
        path = root / item
        if not path.exists():
            print(f"[OK] Optional absent until used: {path}")
        elif has_real_content(path):
            print(f"[OK] Has content: {path}")
        else:
            print(f"[WARN] Empty placeholder directory: {path}")

    return ok


def check_docs(root: Path) -> bool:
    print("\n== Required documents ==")
    ok = True
    for item in REQUIRED_DOCS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Recommended documents ==")
    for item in RECOMMENDED_DOCS:
        ok = check_path(root / item, required=False) and ok

    return ok


def check_scripts(root: Path) -> bool:
    print("\n== Recommended scripts ==")
    ok = True
    for item in RECOMMENDED_SCRIPTS:
        ok = check_path(root / item, required=False) and ok
    return ok


def check_tests(root: Path) -> bool:
    print("\n== Recommended tests ==")
    ok = True
    for item in RECOMMENDED_TESTS:
        ok = check_path(root / item, required=False) and ok
    return ok


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        return read_simple_yaml(path)
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    return data


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return {}
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
        return [parse_scalar(item) for item in items]
    try:
        if any(token in value for token in [".", "e", "E"]):
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"').strip("'")


def read_simple_yaml(path: Path) -> dict[str, Any]:
    """Read the simple project YAML subset without external dependencies."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.rstrip()
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if line.lstrip().startswith("- "):
                continue
            if ":" not in line:
                continue

            indent = len(line) - len(line.lstrip(" "))
            key, value = line.strip().split(":", 1)
            while stack and indent <= stack[-1][0]:
                stack.pop()
            parent = stack[-1][1]
            parsed = parse_scalar(value)
            parent[key] = parsed
            if isinstance(parsed, dict):
                stack.append((indent, parsed))

    if not root:
        raise ValueError("YAML root must be a mapping")
    return root


def check_config_files(root: Path) -> bool:
    print("\n== Controller, planner, and scenario configs ==")
    ok = True

    if yaml is None:
        print("[WARN] PyYAML not installed; using built-in simple YAML parser")

    controller_ids: set[str] = set()
    for controller_id, rel_path in CONTROLLER_CONFIGS.items():
        path = root / rel_path
        if not check_path(path, required=True):
            ok = False
            continue
        try:
            config = read_yaml(path)
        except Exception as exc:
            print(f"[FAIL] Cannot parse controller config {path}: {exc}")
            ok = False
            continue

        actual_id = config.get("controller_id")
        if actual_id != controller_id:
            print(f"[FAIL] Controller id mismatch in {path}: expected {controller_id}, got {actual_id}")
            ok = False
        else:
            print(f"[OK] Controller id: {controller_id}")
            controller_ids.add(controller_id)

        interface = config.get("model_interface")
        if not isinstance(interface, dict):
            print(f"[FAIL] Missing model_interface in {path}")
            ok = False
            continue

        for key in REQUIRED_CONTROLLER_INTERFACE_KEYS:
            if key in interface:
                print(f"[OK] {controller_id} model_interface.{key}")
            else:
                print(f"[FAIL] Missing {controller_id} model_interface.{key}")
                ok = False

        replacement = interface.get("replacement_component")
        if replacement != OFFICIAL_REPLACEMENT_COMPONENT and controller_id != "pid_baseline":
            print(f"[FAIL] {controller_id} replacement_component should be {OFFICIAL_REPLACEMENT_COMPONENT}, got {replacement}")
            ok = False

    for rel_path in PLANNER_CONFIGS:
        path = root / rel_path
        if not check_path(path, required=True):
            ok = False
            continue
        try:
            config = read_yaml(path)
        except Exception as exc:
            print(f"[FAIL] Cannot parse planner config {path}: {exc}")
            ok = False
            continue
        if config.get("planner_id"):
            print(f"[OK] Planner id: {config['planner_id']}")
        else:
            print(f"[FAIL] Missing planner_id in {path}")
            ok = False

    scenario_paths = sorted((root / "scenarios").glob("**/*.yaml"))
    if not scenario_paths:
        print("[FAIL] No scenario YAML files found")
        return False

    experiment_ids: set[str] = set()
    for path in scenario_paths:
        try:
            config = read_yaml(path)
        except Exception as exc:
            print(f"[FAIL] Cannot parse scenario config {path}: {exc}")
            ok = False
            continue

        rel_path = path.relative_to(root)
        missing = [key for key in REQUIRED_SCENARIO_KEYS if key not in config]
        if missing:
            print(f"[FAIL] Missing scenario keys in {rel_path}: {', '.join(missing)}")
            ok = False
            continue

        experiment_id = str(config["experiment_id"])
        if experiment_id in experiment_ids:
            print(f"[FAIL] Duplicate experiment_id: {experiment_id}")
            ok = False
        else:
            experiment_ids.add(experiment_id)

        controller_id = str(config["controller_id"])
        if controller_id in controller_ids:
            print(f"[OK] Scenario {rel_path} uses controller {controller_id}")
        else:
            print(f"[FAIL] Scenario {rel_path} references unknown controller {controller_id}")
            ok = False

        simulation = config.get("simulation", {})
        if not isinstance(simulation, dict):
            print(f"[FAIL] Scenario {rel_path} simulation must be a mapping")
            ok = False
        else:
            missing_sim = [key for key in REQUIRED_SIMULATION_KEYS if key not in simulation]
            if missing_sim:
                print(f"[FAIL] Missing simulation keys in {rel_path}: {', '.join(missing_sim)}")
                ok = False
            elif float(simulation["stop_time_s"]) <= float(simulation["start_time_s"]):
                print(f"[FAIL] Invalid simulation time range in {rel_path}")
                ok = False

        result = config.get("result", {})
        if not isinstance(result, dict):
            print(f"[FAIL] Scenario {rel_path} result must be a mapping")
            ok = False
        else:
            missing_result = [key for key in REQUIRED_RESULT_KEYS if key not in result]
            if missing_result:
                print(f"[FAIL] Missing result keys in {rel_path}: {', '.join(missing_result)}")
                ok = False

    return ok


def check_wrappers() -> bool:
    print("\n== MCP wrapper scripts ==")
    ok = True
    for name, candidates in WRAPPER_SCRIPTS.items():
        found = False
        for item in candidates:
            exists_wsl, executable_wsl = check_wsl_file(item)
            if exists_wsl:
                found = True
                if executable_wsl:
                    print(f"[OK] {name}: WSL:{item}")
                else:
                    print(f"[WARN] {name} found but not executable: WSL:{item}")
                    ok = False
                break

            path = Path(item).expanduser()
            if not path.exists() or not path.is_file():
                continue
            found = True
            if not path.stat().st_mode & 0o111:
                print(f"[WARN] {name} found but not executable: {path}")
                ok = False
            else:
                print(f"[OK] {name}: {path}")
            break

        if not found:
            print(f"[WARN] Missing wrapper: {name}")
            for item in candidates:
                print(f"       checked: {Path(item).expanduser()}")
            ok = False
    return ok


def check_official_case(root: Path) -> bool:
    print("\n== Official quadrotor case ==")
    ok = True
    package_path = root / "QuadrotorModel" / "package.mo"
    if not package_path.exists():
        print(f"[FAIL] Missing official package: {package_path}")
        return False

    package_text = package_path.read_text(encoding="utf-8-sig", errors="replace")
    for model_name in OFFICIAL_MODELS:
        short_name = model_name.rsplit(".", 1)[-1]
        if f"model {short_name} " in package_text:
            print(f"[OK] Official model present: {model_name}")
        else:
            print(f"[FAIL] Official model missing: {model_name}")
            ok = False

    for item in OFFICIAL_SCENARIOS:
        ok = check_path(root / item, required=True) and ok

    for item in OFFICIAL_REFERENCE_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Smoke result evidence ==")
    for item in SMOKE_RESULT_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Disturbance mode-switch evidence ==")
    for item in DISTURBANCE_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Planning reference evidence ==")
    for item in PLANNING_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Formation reference evidence ==")
    for item in FORMATION_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Fault tolerance evidence ==")
    for item in FAULT_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Safety filter evidence ==")
    for item in SAFETY_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Full baseline result guard ==")
    for item, min_duration_s in OFFICIAL_FULL_RESULT_EXPECTATIONS.items():
        path = root / item
        if not path.exists():
            print(f"[OK] Full baseline not present yet: {path}")
            continue
        try:
            duration_s = read_csv_duration(path)
        except Exception as exc:
            print(f"[FAIL] Cannot read duration from {path}: {exc}")
            ok = False
            continue
        if duration_s + 1e-9 >= min_duration_s:
            print(f"[OK] Full baseline duration {duration_s:.3f}s: {path}")
        else:
            print(f"[FAIL] {path} duration {duration_s:.3f}s is shorter than expected {min_duration_s:.3f}s")
            ok = False

    mapping_path = root / "docs" / "index" / "variable_mapping.md"
    if mapping_path.exists():
        mapping_text = mapping_path.read_text(encoding="utf-8", errors="replace")
        for item in OFFICIAL_RESULT_VARIABLE_CANDIDATES:
            if item in mapping_text:
                print(f"[OK] Result mapping candidate documented: {item}")
            else:
                print(f"[FAIL] Result mapping candidate missing from docs: {item}")
                ok = False

    return ok


def read_csv_duration(path: Path) -> float:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "time" not in reader.fieldnames:
            raise ValueError("missing time column")
        first_time = None
        last_time = None
        for row in reader:
            value = row.get("time", "")
            if value == "":
                continue
            current = float(value)
            if first_time is None:
                first_time = current
            last_time = current
        if first_time is None or last_time is None:
            raise ValueError("no time samples")
        return last_time - first_time


def main() -> int:
    root = Path.cwd()
    print(f"Project root: {root}")

    ok = True
    ok = check_dirs(root) and ok
    ok = check_docs(root) and ok
    ok = check_scripts(root) and ok
    ok = check_tests(root) and ok
    ok = check_config_files(root) and ok
    ok = check_official_case(root) and ok
    wrappers_ok = check_wrappers()

    print("\n== Summary ==")
    if ok:
        print("[OK] Required project structure passed.")
    else:
        print("[FAIL] Required project structure has missing items.")

    if wrappers_ok:
        print("[OK] MCP wrapper scripts found.")
    else:
        print("[WARN] MCP wrapper scripts need attention.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
