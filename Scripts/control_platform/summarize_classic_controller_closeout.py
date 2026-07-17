#!/usr/bin/env python3
"""Extend the frozen controller matrix with canonical classic-controller rows."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from audit_classic_controller_coverage import CANONICAL_CONTROLLERS


ROOT = Path(__file__).resolve().parents[2]
BASE_MATRIX = (
    ROOT
    / "Results/control_platform/controller_family_final_acceptance_20260717"
    / "CONTROLLER_FAMILY_FINAL_MATRIX.json"
)
REGISTRY = ROOT / "Config/control_platform/control_module_registry.json"
DEFAULT_OUTPUT = ROOT / "Results/control_platform/classic_controller_closeout_20260717"
WAVE_A_ROOT = ROOT / "Results/control_platform/wave_a_generated_gazebo_20260718"
SOURCE_GATE = "source_gate/CLASSIC_CONTROLLER_SOURCE_GATE.json"
MWORKS_MIL = "mworks/MWORKS_MIL_MANIFEST.json"
MWORKS_CODEGEN = "mworks/MWORKS_CODEGEN_MANIFEST.json"
GENERATED_SIL = "mworks/sil/CLASSIC_CONTROLLER_GENERATED_SIL.json"
ADDITION_CONTROLLERS = {
    "pole_placement_luenberger",
    "mrac",
    "ndi",
    "fopid",
    "h2_state_feedback",
}
TRAJECTORY_CONTROLLERS = {"mrac", "ndi"}

PASSED_MWORKS_SIL = {
    "lqr_baseline",
    "lqi_baseline",
    "so3_attitude",
    "backstepping_baseline",
}
WAVE_A_RUNTIME_CASES = {
    "lqr_baseline": ("lqr_baseline/takeoff_hover_land_retry3_px4_startup", "file_backend"),
    "lqi_baseline": (
        "lqi_baseline/takeoff_hover_land_retry4_ram_dataman_wait120",
        "ram_dataman",
    ),
    "so3_attitude": (
        "so3_attitude/takeoff_hover_land_r1_ram_dataman_wait120",
        "ram_dataman",
    ),
    "backstepping_baseline": (
        "backstepping_baseline/takeoff_hover_land_r1_ram_dataman_wait120",
        "ram_dataman",
    ),
}
BLOCKED_IMPLEMENTATIONS = {"mu_synthesis", "neural_smc"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def evidence_paths(module: dict[str, Any]) -> list[str]:
    return [
        str(value)
        for key, value in module.items()
        if key.startswith("latest_") and key.endswith("_evidence") and value
    ]


def relative_evidence(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def optional_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return read_json(path)


def classic_addition_row(
    item: Any,
    module: dict[str, Any] | None,
    evidence_root: Path,
) -> dict[str, Any]:
    controller = item.module_id
    hover_dir = evidence_root / "gazebo" / controller
    hover_path = hover_dir / "PX4CTRL_BASIC_MISSION_METRICS.json"
    provenance_path = hover_dir / "CLASSIC_CONTROLLER_RUNTIME_PROVENANCE.json"
    hover = optional_json(hover_path)
    provenance = optional_json(provenance_path)

    trajectory_dir = evidence_root / "gazebo" / f"{controller}_figure8"
    trajectory_path = trajectory_dir / "PX4CTRL_BASIC_MISSION_METRICS.json"
    trajectory_provenance_path = trajectory_dir / "CLASSIC_CONTROLLER_RUNTIME_PROVENANCE.json"
    trajectory = optional_json(trajectory_path) if controller in TRAJECTORY_CONTROLLERS else None
    trajectory_provenance = (
        optional_json(trajectory_provenance_path)
        if controller in TRAJECTORY_CONTROLLERS
        else None
    )

    common_paths = [
        evidence_root / SOURCE_GATE,
        evidence_root / MWORKS_MIL,
        evidence_root / MWORKS_CODEGEN,
        evidence_root / GENERATED_SIL,
    ]
    paths = [path for path in common_paths if path.is_file()]
    paths.extend(path for path in (hover_path, provenance_path) if path.is_file())
    if controller in TRAJECTORY_CONTROLLERS:
        paths.extend(
            path
            for path in (trajectory_path, trajectory_provenance_path)
            if path.is_file()
        )

    hover_status = str(hover.get("status")) if hover else None
    provenance_status = str(provenance.get("status")) if provenance else None
    trajectory_status = str(trajectory.get("status")) if trajectory else "not_run"
    trajectory_provenance_status = (
        str(trajectory_provenance.get("status")) if trajectory_provenance else None
    )
    trajectory_metrics = (trajectory or {}).get("trajectory") or {}
    runtime_complete = hover is not None and provenance is not None
    hover_passed = hover_status == "passed" and provenance_status == "passed"
    trajectory_required = controller in TRAJECTORY_CONTROLLERS and hover_passed
    trajectory_passed = (
        trajectory_status == "passed" and trajectory_provenance_status == "passed"
    )

    if not runtime_complete:
        status = "not_run"
        blocker = "Gazebo takeoff-hover-land or same-run provenance not completed"
        claim_ceiling = "mworks_codegen_sil_and_build_provenance_only"
    elif not hover_passed:
        status = "executed_blocked"
        blocker = str(hover.get("reason") or ";".join(provenance.get("errors", [])))
        claim_ceiling = "generated_c_gazebo_executed_hover_acceptance_blocked"
    elif trajectory_required and not trajectory_passed:
        status = "executed_blocked"
        blocker = str(
            (trajectory or {}).get("reason")
            or ";".join((trajectory_provenance or {}).get("errors", []))
        )
        claim_ceiling = "generated_c_gazebo_hover_passed_figure8_acceptance_blocked"
    else:
        status = "accepted"
        blocker = None
        claim_ceiling = (
            "generated_c_gazebo_hover_and_figure8_accepted"
            if trajectory_required
            else "generated_c_gazebo_takeoff_hover_land_accepted"
        )

    steady_hover = (hover or {}).get("steady_hover") or {}
    pre_takeoff = (hover or {}).get("pre_takeoff_state_gate") or {}
    landing = (hover or {}).get("landing_disarm") or {}
    return {
        "cohort": "P11_CLASSIC_ADDITIONS",
        "controller": controller,
        "contract": "canonical_controller_evidence_ladder",
        "status": status,
        "implementation_state": str((module or {}).get("status", "not_implemented")),
        "mworks_codegen_state": "passed",
        "generated_sil_state": "passed",
        "selectable": status == "accepted",
        "mission_status": hover_status,
        "provenance_status": provenance_status,
        "pre_takeoff_status": pre_takeoff.get("status"),
        "takeoff_reached": (hover or {}).get("takeoff_reached_altitude"),
        "landing_disarm": landing.get("success"),
        "hover_xy_rmse_m": steady_hover.get("xy_rmse_m"),
        "hover_z_rmse_m": steady_hover.get("z_abs_rmse_m"),
        "trajectory_status": trajectory_status,
        "trajectory_xyz_rmse_m": trajectory_metrics.get("xyz_rmse_m"),
        "trajectory_xyz_p95_m": trajectory_metrics.get("xyz_p95_m"),
        "trajectory_xyz_max_m": trajectory_metrics.get("xyz_max_m"),
        "first_blocker": blocker,
        "evidence_paths": [relative_evidence(path) for path in paths],
        "claim_ceiling": claim_ceiling,
    }


def wave_a_runtime_row(
    item: Any,
    module: dict[str, Any] | None,
    wave_a_root: Path,
) -> dict[str, Any] | None:
    relative_dir, startup_backend = WAVE_A_RUNTIME_CASES[item.module_id]
    runtime_dir = wave_a_root / relative_dir
    metrics_path = runtime_dir / "PX4CTRL_BASIC_MISSION_METRICS.json"
    provenance_path = runtime_dir / "WAVE_A_GENERATED_RUNTIME_PROVENANCE.json"
    metrics = optional_json(metrics_path)
    provenance = optional_json(provenance_path)
    if metrics is None or provenance is None:
        return None

    metrics_status = str(metrics.get("status"))
    provenance_status = str(provenance.get("status"))
    passed = metrics_status == "passed" and provenance_status == "passed"
    status = "accepted" if passed else "executed_blocked"
    blocker = None
    if not passed:
        blocker = str(
            metrics.get("reason")
            or ";".join(str(value) for value in provenance.get("errors", []))
            or "runtime acceptance or generated-C provenance gate blocked"
        )

    paths = [metrics_path, provenance_path]
    startup_manifest_path = runtime_dir / "PX4_RAM_DATAMAN_RCS.json"
    if startup_manifest_path.is_file():
        paths.append(startup_manifest_path)
    steady_hover = metrics.get("steady_hover") or {}
    pre_takeoff = metrics.get("pre_takeoff_state_gate") or {}
    landing = metrics.get("landing_disarm") or {}
    return {
        "cohort": "P10_CLASSIC_RECONCILIATION",
        "controller": item.module_id,
        "contract": "canonical_controller_evidence_ladder",
        "status": status,
        "implementation_state": str((module or {}).get("status", "not_implemented")),
        "mworks_codegen_state": "passed",
        "generated_sil_state": "passed",
        "selectable": passed,
        "mission_status": metrics_status,
        "provenance_status": provenance_status,
        "px4_startup_backend": startup_backend,
        "pre_takeoff_status": pre_takeoff.get("status"),
        "takeoff_reached": metrics.get("takeoff_reached_altitude"),
        "landing_disarm": landing.get("success"),
        "hover_xy_rmse_m": steady_hover.get("xy_rmse_m"),
        "hover_z_rmse_m": steady_hover.get("z_abs_rmse_m"),
        "trajectory_status": "not_run",
        "first_blocker": blocker,
        "evidence_paths": [relative_evidence(path) for path in paths],
        "claim_ceiling": (
            "generated_c_gazebo_takeoff_hover_land_accepted"
            if passed
            else "generated_c_gazebo_executed_hover_acceptance_blocked"
        ),
    }


def canonical_row(
    item: Any,
    module: dict[str, Any] | None,
    wave_a_root: Path,
) -> dict[str, Any]:
    module_id = item.module_id
    if module_id in PASSED_MWORKS_SIL:
        runtime_row = wave_a_runtime_row(item, module, wave_a_root)
        if runtime_row is not None:
            return runtime_row
        codegen_state = "passed"
        sil_state = "passed"
        blocker = "Gazebo controller-specific gate not run"
    elif module_id == "hinf_hover_wrench":
        codegen_state = "not_run"
        sil_state = "source_oracle_only"
        blocker = "WRENCH allocator/adapter and generated-C Gazebo route are incomplete"
    elif module_id == "mu_synthesis":
        codegen_state = "blocked"
        sil_state = "not_run"
        blocker = "installed Syslab lacks dynamic musyn; constant-matrix mu analysis is not a controller"
    elif module_id == "neural_smc":
        codegen_state = "blocked"
        sil_state = "not_run"
        blocker = "no frozen training dataset or trained Neural-SMC artifact"
    elif item.addition:
        codegen_state = "not_run"
        sil_state = "not_run"
        blocker = "canonical addition not implemented"
    else:
        codegen_state = "not_audited"
        sil_state = "not_audited"
        blocker = "registered implementation has not entered the canonical evidence ladder"

    implementation_state = str(module.get("status", "not_implemented")) if module else "not_implemented"
    if module_id in BLOCKED_IMPLEMENTATIONS:
        implementation_state = "blocked"
    return {
        "cohort": "P10_CLASSIC_RECONCILIATION" if not item.addition else "P11_CLASSIC_ADDITIONS",
        "controller": module_id,
        "contract": "canonical_controller_evidence_ladder",
        "status": "not_run",
        "implementation_state": implementation_state,
        "mworks_codegen_state": codegen_state,
        "generated_sil_state": sil_state,
        "selectable": False,
        "mission_status": None,
        "provenance_status": None,
        "pre_takeoff_status": None,
        "takeoff_reached": None,
        "landing_disarm": None,
        "hover_xy_rmse_m": None,
        "hover_z_rmse_m": None,
        "trajectory_status": "not_run",
        "first_blocker": blocker,
        "evidence_paths": evidence_paths(module or {}),
        "claim_ceiling": str(module.get("claim_ceiling", "not_implemented")) if module else "not_implemented",
    }


def build_payload(
    base: dict[str, Any],
    registry: dict[str, Any],
    evidence_root: Path = DEFAULT_OUTPUT,
    wave_a_root: Path = WAVE_A_ROOT,
) -> dict[str, Any]:
    rows = [dict(row) for row in base.get("rows", [])]
    existing = {str(row.get("controller", "")) for row in rows}
    modules = {
        str(module.get("module_id", "")): module
        for module in registry.get("modules", [])
        if isinstance(module, dict)
    }
    for item in CANONICAL_CONTROLLERS:
        if item.module_id not in existing:
            if item.module_id in ADDITION_CONTROLLERS:
                rows.append(
                    classic_addition_row(
                        item, modules.get(item.module_id), evidence_root
                    )
                )
            else:
                rows.append(
                    canonical_row(
                        item,
                        modules.get(item.module_id),
                        wave_a_root,
                    )
                )
            existing.add(item.module_id)

    counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return {
        "schema": "mosim.classic_controller_final_matrix.v1",
        "status": "closed_with_blockers",
        "base_matrix": BASE_MATRIX.relative_to(ROOT).as_posix(),
        "claim_boundary": (
            "Complete row visibility is not controller acceptance. Each row retains its own "
            "implementation, MWORKS, generated-C, SIL and Gazebo evidence ceiling."
        ),
        "counts": counts,
        "rows": rows,
    }


def write_outputs(payload: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    rows = payload["rows"]
    (output / "CLASSIC_CONTROLLER_FINAL_MATRIX.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    fields = list(rows[0])
    for row in rows[1:]:
        fields.extend(key for key in row if key not in fields)
    with (output / "CLASSIC_CONTROLLER_COMPARISON.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            value = dict(row)
            value["evidence_paths"] = ";".join(value.get("evidence_paths") or [])
            writer.writerow(value)

    lines = [
        "# Classic Controller Closeout Summary",
        "",
        f"Status: `{payload['status']}`.",
        "",
        f"Rows: `{len(rows)}`. "
        + ", ".join(f"`{key}={value}`" for key, value in sorted(payload["counts"].items()))
        + ".",
        "",
        "Complete row visibility is not acceptance. See each row's blocker and claim ceiling.",
        "",
        "## Classic Additions",
        "",
        "| Controller | Final status | Hover XY RMSE (m) | Hover Z RMSE (m) | Trajectory | First blocker |",
        "|---|---|---:|---:|---|---|",
    ]
    for row in rows:
        if row.get("controller") not in ADDITION_CONTROLLERS:
            continue
        xy = row.get("hover_xy_rmse_m")
        z = row.get("hover_z_rmse_m")
        lines.append(
            "| {controller} | {status} | {xy} | {z} | {trajectory} | {blocker} |".format(
                controller=row["controller"],
                status=row["status"],
                xy=f"{xy:.6f}" if isinstance(xy, (int, float)) else "-",
                z=f"{z:.6f}" if isinstance(z, (int, float)) else "-",
                trajectory=row.get("trajectory_status") or "not_run",
                blocker=str(row.get("first_blocker") or "-").replace("|", "/"),
            )
        )
    lines.append("")
    (output / "SUMMARY.md").write_text(
        "\n".join(lines).rstrip() + "\n", encoding="utf-8", newline="\n"
    )
    write_figures(rows, output / "figures")


def write_figures(rows: list[dict[str, Any]], output: Path) -> None:
    import matplotlib.pyplot as plt

    additions = [
        row for row in rows if row.get("controller") in ADDITION_CONTROLLERS
    ]
    output.mkdir(parents=True, exist_ok=True)
    labels = [str(row["controller"]).replace("_", "\n") for row in additions]
    xy = [float(row["hover_xy_rmse_m"]) for row in additions]
    z = [float(row["hover_z_rmse_m"]) for row in additions]
    positions = list(range(len(additions)))
    width = 0.36
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar([x - width / 2 for x in positions], xy, width, label="XY RMSE", color="#2f6f8f")
    ax.bar([x + width / 2 for x in positions], z, width, label="Z RMSE", color="#c45b45")
    ax.axhline(0.02, color="#202020", linestyle="--", linewidth=1.2, label="0.020 m limit")
    ax.set_xticks(positions, labels)
    ax.set_ylabel("Steady-hover RMSE (m)")
    ax.set_title("Classic controller generated-C Gazebo hover comparison")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "classic_additions_hover_rmse.png", dpi=180)
    plt.close(fig)

    trajectories = [
        row for row in additions if row.get("trajectory_xyz_rmse_m") is not None
    ]
    labels = [str(row["controller"]).replace("_", "\n") for row in trajectories]
    rmse = [float(row["trajectory_xyz_rmse_m"]) for row in trajectories]
    p95 = [float(row["trajectory_xyz_p95_m"]) for row in trajectories]
    positions = list(range(len(trajectories)))
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    ax.bar([x - width / 2 for x in positions], rmse, width, label="XYZ RMSE", color="#347a5a")
    ax.bar([x + width / 2 for x in positions], p95, width, label="XYZ P95", color="#d0912f")
    ax.axhline(0.05, color="#347a5a", linestyle="--", linewidth=1.2, label="RMSE limit 0.050 m")
    ax.axhline(0.08, color="#d0912f", linestyle=":", linewidth=1.4, label="P95 limit 0.080 m")
    ax.set_xticks(positions, labels)
    ax.set_ylabel("Figure-eight tracking error (m)")
    ax.set_title("Accepted-hover profiles: representative trajectory gate")
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "classic_additions_figure8_rmse.png", dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-matrix", type=Path, default=BASE_MATRIX)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(
        read_json(args.base_matrix), read_json(args.registry), args.output
    )
    write_outputs(payload, args.output)
    print(json.dumps({"status": payload["status"], "counts": payload["counts"], "rows": len(payload["rows"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
