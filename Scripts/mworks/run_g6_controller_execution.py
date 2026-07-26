#!/usr/bin/env python3
"""Execute the frozen G6 controller matrix with one reusable Sysplorer session.

This runner deliberately separates the two allowed G6 evidence classes:

* ``internal_fixed_input_probe`` verifies an internal graphical control law
  under its declared fixed inputs.  It is never labelled as aircraft tracking.
* ``whole_aircraft_minimum_closure`` executes its named plant-coupled model
  for the source model's declared experiment duration.

Every attempted route receives a durable ``RUN_RECORD.json``.  Failed model
checks, unreadable results, and screenshot failures are retained as terminal
evidence instead of being silently skipped.  The script does not edit model
behavior; it may restore frozen bytes only after proving that MWORKS added
line-ending or trailing-whitespace serialization.  It does not use
ClearAll/ChangeDirectory and closes only its own dedicated Sysplorer session
after the requested batch finishes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MATRIX_PATH = ROOT / "Results/control_platform/g6_controller_execution_20260724/G6_EXECUTION_MATRIX.json"
MATRIX_PATH = DEFAULT_MATRIX_PATH
STATUS_PATH = MATRIX_PATH.parent / "G6_EXECUTION_STATUS.json"
CAPTURE_CMD = ROOT / "Scripts/tools/capture_window_background.cmd"
BASE_MODEL_RELATIVE_PATHS = (
    Path("Models/MoSimQuadrotorModel/package.mo"),
)

MCP_DIR = ROOT / "Scripts/mworks"
if str(MCP_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_DIR))

from run_sysplorer_mcp_smoke import (  # noqa: E402
    DEFAULT_VARIABLES,
    JsonlMcpClient,
    initialize_mcp_client,
    native_result_file,
    prepare_native_result_target,
    read_result_series,
    resolve_native_result_dir,
    resolve_wrapper,
    simulate_modelingpy,
    windows_path,
    wrapper_command,
    write_csv,
    write_metrics,
    write_native_result_manifest,
)


SCHEMA = "mosim.g6_controller_execution_run.v1"
STATUS_SCHEMA = "mosim.g6_controller_execution_status.v1"
SCREENSHOT_SCHEMA = "mosim.g6_controller_execution_screenshot_manifest.v1"
SESSION_CLEANUP_SCHEMA = "mosim.g6_controller_execution_session_cleanup.v1"
REPORT_RESULT_RECONCILIATION_SCHEMA = "mosim.g6_report_result_binding_reconciliation.v1"
INTERNAL_TARGET_TIME = [0.0, 0.2]
SESSION_CLEANUP_TIMEOUT_S = 30.0
RESULT_READY_TIMEOUT_S = 60.0
RESULT_READY_POLL_S = 1.0
LICENSE_OR_LOGIN_RE = re.compile(
    r"license|licen[cs]e|activation|authorize|authorization|login|password|"
    r"L5104-B0|软件尚未激活|激活|授权|登录|密码|演示版|demo",
    re.IGNORECASE,
)
TOPOLOGY_RE = re.compile(r"unconnected|missing wire|no connection|未连线|端口", re.IGNORECASE)
INTERNAL_RE = re.compile(r"internal|dmp|mcp transport|connection refused|broken pipe", re.IGNORECASE)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def configure_matrix_path(value: Path | None) -> None:
    """Select one project-local frozen matrix without touching historical evidence."""

    global MATRIX_PATH, STATUS_PATH
    candidate = DEFAULT_MATRIX_PATH if value is None else value
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    candidate = candidate.resolve()
    results_root = (ROOT / "Results").resolve()
    try:
        candidate.relative_to(results_root)
    except ValueError as exc:
        raise ValueError("matrix path must remain below Results/") from exc
    if candidate.name != "G6_EXECUTION_MATRIX.json":
        raise ValueError("matrix file name must be G6_EXECUTION_MATRIX.json")
    MATRIX_PATH = candidate
    STATUS_PATH = MATRIX_PATH.parent / "G6_EXECUTION_STATUS.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mworks_whitespace_normal_form(source: bytes) -> bytes:
    """Return the sole native serialization normalization accepted by G6.

    Sysplorer may append trailing spaces while writing a graphical model after
    simulation. This helper deliberately accepts no syntax, annotation, port,
    topology, or parameter change: only CR/LF normalization, trailing spaces
    or tabs at the end of a line, and a single terminal line ending are
    normalized. The form is accepted only when it either hashes directly to
    the frozen target or matches a captured exact frozen snapshot whose hash
    equals that target.
    """
    text = source.decode("utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    normalized = "\n".join(line.rstrip(" \t") for line in lines)
    # Sysplorer may omit the final newline while serializing a direct graph.
    # The frozen bytes remain authoritative because this form must hash back to
    # the matrix target before it is ever written to disk.
    if normalized and not normalized.endswith("\n"):
        normalized += "\n"
    return normalized.encode("utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def relative(path: Path | str | None) -> str | None:
    if path is None:
        return None
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(candidate)


def artifact(path: Path | None, role: str) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    return {
        "path": relative(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "claim_role": role,
    }


def base_model_files() -> list[Path]:
    """Return the ordered package roots required by formal whole-aircraft targets."""
    return [ROOT / relative_path for relative_path in BASE_MODEL_RELATIVE_PATHS]


def preload_base_packages(client: JsonlMcpClient) -> list[dict[str, Any]]:
    """Load canonical Modelica package roots once for the dedicated G6 session.

    The project root now owns the Plant package. ``auto_load_deps`` on a leaf
    target is still not sufficient for a clean Sysplorer process, so preload
    the one canonical project package explicitly.
    """
    records: list[dict[str, Any]] = []
    for package_file in base_model_files():
        if not package_file.is_file():
            raise FileNotFoundError(f"Required G6 base package is missing: {package_file}")
        result = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": str(package_file),
                "force_reload": False,
                "auto_load_deps": True,
            },
            timeout_s=300,
        )
        record = {
            "path": relative(package_file),
            "sha256": sha256(package_file),
            "force_reload": False,
            "auto_load_deps": True,
            "ok": bool(result.get("ok")),
        }
        records.append(record)
        if not result.get("ok"):
            raise RuntimeError(f"Required G6 base package load failed: {record['path']}: {result}")
    return records


def load_route_model_prerequisites(
    client: JsonlMcpClient,
    row: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    """Load a route's hash-bound leaf definitions before its target model.

    Most GraphicalMIL routes need no leaf preloads.  The five inherited
    whole-aircraft models embed an unqualified controller Sysblock type, which
    a clean session cannot resolve from package roots alone.  Their frozen
    matrix dependency is loaded explicitly and recorded with the route.
    """
    prerequisites = row.get("model_load_prerequisites", [])
    if not isinstance(prerequisites, list):
        raise RuntimeError("Frozen matrix route model_load_prerequisites must be a list")
    for prerequisite in prerequisites:
        if not isinstance(prerequisite, dict):
            raise RuntimeError("Frozen matrix contains a non-object model load prerequisite")
        path_text = prerequisite.get("model_file")
        model_class = prerequisite.get("model_class")
        expected_hash = prerequisite.get("model_sha256")
        if not isinstance(path_text, str) or not isinstance(model_class, str) or not isinstance(expected_hash, str):
            raise RuntimeError("Frozen matrix contains an incomplete model load prerequisite")
        model_file = ROOT / path_text
        try:
            model_file.resolve().relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"Model load prerequisite leaves project root: {path_text}") from exc
        if not model_file.is_file():
            raise FileNotFoundError(f"Model load prerequisite is missing: {path_text}")
        actual_hash = sha256(model_file)
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Model load prerequisite hash changed after matrix freeze: {actual_hash} != {expected_hash}"
            )
        record = {
            "role": prerequisite.get("role"),
            "source_component": prerequisite.get("source_component"),
            "source_declared_type": prerequisite.get("source_declared_type"),
            "path": relative(model_file),
            "model_class": model_class,
            "sha256": actual_hash,
            "force_reload": False,
            "auto_load_deps": True,
            "ok": False,
        }
        base_model_class = prerequisite.get("base_model_class")
        if isinstance(base_model_class, str) and base_model_class:
            record["base_model_class"] = base_model_class
        records.append(record)
        result = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": str(model_file),
                "force_reload": False,
                "auto_load_deps": True,
            },
            timeout_s=300,
        )
        record["ok"] = bool(result.get("ok"))
        if not record["ok"]:
            raise RuntimeError(f"G6 route prerequisite load failed: {path_text}: {result}")


def archive_existing_route_for_rerun(run_dir: Path) -> str | None:
    """Preserve the prior route bundle before an explicit --rerun overwrite."""
    previous_record = run_dir / "RUN_RECORD.json"
    if not previous_record.is_file():
        return None
    archive_dir = run_dir / "superseded" / datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir.mkdir(parents=True, exist_ok=False)
    copied: list[dict[str, str]] = []
    for name in ("RUN_RECORD.json", "logs", "raw", "metrics", "screenshots"):
        source = run_dir / name
        destination = archive_dir / name
        if source.is_file():
            shutil.copy2(source, destination)
            copied.append({"source": relative(source) or str(source), "archive": relative(destination) or str(destination)})
        elif source.is_dir():
            shutil.copytree(source, destination)
            copied.append({"source": relative(source) or str(source), "archive": relative(destination) or str(destination)})
    write_json(
        archive_dir / "ARCHIVE_MANIFEST.json",
        {
            "schema": "mosim.g6_controller_execution_superseded_run.v1",
            "reason": "explicit --rerun before replacing a terminal G6 route record",
            "archived_at": now_iso(),
            "source_run_dir": relative(run_dir),
            "files": copied,
        },
    )
    return relative(archive_dir)


def verify_frozen_target_hash(
    record: dict[str, Any],
    model_file: Path,
    expected_hash: str,
    phase: str,
    *,
    frozen_target_bytes: bytes | None = None,
    frozen_snapshot_path: str | None = None,
) -> str:
    """Bind every mutable MWORKS phase to the frozen target bytes.

    Sysplorer can materialize native serialization metadata while loading a
    newly created graph. A pre-load-only digest can therefore incorrectly bind
    a later result to earlier source bytes. Record each phase and stop the row
    as soon as the source no longer matches the frozen matrix target.
    """
    current_bytes = model_file.read_bytes()
    actual_hash = hashlib.sha256(current_bytes).hexdigest()
    observations = record.setdefault("target_hash_observations", [])
    if not isinstance(observations, list):
        raise RuntimeError("G6 record target_hash_observations is not a list")
    raw_match = actual_hash == expected_hash
    observation: dict[str, Any] = {
        "phase": phase,
        "sha256": actual_hash,
        "expected_sha256": expected_hash,
        "raw_matches_frozen_target": raw_match,
        "matches_frozen_target": raw_match,
    }
    observations.append(observation)
    if phase == "before_load":
        # Retain the original field for consumers that predate phase records.
        record["verified_target_sha256"] = actual_hash
    if raw_match:
        return actual_hash

    try:
        normalized = mworks_whitespace_normal_form(current_bytes)
    except UnicodeDecodeError as exc:
        raise RuntimeError(
            f"Source hash changed after matrix freeze during {phase}: {actual_hash} != {expected_hash}; "
            "the source is not UTF-8 and cannot qualify for native whitespace normalization"
        ) from exc
    normalized_hash = hashlib.sha256(normalized).hexdigest()
    observation["whitespace_normalized_sha256"] = normalized_hash
    restore_bytes = normalized
    if frozen_target_bytes is None:
        accepted_normalized = normalized_hash == expected_hash
    else:
        frozen_hash = hashlib.sha256(frozen_target_bytes).hexdigest()
        if frozen_hash != expected_hash:
            raise RuntimeError(
                f"Frozen target snapshot hash does not match the matrix during {phase}: "
                f"{frozen_hash} != {expected_hash}"
            )
        frozen_normalized = mworks_whitespace_normal_form(frozen_target_bytes)
        frozen_normalized_hash = hashlib.sha256(frozen_normalized).hexdigest()
        observation.update(
            {
                "frozen_snapshot_sha256": frozen_hash,
                "frozen_whitespace_normalized_sha256": frozen_normalized_hash,
                "frozen_snapshot_path": frozen_snapshot_path,
            }
        )
        accepted_normalized = normalized == frozen_normalized
        restore_bytes = frozen_target_bytes
    if not accepted_normalized:
        raise RuntimeError(
            f"Source hash changed after matrix freeze during {phase}: {actual_hash} != {expected_hash}"
        )

    # A snapshot preserves the exact frozen final-newline convention. Without a
    # snapshot, restoring the normalized bytes remains safe only when that form
    # itself hashes exactly to the matrix target.
    model_file.write_bytes(restore_bytes)
    restored_hash = sha256(model_file)
    observation.update(
        {
            "native_whitespace_only": True,
            "restored_sha256": restored_hash,
            "normalized_source_restored": restored_hash == expected_hash,
            "matches_frozen_target": restored_hash == expected_hash,
        }
    )
    if restored_hash != expected_hash:
        raise RuntimeError(
            f"Native whitespace normalization did not restore the frozen source during {phase}: "
            f"{restored_hash} != {expected_hash}"
        )
    if phase == "before_load":
        record["verified_target_sha256"] = restored_hash
    record.setdefault("accepted_native_source_normalizations", []).append(
        {
            "phase": phase,
            "original_sha256": actual_hash,
            "restored_sha256": restored_hash,
            "rule": "utf8_line_endings_trailing_horizontal_whitespace_and_terminal_newline_only",
            "frozen_snapshot_path": frozen_snapshot_path,
        }
    )
    return restored_hash


def declared_protected_sources(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the deduplicated source boundary that an execution may load.

    A route is not bound by its entry probe alone: MWORKS can also serialize
    the graphical controller core or an explicitly loaded prerequisite.  The
    frozen matrix already declares those three roles, so derive one ordered
    source set from it rather than introducing a second hand-maintained list.
    """

    candidates: list[tuple[str, dict[str, Any]]] = []
    for role in ("target", "controller_core"):
        source = row.get(role)
        if not isinstance(source, dict):
            raise RuntimeError(f"Frozen matrix route {role} is not an object")
        candidates.append((role, source))
    prerequisites = row.get("model_load_prerequisites", [])
    if not isinstance(prerequisites, list):
        raise RuntimeError("Frozen matrix route model_load_prerequisites must be a list")
    for index, source in enumerate(prerequisites):
        if not isinstance(source, dict):
            raise RuntimeError("Frozen matrix contains a non-object model load prerequisite")
        candidates.append((f"model_load_prerequisite[{index}]", source))

    protected: dict[str, dict[str, Any]] = {}
    for role, source in candidates:
        path_text = source.get("model_file")
        expected_hash = source.get("model_sha256")
        model_class = source.get("model_class")
        if not isinstance(path_text, str) or not isinstance(expected_hash, str):
            raise RuntimeError(f"Frozen matrix {role} source binding is incomplete")
        source_file = ROOT / path_text
        try:
            source_file.resolve().relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"Frozen matrix {role} source leaves the project: {path_text}") from exc
        if not source_file.is_file():
            raise FileNotFoundError(f"Frozen matrix {role} source is missing: {path_text}")
        path = relative(source_file)
        if path is None:
            raise RuntimeError(f"Unable to normalize protected source path: {path_text}")
        existing = protected.get(path)
        if existing is None:
            existing = {
                "path": path,
                "expected_sha256": expected_hash,
                "roles": [],
                "model_classes": [],
            }
            protected[path] = existing
        elif existing["expected_sha256"] != expected_hash:
            raise RuntimeError(
                f"Frozen matrix binds protected source {path} to conflicting hashes: "
                f"{existing['expected_sha256']} != {expected_hash}"
            )
        existing["roles"].append(role)
        if isinstance(model_class, str) and model_class and model_class not in existing["model_classes"]:
            existing["model_classes"].append(model_class)
        declared_role = source.get("role")
        if isinstance(declared_role, str) and declared_role:
            declared_roles = existing.setdefault("declared_roles", [])
            if declared_role not in declared_roles:
                declared_roles.append(declared_role)
    return list(protected.values())


