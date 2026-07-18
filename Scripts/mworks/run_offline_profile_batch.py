#!/usr/bin/env python3
"""Run allowlisted offline Model Studio profiles and write a batch index."""

from __future__ import annotations

import argparse
import json
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
    return profiles


def resolve_profile(catalog: dict[str, Any], profile_id: str) -> dict[str, Any]:
    item = profile_map(catalog).get(profile_id)
    if item is None:
        raise ValueError(f"profile_not_allowlisted:{profile_id}")
    if item.get("certification_state") == "blocked_current_run":
        raise ValueError(f"profile_disabled:{profile_id}")
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
    command = [
        sys.executable,
        str(CERTIFIER),
        "--certified-profile-id",
        profile_id,
        "--run-id",
        run_id,
    ]
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-id", action="append", dest="profile_ids")
    parser.add_argument("--batch-id", required=True)
    parser.add_argument("--reuse-generated", action="store_true")
    parser.add_argument("--record-only", action="store_true")
    parser.add_argument("--timeout-s", type=int, default=900)
    args = parser.parse_args()
    if not ID_PATTERN.fullmatch(args.batch_id):
        parser.error("invalid_batch_id")
    if not args.profile_ids:
        parser.error("at_least_one_profile_id_required")
    if len(set(args.profile_ids)) != len(args.profile_ids):
        parser.error("duplicate_profile_id")

    catalog = read_json(CATALOG)
    selected = [(profile_id, resolve_profile(catalog, profile_id)) for profile_id in args.profile_ids]
    output_dir = BATCH_ROOT / args.batch_id
    if output_dir.exists():
        raise SystemExit(f"batch_already_exists:{args.batch_id}")
    output_dir.mkdir(parents=True)
    started = datetime.now().astimezone().isoformat(timespec="seconds")
    records: list[dict[str, Any]] = []
    for index, (profile_id, profile) in enumerate(selected, start=1):
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

    accepted = len(records) == len(selected) and all(item["status"] == "accepted" for item in records)
    manifest = {
        "schema": "mosim.model_studio.offline_batch.v1",
        "batch_id": args.batch_id,
        "status": "accepted" if accepted else "blocked",
        "started_at": started,
        "completed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "requested_profiles": args.profile_ids,
        "completed_profiles": [item["profile_id"] for item in records],
        "records": records,
        "execution": {
            "reuse_generated": args.reuse_generated,
            "record_only": args.record_only,
            "timeout_s": args.timeout_s,
            "stop_on_first_blocker": True,
        },
        "claim_boundary": "Batch orchestration and run-local offline MWORKS certification only; no PX4, Gazebo, ROS1, online co-simulation, or flight acceptance.",
    }
    write_json(output_dir / "BATCH_MANIFEST.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
