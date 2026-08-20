#!/usr/bin/env python3
"""Build a source-only inventory for the 48-controller refactor boundary.

The inventory deliberately separates a registered Studio FormalRunner from a
D2 canonical whole-aircraft binding.  It neither opens MWORKS nor changes a
Modelica source, route, or frozen evidence classification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "Config" / "control_platform" / "control_scheme_catalog.json"
CURRENT_MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
HARNESS_MAP_PATH = ROOT / "Config" / "control_platform" / "formal_closed_loop_harness_map.json"
STUDIO_ROUTES_PATH = ROOT / "Config" / "control_platform" / "model_studio_task_routes_v1.toml"
STUDIO_APP_PATH = ROOT / "apps" / "model_studio" / "src" / "app.jl"
TASK_WRITER_PATH = ROOT / "Scripts" / "ui" / "model_studio_task_config.py"
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "static_audits" / "controller_48_refactor_inventory_20260804"
INVENTORY_NAME = "CONTROLLER_48_REFACTOR_INVENTORY.json"
REPORT_NAME = "CONTROLLER_48_REFACTOR_REPORT.md"
SCHEMA = "mosim.controller_48_refactor_inventory.v1"
MODEL_PREFIX = "MoSimQuadrotorModel."
ADAPTER_PATTERN = re.compile(
    r"MoSimQuadrotorModel\.(?:(Control\.Adapters)|(Experiment\.Adapters))\."
    r"([A-Za-z_][A-Za-z0-9_]*)"
)
EXTENDS_PATTERN = re.compile(r"\bextends\s+(MoSimQuadrotorModel(?:\.[A-Za-z_][A-Za-z0-9_]*)+)")


class InventoryError(ValueError):
    """Raised when one of the source contracts cannot be reconciled."""


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise InventoryError(f"JSON object required: {path.relative_to(ROOT)}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def model_path_for_class(model_class: str) -> Path | None:
    if not model_class.startswith(MODEL_PREFIX):
        return None
    suffix = model_class.removeprefix(MODEL_PREFIX).replace(".", "/")
    return ROOT / "Models" / "MoSimQuadrotorModel" / f"{suffix}.mo"


def declared_model_class(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    within = re.search(r"(?m)^\s*within\s+([^;]+);", text)
    model = re.search(r"(?m)^\s*model\s+([A-Za-z_][A-Za-z0-9_]*)\b", text)
    if within is None or model is None:
        return None
    return f"{within.group(1).strip()}.{model.group(1)}"


def parent_model_files(path: Path, limit: int = 12) -> list[Path]:
    """Return a bounded leaf-to-base chain for source-level plant checks."""
    chain: list[Path] = []
    seen: set[Path] = set()
    current = path
    while current not in seen and len(chain) < limit:
        if not current.is_file():
            break
        seen.add(current)
        chain.append(current)
        text = current.read_text(encoding="utf-8")
        parent = EXTENDS_PATTERN.search(text)
        if parent is None:
            break
        parent_path = model_path_for_class(parent.group(1))
        if parent_path is None or not parent_path.is_file():
            break
        current = parent_path
    return chain


def expected_partial_interface(boundary: str) -> str:
    interfaces = {
        "ATTITUDE_THRUST": "PartialAttitudeThrustController",
        "BODY_RATE_THRUST": "PartialBodyRateThrustController",
        "ROTOR_COMMAND": "PartialRotorCommandController",
        "WRENCH": "PartialWrenchController",
    }
    try:
        return interfaces[boundary]
    except KeyError as exc:
        raise InventoryError(f"unsupported Studio boundary: {boundary}") from exc


def adapter_core_references(adapter_text: str) -> list[str]:
    matches = re.findall(
        r"MoSimQuadrotorModel\.(?:Control\.(?:Implementations|Bridges)|Vehicle\.Blocks)"
        r"(?:\.[A-Za-z_][A-Za-z0-9_]*)+",
        adapter_text,
    )
    return sorted(set(matches))


def build_inventory() -> dict[str, Any]:
    catalog = read_json(CATALOG_PATH)
    current_map = read_json(CURRENT_MAP_PATH)
    harness_map = read_json(HARNESS_MAP_PATH)
    with STUDIO_ROUTES_PATH.open("rb") as handle:
        routes_document = tomllib.load(handle)

    if catalog.get("schema") != "mosim.control_profile_catalog.v2":
        raise InventoryError("control scheme catalog schema is invalid")
    if current_map.get("schema") != "mosim.current_model_entry_map.v1":
        raise InventoryError("current model entry map schema is invalid")
    if harness_map.get("schema") != "mosim.formal_closed_loop_harness_map.v2":
        raise InventoryError("formal harness map schema is invalid")
    if routes_document.get("schema") != "mosim.model_studio_task_routes.v1":
        raise InventoryError("Model Studio route schema is invalid")

    catalog_rows = catalog.get("schemes")
    current_rows = current_map.get("schemes")
    harness_rows = harness_map.get("schemes")
    route_rows = routes_document.get("route")
    if not all(isinstance(rows, list) for rows in (catalog_rows, current_rows, harness_rows, route_rows)):
        raise InventoryError("all source contracts must contain list rows")

    catalog_by_id = {str(row.get("scheme_id")): row for row in catalog_rows if isinstance(row, dict)}
    current_by_id = {str(row.get("scheme_id")): row for row in current_rows if isinstance(row, dict)}
    harness_by_id = {str(row.get("scheme_id")): row for row in harness_rows if isinstance(row, dict)}
    routes_by_id = {str(row.get("controller_id")): row for row in route_rows if isinstance(row, dict)}
    active_ids = set(catalog_by_id)
    if len(active_ids) != 48 or not active_ids:
        raise InventoryError("catalog must contain exactly 48 unique controller IDs")
    if set(current_by_id) != active_ids or set(harness_by_id) != active_ids or set(routes_by_id) != active_ids:
        raise InventoryError("catalog, map, harness, and Studio routes must cover the same 48 IDs")

    rows: list[dict[str, Any]] = []
    for scheme_id in sorted(active_ids):
        catalog_row = catalog_by_id[scheme_id]
        current_row = current_by_id[scheme_id]
        harness_row = harness_by_id[scheme_id]
        route = routes_by_id[scheme_id]
        available = route.get("available")
        runner_file_text = route.get("runner_file")
        runner_class = route.get("runner_class")
        boundary = route.get("boundary")
        if not isinstance(available, bool) or not isinstance(runner_file_text, str) or not isinstance(runner_class, str):
            raise InventoryError(f"{scheme_id}: Studio route is incomplete")
        if not isinstance(boundary, str):
            raise InventoryError(f"{scheme_id}: Studio route boundary is missing")

        runner_file = ROOT / runner_file_text
        runner_exists = runner_file.is_file()
        runner_declared_class = declared_model_class(runner_file) if runner_exists else None
        runner_chain = parent_model_files(runner_file) if runner_exists else []
        runner_chain_text = "\n".join(path.read_text(encoding="utf-8") for path in runner_chain)
        adapter_match = ADAPTER_PATTERN.search(runner_file.read_text(encoding="utf-8")) if runner_exists else None
        adapter_namespace = (
            adapter_match.group(1) or adapter_match.group(2)
            if adapter_match
            else None
        )
        adapter_class = adapter_match.group(3) if adapter_match else None
        adapter_file = None
        if adapter_class:
            adapter_candidates = [
                ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Adapters" / f"{adapter_class}.mo",
                ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Adapters" / f"{adapter_class}.mo",
            ]
            adapter_file = next((path for path in adapter_candidates if path.is_file()), None)
        adapter_exists = adapter_file is not None and adapter_file.is_file()
        adapter_text = adapter_file.read_text(encoding="utf-8") if adapter_exists and adapter_file else ""
        partial_interface = expected_partial_interface(boundary)
        core_file_text = current_row.get("current_model_file")
        core_class = current_row.get("current_model_class")
        core_file = ROOT / str(core_file_text) if isinstance(core_file_text, str) and core_file_text else None
        core_file_exists = core_file is not None and core_file.is_file()
        canonical = harness_row.get("canonical_closed_loop_harness")
        formal_adapter = harness_row.get("formal_adapter")
        embedded_adapter = (
            isinstance(formal_adapter, dict)
            and formal_adapter.get("kind") == "embedded_sysblock_and_physical_plant"
        )
        canonical_public_file = canonical.get("public_entry_file") if isinstance(canonical, dict) else None
        canonical_source_file = canonical.get("whole_aircraft_source_file") if isinstance(canonical, dict) else None
        canonical_paths_exist = all(
            isinstance(path, str) and (ROOT / path).is_file()
            for path in (canonical_public_file, canonical_source_file)
        ) if isinstance(canonical, dict) else False
        prerequisites = harness_row.get("model_load_prerequisites")
        embedded_sysblock_exists = any(
            isinstance(item, dict)
            and item.get("role") == "embedded_sysblock_definition"
            and isinstance(item.get("model_file"), str)
            and (ROOT / item["model_file"]).is_file()
            for item in prerequisites or []
        )
        shared_sunray_plant = "MoSimQuadrotorModel.Vehicle.Sunray150Assembly" in runner_chain_text
        whole_aircraft_shell_state = (
            "shared_sunray150assembly_source_chain"
            if shared_sunray_plant
            else "d2_canonical_embedded_whole_aircraft_profile"
            if canonical_paths_exist and embedded_adapter
            else "not_proven_by_static_runner_chain"
        )
        referenced_sysblock = any(
            ".Control.Implementations.Sysblocks." in reference
            for reference in adapter_core_references(adapter_text)
        )
        if current_row.get("current_model_role") == "graphical_controller_core" and core_file_exists:
            core_surface_state = "current_graphical_sysblock_core"
        elif current_row.get("current_model_role") == "full_profile_whole_aircraft_closed_loop" and embedded_sysblock_exists:
            core_surface_state = "embedded_profile_sysblock_core"
        elif current_row.get("mapping_state") == "planned_profile_no_model" and referenced_sysblock:
            core_surface_state = "source_materialized_outside_frozen_current_map"
        elif current_row.get("entry_type") == "engineering_deployment_baseline":
            core_surface_state = "mworks_equivalent_core_pending"
        else:
            core_surface_state = "core_surface_not_proven"
        rows.append(
            {
                "scheme_id": scheme_id,
                "category": catalog_row.get("category"),
                "entry_type": catalog_row.get("entry_type"),
                "frozen_current_model": {
                    "mapping_state": current_row.get("mapping_state"),
                    "role": current_row.get("current_model_role"),
                    "file": core_file_text,
                    "class": core_class,
                    "file_exists": core_file_exists,
                    "surface_state": core_surface_state,
                },
                "studio_route": {
                    "available": available,
                    "boundary": boundary,
                    "runner_file": runner_file_text,
                    "runner_class": runner_class,
                    "runner_file_exists": runner_exists,
                    "runner_declared_class_matches": runner_declared_class == runner_class,
                    "shared_sunray150assembly_source_chain_present": shared_sunray_plant,
                    "whole_aircraft_shell_static_state": whole_aircraft_shell_state,
                    "source_chain": [repo_path(path) for path in runner_chain],
                },
                "adapter_route": {
                    "class": f"MoSimQuadrotorModel.{adapter_namespace}.{adapter_class}" if adapter_class else None,
                    "file": repo_path(adapter_file) if adapter_file else None,
                    "file_exists": adapter_exists,
                    "typed_partial_interface": partial_interface if partial_interface in adapter_text else None,
                    "binding_mode": "explicit_typed_adapter" if adapter_exists else "embedded_sysblock_and_physical_plant" if embedded_adapter else "not_found",
                    "static_binding_present": adapter_exists or embedded_adapter,
                    "references_frozen_current_core": bool(core_class and core_class in adapter_text),
                    "referenced_project_cores_or_bridges": adapter_core_references(adapter_text),
                },
                "formal_closure": {
                    "state": harness_row.get("formal_harness_state"),
                    "tier": harness_row.get("whole_aircraft_tier"),
                    "minimum_whole_aircraft_closure_eligible": harness_row.get("minimum_whole_aircraft_closure_eligible"),
                    "canonical_harness_files_exist": canonical_paths_exist,
                    "canonical_public_entry_file": canonical_public_file,
                    "canonical_source_file": canonical_source_file,
                },
            }
        )

    studio_app_text = STUDIO_APP_PATH.read_text(encoding="utf-8")
    task_writer_text = TASK_WRITER_PATH.read_text(encoding="utf-8")
    summary = {
        "active_catalog_count": len(rows),
        "mworks_profile_count": sum(row["entry_type"] == "mworks_control_profile" for row in rows),
        "engineering_baseline_count": sum(row["entry_type"] == "engineering_deployment_baseline" for row in rows),
        "frozen_current_model_state_counts": dict(sorted(Counter(str(row["frozen_current_model"]["mapping_state"]) for row in rows).items())),
        "frozen_current_model_file_exists_count": sum(bool(row["frozen_current_model"]["file_exists"]) for row in rows),
        "sysblock_or_core_surface_state_counts": dict(sorted(Counter(str(row["frozen_current_model"]["surface_state"]) for row in rows).items())),
        "studio_available_count": sum(bool(row["studio_route"]["available"]) for row in rows),
        "studio_runner_file_exists_count": sum(bool(row["studio_route"]["runner_file_exists"]) for row in rows),
        "studio_runner_declared_class_matches_count": sum(bool(row["studio_route"]["runner_declared_class_matches"]) for row in rows),
        "studio_runner_shared_sunray150assembly_source_chain_count": sum(bool(row["studio_route"]["shared_sunray150assembly_source_chain_present"]) for row in rows),
        "studio_runner_or_d2_whole_aircraft_shell_count": sum(
            row["studio_route"]["whole_aircraft_shell_static_state"] != "not_proven_by_static_runner_chain" for row in rows
        ),
        "route_explicit_adapter_file_exists_count": sum(bool(row["adapter_route"]["file_exists"]) for row in rows),
        "route_explicit_adapter_typed_interface_count": sum(row["adapter_route"]["typed_partial_interface"] is not None for row in rows),
        "route_adapter_or_embedded_binding_count": sum(bool(row["adapter_route"]["static_binding_present"]) for row in rows),
        "d2_formal_closure_state_counts": dict(sorted(Counter(str(row["formal_closure"]["state"]) for row in rows).items())),
        "d2_canonical_whole_aircraft_harness_count": sum(
            row["formal_closure"]["state"] == "resolved_canonical_whole_aircraft_harness" for row in rows
        ),
        "d2_canonical_harness_files_exist_count": sum(bool(row["formal_closure"]["canonical_harness_files_exist"]) for row in rows),
        "studio_app_reads_authoritative_toml": "MODEL_TASK_ROUTE_CATALOG" in studio_app_text and "load_model_task_routes" in studio_app_text,
        "task_writer_reads_authoritative_toml": "TASK_ROUTE_PATH" in task_writer_text and "load_manual_formal_routes" in task_writer_text,
    }
    return {
        "schema": SCHEMA,
        "scope": "Static inventory only. A Studio route or source path is not MWORKS CheckModel, simulation, performance, code generation, or runtime acceptance evidence.",
        "source_files": {
            "control_scheme_catalog": repo_path(CATALOG_PATH),
            "current_model_entry_map": repo_path(CURRENT_MAP_PATH),
            "formal_closed_loop_harness_map": repo_path(HARNESS_MAP_PATH),
            "model_studio_task_routes": repo_path(STUDIO_ROUTES_PATH),
            "model_studio_app": repo_path(STUDIO_APP_PATH),
            "model_studio_task_writer": repo_path(TASK_WRITER_PATH),
        },
        "source_sha256": {
            "control_scheme_catalog": sha256_file(CATALOG_PATH),
            "current_model_entry_map": sha256_file(CURRENT_MAP_PATH),
            "formal_closed_loop_harness_map": sha256_file(HARNESS_MAP_PATH),
            "model_studio_task_routes": sha256_file(STUDIO_ROUTES_PATH),
            "model_studio_app": sha256_file(STUDIO_APP_PATH),
            "model_studio_task_writer": sha256_file(TASK_WRITER_PATH),
        },
        "summary": summary,
        "refactor_architecture": {
            "canonical_model_root": "Models/MoSimQuadrotorModel/package.mo",
            "layers": [
                "Control/Implementations: preserve graphical controller cores as the topology authority.",
                "Control/Adapters and Control/Bridges: one typed output boundary per controller; bridge use requires an explicit current-source equivalence record.",
                "Experiment/Runners/Base: retain the shared Sunray150Assembly and four boundary families as the plant closure authority.",
                "Experiment/Runners/Formal: retain leaf runners as selectable shells; do not promote their existence to semantic core binding.",
                "Experiment/Templates/IntegratedChains and Templates/Official: preserve the five named whole-aircraft profile pairs until each dependency and hash is migrated.",
                "Config/control_platform: keep catalog, current-map, D2 harness map, and Studio routes as distinct metadata roles.",
                "Results: evidence only; never use a historic Results model copy as a replacement implementation source.",
            ],
            "minimum_next_artifact": "A deterministic 48-row binding manifest that names the core, typed adapter or embedded binding, leaf runner, D2 canonical harness state, source hashes, and claim boundary. Update D2 only after per-route equivalence or dependency review.",
        },
        "prohibited_directory_operations": [
            "Do not create a second Modelica package root or move/delete Models/MoSimQuadrotorModel/package.mo or package.order files as part of this refactor.",
            "Do not bulk-move, flatten, or delete Control/Implementations, Control/Adapters, Control/Bridges, Experiment/Runners, or their package.order files before every affected fully-qualified reference and route is rewritten and checked.",
            "Do not move or delete the five IntegratedChains public aliases or their Templates/Official whole-aircraft sources before a route-specific dependency and hash migration record exists.",
            "Do not treat Results/ model copies, screenshots, or historical manifests as current implementation sources, and do not delete evidence roots to make the workspace look clean.",
            "Do not rewrite generated src/control/codegen/px4ctrl output or runtime adapter sources in a generic 48-route refactor; keep px4ctrl equivalence as a separately gated workstream.",
            "Do not use git reset, git clean, broad staging, or bulk directory moves in this shared worktree.",
        ],
        "estimated_work_scope": {
            "structural_baseline": "3-5 engineer-days: create and check the 48-row binding manifest, reconcile route/test drift, and freeze source hashes without moving Modelica files.",
            "graphical_core_promotions": "41 routes, roughly 0.5-1.5 engineer-days each for public I/O review, typed adapter/equivalence decision, D2 binding, and bounded CheckModel evidence: 21-62 engineer-days.",
            "named_whole_aircraft_profiles": "5 routes, roughly 0.5-1.5 engineer-days each for dependency/hash audits and alias preservation: 3-8 engineer-days.",
            "exception_workstreams": "pid_awff_linear_eso: 1-3 engineer-days to reconcile its frozen map with source and retain negative evidence; px4ctrl: 5-10 engineer-days for a separately reviewed MWORKS-equivalence gate, excluding runtime deployment work.",
            "interactive_validation": "If formal MWORKS acceptance is included, add 12-24 engineer-days for bounded CheckModel/result review across the routes that are actually promoted; license, GUI, and solver blockers are not included in the estimate.",
        },
        "routes": rows,
    }


def markdown_report(inventory: dict[str, Any]) -> str:
    summary = inventory["summary"]
    lines = [
        "# 48 条控制器重构盘点",
        "",
        "## 结论",
        "",
        f"- 活动目录：{summary['active_catalog_count']} 条（{summary['mworks_profile_count']} 个 MWORKS Profile，{summary['engineering_baseline_count']} 条工程基线）。",
        f"- Sysblock 核：41 条 `current_graphical_sysblock_core` + 5 条 `embedded_profile_sysblock_core` = 46 条已映射现状；另有 1 条 `source_materialized_outside_frozen_current_map`（`pid_awff_linear_eso`）和 1 条 `mworks_equivalent_core_pending`（`px4ctrl`）。冻结 current-model 文件存在数为 {summary['frozen_current_model_file_exists_count']}/48，状态分布为 `{summary['frozen_current_model_state_counts']}`。",
        f"- Studio 手动路由：{summary['studio_available_count']}/48 `available=true`，Runner 文件、类声明和“共享 Sunray150Assembly 或 D2 嵌入式整机 Profile”壳为 {summary['studio_runner_file_exists_count']}/48、{summary['studio_runner_declared_class_matches_count']}/48、{summary['studio_runner_or_d2_whole_aircraft_shell_count']}/48；其中显式共享 Sunray150Assembly 继承链为 {summary['studio_runner_shared_sunray150assembly_source_chain_count']}/48。",
        f"- Adapter：{summary['route_explicit_adapter_file_exists_count']}/48 为可解析的显式 Adapter 文件且具类型接口，另 1 条为 D2 的嵌入式 Sysblock + 物理 Plant 绑定；静态绑定总数为 {summary['route_adapter_or_embedded_binding_count']}/48。它只证明路由壳存在，不证明与冻结图形核的行为等价。",
        f"- D2 语义整机闭环：只有 {summary['d2_canonical_whole_aircraft_harness_count']}/48 处于 `resolved_canonical_whole_aircraft_harness`，且其公开入口/整机源文件均存在。D2 分布为 `{summary['d2_formal_closure_state_counts']}`。",
        "- App：当前 Studio App 与任务配置写入器都读取 `model_studio_task_routes_v1.toml`；历史 `mworks_app_entrypoints.json` 不应作为当前路由权威源。",
        "",
        "## 最小风险架构",
        "",
        "`Control/Implementations` 保持图形核权威，`Control/Adapters` 与 `Control/Bridges` 只承载类型边界和经过审查的等效桥，`Experiment/Runners/Base` 保持共享 Sunray150Assembly 植物，`Experiment/Runners/Formal` 保持可选择测试壳。五条 IntegratedChains 及其 Official 源对在逐条依赖/哈希审计前不得拆解。新增的 48 行 binding manifest 应成为重构推进表：每行同时记录核、Adapter/embedded binding、Runner、D2 壳、哈希和证据上限；未通过等效审查的路由仍保留为“可打开”，而不是“已形成语义闭环”。",
        "",
        "## 禁止操作",
        "",
    ]
    lines.extend(f"- {item}" for item in inventory["prohibited_directory_operations"])
    lines.extend(["", "## 工作量范围", ""])
    for label, value in inventory["estimated_work_scope"].items():
        lines.append(f"- `{label}`: {value}")
    lines.extend(["", "## 逐条静态矩阵", "", "| ID | 当前核 | Adapter | Studio Runner | D2 整机壳 |", "|---|---|---|---|---|"])
    for row in inventory["routes"]:
        core = row["frozen_current_model"]
        adapter = row["adapter_route"]
        route = row["studio_route"]
        closure = row["formal_closure"]
        core_text = f"{core['surface_state']} / {core['mapping_state']} / {'exists' if core['file_exists'] else 'no file'}"
        adapter_text = f"{adapter['binding_mode']} / {adapter['typed_partial_interface'] or 'embedded'}"
        runner_text = f"{'exists' if route['runner_file_exists'] else 'missing'} / {route['whole_aircraft_shell_static_state']}"
        d2_text = f"{closure['state']} / {'files exist' if closure['canonical_harness_files_exist'] else 'not canonical'}"
        lines.append(f"| `{row['scheme_id']}` | {core_text} | {adapter_text} | {runner_text} | {d2_text} |")
    lines.extend([
        "",
        "## 证据边界",
        "",
        "本报告只检查当前源路径、类型声明、继承链与配置覆盖关系。它不构成 MWORKS CheckModel、图审、仿真、性能、代码生成、ROS/PX4/Gazebo 或飞行验收。",
        "",
    ])
    return "\n".join(lines)


def write_outputs(inventory: dict[str, Any], output_root: Path) -> tuple[Path, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / INVENTORY_NAME
    report_path = output_root / REPORT_NAME
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(markdown_report(inventory), encoding="utf-8", newline="\n")
    return json_path, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--check", action="store_true", help="fail when generated output differs from current source facts")
    args = parser.parse_args()
    output_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    inventory = build_inventory()
    expected_json = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    expected_report = markdown_report(inventory)
    json_path = output_root / INVENTORY_NAME
    report_path = output_root / REPORT_NAME
    if args.check:
        if not json_path.is_file() or not report_path.is_file():
            print("inventory output is missing")
            return 1
        if json_path.read_text(encoding="utf-8") != expected_json or report_path.read_text(encoding="utf-8") != expected_report:
            print("inventory output is stale")
            return 1
        print(f"PASS {repo_path(json_path)}")
        return 0
    json_path, report_path = write_outputs(inventory, output_root)
    print(f"WROTE {repo_path(json_path)}")
    print(f"WROTE {repo_path(report_path)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InventoryError as exc:
        print(f"ERROR {exc}")
        raise SystemExit(2)