def source_snapshot_name(index: int, path: str) -> str:
    """Build a stable, filesystem-safe snapshot name without changing sources."""

    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(path).name)
    return f"{index:02d}_{stem}"


def freeze_protected_sources(
    *,
    row: dict[str, Any],
    raw_dir: Path,
    record: dict[str, Any],
) -> list[dict[str, Any]]:
    """Capture exact bytes for every source a route is allowed to load.

    Initial bytes must already match the frozen matrix.  Whitespace repair is
    intentionally a separate, auditable command; it must not be silently
    applied while starting a new live simulation.
    """

    snapshot_dir = raw_dir / "frozen_bound_sources"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    bindings: list[dict[str, Any]] = []
    for index, declared in enumerate(declared_protected_sources(row), start=1):
        path = str(declared["path"])
        expected_hash = str(declared["expected_sha256"])
        source_file = ROOT / path
        actual_hash = sha256(source_file)
        if actual_hash != expected_hash:
            raise RuntimeError(
                f"Protected source hash changed before live execution: {path}: "
                f"{actual_hash} != {expected_hash}. Run the explicit native whitespace repair "
                "only after it proves the frozen bytes are recoverable."
            )
        frozen_bytes = source_file.read_bytes()
        snapshot = snapshot_dir / source_snapshot_name(index, path)
        snapshot.write_bytes(frozen_bytes)
        binding: dict[str, Any] = {
            "path": path,
            "expected_sha256": expected_hash,
            "roles": list(declared["roles"]),
            "model_classes": list(declared["model_classes"]),
            "frozen_snapshot": {
                "path": relative(snapshot),
                "sha256": actual_hash,
                "captured_phase": "before_load",
            },
            "hash_observations": [],
        }
        if declared.get("declared_roles"):
            binding["declared_roles"] = list(declared["declared_roles"])
        bindings.append(binding)
    record["protected_sources"] = bindings
    target_binding = next((item for item in bindings if "target" in item["roles"]), None)
    if target_binding is None:
        raise RuntimeError("Frozen matrix protected source set has no target")
    record["frozen_target_snapshot"] = dict(target_binding["frozen_snapshot"])
    record["target_hash_observations"] = target_binding["hash_observations"]
    record["verified_target_sha256"] = target_binding["expected_sha256"]
    return bindings


def load_frozen_protected_snapshot(binding: dict[str, Any]) -> tuple[bytes, str]:
    """Load one exact, hash-bound snapshot from a route execution record."""

    expected_hash = binding.get("expected_sha256")
    snapshot = binding.get("frozen_snapshot")
    if not isinstance(expected_hash, str) or not isinstance(snapshot, dict):
        raise RuntimeError("Protected source snapshot metadata is incomplete")
    path_text = snapshot.get("path")
    if not isinstance(path_text, str):
        raise RuntimeError("Protected source snapshot path is absent")
    snapshot_path = ROOT / path_text
    try:
        snapshot_path.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError("Protected source snapshot leaves the repository") from exc
    if not snapshot_path.is_file():
        raise RuntimeError(f"Protected source snapshot is missing: {relative(snapshot_path)}")
    frozen_bytes = snapshot_path.read_bytes()
    frozen_hash = hashlib.sha256(frozen_bytes).hexdigest()
    if frozen_hash != expected_hash or snapshot.get("sha256") != frozen_hash:
        raise RuntimeError("Protected source snapshot hash differs from its frozen matrix binding")
    return frozen_bytes, relative(snapshot_path) or str(snapshot_path)


def verify_frozen_protected_source_hash(
    binding: dict[str, Any],
    source_file: Path,
    phase: str,
    *,
    frozen_source_bytes: bytes | None = None,
    frozen_snapshot_path: str | None = None,
) -> str:
    """Verify one declared source and restore only native whitespace drift."""

    expected_hash = binding.get("expected_sha256")
    if not isinstance(expected_hash, str):
        raise RuntimeError("Protected source expected hash is absent")
    if frozen_source_bytes is None:
        frozen_source_bytes, frozen_snapshot_path = load_frozen_protected_snapshot(binding)
    frozen_hash = hashlib.sha256(frozen_source_bytes).hexdigest()
    if frozen_hash != expected_hash:
        raise RuntimeError("Protected source frozen snapshot does not match its expected hash")

    current_bytes = source_file.read_bytes()
    actual_hash = hashlib.sha256(current_bytes).hexdigest()
    observations = binding.setdefault("hash_observations", [])
    if not isinstance(observations, list):
        raise RuntimeError("Protected source hash observations are not a list")
    observation: dict[str, Any] = {
        "phase": phase,
        "sha256": actual_hash,
        "expected_sha256": expected_hash,
        "raw_matches_frozen_source": actual_hash == expected_hash,
        "matches_frozen_source": actual_hash == expected_hash,
    }
    observations.append(observation)
    if actual_hash == expected_hash:
        return actual_hash

    try:
        accepted_normalized = mworks_whitespace_normal_form(current_bytes) == mworks_whitespace_normal_form(frozen_source_bytes)
    except UnicodeDecodeError as exc:
        raise RuntimeError(
            f"Protected source hash changed during {phase}: {relative(source_file)}: "
            f"{actual_hash} != {expected_hash}; source is not UTF-8"
        ) from exc
    observation.update(
        {
            "whitespace_normalized_sha256": hashlib.sha256(mworks_whitespace_normal_form(current_bytes)).hexdigest(),
            "frozen_snapshot_sha256": frozen_hash,
            "frozen_whitespace_normalized_sha256": hashlib.sha256(
                mworks_whitespace_normal_form(frozen_source_bytes)
            ).hexdigest(),
            "frozen_snapshot_path": frozen_snapshot_path,
        }
    )
    if not accepted_normalized:
        raise RuntimeError(
            f"Protected source hash changed during {phase}: {relative(source_file)}: "
            f"{actual_hash} != {expected_hash}"
        )
    source_file.write_bytes(frozen_source_bytes)
    restored_hash = sha256(source_file)
    observation.update(
        {
            "native_whitespace_only": True,
            "restored_sha256": restored_hash,
            "normalized_source_restored": restored_hash == expected_hash,
            "matches_frozen_source": restored_hash == expected_hash,
        }
    )
    if restored_hash != expected_hash:
        raise RuntimeError(
            f"Protected source restoration failed during {phase}: {relative(source_file)}: "
            f"{restored_hash} != {expected_hash}"
        )
    binding.setdefault("accepted_native_source_normalizations", []).append(
        {
            "phase": phase,
            "original_sha256": actual_hash,
            "restored_sha256": restored_hash,
            "rule": "utf8_line_endings_trailing_horizontal_whitespace_and_terminal_newline_only",
            "frozen_snapshot_path": frozen_snapshot_path,
        }
    )
    return restored_hash


