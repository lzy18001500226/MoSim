#!/usr/bin/env python3
"""Build an evidence-bounded 48-controller mapping table from current authorities."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATIC_INVENTORY_BUILDER = ROOT / "Scripts" / "quality" / "build_controller_48_refactor_inventory.py"
GOLDEN_MANIFEST = (
    ROOT
    / "Results"
    / "model_library_refactor"
    / "20260810_official_pid_golden_freeze"
    / "GOLDEN_FREEZE_MANIFEST.json"
)
G6_SUPERSESSION_MANIFEST = (
    ROOT
    / "Results"
    / "model_library_refactor"
    / "controller_route_execution_current"
    / "G6_SOURCE_MIGRATION_SUPERSESSION_MANIFEST.json"
)
DEFAULT_SCAN_ARTIFACT = (
    ROOT
    / "Results"
    / "mworks_graphics"
    / "sysblocks_graphical_scan_20260811"
    / "SYSBLOCKS_AND_GRAPHICAL_SCAN_EXPLICIT_ROOTS.json"
)
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "model_library_refactor" / "20260811_a_to_c_cleanup"
JSON_NAME = "CONTROLLER_48_EVIDENCE_MAPPING.json"
MARKDOWN_NAME = "CONTROLLER_48_EVIDENCE_MAPPING.md"
SCHEMA = "mosim.controller_48_evidence_mapping.v1"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_static_inventory() -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("controller_48_inventory", STATIC_INVENTORY_BUILDER)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load static inventory builder: {STATIC_INVENTORY_BUILDER}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    inventory = module.build_inventory()
    if inventory.get("summary", {}).get("active_catalog_count") != 48:
        raise ValueError("static inventory did not return exactly 48 active controllers")
    return inventory


def golden_evidence() -> dict[str, Any]:
    manifest = read_json(GOLDEN_MANIFEST)
    evidence: dict[str, Any] = {
        "manifest": repo_path(GOLDEN_MANIFEST),
        "manifest_sha256": sha256_file(GOLDEN_MANIFEST),
        "verified_native_result": False,
    }
    native = manifest.get("native_result")
    checks = manifest.get("mworks_checks")
    if not isinstance(native, dict) or not isinstance(checks, dict):
        evidence["unavailable_reason"] = "Golden manifest has no native result or MWORKS checks"
        return evidence
    native_path_text = native.get("path")
    if not isinstance(native_path_text, str):
        evidence["unavailable_reason"] = "Golden manifest native result path is invalid"
        return evidence
    native_path = ROOT / native_path_text
    evidence.update(
        {
            "declared_result": native_path_text,
            "declared_result_sha256": native.get("sha256"),
            "declared_result_bytes": native.get("bytes"),
            "timestamp": manifest.get("created_at"),
        }
    )
    if not (
        manifest.get("status") == "frozen"
        and manifest.get("source") == "MWORKS_MCP"
        and checks.get("check_model") is True
        and checks.get("simulate_model") is True
        and checks.get("open_result") is True
        and checks.get("get_var_times") is True
    ):
        evidence["unavailable_reason"] = "Golden manifest does not prove the required MWORKS result checks"
        return evidence
    if not native_path.is_file():
        evidence["unavailable_reason"] = f"Golden native result is missing: {repo_path(native_path)}"
        return evidence
    actual_sha256 = sha256_file(native_path)
    if native.get("sha256") != actual_sha256:
        evidence["unavailable_reason"] = "Golden native result SHA-256 no longer matches its manifest"
        evidence["actual_result_sha256"] = actual_sha256
        return evidence

    runner_path = ROOT / "Models" / "MoSimQuadrotorModel" / "Experiment" / "Runners" / "Golden" / "OfficialPidSingleUavGoldenRunner.mo"
    if not runner_path.is_file():
        evidence["unavailable_reason"] = f"Golden runner source is missing: {repo_path(runner_path)}"
        return evidence
    runner_text = runner_path.read_text(encoding="utf-8")
    core = re.search(
        r"(MoSimQuadrotorModel\.Control\.Implementations\.Graphical\.PID\.OfficialPidSysblockCore)\s+core\b",
        runner_text,
    )
    mapper = re.search(
        r"(MoSimQuadrotorModel\.Control\.Implementations\.Graphical\.PID\.OfficialPidSysblockMapper)\s+mapper\b",
        runner_text,
    )
    diagnostics = re.search(
        r"(MoSimQuadrotorModel\.Control\.Adapters\.OfficialPidSysblockMapperDiagnostics)\s+mapper_diagnostics\b",
        runner_text,
    )
    if core is None or mapper is None or diagnostics is None:
        evidence["unavailable_reason"] = "Golden runner no longer exposes the expected PID core and mapper chain"
        return evidence
    evidence.update(
        {
        "verified_native_result": True,
        "runner": "MoSimQuadrotorModel.Experiment.Baselines.OfficialPidRunner",
        "runner_file": repo_path(runner_path),
        "core_fqn": core.group(1),
        "mapper_fqn": mapper.group(1),
        "diagnostics_adapter_fqn": diagnostics.group(1),
        "result": repo_path(native_path),
        "result_sha256": actual_sha256,
        "result_bytes": native_path.stat().st_size,
        }
    )
    return evidence


def scan_summary(scan_artifact: Path) -> dict[str, Any]:
    scan = read_json(scan_artifact)
    audits = scan.get("metadata_audits")
    if not isinstance(audits, list) or len(audits) != 2:
        raise ValueError("broadened graphics scan must contain exactly Sysblocks and Graphical audits")
    summaries = []
    for audit in audits:
        if not isinstance(audit, dict):
            raise ValueError("invalid graphics scan audit")
        scope = str(audit.get("scope", ""))
        if not (scope.endswith("/Sysblocks") or scope.endswith("/Graphical")):
            raise ValueError(f"unexpected graphics scan root: {scope}")
        summaries.append(
            {
                "scope": scope,
                "scanned_file_count": audit["scanned_file_count"],
                "scanned_model_declaration_count": audit["scanned_model_declaration_count"],
                "sysblock_class_count": audit["sysblock_class_count"],
                "passed_sysblock_class_count": audit["passed_sysblock_class_count"],
                "failed_sysblock_class_count": audit["failed_sysblock_class_count"],
                "failed_sysblock_classes": audit["failed_sysblock_classes"],
            }
        )
    if {item["scope"].rsplit("/", maxsplit=1)[-1] for item in summaries} != {"Sysblocks", "Graphical"}:
        raise ValueError("broadened graphics scan did not cover both required roots")
    return {
        "path": repo_path(scan_artifact),
        "sha256": sha256_file(scan_artifact),
        "overall_ok": scan.get("ok"),
        "roots": summaries,
    }


def supersession_evidence() -> dict[str, Any]:
    manifest = read_json(G6_SUPERSESSION_MANIFEST)
    rule = manifest.get("refreshed_status_rule")
    if not isinstance(rule, str) or "all-pending" not in rule or "never reused" not in rule:
        raise ValueError("G6 supersession record does not establish the current-evidence boundary")
    return {
        "path": repo_path(G6_SUPERSESSION_MANIFEST),
        "sha256": sha256_file(G6_SUPERSESSION_MANIFEST),
        "rule": rule,
        "claim_boundary": manifest.get("claim_boundary"),
    }


def pending_evidence_reason(
    scheme_id: str,
    row: dict[str, Any],
    golden: dict[str, Any],
) -> str:
    if scheme_id == "official_pid":
        reason = golden.get("unavailable_reason", "Golden native result is not verifiable")
        return f"待测：{reason}；不将 Golden manifest 升格为当前执行证据。"
    if scheme_id == "pid_awff_linear_eso":
        return "待测：批准拓扑尚未物化，缺 MWORKS 图形核、Adapter、FormalRunner 与 check_model/Result.msr。"
    if scheme_id == "px4ctrl":
        return "待测：缺 MWORKS 等价图形核、Adapter/Bridge、FormalRunner 及行为等价检查。"
    runner = row["studio_route"]["runner_class"]
    return f"待测：缺当前源绑定的 `check_model` 通过时间戳或该入口的 `Result.msr`；旧 46 路记录已被迁移清单标为不可复用。正式入口：`{runner}`。"


def build_mapping(scan_artifact: Path) -> dict[str, Any]:
    inventory = load_static_inventory()
    catalog = read_json(ROOT / "Config" / "control_platform" / "control_scheme_catalog.json")
    display_name_by_id = {
        item["scheme_id"]: item["display_name_zh"]
        for item in catalog.get("schemes", [])
        if isinstance(item, dict)
        and isinstance(item.get("scheme_id"), str)
        and isinstance(item.get("display_name_zh"), str)
    }
    golden = golden_evidence()
    scan = scan_summary(scan_artifact)
    supersession = supersession_evidence()
    rows = []
    for static_row in inventory["routes"]:
        scheme_id = static_row["scheme_id"]
        if scheme_id not in display_name_by_id:
            raise ValueError(f"catalog display name missing for {scheme_id}")
        frozen = static_row["frozen_current_model"]
        route = static_row["studio_route"]
        adapter = static_row["adapter_route"]
        core_fqn = frozen["class"] if frozen["file_exists"] and frozen["class"] else "未物化"
        if adapter["file_exists"] and adapter["class"]:
            adapter_or_bridge = adapter["class"]
        elif adapter["binding_mode"] == "embedded_sysblock_and_physical_plant":
            adapter_or_bridge = "嵌入式 Sysblock + 物理 Plant"
        elif adapter["class"]:
            adapter_or_bridge = f"未物化（配置引用：{adapter['class']}）"
        else:
            adapter_or_bridge = "未物化"
        if route["runner_file_exists"] and route["runner_declared_class_matches"]:
            formal_entry = route["runner_class"]
        else:
            formal_entry = f"未物化（配置引用：{route['runner_class']}）"
        evidence_status = "pending_current_evidence"
        evidence = pending_evidence_reason(scheme_id, static_row, golden)
        details: dict[str, Any] = {
            "static_current_core_fqn": frozen["class"],
            "static_adapter_or_binding": adapter["class"] or adapter["binding_mode"],
            "static_formal_entry": route["runner_class"],
        }
        if scheme_id == "official_pid" and golden["verified_native_result"]:
            core_fqn = golden["core_fqn"]
            adapter_or_bridge = f"{golden['mapper_fqn']}; {golden['diagnostics_adapter_fqn']}"
            formal_entry = golden["runner"]
            evidence_status = "verified_native_result"
            evidence = f"MWORKS_MCP Result.msr：`{golden['result']}`；时间戳 {golden['timestamp']}。"
            details["golden_runner_core_fqn"] = golden["core_fqn"]
            details["static_current_core_equivalence"] = "not_claimed"
            details["golden_manifest"] = golden["manifest"]
        elif scheme_id == "official_pid":
            details["golden_manifest"] = golden["manifest"]
            details["golden_native_result_verification"] = "unavailable"
            details["golden_unavailable_reason"] = golden["unavailable_reason"]
        rows.append(
            {
                "scheme_id": scheme_id,
                "controller_name": display_name_by_id[scheme_id],
                "sysblock_class_fqn": core_fqn,
                "adapter_or_bridge": adapter_or_bridge,
                "formal_entry": formal_entry,
                "evidence_status": evidence_status,
                "evidence": evidence,
                "details": details,
            }
        )
    if len(rows) != 48 or len({row["scheme_id"] for row in rows}) != 48:
        raise ValueError("mapping must contain exactly 48 unique controller rows")
    evidence_counts = dict(sorted(Counter(row["evidence_status"] for row in rows).items()))
    return {
        "schema": SCHEMA,
        "claim_boundary": "This table maps the current static route authorities. Only a current MWORKS check timestamp or native Result.msr is treated as execution evidence; static paths, screenshots, and superseded records are not promoted to execution acceptance.",
        "sources": {
            "static_inventory_builder": repo_path(STATIC_INVENTORY_BUILDER),
            "static_inventory_builder_sha256": sha256_file(STATIC_INVENTORY_BUILDER),
            "static_inventory_source_hashes": inventory["source_sha256"],
            "broadened_graphics_scan": scan,
            "historical_g6_supersession": supersession,
            "official_pid_golden": golden,
        },
        "summary": {
            "controller_count": len(rows),
            "evidence_status_counts": evidence_counts,
            "broadened_scan_overall_ok": scan["overall_ok"],
        },
        "rows": rows,
    }


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", "<br>")


def markdown_report(mapping: dict[str, Any]) -> str:
    summary = mapping["summary"]
    scan = mapping["sources"]["broadened_graphics_scan"]
    supersession = mapping["sources"]["historical_g6_supersession"]
    golden = mapping["sources"]["official_pid_golden"]
    lines = [
        "# 48 条控制器可核验映射表",
        "",
        "## 证据边界",
        "",
        mapping["claim_boundary"],
        "",
        f"- 行数：{summary['controller_count']}；证据状态：`{summary['evidence_status_counts']}`。",
        f"- 宽扫描：`{scan['path']}`，总体 `ok={scan['overall_ok']}`。",
        f"- 历史 G6 记录：`{supersession['path']}` 明确规定 `{supersession['rule']}`。",
        "",
        "## 映射表",
        "",
        "| 控制器名 | Sysblock 类 FQN | Adapter/Bridge | 正式入口 | 证据 |",
        "|---|---|---|---|---|",
    ]
    if golden["verified_native_result"]:
        lines.insert(
            10,
            "- 官方 PID 的实际 Golden 入口使用 `Graphical.PID.OfficialPidSysblockCore`；冻结静态目录映射中的 `PidFamily.AWFF_PID_Sysblock_Demo` 与其未在本表中声明等价。",
        )
    else:
        lines.insert(
            10,
            f"- 官方 PID Golden 工件不可验证：{golden['unavailable_reason']}。本表不声明其为已验证原生结果。",
        )
    for row in mapping["rows"]:
        lines.append(
            "| "
            + " | ".join(
                markdown_cell(str(row[column]))
                for column in (
                    "controller_name",
                    "sysblock_class_fqn",
                    "adapter_or_bridge",
                    "formal_entry",
                    "evidence",
                )
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def write_outputs(mapping: dict[str, Any], output_root: Path) -> tuple[Path, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / JSON_NAME
    markdown_path = output_root / MARKDOWN_NAME
    json_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_path.write_text(markdown_report(mapping), encoding="utf-8", newline="\n")
    return json_path, markdown_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--scan-artifact", type=Path, default=DEFAULT_SCAN_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="fail when outputs differ from current source evidence")
    args = parser.parse_args()
    output_root = args.output_root if args.output_root.is_absolute() else ROOT / args.output_root
    scan_artifact = args.scan_artifact if args.scan_artifact.is_absolute() else ROOT / args.scan_artifact
    mapping = build_mapping(scan_artifact)
    json_path = output_root / JSON_NAME
    markdown_path = output_root / MARKDOWN_NAME
    expected_json = json.dumps(mapping, ensure_ascii=False, indent=2) + "\n"
    expected_markdown = markdown_report(mapping)
    if args.check:
        if not json_path.is_file() or not markdown_path.is_file():
            print("mapping output is missing")
            return 1
        if json_path.read_text(encoding="utf-8") != expected_json or markdown_path.read_text(encoding="utf-8") != expected_markdown:
            print("mapping output is stale")
            return 1
        print(f"PASS {repo_path(json_path)}")
        return 0
    json_path, markdown_path = write_outputs(mapping, output_root)
    print(f"WROTE {repo_path(json_path)}")
    print(f"WROTE {repo_path(markdown_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
