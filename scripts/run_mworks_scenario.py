#!/usr/bin/env python3
"""Run a scenario YAML through the project Sysplorer MCP evidence pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_FILE_WIN = r"C:\Users\HP\Desktop\Quadrotor\QuadrotorModel\package.mo"
DEFAULT_EXTRA_MODEL_WIN = r"C:\Users\HP\Desktop\Quadrotor\models\QuadrotorExperiments\package.mo"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return {}
    if value in {"true", "false"}:
        return value == "true"
    try:
        if any(token in value for token in [".", "e", "E"]):
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"').strip("'")


def read_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
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
    return root


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        return read_simple_yaml(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Scenario YAML root must be a mapping: {path}")
    return data


def require_mapping(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"Scenario field `{key}` must be a mapping")
    return value


def windows_path(repo_path: str, *, default: str | None = None) -> str:
    if not repo_path:
        if default is None:
            raise ValueError("Missing required path")
        return default
    if ":" in repo_path[:4]:
        return repo_path
    return "C:\\Users\\HP\\Desktop\\Quadrotor\\" + repo_path.replace("/", "\\")


def default_result_base(config: dict[str, Any], experiment_id: str) -> Path:
    scene_id = str(config.get("scene_id", "") or "")
    controller_id = str(config.get("controller_id", "") or "")
    evidence_level = str(config.get("evidence_level", "") or "")

    if "smoke" in experiment_id or "smoke" in scene_id or "smoke" in evidence_level:
        suffix = f"{controller_id}_smoke" if controller_id else experiment_id
        if scene_id.startswith("official_example1") or experiment_id.startswith("official_example1"):
            scene_group = "example1_step"
        elif scene_id.startswith("official_example2") or experiment_id.startswith("official_example2"):
            scene_group = "example2_helix"
        elif scene_id.startswith("official_example3") or experiment_id.startswith("official_example3"):
            scene_group = "example3_figure8"
        elif "robust" in scene_id or "robust" in experiment_id:
            scene_group = "robustness"
            if "mass20" in scene_id or "mass20" in experiment_id:
                suffix = f"mass20_example1_{suffix}"
            elif "rotor1_loss15" in scene_id or "rotor1_loss15" in experiment_id:
                suffix = f"rotor1_loss15_example1_{suffix}"
            elif "wind_gust" in scene_id or "wind_gust" in experiment_id:
                suffix = f"wind_gust_example1_{suffix}"
        else:
            scene_group = scene_id or "misc"
        return Path("results/smoke") / scene_group / suffix

    if scene_id.startswith("official_example1") or experiment_id.startswith("official_example1"):
        return Path("results/official/example1_step")
    if scene_id.startswith("official_example2") or experiment_id.startswith("official_example2"):
        return Path("results/official/example2_helix")
    if scene_id.startswith("official_example3") or experiment_id.startswith("official_example3"):
        return Path("results/official/example3_figure8")
    if "mass20" in scene_id or "mass20" in experiment_id:
        return Path("results/robustness/mass20_example1")
    if "rotor1_loss15" in scene_id or "rotor1_loss15" in experiment_id:
        return Path("results/robustness/rotor1_loss15_example1")
    if "wind_gust" in scene_id or "wind_gust" in experiment_id:
        return Path("results/robustness/wind_gust_example1")
    return Path("results") / "uncategorized" / experiment_id


def scenario_command(args: argparse.Namespace, config: dict[str, Any]) -> list[str]:
    experiment_id = str(config.get("experiment_id", args.scenario.stem))
    model = require_mapping(config, "model")
    controller = require_mapping(config, "controller")
    simulation = require_mapping(config, "simulation")
    result = require_mapping(config, "result")

    model_name = str(model.get("model_name", ""))
    if not model_name:
        raise ValueError(f"Scenario missing model.model_name: {args.scenario}")

    result_base = default_result_base(config, experiment_id)
    raw_file = Path(str(result.get("raw_file", result_base / "raw" / f"{experiment_id}.csv")))
    metrics_json = Path(str(result.get("metrics_file", result_base / "metrics" / f"{experiment_id}.json")))
    metrics_csv = metrics_json.with_suffix(".csv")
    log_file = Path(str(result.get("mcp_log", result_base / "logs" / f"sysplorer_{experiment_id}_mcp.jsonl")))
    stop_time = float(args.stop_time if args.stop_time is not None else simulation.get("stop_time_s", 1.0))
    start_time = float(simulation.get("start_time_s", 0.0))
    target_time = f"{start_time:g},{stop_time:g}"

    model_file = windows_path(str(model.get("base_model_path_hint") or model.get("model_path_hint", "")), default=DEFAULT_MODEL_FILE_WIN)
    extra_model_files: list[str] = []
    sysblock_controller_file = str(controller.get("sysblock_controller_file", ""))
    if sysblock_controller_file:
        extra_model_files.append(windows_path(sysblock_controller_file))
    if str(model.get("source_package", "")) != "QuadrotorModel":
        extra_model_files.append(windows_path(str(model.get("model_path_hint", "")), default=DEFAULT_EXTRA_MODEL_WIN))

    default_evidence_level = (
        str(config.get("evidence_level", ""))
        or (
            "real_sysplorer_mcp_full_improved_pid"
            if str(config.get("controller_id", "")) == "improved_pid"
            else "real_sysplorer_mcp_full_baseline"
        )
    )

    command = [
        sys.executable,
        "scripts/run_sysplorer_mcp_smoke.py",
        "--model-file",
        model_file,
        "--model-name",
        model_name,
        "--target-time",
        target_time,
        "--raw-output",
        str(raw_file),
        "--metrics-json",
        str(metrics_json),
        "--metrics-csv",
        str(metrics_csv),
        "--log-output",
        str(log_file),
        "--scene-id",
        str(config.get("scene_id", experiment_id)),
        "--controller-id",
        str(config.get("controller_id", "")),
        "--evidence-level",
        args.evidence_level or default_evidence_level,
    ]
    for extra_model_file in extra_model_files:
        command.extend(["--extra-model-file", extra_model_file])
    if args.shutdown_session:
        command.append("--shutdown-session")
    return command


def run_postprocess(config: dict[str, Any]) -> None:
    experiment_id = str(config.get("experiment_id", ""))
    model = require_mapping(config, "model")
    result = require_mapping(config, "result")
    raw_file = Path(str(result.get("raw_file", "")))
    metrics_file = Path(str(result.get("metrics_file", "")))
    result_base = default_result_base(config, experiment_id)
    figure_dir = Path(str(result.get("figure_dir", result_base / "figures" / experiment_id)))
    replay_file = Path(str(result.get("replay_file", result_base / "replay" / f"{experiment_id}.json")))

    subprocess.run(
        [
            sys.executable,
            "scripts/plot_results.py",
            str(raw_file),
            str(figure_dir),
            "--metrics",
            str(metrics_file),
            "--title-prefix",
            experiment_id,
        ],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "scripts/generate_replay_from_raw.py",
            str(raw_file),
            str(replay_file),
            "--scene-id",
            str(config.get("scene_id", experiment_id)),
            "--model-name",
            str(model.get("model_name", "")),
            "--description",
            str(model.get("official_description", experiment_id)),
        ],
        cwd=ROOT,
        check=True,
    )
    if config.get("generate_replay_html", False):
        replay_html = Path(str(result.get("replay_html", result_base / "replay_html" / f"{experiment_id}.html")))
        subprocess.run(
            [sys.executable, "scripts/generate_replay_html.py", str(replay_file), str(replay_html)],
            cwd=ROOT,
            check=True,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, help="Scenario YAML path")
    parser.add_argument("--stop-time", type=float, default=None, help="Override scenario stop_time_s")
    parser.add_argument("--evidence-level", default=None, help="Override metrics evidence_level")
    parser.add_argument("--no-postprocess", action="store_true", help="Skip figure and replay generation")
    parser.add_argument("--shutdown-session", action="store_true", help="Request Sysplorer session shutdown after the run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.scenario)
    command = scenario_command(args, config)
    print("Running:", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)
    if not args.no_postprocess:
        run_postprocess(config)
    print(f"Scenario evidence complete: {args.scenario}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
