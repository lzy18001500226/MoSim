#!/usr/bin/env python3
"""Read-only project tools exposed to the Model Studio assistant.

The assistant is intentionally narrower than a general shell agent.  Every
tool reads a bounded, allowlisted part of the repository and returns structured
data.  No tool writes files, starts MWORKS, or communicates with flight/runtime
services.
"""

from __future__ import annotations

import csv
import json
import math
import re
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
TASK_ROUTES_PATH = ROOT / "Config" / "control_platform" / "model_studio_task_routes_v1.toml"
SEVEN_SCENARIOS_PATH = ROOT / "Config" / "control_platform" / "seven_scenario_experiment_profiles_v2.json"
ENTRY_MAP_PATH = ROOT / "Config" / "control_platform" / "current_model_entry_map.json"
CODEGEN_ROOT = ROOT / "src" / "control" / "codegen"
RESULTS_ROOT = ROOT / "Results" / "control_platform"
PHASE2_ROOT = RESULTS_ROOT / "phase2_full_48_climbpath"
G3_STATUS_PATH = PHASE2_ROOT / "g3_repair" / "G3_STATUS.json"
SEVEN_SCENARIO_RESULTS_ROOT = RESULTS_ROOT / "seven_scenario_ab_v2"
MWORKS_DOCS_ROOT = ROOT / "Docs" / "MworksDocs" / "converted"
MWORKS_SKILLS_ROOT = ROOT / "Docs" / "Skills" / "Mworks"
MODELS_ROOT = ROOT / "Models" / "MoSimQuadrotorModel"
WORKFLOWS_ROOT = ROOT / "Docs" / "Workflows"

SAFE_ROOTS = (
    ROOT / "Docs",
    ROOT / "Config",
    ROOT / "Results",
    ROOT / "Models",
    CODEGEN_ROOT,
)
TEXT_SUFFIXES = {".md", ".txt", ".json", ".toml", ".yaml", ".yml", ".py", ".jl", ".mo", ".csv"}
FORBIDDEN_PATH_PARTS = {".git", ".env", ".ssh", "secrets", "tokens", "credentials"}
MAX_FILE_BYTES = 1_500_000
MAX_SEARCH_FILES = 1_200


class ToolError(ValueError):
    """A user-facing tool validation error."""


def _relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _safe_path(relative_path: str, *, require_text: bool = True) -> Path:
    if not isinstance(relative_path, str) or not relative_path.strip():
        raise ToolError("需要项目内相对路径。")
    candidate = Path(relative_path)
    if candidate.is_absolute() or re.match(r"^[A-Za-z]:", relative_path):
        raise ToolError("只允许项目内相对路径。")
    resolved = (ROOT / candidate).resolve()
    if not any(_is_under(resolved, root.resolve()) for root in SAFE_ROOTS):
        raise ToolError("该路径不在助手允许读取的项目目录内。")
    lowered_parts = {part.lower() for part in resolved.parts}
    if lowered_parts & FORBIDDEN_PATH_PARTS or any("secret" in part.lower() for part in resolved.parts):
        raise ToolError("助手不会读取密钥、令牌或本机配置文件。")
    if not resolved.is_file():
        raise ToolError("文件不存在或不是普通文件。")
    if require_text and resolved.suffix.lower() not in TEXT_SUFFIXES:
        raise ToolError("只允许读取文本、配置、模型或 CSV 文件。")
    if resolved.stat().st_size > MAX_FILE_BYTES:
        raise ToolError("文件超过只读分析大小上限，请指定更小的摘要文件。")
    return resolved


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(_read_text(path))
    except json.JSONDecodeError as exc:
        raise ToolError(f"JSON 解析失败：{_relative(path)}") from exc


def _load_g3_status() -> dict[str, Any]:
    if not G3_STATUS_PATH.is_file():
        raise ToolError("G3 状态总账不存在。")
    document = _load_json(G3_STATUS_PATH)
    if not isinstance(document.get("rows"), list):
        raise ToolError("G3 状态总账缺少 rows。")
    return document


