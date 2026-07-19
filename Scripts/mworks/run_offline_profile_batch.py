#!/usr/bin/env python3
"""Run allowlisted offline Model Studio profiles and write a batch index."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "offline_composition_catalog.json"
CERTIFIER = ROOT / "Scripts" / "mworks" / "run_offline_profile_certification.py"
BATCH_ROOT = ROOT / "Results" / "control_platform" / "offline_batches"
BATCH_INDEX_NAME = "BATCH_INDEX.json"
CANCEL_REQUEST_NAME = "CANCEL_REQUEST.json"
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"json_object_required:{path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    write_json(temporary, value)
    temporary.replace(path)


def display_path(path: Path) -> str:
    """Use repository-relative paths when possible, absolute paths otherwise."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def profile_map(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    profiles = {
        str(item["profile_id"]): item
        for item in catalog.get("certified_profiles", [])
        if isinstance(item, dict) and item.get("profile_id")
    }
    for item in catalog.get("disabled_profiles", []):
        if isinstance(item, dict) and item.get("profile_id"):
            profiles.setdefault(str(item["profile_id"]), item)
    for item in catalog.get("custom_profile_proofs", []):
        if isinstance(item, dict) and item.get("profile_id"):
            profiles.setdefault(str(item["profile_id"]), item)
    return profiles


def resolve_profile(catalog: dict[str, Any], profile_id: str) -> dict[str, Any]:
    item = profile_map(catalog).get(profile_id)
    if item is None:
        raise ValueError(f"profile_not_allowlisted:{profile_id}")
    if item.get("certification_state") == "blocked_current_run":
        raise ValueError(f"profile_disabled:{profile_id}")
    if item.get("execution_kind") == "custom_request":
        request_path = ROOT / str(item.get("request_json", ""))
        if item.get("status") != "accepted" or not request_path.is_file():
            raise ValueError(f"custom_profile_request_unavailable:{profile_id}")
    if item.get("vehicle_count") != 1:
        raise ValueError(f"batch_requires_single_uav_profile:{profile_id}")
    if item.get("execution_kind") == "direct_model":
        raise ValueError(f"batch_wrapper_required_for_profile:{profile_id}")
    return item


def unique_run_id(batch_id: str, profile_id: str, index: int) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", profile_id).strip("-").lower()
    return f"batch-{batch_id}-{index:02d}-{slug}"[:96]


def run_one(
    profile_id: str,
    profile: dict[str, Any],
    batch_id: str,
    index: int,
    *,
    reuse_generated: bool,
    record_only: bool,
    timeout_s: int,
    output_dir: Path,
) -> dict[str, Any]:
    run_id = unique_run_id(batch_id, profile_id, index)
    command = [sys.executable, str(CERTIFIER)]
    if profile.get("execution_kind") == "custom_request":
        command.extend(["--request-json", str(ROOT / profile["request_json"])])
    else:
        command.extend(["--certified-profile-id", profile_id])
    command.extend(["--run-id", run_id])
    if reuse_generated:
        command.append("--reuse-generated")
    if record_only:
        command.append("--record-only")
    started = time.time()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_s,
        )
        status = "accepted" if completed.returncode == 0 else "blocked"
        reason = "certification_accepted" if status == "accepted" else "certification_failed"
    except subprocess.TimeoutExpired as exc:
        completed = None
        status = "blocked"
        reason = "certification_timeout"
        stdout = str(exc.stdout or "")
        stderr = str(exc.stderr or "")
    else:
        stdout = completed.stdout
        stderr = completed.stderr

    run_record = {
        "profile_id": profile_id,
        "run_id": run_id,
        "controller_id": profile.get("controller_id"),
        "output_variant": profile.get("output_variant"),
        "status": status,
        "reason_code": reason,
        "return_code": None if completed is None else completed.returncode,
        "duration_s": round(time.time() - started, 3),
        "certification_record": f"Results/mworks_generated_profiles/{run_id}/CERTIFICATION.json",
        "stdout_log": f"{display_path(output_dir)}/{run_id}.stdout.log",
        "stderr_log": f"{display_path(output_dir)}/{run_id}.stderr.log",
    }
    (output_dir / f"{run_id}.stdout.log").write_text(stdout, encoding="utf-8", newline="\n")
    (output_dir / f"{run_id}.stderr.log").write_text(stderr, encoding="utf-8", newline="\n")
    return run_record


def blocked_record(profile_id: str | None, reason_code: str) -> dict[str, Any]:
    """Represent a preflight blocker without starting MWORKS."""
    return {
        "profile_id": profile_id,
        "run_id": None,
        "status": "blocked",
        "reason_code": reason_code,
        "return_code": None,
        "duration_s": 0.0,
        "certification_record": None,
    }


