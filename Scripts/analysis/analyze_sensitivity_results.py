#!/usr/bin/env python3
"""Summarize long-duration MWORKS sensitivity batch records without retuning."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_TITLES = {
    "motor_efficiency_fault": "10.1 单电机效率持续下降",
    "wind_disturbance": "10.2 持续风扰",
    "parameter_mismatch": "10.3 持续参数失配",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def project_relative(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def record_value(record: dict[str, Any]) -> tuple[float, str, str]:
    profile = record.get("profile") if isinstance(record.get("profile"), dict) else {}
    overrides = profile.get("runner_parameter_overrides") if isinstance(profile.get("runner_parameter_overrides"), dict) else {}
    scenario = str(record.get("scenario_id") or "")
    if scenario == "motor_efficiency_fault":
        efficiency = float(overrides["fault_rotor_effectiveness"])
        loss_percent = (1.0 - efficiency) * 100.0
        return loss_percent, f"eta={efficiency:.2f}", f"{loss_percent:.0f}% loss"
    if scenario == "wind_disturbance":
        force = float(overrides["gust_force"][0])
        return force, f"{force:.1f} N", f"{force:.1f} N +X"
    scale = float(overrides["mass_scale"])
    return scale, f"{scale:.1f}x", f"mass/inertia {scale:.1f}x"


def assessment_status(record: dict[str, Any], numerical: dict[str, Any]) -> str:
    if record.get("execution_classification") == "failed_execution_solver_stall":
        return "failed_execution_solver_stall"
    if record.get("status") == "passed":
        return "passed"
    artifacts = record.get("artifacts") if isinstance(record.get("artifacts"), dict) else {}
    raw_present = isinstance(artifacts.get("raw_csv"), str) and bool(artifacts.get("raw_csv"))
    completed_result = raw_present and isinstance(numerical.get("terminal_time_s"), (int, float))
    if completed_result:
        return "failed"
    reasons = " ".join(str(reason) for reason in record.get("failure_reasons", []))
    if "TimeoutError" in reasons:
        return "incomplete_timeout"
    return "incomplete_execution"


def load_records(input_roots: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for root in input_roots:
        resolved = root.resolve() if root.is_absolute() else (ROOT / root).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError as exc:
            raise ValueError(f"Input must remain under the project root: {resolved}") from exc
        if not resolved.is_dir():
            raise FileNotFoundError(f"Sensitivity result root is missing: {resolved}")
        for path in sorted(resolved.glob("*/*/SENSITIVITY_RUN_RECORD.json")):
            try:
                parsed = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                parsed["_record_path"] = project_relative(path)
                records.append(parsed)
    return records


def summarize(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        scenario = str(record.get("scenario_id") or "")
        controller = str(record.get("controller_id") or "")
        if scenario not in SCENARIO_TITLES or not controller:
            continue
        value, compact, label = record_value(record)
        numerical = record.get("numerical_closure") if isinstance(record.get("numerical_closure"), dict) else {}
        row = {
            "controller_id": controller,
            "scenario_id": scenario,
            "profile_id": record.get("profile_id"),
            "disturbance_value": value,
            "disturbance_label": compact,
            "disturbance_description": label,
            "status": assessment_status(record, numerical),
            "record_status": record.get("status"),
            "check_model_status": record.get("check_model_status"),
            "terminal_time_s": numerical.get("terminal_time_s"),
            "terminal_position_error_m": numerical.get("terminal_position_error_m"),
            "maximum_position_error_m": numerical.get("maximum_position_error_m"),
            "position_rmse_m": None,
            "record_path": record.get("_record_path"),
            "failure_reasons": record.get("failure_reasons", []),
        }
        metrics_path = record.get("artifacts", {}).get("metrics_json") if isinstance(record.get("artifacts"), dict) else None
        if isinstance(metrics_path, str):
            candidate = ROOT / metrics_path
            if candidate.is_file():
                try:
                    metrics = json.loads(candidate.read_text(encoding="utf-8"))
                    if isinstance(metrics, dict):
                        row["position_rmse_m"] = metrics.get("position_rmse_m")
                except json.JSONDecodeError:
                    pass
        rows.append(row)
        grouped[(scenario, controller)].append(row)

    thresholds: list[dict[str, Any]] = []
    for (scenario, controller), group in sorted(grouped.items()):
        group.sort(key=lambda item: float(item["disturbance_value"]))
        first_nonpass = next((index for index, item in enumerate(group) if item["status"] != "passed"), len(group))
        contiguous_passes = group[:first_nonpass]
        nonmonotonic = any(item["status"] == "passed" for item in group[first_nonpass:])
        last_pass = contiguous_passes[-1] if contiguous_passes else None
        first_nonpassing = group[first_nonpass] if first_nonpass < len(group) else None
        execution_blocked = bool(first_nonpassing and first_nonpassing["status"] == "failed_execution_solver_stall")
        incomplete = bool(first_nonpassing and first_nonpassing["status"].startswith("incomplete_"))
        if first_nonpass == len(group):
            threshold_status = "no_failure_observed_in_tested_range"
            first_fail = None
            if scenario == "motor_efficiency_fault":
                threshold_description = (
                    f"全部测试的持续效率损失点均通过至 {last_pass['disturbance_value']:.0f}% "
                    f"(eta={1.0-last_pass['disturbance_value']/100.0:.2f})，未观察到失败边界"
                )
            elif scenario == "wind_disturbance":
                threshold_description = (
                    f"全部测试的 +X 风扰点均通过至 {last_pass['disturbance_value']:.1f} N，未观察到失败边界"
                )
            else:
                threshold_description = (
                    f"全部测试的同步质量/惯量倍率均通过至 {last_pass['disturbance_value']:.1f}x，未观察到失败边界"
                )
        elif execution_blocked:
            threshold_status = "execution_blocked"
            threshold_description = "所需仿真在产出完成数值结果前停滞，无法分类"
            first_fail = None
        elif incomplete:
            threshold_status = "incomplete"
            threshold_description = "首个所需扰动点没有完成结果，无法分类"
            first_fail = None
        elif scenario == "motor_efficiency_fault":
            threshold_status = "observed_grid_boundary"
            first_fail = first_nonpassing
            threshold_description = (
                f"持续效率损失 <= {last_pass['disturbance_value']:.0f}% (eta={1.0-last_pass['disturbance_value']/100.0:.2f})"
                if last_pass else "没有通过的持续效率损失采样点"
            )
        elif scenario == "wind_disturbance":
            threshold_status = "observed_grid_boundary"
            first_fail = first_nonpassing
            threshold_description = (
                f"+X 风扰 <= {last_pass['disturbance_value']:.1f} N" if last_pass else "没有通过的 +X 风扰采样点"
            )
        else:
            threshold_status = "observed_grid_boundary"
            first_fail = first_nonpassing
            threshold_description = (
                f"同步质量/惯量倍率 <= {last_pass['disturbance_value']:.1f}x"
                if last_pass else "没有通过的同步质量/惯量倍率采样点"
            )
        thresholds.append({
            "controller_id": controller,
            "scenario_id": scenario,
            "sample_count": len(group),
            "passed_sample_count": sum(item["status"] == "passed" for item in group),
            "failed_sample_count": sum(item["status"] == "failed" for item in group),
            "execution_blocked_sample_count": sum(item["status"] == "failed_execution_solver_stall" for item in group),
            "incomplete_sample_count": sum(item["status"].startswith("incomplete_") for item in group),
            "threshold_status": threshold_status,
            "contiguous_from_low_disturbance": not nonmonotonic,
            "critical_threshold_description": threshold_description,
            "last_passing_sample": last_pass,
            "first_failing_sample": first_fail,
            "claim_boundary": "Observed grid boundary only. It is not an interpolated physical limit or a deployment guarantee.",
        })
    return rows, thresholds


def coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    observed = sorted({str(row["scenario_id"]) for row in rows})
    missing = [scenario for scenario in SCENARIO_TITLES if scenario not in observed]
    incomplete = [row for row in rows if str(row["status"]).startswith("incomplete_")]
    execution_blocked = [row for row in rows if row["status"] == "failed_execution_solver_stall"]
    return {
        "record_count": len(rows),
        "passed_record_count": sum(row["status"] == "passed" for row in rows),
        "physical_gate_failure_count": sum(row["status"] == "failed" for row in rows),
        "observed_scenarios": observed,
        "missing_scenarios": missing,
        "incomplete_record_count": len(incomplete),
        "execution_blocked_record_count": len(execution_blocked),
        "status": (
            "complete" if not missing and not incomplete and not execution_blocked else
            "completed_with_execution_blocked_records" if not missing and not incomplete else
            "partial_or_incomplete"
        ),
    }


def markdown_report(rows: list[dict[str, Any]], thresholds: list[dict[str, Any]], sources: list[str], coverage: dict[str, Any]) -> str:
    by_scenario: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_scenario[row["scenario_id"]].append(row)
    threshold_by_key = {(row["scenario_id"], row["controller_id"]): row for row in thresholds}
    lines = [
        "# 长时扰动灵敏度分析结果",
        "",
        "## 8.6 实验设计与判定边界",
        "",
        "本分析仅包含 15-50 s 的持续电机效率故障、持续 +X 风扰和 0-50 s 的持续质量/惯量失配。未运行短时注入或恢复时间实验。",
        "成功门槛为：原生 MWORKS `CheckModel` 成功、仿真到 50 s、终端位置误差小于 5 m、最大位置误差小于 10 m。临界值是本离散强度网格的观测边界，不做插值或部署外推。",
        "",
        "输入证据根目录：" + ", ".join(f"`{source}`" for source in sources),
        "",
    ]
    if coverage["status"] != "complete":
        lines.extend([
            "## 当前执行状态",
            "",
            "本报告已完成三个场景的记录覆盖，但含执行阻塞：`incomplete_timeout`、`incomplete_execution` 和 `failed_execution_solver_stall` 不被当作控制器物理失效或临界阈值样本。缺失场景不能导出阈值。",
            (
                f"本次输入包含 {coverage['record_count']} 条记录：{coverage['passed_record_count']} 条通过门槛、"
                f"{coverage['physical_gate_failure_count']} 条完成但未通过物理门槛、"
                f"{coverage['execution_blocked_record_count']} 条执行阻塞。"
            ),
            "三个场景均有记录；执行阻塞记录不能用于推导物理鲁棒性临界值。",
            "",
        ])
    for scenario in ("motor_efficiency_fault", "wind_disturbance", "parameter_mismatch"):
        lines.extend([f"## {SCENARIO_TITLES[scenario]}", ""])
        scenario_rows = sorted(by_scenario.get(scenario, []), key=lambda item: (item["controller_id"], item["disturbance_value"]))
        if not scenario_rows:
            lines.extend(["尚无该场景的可解析 MWORKS 运行记录。", ""])
            continue
        lines.extend([
            "| Controller | Disturbance | Status | RMSE (m) | Terminal error (m) | Max error (m) | Stop time (s) |",
            "|---|---|---|---:|---:|---:|---:|",
        ])
        for row in scenario_rows:
            def number(value: Any) -> str:
                return f"{float(value):.6g}" if isinstance(value, (int, float)) else "-"
            lines.append(
                f"| {row['controller_id']} | {row['disturbance_label']} | {row['status']} | "
                f"{number(row['position_rmse_m'])} | {number(row['terminal_position_error_m'])} | "
                f"{number(row['maximum_position_error_m'])} | {number(row['terminal_time_s'])} |"
            )
        lines.extend(["", "观测临界值："])
        for controller in sorted({row["controller_id"] for row in scenario_rows}):
            threshold = threshold_by_key[(scenario, controller)]
            if threshold["threshold_status"] in {"incomplete", "execution_blocked"}:
                lines.append(f"- `{controller}`: {threshold['critical_threshold_description']}.")
                continue
            if threshold["threshold_status"] == "no_failure_observed_in_tested_range":
                lines.append(
                    f"- `{controller}`: {threshold['critical_threshold_description']}；"
                    "这只是已测范围的下界，需更高强度扫描才能定位临界值。"
                )
                continue
            boundary = threshold["critical_threshold_description"]
            if threshold["first_failing_sample"]:
                boundary += f"；下一采样失败点：{threshold['first_failing_sample']['disturbance_label']}"
            if not threshold["contiguous_from_low_disturbance"]:
                boundary += "；采样通过/失败顺序非单调，因此不作单一单调阈值声明"
            lines.append(f"- `{controller}`: {boundary}.")
        lines.append("")
    lines.extend([
        "## Claim Boundary",
        "",
        "这些结果是当前 Modelica FormalRunner 与当前 profile 的 MWORKS MCP 证据。它们不证明真实飞行器参数真值、PX4/Gazebo/ROS 部署性能、恢复时间、控制器重新整定收益或任务级闭环成功。",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, type=Path, help="Sensitivity batch result root; repeat for motor, wind, and parameter roots.")
    parser.add_argument("--output", type=Path, default=Path("Results/control_platform/sensitivity_analysis_long_v1"))
    parser.add_argument("--report", type=Path, default=Path("Docs/灵敏度分析结果报告.md"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.resolve() if args.output.is_absolute() else (ROOT / args.output).resolve()
    report = args.report.resolve() if args.report.is_absolute() else (ROOT / args.report).resolve()
    records = load_records(args.input)
    if not records:
        raise RuntimeError("No SENSITIVITY_RUN_RECORD.json files were found in the requested roots")
    rows, thresholds = summarize(records)
    coverage = coverage_summary(rows)
    source_paths = [project_relative((path.resolve() if path.is_absolute() else (ROOT / path).resolve())) for path in args.input]
    write_json(output / "SENSITIVITY_ANALYSIS_SUMMARY.json", {
        "schema": "mosim.sensitivity_analysis_summary.v1",
        "generated_at": utc_now(),
        "source": "MWORKS_MCP",
        "input_roots": source_paths,
        "run_record_count": len(records),
        "coverage": coverage,
        "rows": rows,
        "thresholds": thresholds,
        "claim_boundary": "Observed long-duration grid thresholds only; no recovery-time or real-aircraft/deployment claim."
    })
    csv_path = output / "SENSITIVITY_ANALYSIS_SUMMARY.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "controller_id", "scenario_id", "profile_id", "disturbance_value", "disturbance_label",
        "status", "position_rmse_m", "terminal_time_s", "terminal_position_error_m",
        "maximum_position_error_m", "record_path",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row.get(field) for field in fields} for row in rows)
    report_text = markdown_report(rows, thresholds, source_paths, coverage)
    write_text(output / "SENSITIVITY_ANALYSIS_SUMMARY.md", report_text)
    write_text(report, report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