def sync_target_protection_aliases(record: dict[str, Any]) -> None:
    """Keep target compatibility fields bound to the target protected source."""

    protected = record.get("protected_sources")
    if not isinstance(protected, list):
        return
    target_binding = next(
        (item for item in protected if isinstance(item, dict) and "target" in item.get("roles", [])),
        None,
    )
    if not isinstance(target_binding, dict):
        return
    observations = target_binding.get("hash_observations")
    if isinstance(observations, list):
        record["target_hash_observations"] = observations
    expected_hash = target_binding.get("expected_sha256")
    if isinstance(expected_hash, str):
        record["verified_target_sha256"] = expected_hash
    snapshot = target_binding.get("frozen_snapshot")
    if isinstance(snapshot, dict):
        record["frozen_target_snapshot"] = dict(snapshot)


def verify_protected_sources(record: dict[str, Any], phase: str) -> dict[str, str]:
    """Verify every target/core/prerequisite source at a single lifecycle phase."""

    protected = record.get("protected_sources")
    if not isinstance(protected, list) or not protected:
        raise RuntimeError("Route has no frozen protected source set")
    verified: dict[str, str] = {}
    for binding in protected:
        if not isinstance(binding, dict):
            raise RuntimeError("Protected source record is not an object")
        path_text = binding.get("path")
        if not isinstance(path_text, str):
            raise RuntimeError("Protected source path is absent")
        source_file = ROOT / path_text
        try:
            source_file.resolve().relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(f"Protected source leaves repository: {path_text}") from exc
        verified[path_text] = verify_frozen_protected_source_hash(binding, source_file, phase)
    sync_target_protection_aliases(record)
    return verified


def parse_declared_stop_time(model_file: Path) -> float:
    text = model_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"\bStopTime\s*=\s*([0-9]+(?:\.[0-9]+)?)", text)
    if not match:
        return 1.0
    value = float(match.group(1))
    if value <= 0.0:
        raise ValueError(f"Invalid declared StopTime in {model_file}: {value}")
    return value


def route_variables(row: dict[str, Any]) -> dict[str, str]:
    values = row.get("probe_contract", {}).get("result_variables")
    if not isinstance(values, list) or not values:
        raise ValueError(f"{row['scheme_id']}: matrix has no result variables")
    variables = {"time": "time"}
    for index, value in enumerate(values, start=1):
        if not isinstance(value, str) or not value.strip():
            continue
        variables[f"result_{index:02d}"] = value.strip()
    if len(variables) == 1:
        raise ValueError(f"{row['scheme_id']}: matrix result variables are empty")
    return variables


def route_profile(row: dict[str, Any], model_file: Path) -> dict[str, Any]:
    evidence_class = row["evidence_class"]
    if evidence_class == "internal_fixed_input_probe":
        return {
            "target_time": INTERNAL_TARGET_TIME,
            "metrics_profile": "diagnostics_smoke",
            "variables": route_variables(row),
            "result_role": "internal_fixed_input_response",
        }
    if evidence_class == "whole_aircraft_minimum_closure":
        stop_time = parse_declared_stop_time(model_file)
        return {
            "target_time": [0.0, stop_time],
            "metrics_profile": "standard_tracking",
            "variables": dict(DEFAULT_VARIABLES),
            "result_role": "formal_whole_aircraft_minimum_closure",
        }
    raise ValueError(f"{row['scheme_id']}: unsupported evidence class {evidence_class}")


def classify_error(error: BaseException | str) -> str:
    text = str(error)
    if LICENSE_OR_LOGIN_RE.search(text):
        return "license_or_login"
    if TOPOLOGY_RE.search(text):
        return "graphical_topology"
    if INTERNAL_RE.search(text):
        return "internal_or_mcp"
    if "check" in text.lower():
        return "model_check_failed"
    if "result" in text.lower() or "variable" in text.lower():
        return "result_binding_failed"
    return "execution_failed"


def json_response_payload(event: dict[str, Any]) -> Any:
    response = event.get("result")
    if not isinstance(response, dict):
        return response
    structured = response.get("structuredContent")
    if isinstance(structured, dict) and isinstance(structured.get("result"), str):
        try:
            return json.loads(structured["result"])
        except json.JSONDecodeError:
            return structured["result"]
    content = response.get("content")
    if isinstance(content, list) and content and isinstance(content[0], dict):
        text = content[0].get("text")
        if isinstance(text, str):
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
    return response


def extract_tool_log(log_path: Path, tool_name: str, output: Path) -> dict[str, Any] | None:
    if not log_path.is_file():
        return None
    requests: dict[Any, dict[str, Any]] = {}
    pairs: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("direction") == "request":
            requests[event.get("id")] = event
        elif event.get("direction") == "response" and event.get("id") in requests:
            request = requests[event["id"]]
            params = request.get("params", {})
            if params.get("name") == tool_name:
                pairs.append(
                    {
                        "request": request,
                        "response": event,
                        "payload": json_response_payload(event),
                    }
                )
    if not pairs:
        return None
    payload = {"tool": tool_name, "entries": pairs}
    write_json(output, payload)
    return payload


def mworks_pid_for_port(port: Any) -> int | None:
    if not isinstance(port, int) or port <= 0:
        return None
    command = (
        "$connection = Get-NetTCPConnection -LocalPort "
        f"{port} -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; "
        "if ($connection) { $connection.OwningProcess }"
    )
    completed = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", command],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=15,
        check=False,
    )
    try:
        return int(completed.stdout.strip())
    except ValueError:
        return None


def show_native_plot(
    client: JsonlMcpClient,
    *,
    native_result: Path,
    variables: dict[str, str],
) -> dict[str, Any]:
    result_file = windows_path(native_result)
    plot_vars = [value for alias, value in variables.items() if alias != "time"]
    source = f"""
import mworks.sysplorer as ModelingPy

results = {{}}
try:
    results["remove_plots"] = ModelingPy.RemovePlots()
except Exception as exc:
    results["remove_plots_error"] = repr(exc)
try:
    results["open_result"] = ModelingPy.OpenResult({result_file!r})
except Exception as exc:
    results["open_result_error"] = repr(exc)
try:
    results["create_plot"] = ModelingPy.CreatePlot(
        id=1,
        x="time",
        y={plot_vars!r},
        resultFile={result_file!r},
    )
except Exception as exc:
    results["create_plot_error"] = repr(exc)
RUN_SCRIPT_RESULT = results
"""
    result = client.call_tool(
        "call_code",
        {"mode": "run_script", "payload": {"python_source": source}},
        timeout_s=60,
    )
    nested = result.get("run_script_result") if isinstance(result.get("run_script_result"), dict) else {}
    if not result.get("ok") or not nested.get("create_plot"):
        raise RuntimeError(f"Native result plot failed: {result}")
    # CreatePlot is asynchronous from the Qt paint cycle.  Give the native
    # result-viewer window one bounded paint interval before PrintWindow.
    time.sleep(0.8)
    return result


def result_viewer_title_pattern(target_class: str) -> str:
    leaf = target_class.rsplit(".", 1)[-1]
    return rf"^{re.escape(leaf)}(?:\[.*\])?\s+-\s+结果查看器$"


def validate_result_window_capture(
    image_path: Path,
    selected: dict[str, Any],
    target_class: str,
) -> dict[str, Any]:
    """Reject a model canvas or blank result window before it reaches reports."""
    expected_title = result_viewer_title_pattern(target_class)
    title = str(selected.get("title") or "")
    title_matches = bool(re.match(expected_title, title))
    if not title_matches:
        return {
            "accepted": False,
            "reason": "capture title is not the route-bound native result viewer",
            "expected_title_regex": expected_title,
            "captured_title": title,
        }

    try:
        with Image.open(image_path) as original:
            image = original.convert("RGB")
        width, height = image.size
        # Exclude the title bar/ribbon.  A rendered plot must retain coloured
        # trace pixels in the chart body; an empty chart or Sysplorer canvas
        # should not pass on dimensions alone.
        chart = image.crop((0, max(1, int(height * 0.20)), width, height))
        trace_pixels = 0
        for red, green, blue in chart.getdata():
            upper = max(red, green, blue)
            lower = min(red, green, blue)
            if upper >= 90 and upper - lower >= 80 and red + green + blue <= 700:
                trace_pixels += 1
        minimum_trace_pixels = max(120, int(chart.width * chart.height * 0.00005))
        accepted = trace_pixels >= minimum_trace_pixels
        return {
            "accepted": accepted,
            "expected_title_regex": expected_title,
            "captured_title": title,
            "image_width": width,
            "image_height": height,
            "chart_trace_pixels": trace_pixels,
            "minimum_trace_pixels": minimum_trace_pixels,
            "reason": None if accepted else "native result viewer contains no detectable rendered curve trace",
        }
    except Exception as exc:
        return {
            "accepted": False,
            "reason": f"cannot inspect captured native result window: {exc!r}",
            "expected_title_regex": expected_title,
            "captured_title": title,
        }


def capture_phase(
    *,
    run_dir: Path,
    phase: str,
    target_class: str,
    expected_pid: int | None,
    destination: Path,
    capture_surface: str,
) -> dict[str, Any]:
    capture_dir = run_dir / "screenshots" / f"capture_{phase}"
    leaf = target_class.rsplit(".", 1)[-1]
    if capture_surface == "model":
        title_regex = f"^{re.escape(leaf)}.*Sysplorer.*$"
    elif capture_surface == "result_viewer":
        title_regex = result_viewer_title_pattern(target_class)
    else:
        raise ValueError(f"Unsupported capture surface: {capture_surface}")
    command = [
        str(CAPTURE_CMD),
        "-TitleRegex",
        title_regex,
        "-ProcessRegex",
        "^mworks$",
        "-OutDir",
        str(capture_dir),
        "-RestoreMinimized",
        "-MinimizeAfter",
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=75,
        check=False,
    )
    capture_stdout = (completed.stdout or "").strip()
    capture_stderr = (completed.stderr or "").strip()
    source_manifest = capture_dir / "capture_manifest.json"
    captures = read_json(source_manifest) if source_manifest.is_file() else []
    if not isinstance(captures, list):
        captures = []
    candidates = [
        item
        for item in captures
        if isinstance(item, dict)
        and item.get("path")
        and item.get("capture_width", 0) >= 500
        and item.get("capture_height", 0) >= 300
        and not item.get("still_minimized_at_capture")
    ]
    if expected_pid is not None:
        candidates = [item for item in candidates if item.get("id") == expected_pid]
    if len(candidates) != 1:
        raise RuntimeError(
            f"{phase}: expected one full MWORKS capture for {leaf} pid={expected_pid}, "
            f"found {len(candidates)}; capture stdout={capture_stdout} stderr={capture_stderr}"
        )
    selected = candidates[0]
    source = Path(str(selected["path"]))
    if not source.is_file() or source.stat().st_size < 10_000:
        raise RuntimeError(f"{phase}: capture file is absent or suspiciously small: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    evidence = {
        "phase": phase,
        "capture_mode": "background_restore_minimize",
        "capture_surface": capture_surface,
        "title_regex": title_regex,
        "target_class": target_class,
        "expected_mworks_pid": expected_pid,
        "source_capture_manifest": relative(source_manifest),
        "source_capture": relative(source),
        "selected": selected,
        "destination": relative(destination),
        "destination_sha256": sha256(destination),
        "destination_bytes": destination.stat().st_size,
        "capture_command_exit_code": completed.returncode,
        "capture_stdout": capture_stdout,
        "capture_stderr": capture_stderr,
    }
    if capture_surface == "result_viewer":
        visual_validation = validate_result_window_capture(destination, selected, target_class)
        evidence["visual_validation"] = visual_validation
        if not visual_validation.get("accepted"):
            raise RuntimeError(f"{phase}: native result-window visual validation failed: {visual_validation}")
    return evidence