def load_retry_source(batch_root: Path, retry_batch_id: str) -> dict[str, Any]:
    if not ID_PATTERN.fullmatch(retry_batch_id):
        raise ValueError(f"invalid_retry_batch_id:{retry_batch_id}")
    source_path = batch_root / retry_batch_id / "BATCH_MANIFEST.json"
    if not source_path.is_file():
        raise ValueError(f"retry_batch_not_found:{retry_batch_id}")
    source = read_json(source_path)
    if source.get("schema") != "mosim.model_studio.offline_batch.v1":
        raise ValueError(f"retry_batch_schema_unsupported:{retry_batch_id}")
    profiles = source.get("requested_profiles")
    if not isinstance(profiles, list) or not profiles or not all(isinstance(item, str) for item in profiles):
        raise ValueError(f"retry_batch_profiles_invalid:{retry_batch_id}")
    return source


def request_cancel(batch_root: Path, batch_id: str) -> dict[str, Any]:
    """Request cancellation at the next safe profile boundary."""
    if not ID_PATTERN.fullmatch(batch_id):
        raise ValueError(f"invalid_cancel_batch_id:{batch_id}")
    output_dir = batch_root / batch_id
    if not output_dir.is_dir():
        raise ValueError(f"cancel_batch_not_found:{batch_id}")
    manifest_path = output_dir / "BATCH_MANIFEST.json"
    if manifest_path.is_file():
        manifest = read_json(manifest_path)
        raise ValueError(f"cancel_batch_already_terminal:{manifest.get('status', 'unknown')}")
    request = {
        "schema": "mosim.model_studio.offline_batch_cancel_request.v1",
        "batch_id": batch_id,
        "requested_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": "after_active_profile_cleanup",
    }
    write_json_atomic(output_dir / CANCEL_REQUEST_NAME, request)
    return request


def read_cancel_request(output_dir: Path) -> dict[str, Any] | None:
    path = output_dir / CANCEL_REQUEST_NAME
    if not path.is_file():
        return None
    request = read_json(path)
    if request.get("schema") != "mosim.model_studio.offline_batch_cancel_request.v1":
        raise ValueError("cancel_request_schema_unsupported")
    return request


def rebuild_batch_index(batch_root: Path = BATCH_ROOT) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for manifest_path in sorted(batch_root.glob("*/BATCH_MANIFEST.json")):
        try:
            manifest = read_json(manifest_path)
            batch_id = str(manifest["batch_id"])
            status = str(manifest["status"])
            if manifest.get("schema") != "mosim.model_studio.offline_batch.v1":
                raise ValueError("unsupported_schema")
            if status not in {"accepted", "blocked", "cancelled"}:
                raise ValueError("invalid_status")
            entries.append(
                {
                    "batch_id": batch_id,
                    "status": status,
                    "started_at": manifest.get("started_at"),
                    "completed_at": manifest.get("completed_at"),
                    "requested_profiles": manifest.get("requested_profiles", []),
                    "completed_profiles": manifest.get("completed_profiles", []),
                    "lineage": manifest.get("lineage", {}),
                    "manifest": display_path(manifest_path),
                }
            )
        except (KeyError, OSError, json.JSONDecodeError, ValueError) as error:
            errors.append({"manifest": display_path(manifest_path), "reason_code": str(error)})
    entries.sort(
        key=lambda item: (
            str(item.get("completed_at") or ""),
            next(
                (
                    path.stat().st_mtime_ns
                    for path in batch_root.glob(f"{item['batch_id']}/BATCH_MANIFEST.json")
                ),
                0,
            ),
            item["batch_id"],
        )
    )
    accepted_count = sum(item["status"] == "accepted" for item in entries)
    blocked_count = sum(item["status"] == "blocked" for item in entries)
    cancelled_count = sum(item["status"] == "cancelled" for item in entries)
    index = {
        "schema": "mosim.model_studio.offline_batch_index.v1",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "latest_batch_id": entries[-1]["batch_id"] if entries else None,
        "summary": {
            "batch_count": len(entries),
            "accepted_count": accepted_count,
            "blocked_count": blocked_count,
            "cancelled_count": cancelled_count,
            "index_error_count": len(errors),
        },
        "entries": entries,
        "index_errors": errors,
    }
    write_json_atomic(batch_root / BATCH_INDEX_NAME, index)
    return index


