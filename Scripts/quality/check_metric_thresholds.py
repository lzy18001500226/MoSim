"""Evaluate MoSim metrics.json against the threshold profile in metrics_schema.

This checker is offline. It validates measured metric values after
compute_tracking_metrics.py or a localization metric generator has produced a
metrics.json packet. It does not start ROS, Gazebo, PX4, MAVROS, RViz, UE, or
MWORKS.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METRICS_SCHEMA = ROOT / "Config" / "profiles" / "metrics_schema.json"


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def metric_value(metric_body: Any, metric_name: str) -> tuple[float | None, str]:
    if not isinstance(metric_body, dict):
        raise ValueError(f"metric {metric_name} must be an object")
    if "value" not in metric_body or "unit" not in metric_body:
        raise ValueError(f"metric {metric_name} must contain value and unit")
    value = metric_body["value"]
    if value is None:
        return None, str(metric_body["unit"])
    try:
        return float(value), str(metric_body["unit"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"metric {metric_name} value is not numeric: {value!r}") from exc


def evaluate_thresholds(metrics_packet: dict[str, Any], manifest_packet: dict[str, Any], metrics_schema: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    manifest = manifest_packet.get("run_manifest", {})
    evaluation_profile = manifest.get("evaluation", {}).get("evaluation_profile")
    required_metrics = manifest.get("evaluation", {}).get("required_metrics", [])
    run_id = manifest.get("run_id")

    if metrics_packet.get("run_id") != run_id:
        add_error(errors, "T-RUNID-01", "metrics.json run_id does not match RUN_MANIFEST.json")

    threshold_profile = metrics_schema.get("threshold_profiles", {}).get(evaluation_profile)
    if not isinstance(threshold_profile, dict):
        add_error(errors, "T-PROFILE-01", f"no threshold profile defined for evaluation_profile={evaluation_profile}")
        return {
            "ok": False,
            "accepted": False,
            "run_id": run_id,
            "evaluation_profile": evaluation_profile,
            "results": [],
            "errors": errors,
            "warnings": warnings,
        }

    thresholds = threshold_profile.get("thresholds", {})
    metric_values = metrics_packet.get("metrics", {})
    results: list[dict[str, Any]] = []
    for metric_name in required_metrics:
        threshold = thresholds.get(metric_name)
        if threshold is None:
            add_error(errors, "T-THRESHOLD-01", f"required metric has no threshold: {metric_name}")
            continue
        metric_body = metric_values.get(metric_name)
        if metric_body is None:
            add_error(errors, "T-METRIC-01", f"required metric missing from metrics.json: {metric_name}")
            continue
        try:
            value, unit = metric_value(metric_body, metric_name)
        except ValueError as exc:
            add_error(errors, "T-METRIC-02", str(exc))
            continue
        expected_unit = str(threshold.get("unit", ""))
        if unit != expected_unit:
            add_error(errors, "T-UNIT-01", f"metric {metric_name} unit {unit} does not match threshold unit {expected_unit}")
            continue
        if value is None:
            add_error(errors, "T-METRIC-03", f"metric {metric_name} has null value and cannot be thresholded")
            continue

        passed = True
        reason = "within_threshold"
        if "max" in threshold and value > float(threshold["max"]):
            passed = False
            reason = f"value {value} exceeds max {threshold['max']}"
        if "min" in threshold and value < float(threshold["min"]):
            passed = False
            reason = f"value {value} below min {threshold['min']}"
        if not passed:
            add_error(errors, "T-FAIL-01", f"{metric_name}: {reason}")
        results.append(
            {
                "metric": metric_name,
                "value": value,
                "unit": unit,
                "threshold": threshold,
                "passed": passed,
                "reason": reason,
            }
        )

    for metric_name in metric_values:
        if metric_name not in thresholds:
            warnings.append({"code": "T-EXTRA-01", "message": f"metric has no threshold and was ignored: {metric_name}"})

    return {
        "ok": not errors,
        "accepted": not errors,
        "run_id": run_id,
        "experiment_profile_id": manifest.get("experiment_profile_id"),
        "evaluation_profile": evaluation_profile,
        "threshold_profile": evaluation_profile,
        "results": results,
        "errors": errors,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metrics_json", help="metrics.json path")
    parser.add_argument("--manifest", required=True, help="RUN_MANIFEST.json path")
    parser.add_argument("--metrics-schema", default=str(DEFAULT_METRICS_SCHEMA), help="Metrics schema JSON path")
    parser.add_argument("--report", help="Optional JSON threshold report output path")
    args = parser.parse_args(argv)

    try:
        metrics_packet = load_json(Path(args.metrics_json))
        manifest_packet = load_json(Path(args.manifest))
        metrics_schema = load_json(Path(args.metrics_schema))
        report = evaluate_thresholds(metrics_packet, manifest_packet, metrics_schema)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
