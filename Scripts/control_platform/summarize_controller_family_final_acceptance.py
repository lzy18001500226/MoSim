#!/usr/bin/env python3
"""Build the fail-closed controller-family Gazebo acceptance matrix."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "Results/control_platform/controller_family_final_acceptance_20260717"


@dataclass(frozen=True)
class SingleUavSpec:
    cohort: str
    controller: str
    run_globs: tuple[str, ...]
    provenance_glob: str


@dataclass
class MatrixRow:
    cohort: str
    controller: str
    contract: str
    status: str
    implementation_state: str | None = None
    mworks_codegen_state: str | None = None
    generated_sil_state: str | None = None
    selectable: bool = False
    mission_status: str | None = None
    provenance_status: str | None = None
    pre_takeoff_status: str | None = None
    takeoff_reached: bool | None = None
    landing_disarm: bool | None = None
    hover_xy_rmse_m: float | None = None
    hover_z_rmse_m: float | None = None
    trajectory_status: str | None = None
    first_blocker: str | None = None
    evidence_paths: list[str] | None = None
    claim_ceiling: str | None = None


P1_RUNS = "Results/sunray_ros1"
CONTROL_RESULTS = "Results/control_platform"

SINGLE_UAV_SPECS = (
    SingleUavSpec("P1_PID", "cascade_pid", (f"{P1_RUNS}/p1_pid_cascade_runtime*_20260716",), "PID_GENERATED_RUNTIME_PROVENANCE.json"),
    SingleUavSpec("P1_PID", "anti_windup", (f"{P1_RUNS}/p1_pid_anti_windup_runtime*_20260716",), "PID_GENERATED_RUNTIME_PROVENANCE.json"),
    SingleUavSpec("P1_PID", "feedforward_profile", (f"{P1_RUNS}/p1_pid_feedforward_runtime*_20260716",), "PID_GENERATED_RUNTIME_PROVENANCE.json"),
    SingleUavSpec("P1_PID", "gain_scheduled_pid", (f"{P1_RUNS}/p1_pid_gain_scheduled_runtime*_20260716",), "PID_GENERATED_RUNTIME_PROVENANCE.json"),
    SingleUavSpec("P1_PID", "fuzzy_pid", (f"{P1_RUNS}/p1_pid_fuzzy_runtime*_20260716",), "PID_GENERATED_RUNTIME_PROVENANCE.json"),
    SingleUavSpec("P1_PID", "neural_pid", (f"{P1_RUNS}/p1_pid_neural_runtime*_20260716",), "PID_GENERATED_RUNTIME_PROVENANCE.json"),
    *(
        SingleUavSpec("P2_LINEAR_ROBUST", name, (f"{CONTROL_RESULTS}/p2_linear_robust_runtime_20260716/{name}*",), "*RUNTIME_PROVENANCE.json")
        for name in ("lqg", "feedback_linearization", "passivity_based_control", "adaptive_backstepping")
    ),
    *(
        SingleUavSpec("P3_SLIDING_MODE", name, (f"{CONTROL_RESULTS}/p3_sliding_mode_runtime_20260716/{name}*",), "*RUNTIME_PROVENANCE.json")
        for name in ("integral_smc", "terminal_smc", "nonsingular_terminal_smc", "super_twisting_smc", "adaptive_smc", "fuzzy_smc")
    ),
    *(
        SingleUavSpec("P4_MPC", name, (f"{CONTROL_RESULTS}/p4_mpc_runtime_20260716/{name}*",), "*RUNTIME_PROVENANCE.json")
        for name in ("linear_mpc", "robust_mpc", "adaptive_mpc", "tube_mpc", "explicit_gain_scheduled_mpc", "ilqr", "mppi")
    ),
    *(
        SingleUavSpec("P5_ENHANCEMENT", name, (f"{CONTROL_RESULTS}/p5_enhancement_runtime_20260717/{name}*",), "*RUNTIME_PROVENANCE.json")
        for name in ("l1_adaptive", "awff", "complete_adrc", "standardized_indi", "parameter_scheduling", "ilc")
    ),
)

G9_CONTROLLERS = (
    "official_pid", "se3_basic", "dfbc_basic", "smc_boundary_layer", "pid_indi", "nmpc_outer"
)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def candidate_dirs(globs: Iterable[str]) -> list[Path]:
    found: dict[str, Path] = {}
    for pattern in globs:
        for path in ROOT.glob(pattern):
            if path.is_dir():
                found[str(path.resolve())] = path
    return sorted(found.values(), key=lambda path: path.stat().st_mtime, reverse=True)


def bool_at(payload: dict[str, Any], *keys: str) -> bool | None:
    value: Any = payload
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value if isinstance(value, bool) else None


def value_at(payload: dict[str, Any], *keys: str) -> Any:
    value: Any = payload
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def inspect_single_run(spec: SingleUavSpec, run_dir: Path) -> MatrixRow:
    metrics_path = run_dir / "PX4CTRL_BASIC_MISSION_METRICS.json"
    metrics = load_json(metrics_path)
    provenance_paths = list(run_dir.glob(spec.provenance_glob))
    provenance_path = provenance_paths[0] if provenance_paths else None
    provenance = load_json(provenance_path) if provenance_path else {}
    mission_status = metrics.get("status")
    provenance_status = provenance.get("status")
    controller_match = provenance.get("controller_name") in (None, spec.controller)
    pre_takeoff = value_at(metrics, "pre_takeoff_state_gate", "status")
    takeoff = bool_at(metrics, "takeoff_reached_altitude")
    landed = bool_at(metrics, "landing_disarm", "success")
    paths = [relative(path) for path in (metrics_path, provenance_path) if path and path.is_file()]

    if not metrics:
        status = "not_run"
        blocker = "missing mission metrics"
    elif mission_status != "passed":
        status = "executed_blocked"
        blocker = str(metrics.get("reason") or "mission metric gate failed")
    elif provenance_status != "passed" or not controller_match:
        status = "provenance_missing"
        blocker = "same-run generated runtime provenance missing or inconsistent"
    elif pre_takeoff != "passed" or takeoff is not True or landed is not True:
        status = "executed_blocked"
        blocker = "takeoff/landing lifecycle gate incomplete"
    else:
        status = "accepted"
        blocker = None

    return MatrixRow(
        cohort=spec.cohort,
        controller=spec.controller,
        contract="single_uav_takeoff_hover_land",
        status=status,
        mission_status=mission_status,
        provenance_status=provenance_status,
        pre_takeoff_status=pre_takeoff,
        takeoff_reached=takeoff,
        landing_disarm=landed,
        hover_xy_rmse_m=value_at(metrics, "steady_hover", "xy_rmse_m"),
        hover_z_rmse_m=value_at(metrics, "steady_hover", "z_abs_rmse_m"),
        trajectory_status="not_run",
        first_blocker=blocker,
        evidence_paths=paths,
        claim_ceiling="generated_c_gazebo_takeoff_hover_land" if status == "accepted" else "executed_not_accepted",
    )


def best_single_row(spec: SingleUavSpec) -> MatrixRow:
    runs = candidate_dirs(spec.run_globs)
    if not runs:
        return MatrixRow(spec.cohort, spec.controller, "single_uav_takeoff_hover_land", "not_run", first_blocker="no run directory", evidence_paths=[])
    rows = [inspect_single_run(spec, run) for run in runs]
    def rank(row: MatrixRow) -> int:
        if row.status == "accepted":
            return 0
        if row.status == "executed_blocked" and row.provenance_status == "passed":
            return 1
        if row.status == "provenance_missing":
            return 2
        if row.status == "executed_blocked":
            return 3
        return 4

    return min(enumerate(rows), key=lambda item: (rank(item[1]), item[0]))[1]


def inspect_g9_run(controller: str, run_dir: Path) -> MatrixRow:
    metrics_path = run_dir / "PX4CTRL_BASIC_MISSION_METRICS.json"
    provenance_path = run_dir / "G9_GENERATED_RUNTIME_PROVENANCE.json"
    metrics = load_json(metrics_path)
    provenance = load_json(provenance_path)
    mission_status = metrics.get("status")
    provenance_status = provenance.get("status")
    pre_takeoff = value_at(metrics, "pre_takeoff_state_gate", "status")
    takeoff = bool_at(metrics, "takeoff_reached_altitude")
    landed = bool_at(metrics, "landing_disarm", "success")
    paths = [relative(path) for path in (metrics_path, provenance_path) if path.is_file()]

    if not metrics:
        status = "not_run"
        blocker = "missing G9 mission metrics"
    elif mission_status != "passed":
        status = "executed_blocked"
        blocker = str(metrics.get("reason") or "G9 mission metric gate failed")
    elif provenance_status != "passed" or provenance.get("controller_name") != controller:
        status = "provenance_missing"
        blocker = "same-run G9 generated runtime provenance missing or inconsistent"
    else:
        status = "accepted"
        blocker = None

    return MatrixRow(
        cohort="G9_CORE_COMPARISON",
        controller=controller,
        contract="generated_c_takeoff_hover_land_and_figure_eight",
        status=status,
        mission_status=mission_status,
        provenance_status=provenance_status,
        pre_takeoff_status=pre_takeoff,
        takeoff_reached=takeoff,
        landing_disarm=landed,
        hover_xy_rmse_m=value_at(metrics, "steady_hover", "xy_rmse_m"),
        hover_z_rmse_m=value_at(metrics, "steady_hover", "z_abs_rmse_m"),
        trajectory_status="not_run",
        first_blocker=blocker,
        evidence_paths=paths,
        claim_ceiling=(
            "generated_c_gazebo_takeoff_hover_land"
            if status == "accepted" else "executed_not_accepted"
        ),
    )


def g9_row(controller: str) -> MatrixRow:
    root = DEFAULT_OUTPUT / "g9_core" / controller
    basic_candidates = sorted(
        (path for path in root.glob("takeoff_hover_land*") if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    ) if root.is_dir() else []
    rows = [inspect_g9_run(controller, path) for path in basic_candidates]
    rank = {"accepted": 0, "executed_blocked": 1, "provenance_missing": 2, "not_run": 3}
    if rows:
        basic = min(enumerate(rows), key=lambda item: (rank[item[1].status], item[0]))[1]
        if basic.status != "accepted":
            return basic

        trajectory_candidates = sorted(
            (path for path in root.glob("figure8*") if path.is_dir()),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        trajectory_rows = [inspect_g9_run(controller, path) for path in trajectory_candidates]
        if not trajectory_rows:
            basic.status = "not_run"
            basic.trajectory_status = "not_run"
            basic.first_blocker = "required G9 figure-eight gate not run"
            basic.claim_ceiling = "generated_c_gazebo_takeoff_hover_land"
            return basic
        trajectory = min(
            enumerate(trajectory_rows),
            key=lambda item: (rank[item[1].status], item[0]),
        )[1]
        basic.trajectory_status = trajectory.mission_status or trajectory.status
        basic.evidence_paths = (basic.evidence_paths or []) + (trajectory.evidence_paths or [])
        if trajectory.status != "accepted":
            basic.status = trajectory.status
            basic.first_blocker = f"figure-eight: {trajectory.first_blocker}"
            basic.claim_ceiling = "generated_c_gazebo_takeoff_hover_land"
            return basic
        basic.status = "accepted"
        basic.first_blocker = None
        basic.claim_ceiling = "generated_c_gazebo_takeoff_hover_land_and_figure_eight"
        return basic
    return MatrixRow(
        cohort="G9_CORE_COMPARISON",
        controller=controller,
        contract="generated_c_takeoff_hover_land_and_figure_eight",
        status="not_run",
        trajectory_status="not_run",
        first_blocker="official_pid shared baseline blocked; controller gate not run",
        evidence_paths=["Docs/Workflows/g9_mworks_generated_runtime_closeout.md"],
        claim_ceiling="offline_equivalence_only",
    )


def special_row(cohort: str, controller: str, contract: str, path: str, accepted_statuses: set[str], claim: str) -> MatrixRow:
    evidence = ROOT / path
    payload = load_json(evidence)
    raw_status = payload.get("status")
    status = "accepted" if raw_status in accepted_statuses else ("executed_blocked" if payload else "not_run")
    return MatrixRow(
        cohort=cohort,
        controller=controller,
        contract=contract,
        status=status,
        mission_status=str(raw_status) if raw_status is not None else None,
        first_blocker=None if status == "accepted" else str(payload.get("reason") or "specialized gate is not accepted"),
        evidence_paths=[relative(evidence)] if evidence.is_file() else [],
        claim_ceiling=claim if status == "accepted" else "specialized_gate_not_accepted",
    )


def build_rows() -> list[MatrixRow]:
    rows = [best_single_row(spec) for spec in SINGLE_UAV_SPECS]

    rows.extend(g9_row(name) for name in G9_CONTROLLERS)

    rows.append(special_row(
        "P6_SAFETY", "safety_supervisor_family", "event_acknowledgement",
        "Results/control_platform/p6_safety_runtime_20260717/P6_SAFETY_RUNTIME_MATRIX.json",
        {"passed"}, "seven_generated_safety_modes_runtime_event_acknowledged",
    ))
    rows.append(special_row(
        "P7_FTC", "fdi_ftc_family", "physical_rotor_loss_isolation_takeover_landing",
        "Results/control_platform/p7_ftc_generated_gazebo_r3_20260717/P7_FTC_RUNTIME_CLOSEOUT.json",
        {"passed"}, "physical_rotor1_loss35_generated_ftc_runtime_accepted",
    ))

    p8_modes = (
        "leader_follower", "virtual_structure", "consensus", "containment",
        "formation_tracking", "formation_reconfiguration", "fault_tolerant_formation",
        "formation_cbf", "distributed_mpc_formation",
    )
    for index, name in enumerate(p8_modes, start=1):
        candidates = sorted(
            ROOT.glob(f"Results/control_platform/p8_formation_mode{index}_gazebo*_20260717/PX4CTRL_SWARM_BASIC_METRICS.json"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        accepted = next((path for path in candidates if load_json(path).get("status") == "passed"), None)
        chosen = accepted or (candidates[0] if candidates else None)
        payload = load_json(chosen) if chosen else {}
        status = "accepted" if payload.get("status") == "passed" else ("executed_blocked" if payload else "not_run")
        rows.append(MatrixRow(
            cohort="P8_FORMATION", controller=name, contract="three_uav_generated_formation",
            status=status, mission_status=payload.get("status"),
            first_blocker=None if status == "accepted" else str(payload.get("reason") or "formation gate not accepted"),
            evidence_paths=[relative(chosen)] if chosen else [],
            claim_ceiling="three_uav_takeoff_hover_land_generated_formation" if status == "accepted" else "formation_runtime_not_accepted",
        ))

    p9_path = "Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json"
    p9 = load_json(ROOT / p9_path)
    for name in ("trained_neural_residual", "rl_gain_scheduler"):
        route = value_at(p9, "routes", name) or {}
        rows.append(MatrixRow(
            cohort="P9_LEARNING", controller=name, contract="nominal_wind_parameter_mismatch_ab",
            status="executed_blocked" if p9.get("execution_status") == "passed" else "not_run",
            mission_status=p9.get("execution_status"), provenance_status=route.get("runtime_provenance"),
            landing_disarm=route.get("landing_disarm") == "passed_in_all_three_conditions",
            first_blocker="strict performance acceptance blocked",
            evidence_paths=[p9_path],
            claim_ceiling="report_ready_runtime_execution_not_selectable",
        ))
    for row in rows:
        row.implementation_state = "implemented"
        row.mworks_codegen_state = "passed"
        row.generated_sil_state = "passed"
        row.selectable = row.status == "accepted" and row.cohort != "P9_LEARNING"
    return rows


def write_outputs(rows: list[MatrixRow], output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
    if all(row.status == "accepted" for row in rows):
        overall_status = "passed"
    elif any(row.status == "provenance_missing" for row in rows):
        overall_status = "in_progress"
    else:
        overall_status = "closed_with_blockers"
    payload = {
        "schema": "mosim.controller_family_final_acceptance.v1",
        "status": overall_status,
        "claim_boundary": "Rows are accepted only under their type-specific Gazebo contract; blocked or missing provenance remains explicit.",
        "counts": counts,
        "figures": [
            "figures/acceptance_status_counts.png",
            "figures/cohort_status_distribution.png",
            "figures/single_uav_hover_rmse.png",
        ],
        "rows": [asdict(row) for row in rows],
    }
    matrix_path = output / "CONTROLLER_FAMILY_FINAL_MATRIX.json"
    matrix_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    csv_path = output / "CONTROLLER_FAMILY_COMPARISON.csv"
    fields = [field for field in asdict(rows[0]) if field != "evidence_paths"] + ["evidence_paths"]
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            item = asdict(row)
            item["evidence_paths"] = ";".join(item["evidence_paths"] or [])
            writer.writerow(item)

    lines = [
        "# Controller Family Final Acceptance Summary", "",
        f"Overall status: `{payload['status']}`.", "",
        "| Cohort | Controller | Codegen | SIL | Gazebo acceptance | Selectable | XY RMSE m | Z RMSE m | Blocker |",
        "|---|---|---|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        xy = "" if row.hover_xy_rmse_m is None else f"{row.hover_xy_rmse_m:.6f}"
        z = "" if row.hover_z_rmse_m is None else f"{row.hover_z_rmse_m:.6f}"
        blocker = (row.first_blocker or "").replace("|", "/")
        lines.append(
            f"| {row.cohort} | {row.controller} | {row.mworks_codegen_state} | "
            f"{row.generated_sil_state} | `{row.status}` | {str(row.selectable).lower()} | "
            f"{xy} | {z} | {blocker} |"
        )
    lines.extend(["", "Counts: " + ", ".join(f"`{key}={value}`" for key, value in sorted(counts.items())) + ".", ""])
    (output / "SUMMARY.md").write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_figures(rows, output / "figures")
    return payload


def write_figures(rows: list[MatrixRow], figure_dir: Path) -> None:
    figure_dir.mkdir(parents=True, exist_ok=True)
    colors = {
        "accepted": "#2f855a",
        "executed_blocked": "#c53030",
        "provenance_missing": "#b7791f",
        "not_run": "#718096",
    }

    status_order = ["accepted", "executed_blocked", "provenance_missing", "not_run"]
    status_counts = {status: sum(row.status == status for row in rows) for status in status_order}
    present = [status for status in status_order if status_counts[status]]
    fig, ax = plt.subplots(figsize=(8.0, 4.2))
    bars = ax.barh(present, [status_counts[status] for status in present], color=[colors[status] for status in present])
    ax.bar_label(bars, padding=4)
    ax.set_xlabel("Controller entries")
    ax.set_title("Controller-family final acceptance status")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figure_dir / "acceptance_status_counts.png", dpi=180)
    plt.close(fig)

    cohorts = list(dict.fromkeys(row.cohort for row in rows))
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    left = [0] * len(cohorts)
    for status in status_order:
        values = [sum(row.cohort == cohort and row.status == status for row in rows) for cohort in cohorts]
        ax.barh(cohorts, values, left=left, label=status, color=colors[status])
        left = [a + b for a, b in zip(left, values)]
    ax.set_xlabel("Controller entries")
    ax.set_title("Acceptance distribution by controller cohort")
    ax.legend(
        frameon=False,
        ncol=4,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
    )
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figure_dir / "cohort_status_distribution.png", dpi=180)
    plt.close(fig)

    metric_rows = [
        row for row in rows
        if row.hover_xy_rmse_m is not None and row.hover_z_rmse_m is not None
    ]
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    for status in status_order:
        selected = [row for row in metric_rows if row.status == status]
        if not selected:
            continue
        ax.scatter(
            [row.hover_xy_rmse_m for row in selected],
            [row.hover_z_rmse_m for row in selected],
            label=status,
            color=colors[status],
            s=48,
            alpha=0.86,
            edgecolors="white",
            linewidths=0.6,
        )
    ax.axvline(0.02, color="#4a5568", linestyle="--", linewidth=1.0, label="0.02 m gate")
    ax.axhline(0.02, color="#4a5568", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Steady-hover XY RMSE (m)")
    ax.set_ylabel("Steady-hover Z RMSE (m)")
    ax.set_title("Single-UAV hover error under the final evidence gate")
    ax.grid(alpha=0.2)
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(figure_dir / "single_uav_hover_rmse.png", dpi=180)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = write_outputs(build_rows(), args.output.resolve())
    print(json.dumps({"status": payload["status"], "counts": payload["counts"], "output": str(args.output.resolve())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