def write_batch_manifest(
    output_dir: Path,
    batch_id: str,
    requested_profiles: list[str],
    records: list[dict[str, Any]],
    *,
    started: str,
    reuse_generated: bool,
    record_only: bool,
    timeout_s: int,
    lineage: dict[str, Any],
    batch_root: Path | None = None,
    cancelled: dict[str, Any] | None = None,
) -> dict[str, Any]:
    accepted = len(records) == len(requested_profiles) and all(
        item["status"] == "accepted" for item in records
    )
    manifest = {
        "schema": "mosim.model_studio.offline_batch.v1",
        "batch_id": batch_id,
        "status": "cancelled" if cancelled is not None else ("accepted" if accepted else "blocked"),
        "started_at": started,
        "completed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "requested_profiles": requested_profiles,
        "completed_profiles": [item["profile_id"] for item in records if item.get("run_id")],
        "records": records,
        "lineage": lineage,
        "cancellation": cancelled,
        "execution": {
            "reuse_generated": reuse_generated,
            "record_only": record_only,
            "timeout_s": timeout_s,
            "stop_on_first_blocker": True,
        },
        "claim_boundary": "Batch orchestration and run-local offline MWORKS certification only; no PX4, Gazebo, ROS1, online co-simulation, or flight acceptance.",
    }
    write_json(output_dir / "BATCH_MANIFEST.json", manifest)
    if batch_root is not None:
        rebuild_batch_index(batch_root)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-id", action="append", dest="profile_ids")
    parser.add_argument("--retry-batch-id")
    parser.add_argument("--batch-id")
    parser.add_argument("--request-cancel")
    parser.add_argument("--reuse-generated", action="store_true")
    parser.add_argument("--record-only", action="store_true")
    parser.add_argument("--timeout-s", type=int, default=900)
    args = parser.parse_args()
    if args.request_cancel:
        if args.batch_id or args.profile_ids or args.retry_batch_id:
            parser.error("cancel_request_cannot_start_batch")
        try:
            request = request_cancel(BATCH_ROOT, args.request_cancel)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(json.dumps({"accepted": False, "reason_code": str(error)}, ensure_ascii=False))
            return 2
        print(json.dumps({"accepted": True, "request": request}, ensure_ascii=False, indent=2))
        return 0
    if not args.batch_id:
        parser.error("batch_id_required")
    if not ID_PATTERN.fullmatch(args.batch_id):
        parser.error("invalid_batch_id")
    if bool(args.profile_ids) == bool(args.retry_batch_id):
        parser.error("exactly_one_profile_source_required")
    if args.profile_ids and len(set(args.profile_ids)) != len(args.profile_ids):
        parser.error("duplicate_profile_id")

    output_dir = BATCH_ROOT / args.batch_id
    if output_dir.exists():
        raise SystemExit(f"batch_already_exists:{args.batch_id}")
    output_dir.mkdir(parents=True)
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    records: list[dict[str, Any]] = []
    selected: list[tuple[str, dict[str, Any]]] = []
    requested_profiles = list(args.profile_ids or [])
    lineage: dict[str, Any] = {
        "root_batch_id": args.batch_id,
        "retry_of": None,
        "attempt": 1,
    }
    profile_id: str | None = requested_profiles[0] if requested_profiles else None
    try:
        if args.retry_batch_id:
            source = load_retry_source(BATCH_ROOT, args.retry_batch_id)
            requested_profiles = list(source["requested_profiles"])
            source_lineage = source.get("lineage", {})
            lineage = {
                "root_batch_id": source_lineage.get("root_batch_id", args.retry_batch_id),
                "retry_of": args.retry_batch_id,
                "attempt": int(source_lineage.get("attempt", 1)) + 1,
            }
        catalog = read_json(CATALOG)
        for profile_id in requested_profiles:
            selected.append((profile_id, resolve_profile(catalog, profile_id)))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        manifest = write_batch_manifest(
            output_dir,
            args.batch_id,
            requested_profiles,
            [blocked_record(profile_id, str(error))],
            started=started,
            reuse_generated=args.reuse_generated,
            record_only=args.record_only,
            timeout_s=args.timeout_s,
            lineage=lineage,
            batch_root=BATCH_ROOT,
        )
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 2
    cancel_request: dict[str, Any] | None = None
    for index, (profile_id, profile) in enumerate(selected, start=1):
        cancel_request = read_cancel_request(output_dir)
        if cancel_request is not None:
            break
        record = run_one(
            profile_id,
            profile,
            args.batch_id,
            index,
            reuse_generated=args.reuse_generated,
            record_only=args.record_only,
            timeout_s=args.timeout_s,
            output_dir=output_dir,
        )
        records.append(record)
        if record["status"] != "accepted":
            break
        cancel_request = read_cancel_request(output_dir)
        if cancel_request is not None:
            break

    manifest = write_batch_manifest(
        output_dir,
        args.batch_id,
        requested_profiles,
        records,
        started=started,
        reuse_generated=args.reuse_generated,
        record_only=args.record_only,
        timeout_s=args.timeout_s,
        lineage=lineage,
        batch_root=BATCH_ROOT,
        cancelled=cancel_request,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if manifest["status"] == "accepted" else (3 if manifest["status"] == "cancelled" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
