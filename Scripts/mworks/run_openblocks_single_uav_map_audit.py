#!/usr/bin/env python3
"""Run the bounded OpenBlocks single-UAV map-review model on an existing Sysplorer port."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import mworks.sysplorer as ModelingPy


ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
MODEL_NAME = "MoSimQuadrotorModel.Guidance.Planning.OpenBlocksSingleUavMapAudit"
LEGACY_MODEL_NAME = "MoSimQuadrotorModel.Guidance.Planning.Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop"
PACKAGE_FILE = ROOT / "Models" / "MoSimQuadrotorModel" / "package.mo"
DISPLAY_FILE = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Guidance"
    / "Planning"
    / "OpenBlocksMapTruthDisplay.mo"
)
MODEL_FILE = (
    ROOT
    / "Models"
    / "MoSimQuadrotorModel"
    / "Guidance"
    / "Planning"
    / "Sunray150PlanningOpenBlocksSingleUavMapAudit.mo"
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True, help="Existing Sysplorer port to reuse; this script never starts Sysplorer.")
    parser.add_argument(
        "--reload-owned-root",
        action="store_true",
        help="Targetedly unload only MoSimQuadrotorModel from a dedicated blank session before source reload.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "Results" / "planning" / "openblocks_single_uav_map_audit_20260730",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    native_result_dir = output_dir / "native_result" / "OpenBlocksSingleUavMapAudit"
    raw_dir = output_dir / "raw"
    native_result_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    report: dict[str, object] = {
        "schema": "mosim.openblocks_single_uav_map_audit.v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "MWORKS_MCP",
        "tool_transport": "official ModelingPy connected explicitly to an already-running Sysplorer port",
        "existing_sysplorer_port": args.port,
        "live_mworks_touched": True,
        "will_not_click_activation_login": True,
        "model_name": MODEL_NAME,
        "claim_boundary": "Map-visualization review only. This bounded 0.2 s run does not establish obstacle avoidance, flight safety, controller performance, or planner acceptance.",
    }

    try:
        # ModelingPy.ConnectSysplorer returns None on a successful connection in
        # this MWORKS release; an exception is the failure signal.
        connection_result = ModelingPy.ConnectSysplorer("127.0.0.1", args.port)
        report["connect_sysplorer"] = True
        report["connect_sysplorer_return"] = repr(connection_result)

        display_class = "MoSimQuadrotorModel.Guidance.Planning.OpenBlocksMapTruthDisplay"
        if args.reload_owned_root:
            report["targeted_root_unload"] = bool(ModelingPy.EraseClasses(("MoSimQuadrotorModel",)))
            if not report["targeted_root_unload"]:
                raise RuntimeError(
                    "Targeted unload of the owned MoSimQuadrotorModel root failed: "
                    f"{ModelingPy.GetLastErrors()}"
                )
        if not ModelingPy.ClassExist(MODEL_NAME) and not ModelingPy.ClassExist(display_class):
            report["open_package_file"] = bool(ModelingPy.OpenModelFile(str(PACKAGE_FILE)))
            if not report["open_package_file"]:
                raise RuntimeError(f"OpenModelFile failed for {PACKAGE_FILE}: {ModelingPy.GetLastErrors()}")

        if not ModelingPy.ClassExist(display_class):
            report["open_display_file"] = bool(ModelingPy.OpenModelFile(str(DISPLAY_FILE)))
            if not report["open_display_file"]:
                raise RuntimeError(f"OpenModelFile failed for {DISPLAY_FILE}: {ModelingPy.GetLastErrors()}")

        if not ModelingPy.ClassExist(MODEL_NAME):
            report["open_audit_model_file"] = bool(ModelingPy.OpenModelFile(str(MODEL_FILE)))
            if not report["open_audit_model_file"]:
                raise RuntimeError(f"OpenModelFile failed for {MODEL_FILE}: {ModelingPy.GetLastErrors()}")
        if not ModelingPy.ClassExist(MODEL_NAME):
            raise RuntimeError(f"Audit model is not available after explicit source loading: {ModelingPy.GetLastErrors()}")

        selected_model = MODEL_NAME
        report["map_source"] = "review-only audit wrapper with canonical global map truth"
        report["model_name"] = selected_model

        report["check_model"] = bool(ModelingPy.CheckModel(selected_model))
        if not report["check_model"]:
            raise RuntimeError(f"CheckModel failed for {selected_model}: {ModelingPy.GetLastErrors()}")

        report["simulate_model"] = bool(
            ModelingPy.SimulateModel(
                selected_model,
                startTime=0.0,
                stopTime=0.2,
                interval=0.01,
                simMode=0,
                path=str(native_result_dir),
            )
        )
        if not report["simulate_model"]:
            raise RuntimeError(f"SimulateModel failed for {selected_model}: {ModelingPy.GetLastErrors()}")

        times = [float(value) for value in ModelingPy.GetVarTimes()]
        if len(times) < 11:
            raise RuntimeError(f"Expected at least 11 samples from bounded map audit, got {len(times)}")
        time_csv = raw_dir / "time_s.csv"
        with time_csv.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["time_s"])
            writer.writerows([[value] for value in times])

        result_candidates = sorted(native_result_dir.rglob("Result.msr"))
        if not result_candidates:
            raise RuntimeError(
                f"Expected a native Result.msr below {native_result_dir}, found none"
            )
        result_file = max(result_candidates, key=lambda candidate: candidate.stat().st_mtime)
        report["native_result_candidates"] = [str(candidate) for candidate in result_candidates]
        report["native_result_file"] = str(result_file)
        report["native_result_exists"] = result_file.exists()
        report["sample_count"] = len(times)
        report["time_start_s"] = times[0]
        report["time_end_s"] = times[-1]
        report["time_csv"] = str(time_csv)

        try:
            report["open_model_diagram"] = bool(ModelingPy.OpenModel(selected_model, ModelingPy.ModelView.Diagram))
        except Exception as exc:
            report["open_model_diagram_error"] = repr(exc)
            report["open_model"] = bool(ModelingPy.OpenModel(selected_model))

        report["open_result"] = bool(ModelingPy.OpenResult(str(result_file)))
        if not report["open_result"]:
            raise RuntimeError(f"OpenResult failed for {result_file}: {ModelingPy.GetLastErrors()}")
        report["create_animation"] = bool(ModelingPy.CreateAnimation())
        if not report["create_animation"]:
            raise RuntimeError(f"CreateAnimation failed: {ModelingPy.GetLastErrors()}")
        report["animation_speed"] = bool(ModelingPy.AnimationSpeed(0.2))
        report["status"] = "completed"
    except Exception as exc:
        report["status"] = "blocked"
        report["error"] = repr(exc)
        try:
            report["last_errors"] = str(ModelingPy.GetLastErrors())
        except Exception as diagnostic_exc:
            report["last_errors_capture_error"] = repr(diagnostic_exc)
    finally:
        report["completed_at"] = datetime.now(timezone.utc).isoformat()
        write_json(output_dir / "MAP_AUDIT_RUN.json", report)

    return 0 if report["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