def archived_report_refresh_authority(
    row: dict[str, Any],
    destination: Path,
    destination_hash: str,
) -> dict[str, Any] | None:
    """Return evidence authorizing a same-route report-image refresh.

    A report image may have been manually curated after an earlier run.  It is
    therefore never overwritten merely because a new capture differs.  The
    only permitted refresh is one whose current destination hash is bound by a
    *passed*, archived run of this exact route, with the archived native result
    screenshot still present and hash-consistent. A re-frozen route may replace
    its controller target, so the archived and current target hashes are recorded
    rather than required to match. This still does not authorize replacing a
    manually curated report asset.
    """
    scheme_id = str(row["scheme_id"])
    report_destination = relative(destination)
    expected_target = row.get("target") if isinstance(row.get("target"), dict) else {}
    expected_model_hash = expected_target.get("model_sha256")
    archive_root = ROOT / str(row["result_root"]) / "superseded"
    if not archive_root.is_dir() or not isinstance(report_destination, str) or not isinstance(expected_model_hash, str):
        return None

    for archive_dir in sorted((path for path in archive_root.iterdir() if path.is_dir()), reverse=True):
        record_path = archive_dir / "RUN_RECORD.json"
        archived_capture = archive_dir / "screenshots" / "02_result_window.png"
        if not record_path.is_file() or not archived_capture.is_file():
            continue
        try:
            record = read_json(record_path)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(record, dict) or record.get("status") != "passed" or record.get("scheme_id") != scheme_id:
            continue
        matrix = record.get("matrix")
        target = matrix.get("target") if isinstance(matrix, dict) and isinstance(matrix.get("target"), dict) else {}
        archived_model_hash = target.get("model_sha256")
        if not isinstance(archived_model_hash, str) or not archived_model_hash:
            continue
        report = record.get("report_result_screenshot")
        if not isinstance(report, dict):
            continue
        if report.get("destination") != report_destination or report.get("sha256") != destination_hash:
            continue
        if sha256(archived_capture) != destination_hash:
            continue
        return {
            "archive": relative(archive_dir),
            "record": relative(record_path),
            "archived_capture": relative(archived_capture),
            "scheme_id": scheme_id,
            "archived_model_sha256": archived_model_hash,
            "current_model_sha256": expected_model_hash,
            "target_transition": archived_model_hash != expected_model_hash,
            "report_destination": report_destination,
            "destination_sha256_before_refresh": destination_hash,
        }
    return None


def atomic_copy2(source: Path, destination: Path) -> None:
    """Copy a verified report asset without exposing a partial destination."""
    temporary = destination.with_name(f".{destination.name}.{os.getpid()}.{time.time_ns()}.tmp")
    try:
        shutil.copy2(source, temporary)
        if sha256(temporary) != sha256(source):
            raise RuntimeError(f"Atomic report copy hash mismatch: {relative(destination)}")
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def materialize_report_result(row: dict[str, Any], source: Path) -> dict[str, Any] | None:
    required = row.get("required_artifacts")
    report_path = required.get("report_result_screenshot") if isinstance(required, dict) else None
    if not isinstance(report_path, str) or not report_path:
        return None
    destination = ROOT / report_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha256(source)
    existing_hash = sha256(destination) if destination.exists() else None
    refresh_authority = None
    if existing_hash is not None and existing_hash != source_hash:
        refresh_authority = archived_report_refresh_authority(row, destination, existing_hash)
        if refresh_authority is None:
            raise RuntimeError(
                f"Refusing to replace a different report result screenshot: {relative(destination)}"
            )
    if existing_hash != source_hash:
        atomic_copy2(source, destination)
    result = {
        "source": relative(source),
        "destination": relative(destination),
        "sha256": source_hash,
        "bytes": destination.stat().st_size,
    }
    if refresh_authority:
        result["refresh_authority"] = refresh_authority
    return result


def project_file(path_text: object, label: str) -> Path:
    """Resolve one record-declared file while keeping offline repairs in-tree."""

    if not isinstance(path_text, str) or not path_text:
        raise RuntimeError(f"{label} path is absent")
    candidate = (ROOT / path_text).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError(f"{label} leaves the project root: {path_text}") from exc
    return candidate


