#!/usr/bin/env python3
"""Build the static live-gate runner contract for MoSimQuadrotorModel.

This is a file-only checker/manifest generator. It reads the 023 formal smoke
surface artifacts, resolves the current project-owned Modelica source anchors,
and emits the future load/check/simulate/result-variable contract for a later
MWORKS task. It does not call MWORKS, Sysplorer, MCP, check_model, or simulate.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-LIVE-GATE-RUNNER-STATIC-HARDENING-20260608-024"
INPUT_REQUEST_ID = "PMO-MWORKS-R1-MOSIMQUAD-FORMAL-SMOKE-SURFACE-STATIC-PREP-20260608-023"

ROOT_CONSOLIDATION_DIR = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260722_mosimquad_model_root_consolidation"
)
DEFAULT_INPUT_DIR = ROOT_CONSOLIDATION_DIR / "formal_smoke_surface"
DEFAULT_OUTPUT_DIR = ROOT_CONSOLIDATION_DIR / "live_gate_runner"

CANONICAL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
BASELINE_PACKAGE = ROOT / "References" / "MWORKS" / "QuadrotorModel" / "package.mo"
FORMAL_DYNAMICS_DIR = CANONICAL_ROOT / "Dynamics"
FORMAL_PARAMETERS_DIR = CANONICAL_ROOT / "Parameters"
COMPAT_DIR = ROOT / "Models" / "QuadrotorExperiments" / "DynamicsUpgrade"

OUTPUT_FILES = [
    "live_gate_runner_plan.json",
    "live_gate_runner_plan.md",
    "target_resolution_check.json",
    "result_variable_probe_plan.json",
    "future_live_runner_contract.md",
    "changed_files.json",
    "static_validation_summary.json",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_order(path: Path) -> list[str]:
    return [line.strip() for line in read_text(path).splitlines() if line.strip()]


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def last_segment(fq_name: str) -> str:
    return fq_name.rsplit(".", 1)[-1]


def add_finding(
    findings: list[dict[str, Any]],
    *,
    code: str,
    message: str,
    severity: str = "error",
    target: str | None = None,
) -> None:
    entry: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if target:
        entry["target"] = target
    findings.append(entry)


def require_contains(
    findings: list[dict[str, Any]],
    text: str,
    snippet: str,
    *,
    code: str,
    target: str,
) -> bool:
    if snippet in text:
        return True
    add_finding(
        findings,
        code=code,
        message=f"missing source snippet {snippet!r}",
        target=target,
    )
    return False


def index_expected_variables(expected_variables: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in expected_variables.get("targets", []):
        target = item.get("target")
        if isinstance(target, str):
            indexed[target] = item
    return indexed


def index_matrix(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in matrix.get("targets", []):
        target = item.get("formal_target")
        if isinstance(target, str):
            indexed[target] = item
    return indexed


def validate_input_schemas(
    matrix: dict[str, Any],
    future_surface: dict[str, Any],
    expected_variables: dict[str, Any],
    findings: list[dict[str, Any]],
) -> None:
    if matrix.get("request_id") != INPUT_REQUEST_ID:
        add_finding(
            findings,
            code="unexpected_matrix_request_id",
            message=f"formal matrix request_id is {matrix.get('request_id')!r}",
        )
    if future_surface.get("request_id") != INPUT_REQUEST_ID:
        add_finding(
            findings,
            code="unexpected_future_surface_request_id",
            message=f"future surface request_id is {future_surface.get('request_id')!r}",
        )
    if expected_variables.get("request_id") != INPUT_REQUEST_ID:
        add_finding(
            findings,
            code="unexpected_expected_variables_request_id",
            message=f"expected variables request_id is {expected_variables.get('request_id')!r}",
        )


def build_resolution_check(
    matrix: dict[str, Any],
    future_surface: dict[str, Any],
    expected_variables: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    validate_input_schemas(matrix, future_surface, expected_variables, findings)

    target_index = index_matrix(matrix)
    expected_index = index_expected_variables(expected_variables)
    parameter_target = expected_variables.get("parameter_target", {})
    parameter_name = parameter_target.get("formal_target")

    canonical_package_path = CANONICAL_ROOT / "package.mo"
    canonical_order_path = CANONICAL_ROOT / "package.order"
    formal_package_path = FORMAL_DYNAMICS_DIR / "package.mo"
    formal_order_path = FORMAL_DYNAMICS_DIR / "package.order"
    compat_package_path = COMPAT_DIR / "package.mo"
    compat_order_path = COMPAT_DIR / "package.order"
    parameter_package_path = FORMAL_PARAMETERS_DIR / "package.mo"
    parameter_order_path = FORMAL_PARAMETERS_DIR / "package.order"

    canonical_order = read_order(canonical_order_path) if canonical_order_path.exists() else []
    formal_package = read_text(formal_package_path) if formal_package_path.exists() else ""
    formal_order = read_order(formal_order_path) if formal_order_path.exists() else []
    compat_package = read_text(compat_package_path) if compat_package_path.exists() else ""
    compat_order = read_order(compat_order_path) if compat_order_path.exists() else []
    parameter_package = read_text(parameter_package_path) if parameter_package_path.exists() else ""
    parameter_order = read_order(parameter_order_path) if parameter_order_path.exists() else []

    if not BASELINE_PACKAGE.is_file():
        add_finding(
            findings,
            code="official_baseline_package_missing",
            message="official QuadrotorModel baseline package is missing",
            target=rel(BASELINE_PACKAGE),
        )
    if not canonical_package_path.is_file():
        add_finding(
            findings,
            code="canonical_root_package_missing",
            message="MoSimQuadrotorModel package is missing",
            target=rel(canonical_package_path),
        )
    if "Dynamics" not in canonical_order:
        add_finding(
            findings,
            code="canonical_root_dynamics_missing",
            message="MoSimQuadrotorModel/package.order no longer exposes Dynamics",
            target=rel(canonical_order_path),
        )

    check_targets = future_surface.get("check_model_target_order", [])
    simulate_targets = future_surface.get("minimal_simulate_order_after_all_checks_pass", [])
    if not isinstance(check_targets, list):
        add_finding(
            findings,
            code="check_targets_not_list",
            message="future_live_validation_surface.check_model_target_order is not a list",
        )
        check_targets = []
    if not isinstance(simulate_targets, list):
        add_finding(
            findings,
            code="simulate_targets_not_list",
            message="future_live_validation_surface.minimal_simulate_order_after_all_checks_pass is not a list",
        )
        simulate_targets = []

    expected_check_targets = [parameter_name] + [
        item["formal_target"]
        for item in sorted(
            matrix.get("targets", []),
            key=lambda item: item.get("check_model_order", 9999),
        )
    ]
    expected_sim_targets = [
        item["formal_target"]
        for item in sorted(
            (
                item
                for item in matrix.get("targets", [])
                if item.get("simulate_order_after_all_checks") is not None
            ),
            key=lambda item: item.get("simulate_order_after_all_checks", 9999),
        )
    ]

    if check_targets != expected_check_targets:
        add_finding(
            findings,
            code="check_target_order_drift",
            message="future check_model order no longer matches the formal target matrix",
        )
    if simulate_targets != expected_sim_targets:
        add_finding(
            findings,
            code="simulate_target_order_drift",
            message="future SimulateModel order no longer matches the formal target matrix",
        )

    matrix_targets = set(target_index)
    expected_targets = set(expected_index)
    for target in sorted(matrix_targets ^ expected_targets):
        add_finding(
            findings,
            code="expected_variables_target_mismatch",
            message="target appears in only one of matrix or expected variables manifest",
            target=target,
        )

    resolutions: list[dict[str, Any]] = []

    if isinstance(parameter_name, str):
        parameter_checks = {
            "package_order_contains": last_segment(parameter_name) in parameter_order,
            "package_defines_record": f"record {last_segment(parameter_name)}" in parameter_package,
            "expected_fields_present": [],
        }
        for field in parameter_target.get("expected_fields", []):
            present = isinstance(field, str) and field in parameter_package
            parameter_checks["expected_fields_present"].append({"field": field, "present": present})
            if not present:
                add_finding(
                    findings,
                    code="parameter_field_missing",
                    message=f"parameter field {field!r} is missing",
                    target=parameter_name,
                )
        if not parameter_checks["package_order_contains"]:
            add_finding(
                findings,
                code="parameter_package_order_missing",
                message="parameter target is absent from package.order",
                target=parameter_name,
            )
        if not parameter_checks["package_defines_record"]:
            add_finding(
                findings,
                code="parameter_record_missing",
                message="parameter target record is absent from package.mo",
                target=parameter_name,
            )
        resolutions.append(
            {
                "target": parameter_name,
                "kind": "parameter_record",
                "source_file": rel(parameter_package_path),
                "static_status": "resolved"
                if not any(not item["present"] for item in parameter_checks["expected_fields_present"])
                else "failed",
                "checks": parameter_checks,
            }
        )
    else:
        add_finding(
            findings,
            code="parameter_target_missing",
            message="expected_result_variables parameter_target.formal_target is missing",
        )

    for target in check_targets:
        if target == parameter_name:
            continue
        item = target_index.get(target)
        if not item:
            add_finding(
                findings,
                code="target_missing_from_matrix",
                message="future check target is absent from formal_smoke_target_matrix",
                target=str(target),
            )
            continue

        formal_name = last_segment(item["formal_target"])
        compat_name = last_segment(item["compat_alias"])
        implementation_name = last_segment(item["implementation_model"])
        implementation_path = ROOT / item["implementation_file"]
        formal_source_path = FORMAL_DYNAMICS_DIR / f"{formal_name}.mo"
        formal_text = read_text(formal_source_path) if formal_source_path.exists() else ""

        checks = {
            "formal_package_order_contains": formal_name in formal_order,
            "formal_package_defines_model": f"model {formal_name}" in formal_text,
            "formal_source_owns_implementation": (
                implementation_path == formal_source_path
                and item["implementation_model"] == item["formal_target"]
                and implementation_name == formal_name
            ),
            "formal_source_has_no_legacy_namespace": "QuadrotorExperiments" not in formal_text,
            "formal_source_is_not_compatibility_alias": "Deprecated compatibility alias" not in formal_text,
            "compat_package_order_contains": compat_name in compat_order,
            "compat_package_defines_model": f"model {compat_name}" in compat_package,
            "compat_alias_extends_formal_implementation": (
                f"extends {item['formal_target']};" in compat_package
            ),
            "implementation_file_exists": implementation_path.is_file(),
            "implementation_defines_model": f"model {implementation_name}" in formal_text,
            "required_source_anchors": [],
            "expected_result_variables_match": (
                expected_index.get(item["formal_target"], {}).get("expected_result_variables")
                == item.get("expected_result_variables")
            ),
            "expected_result_source_matches": (
                expected_index.get(item["formal_target"], {}).get("source")
                == item.get("implementation_file")
            ),
        }

        for check_name, passed in checks.items():
            if check_name == "required_source_anchors":
                continue
            if not passed:
                add_finding(
                    findings,
                    code=check_name,
                    message=f"static resolution check failed: {check_name}",
                    target=item["formal_target"],
                )

        for snippet in item.get("required_source_anchors", []):
            present = isinstance(snippet, str) and snippet in formal_text
            checks["required_source_anchors"].append({"snippet": snippet, "present": present})
            if not present:
                add_finding(
                    findings,
                    code="required_source_anchor_missing",
                    message=f"required canonical source anchor missing: {snippet!r}",
                    target=item["formal_target"],
                )

        resolutions.append(
            {
                "target": item["formal_target"],
                "kind": "dynamics_model",
                "compat_alias": item["compat_alias"],
                "implementation_model": item["implementation_model"],
                "formal_source_file": rel(formal_source_path),
                "source_file": item["implementation_file"],
                "check_model_order": item.get("check_model_order"),
                "simulate_order_after_all_checks": item.get("simulate_order_after_all_checks"),
                "static_status": "resolved"
                if not any(
                    isinstance(value, bool) and not value
                    for key, value in checks.items()
                    if key != "required_source_anchors"
                )
                and all(anchor["present"] for anchor in checks["required_source_anchors"])
                else "failed",
                "checks": checks,
            }
        )

    for target in simulate_targets:
        item = target_index.get(target)
        if not item:
            add_finding(
                findings,
                code="simulate_target_missing_from_matrix",
                message="future SimulateModel target is absent from formal_smoke_target_matrix",
                target=str(target),
            )
            continue
        if item.get("simulate_order_after_all_checks") is None:
            add_finding(
                findings,
                code="simulate_target_not_marked_simulatable",
                message="future SimulateModel target has no simulate order in formal_smoke_target_matrix",
                target=str(target),
            )

    result = {
        "schema": "mosim.mworks.live_gate_target_resolution_check.v2",
        "request_id": REQUEST_ID,
        "input_request_id": INPUT_REQUEST_ID,
        "status": "passed_static" if not findings else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "input_artifacts": [
            rel(DEFAULT_INPUT_DIR / "formal_smoke_target_matrix.json"),
            rel(DEFAULT_INPUT_DIR / "future_live_validation_surface.json"),
            rel(DEFAULT_INPUT_DIR / "expected_result_variables.json"),
        ],
        "source_anchors": {
            "official_baseline_package": rel(BASELINE_PACKAGE),
            "canonical_root_package": rel(canonical_package_path),
            "canonical_root_order": rel(canonical_order_path),
            "formal_dynamics_package": rel(formal_package_path),
            "formal_dynamics_order": rel(formal_order_path),
            "formal_parameters_package": rel(parameter_package_path),
            "formal_parameters_order": rel(parameter_order_path),
            "legacy_compatibility_dynamics_package": rel(compat_package_path),
            "legacy_compatibility_dynamics_order": rel(compat_order_path),
        },
        "target_count": len(resolutions),
        "dynamics_target_count": len([item for item in resolutions if item["kind"] == "dynamics_model"]),
        "parameter_target_count": len([item for item in resolutions if item["kind"] == "parameter_record"]),
        "findings": findings,
        "resolutions": resolutions,
        "static_rejection_contract": [
            "Reject if the official baseline package or canonical MoSimQuadrotorModel root is missing.",
            "Reject if any target in future_live_validation_surface is absent from formal_smoke_target_matrix.",
            "Reject if expected_result_variables target lists or source paths drift from the formal target matrix.",
            "Reject if a formal Dynamics source is no longer its own canonical implementation or reintroduces a legacy namespace.",
            "Reject if a legacy DynamicsUpgrade alias no longer extends the canonical formal implementation.",
            "Reject if the future SimulateModel queue contains a non-smoke/check-only target.",
        ],
    }
    return result, findings

def build_runner_plan(
    matrix: dict[str, Any],
    future_surface: dict[str, Any],
    expected_variables: dict[str, Any],
    resolution_check: dict[str, Any],
) -> dict[str, Any]:
    target_index = index_matrix(matrix)
    expected_index = index_expected_variables(expected_variables)
    parameter_target = expected_variables.get("parameter_target", {})
    check_targets = future_surface.get("check_model_target_order", [])
    simulate_targets = future_surface.get("minimal_simulate_order_after_all_checks_pass", [])

    check_plan: list[dict[str, Any]] = []
    for order, target in enumerate(check_targets, start=1):
        if target == parameter_target.get("formal_target"):
            check_plan.append(
                {
                    "order": order,
                    "operation": "check_model",
                    "target": target,
                    "target_kind": "parameter_provenance_record",
                    "source_file": parameter_target.get("implementation_file"),
                    "expected_fields": parameter_target.get("expected_fields", []),
                    "blocker_on": [
                        "target missing or renamed",
                        "record source lacks source-labeled provenance fields",
                        "future MWORKS check_model reports authorization, translation, or structural error",
                    ],
                }
            )
            continue

        item = target_index.get(target, {})
        check_plan.append(
            {
                "order": order,
                "operation": "check_model",
                "target": target,
                "target_kind": "canonical_dynamics_implementation",
                "compat_alias": item.get("compat_alias"),
                "implementation_model": item.get("implementation_model"),
                "implementation_file": item.get("implementation_file"),
                "expected_result_variables": expected_index.get(target, {}).get("expected_result_variables", []),
                "blocker_on": [
                    "target missing or renamed",
                    "canonical implementation or compatibility alias missing",
                    "future MWORKS check_model reports authorization, translation, package, or structural error",
                ],
            }
        )

    simulate_plan: list[dict[str, Any]] = []
    for order, target in enumerate(simulate_targets, start=1):
        item = target_index.get(target, {})
        simulate_plan.append(
            {
                "order": order,
                "operation": "SimulateModel",
                "target": target,
                "only_after": "all check_model plan entries pass in this exact order",
                "implementation_file": item.get("implementation_file"),
                "expected_result_variables": expected_index.get(target, {}).get("expected_result_variables", []),
                "result_probe_required": True,
                "blocker_on": [
                    "any preceding check_model target failed",
                    "SimulateModel fails or has no native result/.msr locator",
                    "any expected result variable is missing from native result/.msr evidence",
                ],
            }
        )

    return {
        "schema": "mosim.mworks.live_gate_runner_plan.v1",
        "request_id": REQUEST_ID,
        "input_request_id": INPUT_REQUEST_ID,
        "status": "passed_static" if resolution_check["status"] == "passed_static" else "failed_static",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "runner_mode": "future_live_contract_static_only",
        "input_artifacts": {
            "formal_smoke_target_matrix": rel(DEFAULT_INPUT_DIR / "formal_smoke_target_matrix.json"),
            "future_live_validation_surface": rel(DEFAULT_INPUT_DIR / "future_live_validation_surface.json"),
            "expected_result_variables": rel(DEFAULT_INPUT_DIR / "expected_result_variables.json"),
        },
        "future_preflight_boundary": [
            "A future live task must collect its own bounded single-thread MWORKS preflight before any load, check, or simulation action.",
            "Stop before load/check/simulate on demo, login, activation, authorization, GUI error-report, mixed license, visible unknown, unavailable, or unknown state.",
            "Do not open, close, restart, maximize, screenshot, log into, or operate MWORKS from this static runner.",
        ],
        "future_load_plan": [
            {
                "order": 1,
                "operation": "model_manager.load_file",
                "file": rel(BASELINE_PACKAGE),
                "force_reload": True,
                "static_file_status": "exists" if BASELINE_PACKAGE.exists() else "missing",
                "role": "official_baseline_dependency",
            },
            {
                "order": 2,
                "operation": "model_manager.load_file",
                "file": rel(CANONICAL_ROOT / "package.mo"),
                "force_reload": True,
                "static_file_status": "exists" if (CANONICAL_ROOT / "package.mo").exists() else "missing",
                "role": "sole_project_owned_implementation_root",
            },
        ],
        "future_check_model_plan": check_plan,
        "future_simulate_model_plan": simulate_plan,
        "result_variable_probe_manifest": rel(DEFAULT_OUTPUT_DIR / "result_variable_probe_plan.json"),
        "target_resolution_manifest": rel(DEFAULT_OUTPUT_DIR / "target_resolution_check.json"),
        "stop_conditions": [
            "target resolution status is not passed_static",
            "license/login/authorization/GUI/preflight state is blocking or unknown in a future live task",
            "any check_model target fails",
            "any simulate target fails",
            "any expected result variable is absent from the future native result/.msr output",
            "a future repair would change dynamics behavior or tune parameters",
        ],
        "forbidden_future_shortcuts": [
            "Do not use check_model(reload_mo_path=...) as a reload shortcut.",
            "Do not call ClearAll or ChangeDirectory.",
            "Do not run SimulateModel before every check_model target passes.",
            "Do not treat a JSON packet, ledger, or PROGRESS entry as engineering evidence.",
        ],
        "findings": resolution_check["findings"],
    }


def build_result_probe_plan(
    matrix: dict[str, Any],
    future_surface: dict[str, Any],
    expected_variables: dict[str, Any],
) -> dict[str, Any]:
    target_index = index_matrix(matrix)
    expected_index = index_expected_variables(expected_variables)
    simulate_targets = set(future_surface.get("minimal_simulate_order_after_all_checks_pass", []))

    probes: list[dict[str, Any]] = []
    for target, item in sorted(
        target_index.items(),
        key=lambda pair: pair[1].get("check_model_order", 9999),
    ):
        expected = expected_index.get(target, {}).get("expected_result_variables", [])
        is_simulated = target in simulate_targets
        probes.append(
            {
                "target": target,
                "role": item.get("role"),
                "probe_phase": "after_simulate_model" if is_simulated else "future_observability_queue_check_only",
                "implementation_file": item.get("implementation_file"),
                "expected_result_variables": expected,
                "missing_variable_classification": "smoke_surface_blocker",
                "live_evidence_required_in_future_task": is_simulated,
                "not_claimed_by_024": True,
            }
        )

    return {
        "schema": "mosim.mworks.result_variable_probe_plan.v1",
        "request_id": REQUEST_ID,
        "status": "prepared_static_only",
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "boundary": "This manifest defines future native result/.msr probes only; 024 does not claim variables were produced by MWORKS.",
        "probe_count": len(probes),
        "simulate_probe_count": len([item for item in probes if item["probe_phase"] == "after_simulate_model"]),
        "check_only_observability_count": len(
            [item for item in probes if item["probe_phase"] == "future_observability_queue_check_only"]
        ),
        "probes": probes,
    }


def write_plan_markdown(path: Path, plan: dict[str, Any]) -> None:
    lines = [
        "# MoSimQuadrotorModel Live Gate Runner Plan",
        "",
        f"Request: `{REQUEST_ID}`",
        "",
        "Static-only contract. This artifact does not call or prove MWORKS load, `check_model`, `SimulateModel`, result variables, graphical acceptance, controller performance, runtime ack, or closed loop.",
        "",
        "## Future Load",
        "",
    ]
    for item in plan["future_load_plan"]:
        lines.append(f"- {item['order']}. `{item['operation']}` `{item['file']}` force_reload={item['force_reload']}")

    lines.extend(["", "## Future Check Model Order", ""])
    for item in plan["future_check_model_plan"]:
        lines.append(f"- {item['order']}. `{item['target']}` ({item['target_kind']})")

    lines.extend(["", "## Future Simulate Model Order", ""])
    for item in plan["future_simulate_model_plan"]:
        lines.append(
            f"- {item['order']}. `{item['target']}` after all checks pass; probe {len(item['expected_result_variables'])} variables"
        )

    lines.extend(["", "## Stop Conditions", ""])
    for item in plan["stop_conditions"]:
        lines.append(f"- {item}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_contract_markdown(path: Path, resolution_check: dict[str, Any]) -> None:
    lines = [
        "# Static Live Gate Runner Contract",
        "",
        f"Request: `{REQUEST_ID}`",
        "",
        "## Static Rejection Rules",
        "",
    ]
    for item in resolution_check["static_rejection_contract"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- 024 may claim only static live-gate runner/checker hardening.",
            "- 024 does not claim live MWORKS load, `check_model`, `SimulateModel`, native result, `.msr`, graphical/layout acceptance, controller performance, planner readiness, runtime ack, identified parameter truth, mission success, or closed loop.",
            "- Future live work must preserve the 023 target order and stop on missing or renamed targets.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_changed_files(out_dir: Path) -> dict[str, Any]:
    evidence_files = [rel(out_dir / filename) for filename in OUTPUT_FILES]
    return {
        "schema": "mosim.changed_files_manifest.v1",
        "request_id": REQUEST_ID,
        "source_files_changed_by_024": [],
        "modelica_source_files_changed": [],
        "script_files_changed_by_024": [
            "Scripts/mworks/build_mosimquad_live_gate_runner_plan.py",
            "Scripts/tests/test_mosimquad_live_gate_runner_plan.py",
        ],
        "evidence_files_written_by_024": evidence_files,
        "return_packet_expected": "Results/agent_packets/returns/PMO-MWORKS-R1-MOSIMQUAD-LIVE-GATE-RUNNER-STATIC-HARDENING-20260608-024.json",
    }


def build_summary(resolution_check: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    return {
        "schema": "mosim.mworks.static_validation_summary.v1",
        "request_id": REQUEST_ID,
        "status": "passed" if resolution_check["status"] == "passed_static" else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "input_request_id": INPUT_REQUEST_ID,
        "target_count": resolution_check["target_count"],
        "dynamics_target_count": resolution_check["dynamics_target_count"],
        "parameter_target_count": resolution_check["parameter_target_count"],
        "findings": resolution_check["findings"],
        "source_diff_required": False,
        "source_diff_performed": False,
        "evidence_files": [rel(out_dir / filename) for filename in OUTPUT_FILES],
        "claim_boundary": [
            "024 prepares a static future live-gate runner/checker contract only.",
            "024 does not call or prove MWORKS load, check_model, SimulateModel, result variables, graphical/layout acceptance, controller performance, planner_ready, runtime ack, mission success, identified parameter truth, or closed_loop.",
        ],
    }


def generate(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    matrix = read_json(input_dir / "formal_smoke_target_matrix.json")
    future_surface = read_json(input_dir / "future_live_validation_surface.json")
    expected_variables = read_json(input_dir / "expected_result_variables.json")

    resolution_check, _ = build_resolution_check(matrix, future_surface, expected_variables)
    runner_plan = build_runner_plan(matrix, future_surface, expected_variables, resolution_check)
    result_probe_plan = build_result_probe_plan(matrix, future_surface, expected_variables)
    changed_files = build_changed_files(output_dir)
    summary = build_summary(resolution_check, output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "target_resolution_check.json", resolution_check)
    write_json(output_dir / "live_gate_runner_plan.json", runner_plan)
    write_plan_markdown(output_dir / "live_gate_runner_plan.md", runner_plan)
    write_json(output_dir / "result_variable_probe_plan.json", result_probe_plan)
    write_contract_markdown(output_dir / "future_live_runner_contract.md", resolution_check)
    write_json(output_dir / "changed_files.json", changed_files)
    write_json(output_dir / "static_validation_summary.json", summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    input_dir = args.input_dir if args.input_dir.is_absolute() else ROOT / args.input_dir
    output_dir = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    summary = generate(input_dir, output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
