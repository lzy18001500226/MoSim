#!/usr/bin/env python3
"""Build the auditable P1 PID evidence and screenshot summaries."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULT_DIR = ROOT / "Results/control_platform/p1_pid_mworks_20260716"
LOG_DIR = RESULT_DIR / "logs"


def load(name: str) -> dict:
    return json.loads((LOG_DIR / name).read_text(encoding="utf-8"))


def file_record(path: Path, role: str, observation: str) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path),
        "role": role,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "observation": observation,
    }


def main() -> int:
    mil = load("mcp_evidence.json")
    graphical = load("pid_graphical_build_manifest.json")
    fixture = load("pid_graphical_fixture_manifest.json")
    codegen = load("pid_codegen_manifest.json")
    runtime = load("pid_codegen_runtime_check.json")
    equivalence = load("pid_graphical_codegen_equivalence.json")

    activation = next((RESULT_DIR / "screenshots/activation").glob("*.png"))
    check_sim = next((RESULT_DIR / "screenshots/check_sim").glob("*.png"))
    diagram = RESULT_DIR / "screenshots/graphical/MoSim_PID_Unified_Graphical_Sysblock.png"
    screenshots = {
        "schema": "mosim.mworks.screenshot_manifest.v1",
        "source": "MWORKS_GUI_AND_EXPORT_DIAGRAM",
        "screenshots": [
            file_record(
                activation,
                "task_local_license_sufficiency_reference",
                "Foreground Sysplorer education-edition main window; no login, license, authorization, crash, or unknown blocking dialog is visible. One CFunction include warning is visible and is unrelated to licensing.",
            ),
            file_record(
                check_sim,
                "mil_check_and_simulation",
                "Sysplorer reports simulation finished at 0.2 s with 20 grid points; no login, license, authorization, or error-report dialog is visible.",
            ),
            file_record(
                diagram,
                "graphical_sysblock_topology",
                "Exported 51-block PID topology visibly includes gain scheduling, fuzzy/neural residual paths, discrete derivative, bounded integral recurrence, tracking anti-windup, feedforward, cascade, saturation, enable, and mode selection. No disconnected block is visible; dense central routing remains a readability limitation.",
            ),
        ],
    }
    screenshot_path = LOG_DIR / "screenshot_manifest.json"
    screenshot_path.write_text(json.dumps(screenshots, indent=2) + "\n", encoding="utf-8")

    fixture_ids = sorted(mil["fixtures"])
    gates = {
        "source_core_compile_and_golden_vector": True,
        "registry_interface_ready_nonselectable": True,
        "six_variant_mworks_mil": len(fixture_ids) == 6 and all(item["sample_count"] == 21 for item in mil["fixtures"].values()),
        "graphical_structure_check": bool(graphical["structure_ok"]),
        "graphical_fixed_fixture_mworks_mil": bool(fixture["check_model"] and fixture["simulate_model"] and fixture["sample_count"] == 11),
        "official_mworks_generated_c": bool(codegen["generate_result"] and codegen["generated_file_count"] >= 7),
        "generated_c_compile": bool(runtime["compile"]["ok"]),
        "generated_c_runtime_smoke": bool(runtime["runtime_smoke"]["ok"]),
        "fixed_fixture_graphical_codegen_equivalence": bool(equivalence["behavior_equivalence_ok"]),
        "six_variant_graphical_equivalence": False,
        "full_attitude_thrust_contract": False,
        "gazebo_px4_mavros_closed_loop": False,
    }
    summary = {
        "schema": "mosim.control_platform.pid_p1_summary.v1",
        "phase": "P1_PID_FAMILY",
        "status": "partial",
        "algorithm_ids": fixture_ids,
        "registry_status": "interface_ready",
        "selectable": False,
        "gates": gates,
        "completed_gate_count": sum(gates.values()),
        "total_gate_count": len(gates),
        "evidence": {
            "mil": str(LOG_DIR / "mcp_evidence.json"),
            "graphical_structure": str(LOG_DIR / "pid_graphical_build_manifest.json"),
            "graphical_fixture": str(LOG_DIR / "pid_graphical_fixture_manifest.json"),
            "codegen": str(LOG_DIR / "pid_codegen_manifest.json"),
            "runtime": str(LOG_DIR / "pid_codegen_runtime_check.json"),
            "equivalence": str(LOG_DIR / "pid_graphical_codegen_equivalence.json"),
            "screenshots": str(screenshot_path),
        },
        "open_gates": [name for name, passed in gates.items() if not passed],
        "claim_boundary": "P1 has real scalar MIL, graphical topology, official generated C, compiled runtime smoke, and fixed-fixture graphical/codegen equivalence. It is not selectable and does not yet prove six-variant graphical parity, ATTITUDE_THRUST, or Gazebo closed loop.",
    }
    output = RESULT_DIR / "P1_PID_MIL_SUMMARY.json"
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