def png_metadata(path: Path, label: str) -> dict[str, Any]:
    """Validate a whole-window PNG before it is made a report evidence binding."""

    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format != "PNG":
                raise RuntimeError(f"{label} is not PNG")
            width, height = image.size
    except Exception as exc:
        raise RuntimeError(f"{label} is not a readable PNG: {path}") from exc
    if width <= 0 or height <= 0:
        raise RuntimeError(f"{label} has invalid dimensions: {path}")
    return {"path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size, "width": width, "height": height}


def next_report_asset_archive_dir(run_dir: Path) -> Path:
    """Allocate a per-route archive without colliding with ordinary rerun snapshots."""

    root = run_dir / "superseded" / "report_asset_reconciliation"
    root.mkdir(parents=True, exist_ok=True)
    for suffix in range(1000):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        name = stamp if suffix == 0 else f"{stamp}_{suffix:03d}"
        candidate = root / name
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            continue
    raise RuntimeError(f"Unable to allocate report-asset archive below {relative(root)}")


def validate_result_binding_reconciliation(
    row: dict[str, Any],
    record: dict[str, Any],
    run_dir: Path,
) -> tuple[Path, Path, dict[str, Any], dict[str, Any]]:
    """Prove a failed report copy is the only missing G6 acceptance artifact."""

    scheme_id = str(row.get("scheme_id") or "")
    if record.get("scheme_id") != scheme_id:
        raise RuntimeError(f"{scheme_id}: RUN_RECORD scheme_id does not match the frozen matrix")
    if record.get("status") != "result_binding_failed":
        raise RuntimeError(f"{scheme_id}: only result_binding_failed records can be reconciled")

    required = row.get("required_artifacts")
    report_text = required.get("report_result_screenshot") if isinstance(required, dict) else None
    report_destination = project_file(report_text, f"{scheme_id}: report result screenshot")
    expected_error = f"Refusing to replace a different report result screenshot: {relative(report_destination)}"
    error = record.get("error")
    error_message = error.get("message") if isinstance(error, dict) else None
    if error_message != expected_error:
        raise RuntimeError(f"{scheme_id}: result-binding failure is not the guarded report-slot conflict")
    if not report_destination.is_file():
        raise RuntimeError(f"{scheme_id}: existing report result screenshot is missing")

    row_target = row.get("target") if isinstance(row.get("target"), dict) else {}
    record_matrix = record.get("matrix") if isinstance(record.get("matrix"), dict) else {}
    record_target = record_matrix.get("target") if isinstance(record_matrix.get("target"), dict) else {}
    if row_target.get("model_sha256") != record_target.get("model_sha256"):
        raise RuntimeError(f"{scheme_id}: RUN_RECORD target hash differs from the frozen matrix")

    cleanup = record.get("session_cleanup")
    if not isinstance(cleanup, dict) or cleanup.get("verified_closed") is not True:
        raise RuntimeError(f"{scheme_id}: dedicated Sysplorer session was not verified closed")
    post_shutdown = record.get("post_session_source_validation")
    if not isinstance(post_shutdown, dict) or post_shutdown.get("state") != "passed":
        raise RuntimeError(f"{scheme_id}: post-session source validation did not pass")
    protected_hashes = post_shutdown.get("protected_source_sha256")
    if not isinstance(protected_hashes, dict) or not protected_hashes:
        raise RuntimeError(f"{scheme_id}: post-session protected-source hashes are absent")
    for source_text, expected_hash in protected_hashes.items():
        source_file = project_file(source_text, f"{scheme_id}: protected source")
        if not source_file.is_file() or not isinstance(expected_hash, str) or sha256(source_file) != expected_hash:
            raise RuntimeError(f"{scheme_id}: protected source changed after the completed MWORKS session")

    readiness = record.get("result_readiness")
    attempts = readiness.get("attempts") if isinstance(readiness, dict) else None
    if not isinstance(readiness, dict) or readiness.get("state") != "ready" or not isinstance(attempts, list):
        raise RuntimeError(f"{scheme_id}: native result readiness is incomplete")
    if not any(
        isinstance(attempt, dict)
        and attempt.get("time_reaches_expected_stop") is True
        and attempt.get("full_series_ready") is True
        for attempt in attempts
    ):
        raise RuntimeError(f"{scheme_id}: no complete result series reaches the declared stop time")
    native_result = project_file(record.get("native_result_locator"), f"{scheme_id}: native result")
    if not native_result.is_file():
        raise RuntimeError(f"{scheme_id}: native Result.msr is missing")
    metrics = run_dir / "metrics" / "metrics.json"
    if not metrics.is_file():
        raise RuntimeError(f"{scheme_id}: metrics.json is missing")

    source_capture = run_dir / "screenshots" / "02_result_window.png"
    if not source_capture.is_file():
        raise RuntimeError(f"{scheme_id}: current native result-window screenshot is missing")
    source_metadata = png_metadata(source_capture, f"{scheme_id}: native result-window screenshot")
    source_relative = relative(source_capture)
    phase_captures = record.get("mworks_phase_screenshots")
    if not isinstance(phase_captures, list) or not any(
        isinstance(capture, dict)
        and capture.get("phase") == "result_window"
        and capture.get("destination") == source_relative
        and capture.get("destination_sha256") == source_metadata["sha256"]
        for capture in phase_captures
    ):
        raise RuntimeError(f"{scheme_id}: RUN_RECORD does not bind the current native result-window screenshot")
    manifest_path = run_dir / "logs" / "screenshot_manifest.json"
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{scheme_id}: screenshot manifest is unreadable") from exc
    manifest_captures = manifest.get("captures") if isinstance(manifest, dict) else None
    if not isinstance(manifest_captures, list) or not any(
        isinstance(capture, dict)
        and capture.get("phase") == "result_window"
        and capture.get("destination") == source_relative
        and capture.get("destination_sha256") == source_metadata["sha256"]
        for capture in manifest_captures
    ):
        raise RuntimeError(f"{scheme_id}: screenshot manifest does not bind the current result-window screenshot")

    report_metadata = png_metadata(report_destination, f"{scheme_id}: existing report result screenshot")
    if report_metadata["sha256"] == source_metadata["sha256"]:
        raise RuntimeError(f"{scheme_id}: report screenshot already matches the current native capture")
    return report_destination, source_capture, report_metadata, source_metadata


def reconcile_report_result_binding(row: dict[str, Any]) -> dict[str, Any]:
    """Archive one explicitly selected legacy report image and bind its completed native capture.

    This is deliberately an offline remediation path.  It is only available to
    a route whose MWORKS run, result read, screenshot capture, source integrity,
    and dedicated-session cleanup have already succeeded.  It never invokes
    MWORKS and never changes a controller/model source file.
    """

    scheme_id = str(row.get("scheme_id") or "")
    run_dir = project_file(row.get("result_root"), f"{scheme_id}: result root")
    record_path = run_dir / "RUN_RECORD.json"
    try:
        record = read_json(record_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"{scheme_id}: RUN_RECORD is unreadable") from exc
    if not isinstance(record, dict):
        raise RuntimeError(f"{scheme_id}: RUN_RECORD must be an object")

    report_destination, source_capture, report_before, source_metadata = validate_result_binding_reconciliation(
        row, record, run_dir
    )
    archive_dir = next_report_asset_archive_dir(run_dir)
    archived_report = archive_dir / "report_result_before_reconciliation.png"
    archive_manifest = archive_dir / "REPORT_RESULT_ASSET_ARCHIVE_MANIFEST.json"
    original_error = record.get("error")
    reconciliation = {
        "schema": REPORT_RESULT_RECONCILIATION_SCHEMA,
        "scheme_id": scheme_id,
        "reconciled_at": now_iso(),
        "mode": "offline_explicit_report_slot_reconciliation",
        "scope": "Archive the existing unbound report image and bind a completed current native MWORKS result-window capture. No MWORKS session, model source, controller source, or result data was changed.",
        "previous_status": record.get("status"),
        "previous_error": original_error,
        "report_asset_before": report_before,
        "archived_report_asset": relative(archived_report),
        "current_native_result_capture": source_metadata,
        "native_result": relative(project_file(record.get("native_result_locator"), f"{scheme_id}: native result")),
        "metrics": relative(run_dir / "metrics" / "metrics.json"),
        "screenshot_manifest": relative(run_dir / "logs" / "screenshot_manifest.json"),
        "post_session_source_validation": record.get("post_session_source_validation"),
        "session_cleanup": record.get("session_cleanup"),
    }
    try:
        atomic_copy2(report_destination, archived_report)
        if sha256(archived_report) != report_before["sha256"]:
            raise RuntimeError(f"{scheme_id}: archived report asset hash mismatch")
        write_json(archive_manifest, reconciliation)
        atomic_copy2(source_capture, report_destination)
        if sha256(report_destination) != source_metadata["sha256"]:
            raise RuntimeError(f"{scheme_id}: report screenshot copy hash mismatch")

        record["status"] = "passed"
        record.pop("error", None)
        record["report_result_screenshot"] = {
            "source": relative(source_capture),
            "destination": relative(report_destination),
            "sha256": source_metadata["sha256"],
            "bytes": source_metadata["bytes"],
            "reconciliation": {
                "archive_manifest": relative(archive_manifest),
                "archived_report_asset": relative(archived_report),
                "previous_report_sha256": report_before["sha256"],
                "previous_status": "result_binding_failed",
                "mode": "offline_explicit_report_slot_reconciliation",
            },
        }
        record["report_result_binding_reconciliation"] = reconciliation
        record["report_result_binding_reconciled_at"] = now_iso()
        artifact_refs = record.setdefault("artifact_refs", [])
        report_artifact = artifact(report_destination, "figure")
        if isinstance(artifact_refs, list) and report_artifact and not any(
            isinstance(item, dict) and item.get("path") == report_artifact["path"] for item in artifact_refs
        ):
            artifact_refs.append(report_artifact)
        write_json(record_path, record)
    except Exception:
        if archived_report.is_file() and sha256(report_destination) != report_before["sha256"]:
            atomic_copy2(archived_report, report_destination)
        raise
    return {
        "scheme_id": scheme_id,
        "run_record": relative(record_path),
        "report_destination": relative(report_destination),
        "current_capture_sha256": source_metadata["sha256"],
        "archive_manifest": relative(archive_manifest),
        "archived_report_asset": relative(archived_report),
    }


def write_screenshot_manifest(logs_dir: Path, record: dict[str, Any]) -> Path:
    output = logs_dir / "screenshot_manifest.json"
    write_json(
        output,
        {
            "schema": SCREENSHOT_SCHEMA,
            "scheme_id": record.get("scheme_id"),
            "source": record.get("source"),
            "target": record.get("matrix", {}).get("target"),
            "captures": record.get("mworks_phase_screenshots", []),
            "claim_boundary": record.get("claim_boundary"),
        },
    )
    return output


def prepare_route_native_result(
    native_dir: Path,
    target_class: str,
) -> tuple[Path, Path, dict[str, Any]]:
    """Allocate an isolated native-result root for this exact execution.

    ``SimulateModel`` appends ``-1``/``-2`` below a reused root whenever a
    result viewer or a prior run retains a model folder.  Looking for the
    latest sibling afterward is ambiguous and can bind a screenshot to stale
    data.  Each G6 execution therefore gets a new root; old native results are
    retained for provenance and cannot interfere with the current locator.
    """
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_root = native_dir.with_name(f"{native_dir.name}_g6_{stamp}")
    suffix = 1
    while run_root.exists():
        run_root = native_dir.with_name(f"{native_dir.name}_g6_{stamp}_{suffix}")
        suffix += 1
    run_root.mkdir(parents=True, exist_ok=False)
    expected = prepare_native_result_target(native_result_file(run_root, target_class))
    return run_root, expected, {
        "mode": "fresh_root_per_execution",
        "preferred_root": relative(native_dir),
        "root": relative(run_root),
    }


def resolve_written_native_result(native_dir: Path, target_class: str, expected: Path) -> Path:
    """Bind the current run to the actual Result.msr emitted by Sysplorer."""
    if expected.is_file():
        return expected
    leaf = target_class.rsplit(".", 1)[-1]
    candidates = [path for path in native_dir.glob(f"{leaf}*/Result.msr") if path.is_file()]
    if len(candidates) != 1:
        rendered = ", ".join(relative(path) or str(path) for path in candidates)
        raise RuntimeError(
            f"Expected one current native Result.msr under {relative(native_dir)}, found {len(candidates)}: {rendered}"
        )
    return candidates[0]


def _result_time_values(response: dict[str, Any]) -> list[float]:
    """Return a finite time series from one result-manager probe, if available."""
    data = response.get("data") if response.get("ok") else None
    if not (isinstance(data, list) and data and isinstance(data[0], list)):
        return []
    values: list[float] = []
    for value in data[0]:
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return []
        if not math.isfinite(numeric):
            return []
        values.append(numeric)
    return values


def open_native_result_for_reading(client: JsonlMcpClient, native_result: Path) -> dict[str, Any]:
    """Bind a persisted native result to the current Sysplorer result context."""
    result_file = windows_path(native_result)
    source = f"""
import mworks.sysplorer as ModelingPy

results = {{}}
try:
    results["open_result"] = ModelingPy.OpenResult({result_file!r})
except Exception as exc:
    results["open_result_error"] = repr(exc)
RUN_SCRIPT_RESULT = results
"""
    result = client.call_tool(
        "call_code",
        {"mode": "run_script", "payload": {"python_source": source}},
        timeout_s=60,
    )
    nested = result.get("run_script_result") if isinstance(result.get("run_script_result"), dict) else {}
    if not result.get("ok") or nested.get("open_result") is not True:
        raise RuntimeError(f"Native Result.msr OpenResult failed: {result}")
    return result


def wait_for_fresh_result_artifacts(
    client: JsonlMcpClient,
    *,
    model_name: str,
    variables: dict[str, str],
    native_dir: Path,
    expected_native: Path,
    expected_stop_time: float,
    not_before_unix: float,
    timeout_s: float = RESULT_READY_TIMEOUT_S,
    poll_interval_s: float = RESULT_READY_POLL_S,
) -> dict[str, Any]:
    """Wait for this run's native result and complete, non-stale time series.

    Sysplorer can expose a declared result-variable type before the simulator
    has materialized samples. A type probe or a scalar zero at ``end`` is not
    enough to accept a run. This gate binds a result to the current invocation
    only after a fresh ``Result.msr`` and a time sequence through the declared
    stop time both exist.
    """
    if expected_stop_time <= 0:
        raise ValueError(f"expected_stop_time must be positive, got {expected_stop_time}")
    if "time" not in variables:
        raise ValueError("result readiness requires a time variable alias")

    deadline = time.monotonic() + max(0.0, timeout_s)
    started_monotonic = time.monotonic()
    tolerance = max(1e-6, abs(expected_stop_time) * 1e-3)
    attempts: list[dict[str, Any]] = []
    last_read_error: str | None = None
    opened_native_result: Path | None = None

    while True:
        native_result: Path | None = None
        series: dict[str, list[float]] | None = None
        attempt: dict[str, Any] = {"elapsed_s": round(time.monotonic() - started_monotonic, 3)}
        try:
            candidate = resolve_written_native_result(native_dir, model_name, expected_native)
            mtime = candidate.stat().st_mtime
            attempt["native_result"] = relative(candidate)
            attempt["native_result_mtime_unix"] = mtime
            attempt["native_result_fresh"] = mtime >= not_before_unix - 2.0
            if attempt["native_result_fresh"]:
                native_result = candidate
        except Exception as exc:
            attempt["native_result_error"] = str(exc)

        if native_result is not None and native_result != opened_native_result:
            try:
                open_native_result_for_reading(client, native_result)
                opened_native_result = native_result
                attempt["native_result_opened"] = True
            except Exception as exc:
                attempt["native_result_open_error"] = str(exc)
                last_read_error = str(exc)

        try:
            time_probe = client.call_tool(
                "result_manager",
                {
                    "action": "get_vars_values",
                    "model_name": model_name,
                    "var_names": [variables["time"]],
                },
                timeout_s=45,
            )
            time_values = _result_time_values(time_probe)
            attempt["time_sample_count"] = len(time_values)
            if time_values:
                attempt["time_start"] = time_values[0]
                attempt["time_end"] = time_values[-1]
                attempt["time_reaches_expected_stop"] = time_values[-1] >= expected_stop_time - tolerance
            else:
                attempt["time_reaches_expected_stop"] = False
        except Exception as exc:
            attempt["time_probe_error"] = str(exc)
            attempt["time_reaches_expected_stop"] = False

        if native_result is not None and attempt.get("time_reaches_expected_stop"):
            try:
                candidate_series = read_result_series(client, model_name, variables)
                full_time = candidate_series.get("time", [])
                if (
                    len(full_time) > 10
                    and all(math.isfinite(float(value)) for value in full_time)
                    and float(full_time[-1]) >= expected_stop_time - tolerance
                ):
                    series = candidate_series
                    attempt["full_series_ready"] = True
                else:
                    attempt["full_series_ready"] = False
                    attempt["full_series_time_sample_count"] = len(full_time)
                    attempt["full_series_time_end"] = float(full_time[-1]) if full_time else None
                    last_read_error = "full result series is incomplete or does not reach the expected stop time"
            except Exception as exc:
                attempt["full_series_ready"] = False
                last_read_error = str(exc)
                attempt["full_series_error"] = last_read_error

        attempts.append(attempt)
        if native_result is not None and series is not None:
            return {
                "native_result": native_result,
                "series": series,
                "readiness": {
                    "state": "ready",
                    "expected_stop_time": expected_stop_time,
                    "timeout_s": timeout_s,
                    "attempt_count": len(attempts),
                    "attempts": attempts,
                },
            }
        if time.monotonic() >= deadline:
            break
        time.sleep(max(0.0, poll_interval_s))

    last = attempts[-1] if attempts else {}
    raise RuntimeError(
        "Result readiness timeout: this invocation did not produce a fresh native Result.msr "
        f"and a complete time series through {expected_stop_time:g}s within {timeout_s:g}s; "
        f"last_observation={last}; last_full_series_error={last_read_error}"
    )


def existing_terminal_record(run_dir: Path) -> dict[str, Any] | None:
    record_path = run_dir / "RUN_RECORD.json"
    if not record_path.is_file():
        return None
    try:
        record = read_json(record_path)
    except (OSError, json.JSONDecodeError):
        return None
    if isinstance(record, dict) and record.get("status") in {
        "passed",
        "model_check_failed",
        "result_binding_failed",
        "graphical_topology",
        "execution_failed",
        "source_hash_mismatch",
        "session_cleanup_unverified",
        "screenshot_failed",
        "license_or_login",
        "internal_or_mcp",
    }:
        return record
    return None


def status_summary(matrix: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for row in matrix["rows"]:
        run_dir = ROOT / row["result_root"]
        record = existing_terminal_record(run_dir)
        status = record.get("status") if record else "pending"
        counts[status] = counts.get(status, 0) + 1
        rows.append(
            {
                "scheme_id": row["scheme_id"],
                "category": row["category"],
                "evidence_class": row["evidence_class"],
                "status": status,
                "run_record": relative(run_dir / "RUN_RECORD.json") if record else None,
            }
        )
    return {
        "schema": STATUS_SCHEMA,
        "generated_at": now_iso(),
        "matrix": relative(MATRIX_PATH),
        "matrix_sha256": sha256(MATRIX_PATH),
        "summary": {
            "route_count": len(rows),
            "terminal_count": sum(value for key, value in counts.items() if key != "pending"),
            "passed_count": counts.get("passed", 0),
            "pending_count": counts.get("pending", 0),
            "status_counts": counts,
        },
        "rows": rows,
    }


def write_status(matrix: dict[str, Any]) -> None:
    write_json(STATUS_PATH, status_summary(matrix))


def close_dedicated_session(
    client: JsonlMcpClient,
    *,
    session: dict[str, Any] | None,
    output: Path,
) -> dict[str, Any]:
    """Close only the Sysplorer instance bound to this runner's MCP port."""
    port = session.get("dedicated_sysplorer_port") if isinstance(session, dict) else None
    expected_pid = session.get("mworks_pid") if isinstance(session, dict) else None
    cleanup: dict[str, Any] = {
        "schema": SESSION_CLEANUP_SCHEMA,
        "created_at": now_iso(),
        "scope": "runner-owned dedicated Sysplorer session only; no pre-existing MWORKS instance is targeted",
        "dedicated_sysplorer_port": port,
        "expected_mworks_pid": expected_pid,
        "requested": False,
        "verified_closed": False,
    }
    if not isinstance(port, int) or port <= 0:
        cleanup["reason"] = "no dedicated Sysplorer port was recorded"
        write_json(output, cleanup)
        return cleanup

    if not isinstance(expected_pid, int) or expected_pid <= 0:
        expected_pid = mworks_pid_for_port(port)
        cleanup["expected_mworks_pid"] = expected_pid
    if not isinstance(expected_pid, int) or expected_pid <= 0:
        cleanup["reason"] = "dedicated Sysplorer port has no resolvable MWORKS process before shutdown"
        write_json(output, cleanup)
        return cleanup

    cleanup["requested"] = True
    try:
        cleanup["shutdown_response"] = client.call_tool(
            "session_manager",
            {"action": "shutdown", "exit_port": port},
            timeout_s=60,
        )
        # The MWORKS exit API acknowledges before the dedicated process has
        # necessarily released its TCP port. Keep a bounded grace period so a
        # successful, runner-owned close is not reported as a false cleanup
        # failure merely because Sysplorer is flushing its session state.
        deadline = time.monotonic() + SESSION_CLEANUP_TIMEOUT_S
        observed_pid: int | None = None
        while time.monotonic() < deadline:
            observed_pid = mworks_pid_for_port(port)
            if observed_pid is None or observed_pid != expected_pid:
                cleanup["verified_closed"] = True
                break
            time.sleep(0.5)
        cleanup["observed_mworks_pid_after_shutdown"] = observed_pid
        cleanup["post_shutdown_wait_seconds"] = SESSION_CLEANUP_TIMEOUT_S
        if not cleanup["verified_closed"]:
            cleanup["reason"] = "dedicated Sysplorer port still belongs to the expected runner-owned MWORKS process"
    except Exception as exc:
        cleanup["error"] = {
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }

    # A timed-out MCP request can leave its runner-owned MWORKS process alive
    # even though the normal session-manager shutdown never returned.  Do not
    # kill arbitrary MWORKS instances: this fallback is permitted only when
    # the recorded dedicated port still resolves to the same recorded PID.
    if cleanup["verified_closed"] is not True:
        observed_before_force = mworks_pid_for_port(port)
        force_cleanup: dict[str, Any] = {
            "requested": False,
            "expected_mworks_pid": expected_pid,
            "observed_mworks_pid_before_force": observed_before_force,
            "scope": "runner-owned dedicated MWORKS PID only",
        }
        if observed_before_force == expected_pid:
            force_cleanup["requested"] = True
            try:
                forced = subprocess.run(
                    ["taskkill", "/PID", str(expected_pid), "/F"],
                    cwd=ROOT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    timeout=30,
                    check=False,
                )
                force_cleanup["exit_code"] = forced.returncode
                force_cleanup["stdout"] = forced.stdout
                force_cleanup["stderr"] = forced.stderr
                deadline = time.monotonic() + SESSION_CLEANUP_TIMEOUT_S
                observed_after_force: int | None = observed_before_force
                while time.monotonic() < deadline:
                    observed_after_force = mworks_pid_for_port(port)
                    if observed_after_force is None or observed_after_force != expected_pid:
                        cleanup["verified_closed"] = True
                        break
                    time.sleep(0.5)
                force_cleanup["observed_mworks_pid_after_force"] = observed_after_force
                force_cleanup["verified_closed"] = cleanup["verified_closed"] is True
                if cleanup["verified_closed"]:
                    cleanup["observed_mworks_pid_after_shutdown"] = observed_after_force
                    cleanup["reason"] = "MCP shutdown did not verify closure; guarded runner-owned process termination verified it"
            except Exception as exc:
                force_cleanup["error"] = {
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                }
        else:
            force_cleanup["reason"] = "dedicated port no longer resolves to the recorded runner-owned MWORKS PID; force termination was not allowed"
        cleanup["force_process_termination"] = force_cleanup
    cleanup["finished_at"] = now_iso()
    write_json(output, cleanup)
    return cleanup


def load_frozen_target_snapshot(
    record: dict[str, Any],
    expected_hash: str,
) -> tuple[bytes | None, str | None]:
    """Read a runner-captured frozen source snapshot when a record has one."""

    snapshot = record.get("frozen_target_snapshot")
    if snapshot is None:
        return None, None
    if not isinstance(snapshot, dict):
        raise RuntimeError("Frozen target snapshot metadata is not an object")
    path_text = snapshot.get("path")
    if not isinstance(path_text, str):
        raise RuntimeError("Frozen target snapshot path is absent")
    snapshot_path = ROOT / path_text
    try:
        snapshot_path.resolve().relative_to(ROOT.resolve())
    except ValueError as exc:
        raise RuntimeError("Frozen target snapshot path leaves the repository") from exc
    if not snapshot_path.is_file():
        raise RuntimeError(f"Frozen target snapshot is missing: {relative(snapshot_path)}")
    snapshot_bytes = snapshot_path.read_bytes()
    snapshot_hash = hashlib.sha256(snapshot_bytes).hexdigest()
    if snapshot_hash != expected_hash:
        raise RuntimeError(
            f"Frozen target snapshot hash does not match the matrix: {snapshot_hash} != {expected_hash}"
        )
    declared_hash = snapshot.get("sha256")
    if declared_hash is not None and declared_hash != snapshot_hash:
        raise RuntimeError("Frozen target snapshot metadata hash differs from its file")
    return snapshot_bytes, relative(snapshot_path)


def git_head_frozen_target_snapshot(model_file: Path, expected_hash: str) -> tuple[bytes, str]:
    """Recover a legacy run only when HEAD exactly owns its matrix source bytes."""

    try:
        project_relative = model_file.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise RuntimeError("Legacy frozen-source recovery path leaves the repository") from exc
    blob = subprocess.run(
        ["git", "show", f"HEAD:{project_relative}"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if blob.returncode != 0:
        detail = blob.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Unable to read HEAD source for legacy recovery: {detail}")
    source_hash = hashlib.sha256(blob.stdout).hexdigest()
    if source_hash != expected_hash:
        raise RuntimeError(
            f"HEAD source hash does not match the frozen matrix target: {source_hash} != {expected_hash}"
        )
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )
    if revision.returncode != 0:
        raise RuntimeError("Unable to identify HEAD for legacy frozen-source recovery")
    return blob.stdout, f"git:HEAD:{project_relative}@{revision.stdout.strip()}"


def load_prior_protected_snapshot(
    record: dict[str, Any],
    model_file: Path,
    expected_hash: str,
) -> tuple[bytes | None, str | None]:
    """Reuse a prior exact protected-source snapshot when one matches a source."""

    protected = record.get("protected_sources")
    if not isinstance(protected, list):
        return None, None
    wanted_path = relative(model_file)
    for binding in protected:
        if not isinstance(binding, dict) or binding.get("path") != wanted_path:
            continue
        if binding.get("expected_sha256") != expected_hash:
            raise RuntimeError("Prior protected source snapshot has a conflicting expected hash")
        return load_frozen_protected_snapshot(binding)
    return None, None


def apply_after_session_shutdown_validation(
    *,
    record: dict[str, Any],
    model_file: Path,
    expected_hash: str,
    cleanup: dict[str, Any] | None,
    cleanup_log: Path,
) -> dict[str, Any]:
    """Bind a completed route to the source state after its MWORKS process exits.

    Sysplorer can defer native graphical serialization until its dedicated
    process exits. A route is therefore not source-bound merely because the
    bytes matched before ``RUN_RECORD.json`` was written. This function is
    deliberately file-only: it runs only after the runner-owned process is
    confirmed closed and may restore the same strictly whitespace-only form as
    the in-session guard.
    """
    cleanup_reference = {
        "log": relative(cleanup_log),
        "requested": bool(cleanup.get("requested")) if isinstance(cleanup, dict) else False,
        "verified_closed": bool(cleanup.get("verified_closed")) if isinstance(cleanup, dict) else False,
        "finished_at": cleanup.get("finished_at") if isinstance(cleanup, dict) else None,
    }
    record["session_cleanup"] = cleanup_reference
    outcome: dict[str, Any] = {
        "scheme_id": record.get("scheme_id"),
        "status_before_validation": record.get("status"),
        "cleanup_verified_closed": cleanup_reference["verified_closed"],
        "integrity_ok": False,
    }

    if cleanup_reference["verified_closed"] is not True:
        if record.get("status") == "passed":
            record["status"] = "session_cleanup_unverified"
            record["error"] = {
                "message": "Runner-owned dedicated Sysplorer session was not verified closed; post-session source validation was not accepted.",
            }
        record["post_session_source_validation"] = {
            "phase": "after_session_shutdown",
            "state": "not_run",
            "reason": "dedicated_session_cleanup_not_verified",
        }
        outcome["status"] = record.get("status")
        outcome["reason"] = "dedicated_session_cleanup_not_verified"
        return outcome

    try:
        if isinstance(record.get("protected_sources"), list) and record["protected_sources"]:
            protected_hashes = verify_protected_sources(record, "after_session_shutdown")
            restored_hash = protected_hashes.get(relative(model_file) or str(model_file))
            if restored_hash != expected_hash:
                raise RuntimeError("Protected target source was not present in the post-session source set")
        else:
            # Preserve auditability of records created before the protected-core
            # contract. They remain legacy target-only records rather than being
            # silently upgraded to full source-bound evidence.
            frozen_target_bytes, frozen_snapshot_path = load_frozen_target_snapshot(record, expected_hash)
            restored_hash = verify_frozen_target_hash(
                record,
                model_file,
                expected_hash,
                "after_session_shutdown",
                frozen_target_bytes=frozen_target_bytes,
                frozen_snapshot_path=frozen_snapshot_path,
            )
    except Exception as exc:
        record["status"] = "source_hash_mismatch"
        record["error"] = {
            "message": str(exc),
            "traceback": traceback.format_exc(),
        }
        record["post_session_source_validation"] = {
            "phase": "after_session_shutdown",
            "state": "source_hash_mismatch",
        }
        outcome.update(
            {
                "status": "source_hash_mismatch",
                "reason": str(exc),
            }
        )
        return outcome

    record["post_session_source_validation"] = {
        "phase": "after_session_shutdown",
        "state": "passed",
        "verified_target_sha256": restored_hash,
    }
    if isinstance(record.get("protected_sources"), list) and record["protected_sources"]:
        record["post_session_source_validation"]["protected_source_sha256"] = protected_hashes
    outcome.update(
        {
            "status": record.get("status"),
            "integrity_ok": True,
            "verified_target_sha256": restored_hash,
        }
    )
    return outcome


def reconcile_routes_after_session_shutdown(
    *,
    rows: list[dict[str, Any]],
    cleanup: dict[str, Any] | None,
    cleanup_log: Path,
) -> list[dict[str, Any]]:
    """Persist the post-shutdown source guard for every route attempted in a batch."""
    outcomes: list[dict[str, Any]] = []
    for row in rows:
        scheme_id = str(row.get("scheme_id") or "")
        run_dir = ROOT / str(row.get("result_root") or "")
        record_path = run_dir / "RUN_RECORD.json"
        outcome: dict[str, Any] = {
            "scheme_id": scheme_id,
            "run_record": relative(record_path),
            "integrity_ok": False,
        }
        if not record_path.is_file():
            outcome.update({"status": "missing_run_record", "reason": "post-session validation has no route record"})
            outcomes.append(outcome)
            continue
        try:
            record = read_json(record_path)
            if not isinstance(record, dict):
                raise ValueError("RUN_RECORD root is not an object")
            target = row.get("target")
            if not isinstance(target, dict):
                raise ValueError("matrix target is not an object")
            model_file_text = target.get("model_file")
            expected_hash = target.get("model_sha256")
            if not isinstance(model_file_text, str) or not isinstance(expected_hash, str):
                raise ValueError("matrix target source binding is incomplete")
            result = apply_after_session_shutdown_validation(
                record=record,
                model_file=ROOT / model_file_text,
                expected_hash=expected_hash,
                cleanup=cleanup,
                cleanup_log=cleanup_log,
            )
            record["post_session_validation_finished_at"] = now_iso()
            write_json(record_path, record)
            outcome.update(result)
        except Exception as exc:
            outcome.update(
                {
                    "status": "post_session_validation_failed",
                    "reason": str(exc),
                }
            )
        outcomes.append(outcome)
    return outcomes


def repair_native_whitespace_rows(rows: list[dict[str, Any]]) -> tuple[Path, bool]:
    """Restore only demonstrably native whitespace drift without opening MWORKS.

    This recovery command is for records stopped by the post-session source
    guard. The normalized current bytes must match an exact frozen source whose
    hash is bound to the matrix before the runner restores it, so it cannot
    repair a changed controller equation, port, parameter, or connection.
    """

    repair_root = MATRIX_PATH.parent / "native_serialization_repairs"
    repair_path = repair_root / f"native_whitespace_repair_{time.strftime('%Y%m%d_%H%M%S')}.json"
    entries: list[dict[str, Any]] = []
    all_restored = True
    for row in rows:
        scheme_id = str(row.get("scheme_id") or "")
        entry: dict[str, Any] = {"scheme_id": scheme_id, "status": "rejected"}
        try:
            run_root_text = row.get("result_root")
            if not isinstance(run_root_text, str):
                raise RuntimeError("matrix result root is incomplete")
            run_record_path = ROOT / run_root_text / "RUN_RECORD.json"
            prior_record = read_json(run_record_path) if run_record_path.is_file() else {}
            if not isinstance(prior_record, dict):
                raise RuntimeError("existing route record is not an object")
            repaired_sources: list[dict[str, Any]] = []
            for declared in declared_protected_sources(row):
                model_file = ROOT / str(declared["path"])
                expected_hash = str(declared["expected_sha256"])
                before_hash = sha256(model_file)
                frozen_source_bytes, frozen_snapshot_path = load_prior_protected_snapshot(
                    prior_record,
                    model_file,
                    expected_hash,
                )
                if frozen_source_bytes is None:
                    frozen_source_bytes, frozen_snapshot_path = git_head_frozen_target_snapshot(
                        model_file,
                        expected_hash,
                    )
                binding: dict[str, Any] = {
                    "path": relative(model_file),
                    "expected_sha256": expected_hash,
                    "roles": list(declared["roles"]),
                    "model_classes": list(declared["model_classes"]),
                    "hash_observations": [],
                }
                restored_hash = verify_frozen_protected_source_hash(
                    binding,
                    model_file,
                    "manual_native_whitespace_repair",
                    frozen_source_bytes=frozen_source_bytes,
                    frozen_snapshot_path=frozen_snapshot_path,
                )
                repaired_sources.append(
                    {
                        "path": relative(model_file),
                        "roles": list(declared["roles"]),
                        "expected_sha256": expected_hash,
                        "before_sha256": before_hash,
                        "restored_sha256": restored_hash,
                        "frozen_source_origin": frozen_snapshot_path,
                        "observations": binding["hash_observations"],
                    }
                )
            entry.update(
                {
                    "status": "restored",
                    "protected_sources": repaired_sources,
                }
            )
        except Exception as exc:
            entry["reason"] = str(exc)
            all_restored = False
        entries.append(entry)
    write_json(
        repair_path,
        {
            "schema": "mosim.g6_native_whitespace_repair.v1",
            "generated_at": now_iso(),
            "matrix": {"path": relative(MATRIX_PATH), "sha256": sha256(MATRIX_PATH)},
            "claim_boundary": "File-only recovery. It restores source bytes only when current and frozen bytes have an identical native whitespace normal form, while the exact frozen snapshot hashes to the matrix target. Legacy records may use the exact matching HEAD blob as that snapshot. It does not execute MWORKS or validate controller behavior.",
            "entries": entries,
            "ok": all_restored,
        },
    )
    return repair_path, all_restored


def run_route(
    *,
    client: JsonlMcpClient,
    row: dict[str, Any],
    session: dict[str, Any],
    expected_pid: int | None,
    superseded_record_archive: str | None = None,
) -> dict[str, Any]:
    scheme_id = str(row["scheme_id"])
    run_dir = ROOT / row["result_root"]
    logs_dir = run_dir / "logs"
    raw_dir = run_dir / "raw"
    metrics_dir = run_dir / "metrics"
    screenshots_dir = run_dir / "screenshots"
    for directory in (logs_dir, raw_dir, metrics_dir, screenshots_dir):
        directory.mkdir(parents=True, exist_ok=True)

    log_path = logs_dir / "mcp.jsonl"
    log_path.write_text("", encoding="utf-8")
    client.set_log_path(log_path)
    model_file = ROOT / row["target"]["model_file"]
    target_class = str(row["target"]["model_class"])
    start_at = now_iso()
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "scheme_id": scheme_id,
        "category": row["category"],
        "evidence_class": row["evidence_class"],
        "claim_boundary": row["claim_boundary"],
        "source": "MWORKS_MCP",
        "started_at": start_at,
        "status": "running",
        "matrix": {
            "path": relative(MATRIX_PATH),
            "sha256": sha256(MATRIX_PATH),
            "target": row["target"],
            "model_load_prerequisites": row.get("model_load_prerequisites", []),
            "controller_core": row["controller_core"],
            "probe_contract": row["probe_contract"],
        },
        "session": session,
        "will_not_click_activation_login": True,
        "live_mworks_touched": True,
        "mworks_phase_screenshots": [],
        "mworks_phase_observations": [],
        "artifact_refs": [],
        "model_load_prerequisites": [],
        "target_hash_observations": [],
    }
    if superseded_record_archive:
        record["supersedes"] = superseded_record_archive

    try:
        freeze_protected_sources(row=row, raw_dir=raw_dir, record=record)
        verify_protected_sources(record, "before_load")
        profile = route_profile(row, model_file)
        record["run_profile"] = {
            "target_time": profile["target_time"],
            "metrics_profile": profile["metrics_profile"],
            "variables": profile["variables"],
            "result_role": profile["result_role"],
        }
        load_route_model_prerequisites(client, row, record["model_load_prerequisites"])
        verify_protected_sources(record, "after_prerequisite_load")
        load_result = client.call_tool(
            "model_manager",
            {
                "action": "load_file",
                "file_path": str(model_file),
                # A forced target reload unloads project-root classes and would
                # discard the hash-bound Sysblock loaded immediately above.
                "force_reload": False,
                "auto_load_deps": True,
            },
            timeout_s=300,
        )
        if not load_result.get("ok"):
            raise RuntimeError(f"Model load failed: {load_result}")
        verify_protected_sources(record, "after_load")
        check_result = client.call_tool(
            "check_model",
            {"model_name": target_class, "stop_on_error": True},
            timeout_s=300,
        )
        write_json(logs_dir / "check_model_direct.json", check_result)
        if not check_result.get("ok"):
            raise RuntimeError(f"CheckModel failed: {check_result}")
        verify_protected_sources(record, "after_check")
        client.call_tool("model_manager", {"action": "open", "model_name": target_class}, timeout_s=60)
        verify_protected_sources(record, "after_open")
        after_check = capture_phase(
            run_dir=run_dir,
            phase="after_check",
            target_class=target_class,
            expected_pid=expected_pid,
            destination=screenshots_dir / "01_after_check.png",
            capture_surface="model",
        )
        record["mworks_phase_screenshots"].append(after_check)
        record["mworks_phase_observations"].append("CheckModel succeeded and the rendered graphical model was captured.")

        raw_output = raw_dir / "result.csv"
        metrics_json = metrics_dir / "metrics.json"
        metrics_csv = metrics_dir / "metrics.csv"
        native_preferred = raw_dir / "native_result"
        native_dir, native_manifest = resolve_native_result_dir(raw_output, native_preferred, target_class)
        native_dir, expected_native, native_root_resolution = prepare_route_native_result(native_dir, target_class)
        record["native_result_root"] = native_root_resolution
        simulation_started_unix = time.time()
        sim_result = simulate_modelingpy(
            client,
            model_name=target_class,
            target_time=profile["target_time"],
            native_result_dir=native_dir,
            verify_result_var=next(value for key, value in profile["variables"].items() if key != "time"),
            verify_time_point="end",
        )
        write_json(logs_dir / "simulate_model_direct.json", sim_result)
        if not sim_result.get("ok"):
            raise RuntimeError(f"Simulation failed: {sim_result}")
        verify_protected_sources(record, "after_simulation")
        if sim_result.get("simulate_api_reported_failure"):
            record["mworks_phase_observations"].append(
                "SimulateModel reported false. The result remains provisional until the current native Result.msr and complete time series pass the freshness gate."
            )
        readiness = wait_for_fresh_result_artifacts(
            client,
            model_name=target_class,
            variables=profile["variables"],
            native_dir=native_dir,
            expected_native=expected_native,
            expected_stop_time=float(profile["target_time"][1]),
            not_before_unix=simulation_started_unix,
        )
        record["result_readiness"] = readiness["readiness"]
        native_result = readiness["native_result"]
        series = readiness["series"]
        write_native_result_manifest(
            native_manifest,
            native_result_dir=native_dir,
            native_result=native_result,
            model_name=target_class,
        )
        record["native_result_locator"] = relative(native_result)
        write_csv(series, profile["variables"], raw_output)
        write_metrics(
            raw_output,
            metrics_json,
            metrics_csv,
            "g6_internal_fixed_input_probe" if row["evidence_class"] == "internal_fixed_input_probe" else "g6_whole_aircraft_minimum_closure",
            scheme_id,
            row["evidence_class"],
            profile["metrics_profile"],
        )
        metrics = read_json(metrics_json)
        if not metrics.get("valid"):
            raise RuntimeError(f"Result metrics did not satisfy the evidence profile: {metrics}")
        plot_result = show_native_plot(client, native_result=native_result, variables=profile["variables"])
        write_json(logs_dir / "open_native_result_plot.json", plot_result)
        result_capture = capture_phase(
            run_dir=run_dir,
            phase="result_window",
            target_class=target_class,
            expected_pid=expected_pid,
            destination=screenshots_dir / "02_result_window.png",
            capture_surface="result_viewer",
        )
        record["mworks_phase_screenshots"].append(result_capture)
        report_result = materialize_report_result(row, screenshots_dir / "02_result_window.png")
        if report_result:
            record["report_result_screenshot"] = report_result
        record["mworks_phase_observations"].append(
            "Native Result.msr was opened and the declared result variables were plotted before capture."
        )
        verify_protected_sources(record, "before_record")
        record["status"] = "passed"
        record["metrics_summary"] = {
            "row_count": metrics.get("row_count"),
            "duration_s": metrics.get("duration_s"),
            "nan_count": metrics.get("nan_count"),
            "valid": metrics.get("valid"),
        }
        for candidate in (
            artifact(raw_output, "raw"),
            artifact(metrics_json, "metrics"),
            artifact(metrics_csv, "metrics"),
            artifact(native_result, "native_result"),
            artifact(screenshots_dir / "01_after_check.png", "figure"),
            artifact(screenshots_dir / "02_result_window.png", "figure"),
            artifact(log_path, "log"),
        ):
            if candidate:
                record["artifact_refs"].append(candidate)
    except Exception as exc:  # Preserve a route-level terminal record and continue when safe.
        message = str(exc)
        classification = classify_error(message)
        if "Source hash changed" in message:
            classification = "source_hash_mismatch"
        if classification == "execution_failed" and "capture" in message.lower():
            classification = "screenshot_failed"
        record["status"] = classification
        record["error"] = {
            "message": message,
            "traceback": traceback.format_exc(),
        }
        for candidate in (
            artifact(log_path, "log"),
            artifact(logs_dir / "check_model_direct.json", "log"),
            artifact(logs_dir / "simulate_model_direct.json", "log"),
            artifact(raw_dir / "result.csv", "raw"),
            artifact(metrics_dir / "metrics.json", "metrics"),
            artifact(screenshots_dir / "01_after_check.png", "figure"),
            artifact(screenshots_dir / "02_result_window.png", "figure"),
        ):
            if candidate:
                record["artifact_refs"].append(candidate)
    finally:
        extract_tool_log(log_path, "check_model", logs_dir / "check_model.json")
        extract_tool_log(log_path, "call_code", logs_dir / "simulate_model.json")
        record["finished_at"] = now_iso()
        screenshot_manifest = write_screenshot_manifest(logs_dir, record)
        manifest_artifact = artifact(screenshot_manifest, "log")
        if manifest_artifact and not any(item.get("path") == manifest_artifact["path"] for item in record["artifact_refs"]):
            record["artifact_refs"].append(manifest_artifact)
        try:
            write_json(run_dir / "RUN_RECORD.json", record)
        except Exception:
            fallback = logs_dir / "run_record_write_failure.txt"
            fallback.write_text(traceback.format_exc(), encoding="utf-8")
            raise
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix",
        type=Path,
        help=(
            "project-local frozen G6 matrix below Results/; default preserves the historical "
            "execution root"
        ),
    )
    parser.add_argument("--only", help="Comma-separated scheme IDs to run; defaults to every pending route.")
    parser.add_argument("--limit", type=int, help="Bound the number of routes attempted this invocation.")
    parser.add_argument("--rerun", action="store_true", help="Re-run routes with an existing terminal record.")
    parser.add_argument(
        "--repair-native-whitespace",
        action="store_true",
        help=(
            "Restore selected source files only when their native whitespace normal form matches an exact "
            "frozen source snapshot. This performs no MWORKS operation and is intended before --rerun."
        ),
    )
    parser.add_argument(
        "--reconcile-report-result-bindings",
        action="store_true",
        help=(
            "Offline-only: for explicitly named result_binding_failed routes, archive the conflicting "
            "legacy report result image and bind the already completed current native result-window capture."
        ),
    )
    parser.add_argument(
        "--continue-after-infrastructure-error",
        action="store_true",
        help="Continue after a license/login or MCP-internal incident. Default stops the batch safely.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_matrix_path(args.matrix)
    if not MATRIX_PATH.is_file():
        raise SystemExit(f"G6 matrix is missing: {MATRIX_PATH}")
    matrix = read_json(MATRIX_PATH)
    if matrix.get("schema") != "mosim.g6_controller_execution_matrix.v1":
        raise SystemExit(f"Unexpected G6 matrix schema: {matrix.get('schema')}")
    rows = matrix.get("rows")
    if not isinstance(rows, list) or len(rows) != 46:
        raise SystemExit("G6 matrix must contain exactly 46 routes")
    if args.repair_native_whitespace and args.rerun:
        raise SystemExit("--repair-native-whitespace and --rerun are separate operations")
    if args.reconcile_report_result_bindings and (args.rerun or args.repair_native_whitespace):
        raise SystemExit("--reconcile-report-result-bindings is separate from --rerun and --repair-native-whitespace")
    if args.repair_native_whitespace and not args.only:
        raise SystemExit("--repair-native-whitespace requires an explicit --only route list")
    if args.reconcile_report_result_bindings and not args.only:
        raise SystemExit("--reconcile-report-result-bindings requires an explicit --only route list")

    selected_ids = {item.strip() for item in args.only.split(",") if item.strip()} if args.only else None
    selected_rows: list[dict[str, Any]] = []
    for row in rows:
        if selected_ids is not None and row.get("scheme_id") not in selected_ids:
            continue
        run_dir = ROOT / row["result_root"]
        if (
            not args.repair_native_whitespace
            and not args.rerun
            and not args.reconcile_report_result_bindings
            and existing_terminal_record(run_dir)
        ):
            continue
        selected_rows.append(row)
    if selected_ids is not None:
        missing = selected_ids - {str(row.get("scheme_id")) for row in rows}
        if missing:
            raise SystemExit(f"Unknown scheme IDs: {', '.join(sorted(missing))}")
    if args.limit is not None:
        if args.limit <= 0:
            raise SystemExit("--limit must be positive")
        selected_rows = selected_rows[: args.limit]
    if args.repair_native_whitespace:
        repair_path, ok = repair_native_whitespace_rows(selected_rows)
        print(f"Native whitespace repair manifest: {relative(repair_path)}")
        return 0 if ok else 1
    if args.reconcile_report_result_bindings:
        reconciled: list[dict[str, Any]] = []
        failures: list[str] = []
        for row in selected_rows:
            try:
                result = reconcile_report_result_binding(row)
                reconciled.append(result)
                print(f"{result['scheme_id']}: report result binding reconciled")
            except Exception as exc:
                failures.append(f"{row.get('scheme_id')}: {exc}")
                print(f"{row.get('scheme_id')}: report result binding not reconciled: {exc}", file=sys.stderr)
        write_status(matrix)
        print(f"Reconciled report result bindings: {len(reconciled)}")
        if failures:
            return 1
        return 0
    if not selected_rows:
        write_status(matrix)
        print("No G6 routes need execution.")
        return 0

    batch_log = MATRIX_PATH.parent / "logs" / f"g6_batch_{time.strftime('%Y%m%d_%H%M%S')}.jsonl"
    batch_log.parent.mkdir(parents=True, exist_ok=True)
    client = JsonlMcpClient(wrapper_command(resolve_wrapper(None)), batch_log)
    attempted = 0
    session: dict[str, Any] | None = None
    cleanup: dict[str, Any] | None = None
    attempted_rows: list[dict[str, Any]] = []
    post_session_outcomes: list[dict[str, Any]] = []
    try:
        health = initialize_mcp_client(client)
        startup = health.get("sysplorer_startup") if isinstance(health.get("sysplorer_startup"), dict) else {}
        expected_pid = mworks_pid_for_port(startup.get("dedicated_sysplorer_port"))
        session = {
            "health": health,
            "dedicated_sysplorer_port": startup.get("dedicated_sysplorer_port"),
            "mworks_pid": expected_pid,
            "batch_log": relative(batch_log),
        }
        session["dependency_preload"] = preload_base_packages(client)
        for row in selected_rows:
            attempted += 1
            attempted_rows.append(row)
            run_dir = ROOT / row["result_root"]
            superseded_record_archive = (
                archive_existing_route_for_rerun(run_dir)
                if args.rerun and existing_terminal_record(run_dir)
                else None
            )
            record = run_route(
                client=client,
                row=row,
                session=session,
                expected_pid=expected_pid,
                superseded_record_archive=superseded_record_archive,
            )
            write_status(matrix)
            print(f"{record['scheme_id']}: {record['status']}")
            if (
                record["status"] in {"license_or_login", "internal_or_mcp"}
                and not args.continue_after_infrastructure_error
            ):
                print("Stopping batch after infrastructure incident; route record and status were preserved.")
                break
    finally:
        cleanup_log = batch_log.with_name(batch_log.stem + "_session_cleanup.json")
        cleanup = close_dedicated_session(
            client,
            session=session,
            output=cleanup_log,
        )
        try:
            client.close()
        finally:
            post_session_outcomes = reconcile_routes_after_session_shutdown(
                rows=attempted_rows,
                cleanup=cleanup,
                cleanup_log=cleanup_log,
            )
            write_status(matrix)
    print(f"Attempted routes: {attempted}")
    if cleanup and cleanup.get("requested") and not cleanup.get("verified_closed"):
        print("Dedicated Sysplorer session cleanup was not verified; inspect the cleanup record.", file=sys.stderr)
        return 2
    if any(outcome.get("integrity_ok") is False for outcome in post_session_outcomes):
        print("Post-session source validation did not preserve every attempted route; inspect RUN_RECORD.json.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