def _g3_rows(controller_ids: list[str] | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    document = _load_g3_status()
    rows = [item for item in document["rows"] if isinstance(item, dict)]
    if not controller_ids:
        return document, rows
    requested = {str(item) for item in controller_ids if str(item).strip()}
    known = {str(row.get("controller_id")) for row in rows}
    missing = sorted(requested - known)
    if missing:
        raise ToolError("G3 总账中没有控制器：" + ", ".join(missing))
    return document, [row for row in rows if str(row.get("controller_id")) in requested]


def _result_record_summary(path: Path, document: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": _relative(path),
        "controller_id": document.get("controller_id"),
        "scenario_id": document.get("scenario_id"),
        "status": document.get("status"),
        "failure_class": document.get("failure_class"),
        "position_rmse_m": document.get("position_rmse_m"),
        "terminal_position_error_norm_m": document.get("terminal_position_error_norm_m"),
        "terminal_time_s": document.get("terminal_time_s"),
    }


def _find_run_records(controller_id: str, scenario_id: str = "") -> list[dict[str, Any]]:
    if not isinstance(controller_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", controller_id):
        raise ToolError("controller_id 只能包含字母、数字、下划线或连字符。")
    scenario = scenario_id.strip() if isinstance(scenario_id, str) else ""
    if scenario and not re.fullmatch(r"[A-Za-z0-9_-]+", scenario):
        raise ToolError("scenario_id 只能包含字母、数字、下划线或连字符。")
    records: list[dict[str, Any]] = []
    for root in (PHASE2_ROOT, SEVEN_SCENARIO_RESULTS_ROOT):
        if not root.is_dir():
            continue
        for path in root.rglob("RUN_RECORD.json"):
            if len(records) >= 80:
                break
            try:
                document = _load_json(path)
            except ToolError:
                continue
            if document.get("controller_id") != controller_id:
                continue
            if scenario and document.get("scenario_id") != scenario:
                continue
            records.append(_result_record_summary(path, document))
    return sorted(records, key=lambda row: row["path"])


def _metric_values(document: Any, prefix: str = "", found: dict[str, Any] | None = None) -> dict[str, Any]:
    result = found if found is not None else {}
    if len(result) >= 80:
        return result
    if isinstance(document, dict):
        for key, value in document.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            key_text = str(key).casefold()
            if isinstance(value, (int, float, str, bool)) and any(
                token in key_text
                for token in ("rmse", "error", "overshoot", "settling", "energy", "terminal", "status", "failure", "completed")
            ):
                result[path] = value
            elif isinstance(value, (dict, list)):
                _metric_values(value, path, result)
    elif isinstance(document, list):
        for index, value in enumerate(document[:30]):
            _metric_values(value, f"{prefix}[{index}]", result)
    return result


def _search_text_roots(query: str, roots: list[Path], *, suffixes: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(query, str) or not query.strip():
        raise ToolError("搜索词不能为空。")
    needle = query.casefold().strip()
    allowed_suffixes = suffixes or TEXT_SUFFIXES
    matches: list[dict[str, Any]] = []
    inspected = 0
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if inspected >= MAX_SEARCH_FILES or len(matches) >= 30:
                break
            if not path.is_file() or path.suffix.lower() not in allowed_suffixes:
                continue
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            inspected += 1
            try:
                lines = _read_text(path).splitlines()
            except OSError:
                continue
            for line_number, line in enumerate(lines, start=1):
                if needle in line.casefold():
                    matches.append({"path": _relative(path), "line": line_number, "preview": _compact(line, 360)})
                    break
        if inspected >= MAX_SEARCH_FILES or len(matches) >= 30:
            break
    return {"query": query, "inspected_files": inspected, "matches": matches}


def _resolve_model_file(relative_path_or_class: str) -> Path:
    if not isinstance(relative_path_or_class, str) or not relative_path_or_class.strip():
        raise ToolError("需要 Modelica 相对路径或类名。")
    value = relative_path_or_class.strip()
    if value.endswith(".mo") or "/" in value or "\\" in value:
        path = _safe_path(value)
        if not _is_under(path, MODELS_ROOT) or path.suffix.lower() != ".mo":
            raise ToolError("只允许分析 Models/MoSimQuadrotorModel 下的 .mo 文件。")
        return path
    leaf = value.rsplit(".", 1)[-1]
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", leaf):
        raise ToolError("Modelica 类名格式无效。")
    matches = sorted(path for path in MODELS_ROOT.rglob(leaf + ".mo") if path.is_file())
    if not matches:
        raise ToolError(f"未找到 Modelica 类：{value}")
    if len(matches) > 1:
        raise ToolError("类名不唯一，请改用项目内 .mo 相对路径：" + ", ".join(_relative(path) for path in matches[:5]))
    return matches[0]


def _load_task_routes() -> tuple[list[str], dict[str, dict[str, Any]]]:
    if not TASK_ROUTES_PATH.is_file():
        raise ToolError("Model Studio 任务路由表不存在。")
    with TASK_ROUTES_PATH.open("rb") as handle:
        document = tomllib.load(handle)
    if document.get("schema") != "mosim.model_studio_task_routes.v1":
        raise ToolError("Model Studio 任务路由表 schema 不匹配。")
    routes = {
        str(item["controller_id"]): dict(item)
        for item in document.get("route", [])
        if isinstance(item, dict) and item.get("controller_id")
    }
    return [str(item) for item in document.get("formal_task_ids", [])], routes


def _compact(value: Any, limit: int = 500) -> str:
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def get_current_studio_context(context_text: str = "") -> dict[str, Any]:
    """Return the user-visible Studio context passed by the front end."""
    return {"context": _compact(context_text, 2400), "read_only": True}


def list_formal_runner_routes(available_only: bool = True) -> dict[str, Any]:
    """List registered Model Studio FormalRunner routes."""
    formal_task_ids, routes = _load_task_routes()
    rows = []
    for controller_id, route in sorted(routes.items()):
        if available_only and not bool(route.get("available")):
            continue
        rows.append(
            {
                "controller_id": controller_id,
                "available": bool(route.get("available")),
                "boundary": route.get("boundary"),
                "runner_class": route.get("runner_class"),
                "reason": route.get("reason"),
            }
        )
    return {
        "formal_task_ids": formal_task_ids,
        "route_count": len(rows),
        "routes": rows,
        "source": _relative(TASK_ROUTES_PATH),
    }


def get_controller_route(controller_id: str) -> dict[str, Any]:
    """Return the declared Studio route for one controller."""
    _, routes = _load_task_routes()
    route = routes.get(controller_id)
    if route is None:
        raise ToolError(f"未找到控制器路由：{controller_id}")
    response = {"controller_id": controller_id, **route, "source": _relative(TASK_ROUTES_PATH)}
    runner_file = route.get("runner_file")
    if isinstance(runner_file, str) and runner_file:
        response["runner_file_exists"] = (ROOT / runner_file).is_file()
    return response


def list_seven_scenario_profiles() -> dict[str, Any]:
    """List the frozen v2 seven-scenario profiles and their declared injections."""
    document = _load_json(SEVEN_SCENARIOS_PATH)
    profiles = []
    for item in document.get("profiles", []):
        if not isinstance(item, dict):
            continue
        overrides = item.get("runner_parameter_overrides", {})
        profiles.append(
            {
                "scenario_id": item.get("scenario_id"),
                "profile_id": item.get("profile_id"),
                "duration_s": item.get("duration_s"),
                "gust_force": overrides.get("gust_force"),
                "mass_scale": overrides.get("mass_scale"),
                "fault_start_s": overrides.get("fault_start_s"),
                "fault_rotor_effectiveness": overrides.get("fault_rotor_effectiveness"),
            }
        )
    return {
        "status": document.get("status"),
        "profile_count": len(profiles),
        "profiles": profiles,
        "source": _relative(SEVEN_SCENARIOS_PATH),
    }


def get_controller_implementation_summary(controller_id: str = "") -> dict[str, Any]:
    """Read the current model-entry mapping without inferring performance."""
    document = _load_json(ENTRY_MAP_PATH)
    schemes = [item for item in document.get("schemes", []) if isinstance(item, dict)]
    if controller_id:
        schemes = [item for item in schemes if item.get("scheme_id") == controller_id]
        if not schemes:
            raise ToolError(f"当前模型映射中没有控制器：{controller_id}")
    rows = []
    for item in schemes[:80]:
        rows.append(
            {
                "scheme_id": item.get("scheme_id"),
                "display_name_zh": item.get("display_name_zh"),
                "category": item.get("category"),
                "implementation_status": item.get("implementation_status"),
                "mapping_state": item.get("mapping_state"),
                "current_model_class": item.get("current_model_class"),
                "next_gate": item.get("next_gate"),
            }
        )
    return {
        "summary": document.get("summary", {}),
        "schemes": rows,
        "source": _relative(ENTRY_MAP_PATH),
        "warning": "实现或入口存在不等同于性能通过、代码生成或运行时部署通过。",
    }


def list_mworks_documents() -> dict[str, Any]:
    """List converted MWORKS documents available to the assistant."""
    docs_root = ROOT / "Docs" / "MworksDocs" / "converted"
    if not docs_root.is_dir():
        return {"document_count": 0, "documents": [], "source": "Docs/MworksDocs/converted/"}
    docs = [
        {"path": _relative(path), "title": path.stem, "category": path.parent.name}
        for path in sorted(docs_root.rglob("*.md"))
        if path.is_file() and path.stat().st_size <= MAX_FILE_BYTES
    ]
    return {"document_count": len(docs), "documents": docs, "source": _relative(docs_root)}


def read_project_document(relative_path: str, line_start: int = 1, line_end: int = 160) -> dict[str, Any]:
    """Read a bounded line range from one allowlisted project text file."""
    path = _safe_path(relative_path)
    if line_start < 1 or line_end < line_start:
        raise ToolError("行范围无效。")
    if line_end - line_start > 299:
        raise ToolError("一次最多读取 300 行。")
    lines = _read_text(path).splitlines()
    selected = lines[line_start - 1 : line_end]
    return {
        "path": _relative(path),
        "line_start": line_start,
        "line_end": min(line_end, len(lines)),
        "line_count": len(lines),
        "content": "\n".join(selected),
    }


def search_project_docs(query: str, scope: str = "docs") -> dict[str, Any]:
    """Search bounded text files in Docs, selected Config, or selected Results."""
    if not isinstance(query, str) or not query.strip():
        raise ToolError("搜索词不能为空。")
    needle = query.casefold().strip()
    roots = {
        "docs": [ROOT / "Docs"],
        "config": [ROOT / "Config" / "control_platform", ROOT / "Config" / "profiles"],
        "results": [
            ROOT / "Results" / "control_platform" / "phase2_full_48_climbpath" / "g3_repair",
            ROOT / "Results" / "control_platform" / "seven_scenario_ab_v2",
            ROOT / "Results" / "control_platform" / "sensitivity_wind_v1",
        ],
    }
    if scope not in roots:
        raise ToolError("scope 只能是 docs、config 或 results。")
    matches: list[dict[str, Any]] = []
    inspected = 0
    for root in roots[scope]:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if inspected >= MAX_SEARCH_FILES or len(matches) >= 30:
                break
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            inspected += 1
            try:
                lines = _read_text(path).splitlines()
            except OSError:
                continue
            for line_number, line in enumerate(lines, start=1):
                if needle in line.casefold():
                    matches.append(
                        {"path": _relative(path), "line": line_number, "preview": _compact(line, 360)}
                    )
                    break
        if inspected >= MAX_SEARCH_FILES or len(matches) >= 30:
            break
    return {"query": query, "scope": scope, "inspected_files": inspected, "matches": matches}


def parse_simulation_csv(relative_path: str, columns: list[str] | None = None) -> dict[str, Any]:
    """Summarize a project CSV result without changing it."""
    path = _safe_path(relative_path)
    if path.suffix.lower() != ".csv":
        raise ToolError("该工具只接受 CSV 文件。")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        requested = columns or fieldnames[:8]
        missing = [name for name in requested if name not in fieldnames]
        if missing:
            raise ToolError("CSV 缺少列：" + ", ".join(missing))
        numeric: dict[str, list[float]] = defaultdict(list)
        preview: list[dict[str, str]] = []
        row_count = 0
        for row in reader:
            row_count += 1
            if len(preview) < 5:
                preview.append({name: row.get(name, "") for name in requested})
            for name in requested:
                try:
                    value = float(row[name])
                except (TypeError, ValueError):
                    continue
                if math.isfinite(value):
                    numeric[name].append(value)
    statistics = {
        name: {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
        }
        for name, values in numeric.items()
        if values
    }
    return {
        "path": _relative(path),
        "row_count": row_count,
        "columns": fieldnames,
        "preview": preview,
        "statistics": statistics,
    }


def compute_controller_metrics(
    relative_path: str,
    error_column: str = "",
    time_column: str = "",
    settling_threshold: float | None = None,
) -> dict[str, Any]:
    """Compute transparent scalar error metrics from one already-exported CSV."""
    path = _safe_path(relative_path)
    if path.suffix.lower() != ".csv":
        raise ToolError("该工具只接受 CSV 文件。")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        candidates = [
            "position_error_norm", "position_error", "tracking_error", "error_norm", "error",
        ]
        column = error_column or next((name for name in candidates if name in fieldnames), "")
        if not column or column not in fieldnames:
            raise ToolError("未找到误差列，请先用 parse_simulation_csv 查看列名后指定 error_column。")
        if time_column and time_column not in fieldnames:
            raise ToolError("CSV 缺少 time_column：" + time_column)
        errors: list[float] = []
        times: list[float] = []
        for index, row in enumerate(reader):
            try:
                error = float(row.get(column, ""))
            except (TypeError, ValueError):
                continue
            if not math.isfinite(error):
                continue
            errors.append(error)
            if time_column:
                try:
                    time_value = float(row.get(time_column, ""))
                except (TypeError, ValueError):
                    time_value = float(index)
            else:
                time_value = float(index)
            times.append(time_value if math.isfinite(time_value) else float(index))
    if not errors:
        raise ToolError("误差列中没有可用的有限数值。")
    absolute_errors = [abs(value) for value in errors]
    peak = max(absolute_errors)
    threshold = settling_threshold if settling_threshold is not None else 0.05 * peak
    if not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or threshold < 0:
        raise ToolError("settling_threshold 必须是非负有限数。")
    last_above = max((index for index, value in enumerate(absolute_errors) if value > threshold), default=-1)
    settling_time = times[last_above + 1] if last_above + 1 < len(times) else None
    return {
        "path": _relative(path),
        "error_column": column,
        "time_column": time_column or "row_index",
        "sample_count": len(errors),
        "rmse": math.sqrt(sum(value * value for value in errors) / len(errors)),
        "maximum_abs_error": peak,
        "terminal_abs_error": absolute_errors[-1],
        "settling_threshold": threshold,
        "estimated_settling_time": settling_time,
        "note": "调节时间仅基于导出误差列与给定阈值估算，不替代正式指标定义。",
    }


def compare_controllers(controller_ids: list[str] | None = None) -> dict[str, Any]:
    """Compare already-recorded G3 scalar values without creating a new ranking claim."""
    document, rows = _g3_rows(controller_ids)
    comparison = [
        {
            "controller_id": row.get("controller_id"),
            "status": row.get("status"),
            "failure_class": row.get("failure_class"),
            "position_rmse_m": row.get("position_rmse_m"),
            "terminal_position_error_norm_m": row.get("terminal_position_error_norm_m"),
            "effective_source": row.get("effective_source"),
        }
        for row in rows
    ]
    return {
        "source": _relative(G3_STATUS_PATH),
        "controller_count": len(comparison),
        "rows": comparison,
        "gate_summary": {
            "effective_passed_count": document.get("effective_passed_count"),
            "effective_failed_count": document.get("effective_failed_count"),
        },
        "warning": "这是同一 G3 总账中的已记录标量对照；不等同于跨场景鲁棒性排名或运行时部署结论。",
    }


def extract_simulation_metrics(relative_path: str) -> dict[str, Any]:
    """Extract metric-like fields from one existing JSON result record."""
    path = _safe_path(relative_path)
    if path.suffix.lower() != ".json":
        raise ToolError("该工具只接受 JSON 结果或总账文件。")
    document = _load_json(path)
    return {
        "path": _relative(path),
        "metrics": _metric_values(document),
        "note": "仅提取现有记录中的指标字段；没有运行仿真或重新计算未导出的指标。",
    }


def validate_gate_status(controller_id: str = "") -> dict[str, Any]:
    """Read the frozen G3 gate ledger, globally or for one controller."""
    requested = [controller_id] if controller_id.strip() else None
    document, rows = _g3_rows(requested)
    if requested:
        row = rows[0]
        return {
            "source": _relative(G3_STATUS_PATH),
            "controller_id": row.get("controller_id"),
            "status": row.get("status"),
            "failure_class": row.get("failure_class"),
            "failure_reasons": row.get("failure_reasons", []),
            "position_rmse_m": row.get("position_rmse_m"),
            "terminal_position_error_norm_m": row.get("terminal_position_error_norm_m"),
            "effective_run_record": row.get("effective_run_record"),
        }
    return {
        "source": _relative(G3_STATUS_PATH),
        "completed": document.get("completed"),
        "g2_baseline_passed_count": document.get("g2_baseline_passed_count"),
        "effective_passed_count": document.get("effective_passed_count"),
        "effective_failed_count": document.get("effective_failed_count"),
        "effective_failure_counts": document.get("effective_failure_counts", {}),
        "note": "门禁状态来自冻结总账，不会在助手中重跑或改变。",
    }


def locate_run_record(controller_id: str, scenario_id: str = "") -> dict[str, Any]:
    """Locate bounded existing RUN_RECORD.json files for a controller/scenario."""
    records = _find_run_records(controller_id, scenario_id)
    return {
        "controller_id": controller_id,
        "scenario_id": scenario_id or None,
        "record_count": len(records),
        "records": records,
        "note": "仅定位已有记录，不代表该路线可在当前会话重新执行。",
    }


def diagnose_solver_stall(controller_id: str) -> dict[str, Any]:
    """Summarize timeout/stall evidence from existing run records only."""
    records = _find_run_records(controller_id)
    timed_out = [item for item in records if item.get("failure_class") == "simulation_timeout"]
    return {
        "controller_id": controller_id,
        "matching_records": timed_out,
        "stalled": bool(timed_out),
        "scope": "仅分析已有 RUN_RECORD；未连接 MWORKS 会话、未检查求解器进程。",
        "manual_next_step": "在获授权的 MWORKS 原生界面复查同一 Runner 的日志、模型诊断和停止时刻。",
    }


def analyze_mcp_timeout(controller_id: str) -> dict[str, Any]:
    """Search existing failure text for MCP/session-timeout evidence without probing a live session."""
    records = _find_run_records(controller_id)
    timeout_records = [
        item for item in records
        if item.get("failure_class") in {"simulation_timeout", "check_model_failed", "simulate_failed"}
    ]
    return {
        "controller_id": controller_id,
        "candidate_records": timeout_records,
        "live_probe": False,
        "note": "该结果不是 MCP 健康检查；它只是现有运行记录的超时/失败线索。",
        "manual_next_step": "需要实时 MCP 诊断时，按当前授权在原生 MWORKS 会话中人工执行。",
    }


def generate_trajectory_plot(relative_path: str, x_column: str, y_column: str, z_column: str = "") -> dict[str, Any]:
    """Validate plot inputs and return a manual trajectory-plot specification; never writes a figure."""
    summary = parse_simulation_csv(relative_path, [name for name in (x_column, y_column, z_column) if name])
    return {
        "source": summary["path"],
        "plot_spec": {"kind": "trajectory", "x": x_column, "y": y_column, "z": z_column or None},
        "execution": "未生成文件。请在 MWORKS 原生结果查看器或经授权的图表流程中按此列映射手动导出。",
    }


def generate_comparison_chart(controller_ids: list[str] | None = None) -> dict[str, Any]:
    """Prepare a chart data contract from existing G3 scalar values; never writes a chart."""
    comparison = compare_controllers(controller_ids)
    return {
        "source": comparison["source"],
        "series": comparison["rows"],
        "chart_spec": {"kind": "grouped_bar", "metrics": ["position_rmse_m", "terminal_position_error_norm_m"]},
        "execution": "未生成图表文件；请在报告图表流程中人工审阅、生成并保存。",
    }


def export_report_figure(source_relative_path: str, figure_name: str) -> dict[str, Any]:
    """Validate a prospective report-figure source and return a no-write handoff."""
    source = _safe_path(source_relative_path)
    if not isinstance(figure_name, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", figure_name):
        raise ToolError("figure_name 只能使用 1-80 个字母、数字、下划线或连字符。")
    return {
        "source": _relative(source),
        "suggested_figure_name": figure_name,
        "suggested_destination": "Docs/报告/图/" + figure_name,
        "execution": "助手没有写入或导出图表；由用户在原生图表工具中确认后执行。",
    }


def create_performance_heatmap(controller_ids: list[str] | None = None) -> dict[str, Any]:
    """Return a heatmap-ready read-only matrix from the G3 ledger."""
    comparison = compare_controllers(controller_ids)
    return {
        "source": comparison["source"],
        "matrix_columns": ["controller_id", "position_rmse_m", "terminal_position_error_norm_m", "status", "failure_class"],
        "matrix_rows": comparison["rows"],
        "execution": "未生成热力图；矩阵仅供人工图表流程使用。",
    }


def read_mworks_doc_section(document_path: str, line_start: int = 1, line_end: int = 160) -> dict[str, Any]:
    """Read one bounded section from converted MWORKS documentation."""
    path = _safe_path(document_path)
    if not _is_under(path, MWORKS_DOCS_ROOT):
        raise ToolError("该工具只读取 Docs/MworksDocs/converted/ 下的转换文档。")
    return read_project_document(_relative(path), line_start, line_end)


def search_doc_index(query: str) -> dict[str, Any]:
    """Search converted MWORKS documentation and return existing matching sections."""
    result = _search_text_roots(query, [MWORKS_DOCS_ROOT], suffixes={".md"})
    return {"source": _relative(MWORKS_DOCS_ROOT), **result}


def search_modelica_syntax(query: str) -> dict[str, Any]:
    """Search project Modelica source text without loading or checking a model."""
    result = _search_text_roots(query, [MODELS_ROOT], suffixes={".mo"})
    return {
        "source": _relative(MODELS_ROOT),
        **result,
        "note": "这是静态文本检索，不代表 MWORKS CheckModel 或图形连线验证。",
    }


def search_control_theory(query: str) -> dict[str, Any]:
    """Search locally converted theory/reference text and design documentation."""
    result = _search_text_roots(query, [MWORKS_DOCS_ROOT, ROOT / "Docs" / "Design"], suffixes={".md", ".txt"})
    return {"sources": ["Docs/MworksDocs/converted/", "Docs/Design/"], **result}


def list_available_skills() -> dict[str, Any]:
    """List the actual project-local MWORKS skill entry points."""
    skills = []
    if MWORKS_SKILLS_ROOT.is_dir():
        for path in sorted(MWORKS_SKILLS_ROOT.rglob("SKILL.md")):
            skills.append({"name": path.parent.name, "path": _relative(path)})
    return {
        "skill_count": len(skills),
        "skills": skills,
        "note": "技能文档用于人工操作指导；本助手不会自动执行其中的 MWORKS 或运行时动作。",
    }


def get_model_dependencies(relative_path_or_class: str) -> dict[str, Any]:
    """Extract static Modelica dependency tokens for one active project model file."""
    path = _resolve_model_file(relative_path_or_class)
    source = _read_text(path)
    patterns = {
        "extends": r"^\s*extends\s+([A-Za-z_][A-Za-z0-9_\.]*)",
        "imports": r"^\s*import\s+([A-Za-z_][A-Za-z0-9_\.\*]*)",
        "replaceable_models": r"\breplaceable\s+model\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_\.]*)",
        "redeclares": r"\bredeclare\s+(?:model|package)\s+([A-Za-z_][A-Za-z0-9_]*)",
    }
    dependencies: dict[str, list[Any]] = {}
    for key, pattern in patterns.items():
        matches = re.findall(pattern, source, flags=re.MULTILINE)
        normalized = [" = ".join(item) if isinstance(item, tuple) else item for item in matches]
        dependencies[key] = normalized[:80]
    return {
        "path": _relative(path),
        "dependencies": dependencies,
        "note": "这是静态依赖令牌提取；不解析 MWORKS 完整实例化层级。",
    }


def validate_sysblock_connections(relative_path_or_class: str) -> dict[str, Any]:
    """Report static connect() observations for a Modelica file; it is not a graphical validation."""
    path = _resolve_model_file(relative_path_or_class)
    source = _read_text(path)
    connections = re.findall(r"\bconnect\s*\(\s*([^,()]+)\s*,\s*([^)]+)\)", source)
    endpoint_pairs = [{"from": _compact(left, 180), "to": _compact(right, 180)} for left, right in connections[:80]]
    return {
        "path": _relative(path),
        "static_connect_count": len(connections),
        "connections": endpoint_pairs,
        "manual_check_required": True,
        "note": "仅统计源码 connect() 调用；未打开 Sysblock 图，不构成端口类型或图形连线通过结论。",
    }


def list_codegen_artifacts() -> dict[str, Any]:
    """List tracked generated-code delivery directories and manifests."""
    if not CODEGEN_ROOT.is_dir():
        return {"root": _relative(CODEGEN_ROOT), "directories": [], "exists": False}
    directories = []
    for child in sorted(CODEGEN_ROOT.iterdir()):
        if not child.is_dir():
            continue
        manifests = [path.name for path in child.glob("*manifest*.json")]
        directories.append({"path": _relative(child), "manifests": manifests})
    return {"root": _relative(CODEGEN_ROOT), "directories": directories, "exists": True}


def recommend_manual_workflow(topic: str) -> dict[str, Any]:
    """Recommend a real workflow path; never execute it."""
    topic_key = (topic or "").casefold()
    candidates = [
        ("代码生成", "Docs/Workflows/MoSim Agent执行任务指令.md", "打开 MWORKS 模型后，在原生代码生成页签手动导出。"),
        ("结果", "Docs/Skills/Mworks/mworks-simulation-evidence/SKILL.md", "先保留 Result.msr、运行记录和指标，再进行只读分析。"),
        ("仿真", "Docs/Workflows/mainline_operations_board.md", "先确认当前授权范围和模型入口；Studio 不替代 MWORKS 的手动仿真。"),
        ("故障", "Config/control_platform/seven_scenario_experiment_profiles_v2.json", "先冻结场景参数，再在 MWORKS 中手动执行；不要将 UI 设置视为结果。"),
        ("qgc", "Docs/Design/架构.md", "QGC/Gazebo/PX4 属于独立运行时证据线，助手只能提供边界说明。"),
    ]
    selected = [row for row in candidates if row[0].casefold() in topic_key]
    if not selected:
        selected = candidates[:3]
    workflows = []
    for _, relative_path, guidance in selected:
        workflows.append(
            {
                "path": relative_path,
                "exists": (ROOT / relative_path).is_file(),
                "guidance": guidance,
            }
        )
    return {"topic": topic, "recommendations": workflows, "execution": "未执行任何工作流。"}


def get_agent_capabilities() -> dict[str, Any]:
    """State the assistant's hard safety boundary."""
    return {
        "capabilities": [
            "读取当前 Studio 上下文",
            "检索项目文档、配置和已存在结果摘要",
            "查询控制器 FormalRunner 路由与冻结场景",
            "汇总允许路径下 CSV 的基础统计和透明误差指标",
            "读取冻结门禁、运行记录和 Modelica 静态连接/依赖",
            "准备人工绘图与报告导出所需的只读数据",
            "给出 MWORKS 手动操作与证据边界说明",
        ],
        "blocked_actions": [
            "修改 Models、Config 或 Results",
            "启动 CheckModel 或仿真",
            "执行 GenerateModelCode 或编译",
            "发送 QGC、Gazebo、PX4、ROS 或 MAVROS 命令",
            "读取密钥、本机配置或项目外路径",
        ],
        "read_only": True,
    }


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., dict[str, Any]]


def _schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


TOOLS: dict[str, ToolSpec] = {
    "get_current_studio_context": ToolSpec(
        "get_current_studio_context",
        "读取当前 Model Studio 选择的只读上下文。",
        _schema({"context_text": {"type": "string"}}),
        get_current_studio_context,
    ),
    "list_formal_runner_routes": ToolSpec(
        "list_formal_runner_routes",
        "列出 Model Studio 已登记的 FormalRunner 路由和输出边界。",
        _schema({"available_only": {"type": "boolean"}}),
        list_formal_runner_routes,
    ),
    "get_controller_route": ToolSpec(
        "get_controller_route",
        "查询一个控制器的 Studio FormalRunner 路由。",
        _schema({"controller_id": {"type": "string"}}, ["controller_id"]),
        get_controller_route,
    ),
    "list_seven_scenario_profiles": ToolSpec(
        "list_seven_scenario_profiles",
        "读取冻结的 v2 七场景配置和故障注入参数。",
        _schema({}),
        list_seven_scenario_profiles,
    ),
    "get_controller_implementation_summary": ToolSpec(
        "get_controller_implementation_summary",
        "查询当前 Modelica 控制模块映射，不能据此推断性能通过。",
        _schema({"controller_id": {"type": "string"}}),
        get_controller_implementation_summary,
    ),
    "list_mworks_documents": ToolSpec(
        "list_mworks_documents",
        "列出已转换的 MWORKS 文档。",
        _schema({}),
        list_mworks_documents,
    ),
    "read_project_document": ToolSpec(
        "read_project_document",
        "读取允许目录内一个文本文件的有限行范围。不能读取密钥或项目外文件。",
        _schema(
            {
                "relative_path": {"type": "string"},
                "line_start": {"type": "integer", "minimum": 1},
                "line_end": {"type": "integer", "minimum": 1},
            },
            ["relative_path"],
        ),
        read_project_document,
    ),
    "search_project_docs": ToolSpec(
        "search_project_docs",
        "在受限的 Docs、Config 或结果摘要目录中搜索关键词。",
        _schema(
            {
                "query": {"type": "string"},
                "scope": {"type": "string", "enum": ["docs", "config", "results"]},
            },
            ["query"],
        ),
        search_project_docs,
    ),
    "parse_simulation_csv": ToolSpec(
        "parse_simulation_csv",
        "只读汇总一个允许路径下 CSV 的列、预览和基础统计。",
        _schema(
            {
                "relative_path": {"type": "string"},
                "columns": {"type": "array", "items": {"type": "string"}},
            },
            ["relative_path"],
        ),
        parse_simulation_csv,
    ),
    "compute_controller_metrics": ToolSpec(
        "compute_controller_metrics",
        "从已有 CSV 的指定误差列计算 RMSE、峰值、终端误差和估算调节时间，不运行仿真。",
        _schema(
            {
                "relative_path": {"type": "string"},
                "error_column": {"type": "string"},
                "time_column": {"type": "string"},
                "settling_threshold": {"type": "number", "minimum": 0},
            },
            ["relative_path"],
        ),
        compute_controller_metrics,
    ),
    "compare_controllers": ToolSpec(
        "compare_controllers",
        "从冻结 G3 总账对照已记录的控制器标量；不能推断跨场景鲁棒性或运行时部署。",
        _schema({"controller_ids": {"type": "array", "items": {"type": "string"}}}),
        compare_controllers,
    ),
    "extract_simulation_metrics": ToolSpec(
        "extract_simulation_metrics",
        "从已有 JSON 运行记录或总账提取指标字段，不重跑或重算未导出的指标。",
        _schema({"relative_path": {"type": "string"}}, ["relative_path"]),
        extract_simulation_metrics,
    ),
    "validate_gate_status": ToolSpec(
        "validate_gate_status",
        "读取冻结 G3 门禁总账的全局或单控制器状态。",
        _schema({"controller_id": {"type": "string"}}),
        validate_gate_status,
    ),
    "locate_run_record": ToolSpec(
        "locate_run_record",
        "定位已有 RUN_RECORD.json，不表示可以在当前会话重新执行。",
        _schema(
            {"controller_id": {"type": "string"}, "scenario_id": {"type": "string"}},
            ["controller_id"],
        ),
        locate_run_record,
    ),
    "diagnose_solver_stall": ToolSpec(
        "diagnose_solver_stall",
        "从已有运行记录汇总 simulation_timeout 线索，不连接实时求解器。",
        _schema({"controller_id": {"type": "string"}}, ["controller_id"]),
        diagnose_solver_stall,
    ),
    "analyze_mcp_timeout": ToolSpec(
        "analyze_mcp_timeout",
        "从已有失败记录汇总超时线索；不探测或操作实时 MCP 会话。",
        _schema({"controller_id": {"type": "string"}}, ["controller_id"]),
        analyze_mcp_timeout,
    ),
    "generate_trajectory_plot": ToolSpec(
        "generate_trajectory_plot",
        "校验已有 CSV 的轨迹列并给出人工绘图输入，不生成或写入图表。",
        _schema(
            {
                "relative_path": {"type": "string"},
                "x_column": {"type": "string"},
                "y_column": {"type": "string"},
                "z_column": {"type": "string"},
            },
            ["relative_path", "x_column", "y_column"],
        ),
        generate_trajectory_plot,
    ),
    "generate_comparison_chart": ToolSpec(
        "generate_comparison_chart",
        "从冻结 G3 总账准备对比图数据，不生成或写入图表。",
        _schema({"controller_ids": {"type": "array", "items": {"type": "string"}}}),
        generate_comparison_chart,
    ),
    "export_report_figure": ToolSpec(
        "export_report_figure",
        "校验报告图候选数据源并给出人工导出交接，不写入 Docs。",
        _schema(
            {"source_relative_path": {"type": "string"}, "figure_name": {"type": "string"}},
            ["source_relative_path", "figure_name"],
        ),
        export_report_figure,
    ),
    "create_performance_heatmap": ToolSpec(
        "create_performance_heatmap",
        "从冻结 G3 总账返回热力图数据矩阵，不生成文件。",
        _schema({"controller_ids": {"type": "array", "items": {"type": "string"}}}),
        create_performance_heatmap,
    ),
    "read_mworks_doc_section": ToolSpec(
        "read_mworks_doc_section",
        "读取已转换 MWORKS 文档中的有限行范围。",
        _schema(
            {
                "document_path": {"type": "string"},
                "line_start": {"type": "integer", "minimum": 1},
                "line_end": {"type": "integer", "minimum": 1},
            },
            ["document_path"],
        ),
        read_mworks_doc_section,
    ),
    "search_doc_index": ToolSpec(
        "search_doc_index",
        "在已转换 MWORKS 文档中搜索相关章节。",
        _schema({"query": {"type": "string"}}, ["query"]),
        search_doc_index,
    ),
    "search_modelica_syntax": ToolSpec(
        "search_modelica_syntax",
        "在项目 Modelica 源码中静态检索语法或变量，不加载或检查模型。",
        _schema({"query": {"type": "string"}}, ["query"]),
        search_modelica_syntax,
    ),
    "search_control_theory": ToolSpec(
        "search_control_theory",
        "在本地转换文档和设计文档中检索控制理论相关内容。",
        _schema({"query": {"type": "string"}}, ["query"]),
        search_control_theory,
    ),
    "list_available_skills": ToolSpec(
        "list_available_skills",
        "列出项目本地可供人工遵循的 MWORKS Skill 文档。",
        _schema({}),
        list_available_skills,
    ),
    "get_model_dependencies": ToolSpec(
        "get_model_dependencies",
        "提取一个项目 Modelica 类的静态 extends、import、replaceable 和 redeclare 依赖令牌。",
        _schema({"relative_path_or_class": {"type": "string"}}, ["relative_path_or_class"]),
        get_model_dependencies,
    ),
    "validate_sysblock_connections": ToolSpec(
        "validate_sysblock_connections",
        "统计一个 Modelica 文件的 connect() 调用；这不是 MWORKS 图形或端口类型验证。",
        _schema({"relative_path_or_class": {"type": "string"}}, ["relative_path_or_class"]),
        validate_sysblock_connections,
    ),
    "list_codegen_artifacts": ToolSpec(
        "list_codegen_artifacts",
        "列出 src/control/codegen 下的交付目录与 manifest。",
        _schema({}),
        list_codegen_artifacts,
    ),
    "recommend_manual_workflow": ToolSpec(
        "recommend_manual_workflow",
        "推荐已有工作流或手动步骤，不会执行任何工作流。",
        _schema({"topic": {"type": "string"}}, ["topic"]),
        recommend_manual_workflow,
    ),
    "get_agent_capabilities": ToolSpec(
        "get_agent_capabilities",
        "显示助手可做和明确禁止做的操作。",
        _schema({}),
        get_agent_capabilities,
    ),
}


def openai_tool_definitions() -> list[dict[str, Any]]:
    """Return OpenAI Responses function definitions for the safe tool catalog."""
    return [
        {
            "type": "function",
            "name": spec.name,
            "description": spec.description,
            "parameters": spec.parameters,
            # Optional tool parameters are intentionally supported. Keeping
            # strict false preserves compatibility with OpenAI-compatible
            # Responses gateways that reject strict schemas with optionals.
            "strict": False,
        }
        for spec in TOOLS.values()
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute one allowlisted read-only tool and normalize failures."""
    spec = TOOLS.get(name)
    if spec is None:
        return {"ok": False, "error": "unknown_tool", "message": f"未注册只读工具：{name}"}
    if not isinstance(arguments, dict):
        return {"ok": False, "error": "invalid_arguments", "message": "工具参数必须是对象。"}
    try:
        return {"ok": True, "result": spec.handler(**arguments)}
    except (ToolError, TypeError, ValueError) as exc:
        return {"ok": False, "error": "tool_validation_failed", "message": str(exc)}
    except OSError as exc:
        return {"ok": False, "error": "tool_io_failed", "message": _compact(exc, 240)}
