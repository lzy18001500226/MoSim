#!/usr/bin/env python3
"""Build a conservative manifest for the non-frontend submission package.

The manifest audits package boundaries only. It does not copy, delete, stage,
or publish files. Frontend trees, generated temporary outputs, and unreviewed
external repositories are explicitly excluded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "Results" / "control_platform" / "non_frontend_evidence_index_20260718" / "NON_FRONTEND_SUBMISSION_PACKAGE_MANIFEST.json"

REQUIRED_PATHS = [
    "AGENTS.md",
    "Docs/user_manual.md",
    "Docs/Workflows/pre_submit_check.md",
    "Docs/Workflows/mainline_operations_board.md",
    "Docs/Workflows/sunray_ros1_current_runtime_lane.md",
    "Docs/Workflows/sunray_ros1_execution_checklist.md",
    "Models",
    "Config/control_platform",
    "Scripts/control_platform",
    "Scripts/sunray",
    "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_REQUIREMENT_EVIDENCE_MATRIX.json",
    "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_REPORT_SOURCE.json",
    "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_DELIVERY_MANIFEST.json",
]

TRACKED_INCLUDE_ROOTS = [
    "Config",
    "Models",
    "Scripts/control_platform",
    "Scripts/mworks",
    "Scripts/quality",
    "Scripts/sunray",
    "Scripts/tests",
]
EXPLICIT_FILES = [
    "AGENTS.md",
    "README.md",
    "PROGRESS.md",
    "pyproject.toml",
    "uv.lock",
    "Docs/user_manual.md",
    "Docs/simulation_report.md",
    "Docs/Design/架构.md",
    "Docs/Workflows/mainline_operations_board.md",
    "Docs/Workflows/pre_submit_check.md",
    "Docs/Workflows/sunray_ros1_current_runtime_lane.md",
    "Docs/Workflows/sunray_ros1_execution_checklist.md",
]
EVIDENCE_ROOTS = [
    "Results/control_platform/classic_controller_closeout_20260717",
    "Results/control_platform/final_controller_ab_20260718",
    "Results/control_platform/final_controller_ab_motor_fault_r2_20260718",
    "Results/control_platform/p6_safety_runtime_20260717",
    "Results/control_platform/p7_ftc_generated_gazebo_r3_20260717",
    "Results/control_platform/p8_formation_mode1_gazebo_r7_20260717",
    "Results/control_platform/p9_learning_gazebo_r4_20260717",
    "Results/control_platform/non_frontend_evidence_index_20260718",
]
EXCLUDE_ROOTS = [
    "apps/flight_console",
    "apps/model_studio",
    "UE5",
    "References",
    ".git",
    "Results/native_result_cache",
    "Results/agent_runs",
    "Docs/Cache/agent_legacy",
]
EXCLUDE_NAME_PARTS = ["__pycache__", ".pytest_cache", ".gradle", ".o", ".pyc", ".tmp", ".err", ".out", ".venv"]
EXCLUDE_PATH_PARTS = ["frontend", "flight_console", "model_studio", "unreal", "qgc", "orchestrator"]
INLINE_HASH_LIMIT_BYTES = 1024 * 1024
SELF_REFERENTIAL_OUTPUTS = {
    "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_SUBMISSION_PACKAGE_MANIFEST.json",
    "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_SUBMISSION_PACKAGE_MANIFEST.md",
    "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_FINAL_QA_AUDIT.json",
    "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_FINAL_QA_AUDIT.md",
}


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_excluded(path: Path) -> bool:
    path_text = rel(path)
    filter_text = path_text.lower().replace("non_frontend", "nonfrontend")
    return any(path_text == root or path_text.startswith(root + "/") for root in EXCLUDE_ROOTS) or any(
        part in path.name for part in EXCLUDE_NAME_PARTS
    ) or any(part in filter_text for part in EXCLUDE_PATH_PARTS)


def tracked_paths() -> set[str]:
    pathspecs = [*TRACKED_INCLUDE_ROOTS, *EXPLICIT_FILES]
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *pathspecs],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}


def selected_paths() -> list[Path]:
    tracked = tracked_paths()
    selected: set[str] = set()
    for value in tracked:
        path = repo_path(value)
        if not is_excluded(path) and (
            value in EXPLICIT_FILES or any(value == root or value.startswith(root + "/") for root in TRACKED_INCLUDE_ROOTS)
        ):
            selected.add(value)
    for root_name in EVIDENCE_ROOTS:
        root = repo_path(root_name)
        if not root.exists():
            continue
        for path in root.rglob("*"):
            try:
                relative_path = rel(path)
                if path.is_file() and relative_path not in SELF_REFERENTIAL_OUTPUTS and not is_excluded(path):
                    selected.add(relative_path)
            except OSError:
                continue
    return [repo_path(value) for value in sorted(selected)]


def required_records() -> list[dict[str, Any]]:
    records = []
    for value in REQUIRED_PATHS:
        path = repo_path(value)
        records.append({"path": value, "exists": path.exists(), "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing"})
    return records


def candidate_files() -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    inaccessible: list[str] = []
    for path in selected_paths():
        try:
            size = path.stat().st_size
        except OSError:
            inaccessible.append(rel(path))
            continue
        record: dict[str, Any] = {"path": rel(path), "size_bytes": size, "over_100mb": size > 100 * 1024 * 1024}
        if size <= INLINE_HASH_LIMIT_BYTES:
            record["sha256"] = sha256(path)
        else:
            record["hash_deferred"] = True
        records.append(record)
    return sorted(records, key=lambda item: item["path"]), sorted(set(inaccessible))


def build() -> dict[str, Any]:
    required = required_records()
    files, inaccessible = candidate_files()
    missing = [item["path"] for item in required if not item["exists"]]
    oversized = [item["path"] for item in files if item["over_100mb"]]
    return {
        "schema": "mosim.non_frontend_submission_package_manifest.v1",
        "date": "2026-07-18",
        "status": "package_boundary_audit_not_published",
        "scope": {
            "frontend_excluded": True,
            "selection_policy": "tracked project-owned control/runtime files plus explicit current authority evidence",
            "tracked_include_roots": TRACKED_INCLUDE_ROOTS,
            "explicit_files": EXPLICIT_FILES,
            "evidence_roots": EVIDENCE_ROOTS,
            "exclude_roots": EXCLUDE_ROOTS,
            "exclude_name_parts": EXCLUDE_NAME_PARTS,
            "exclude_path_parts": EXCLUDE_PATH_PARTS,
        },
        "required_paths": required,
        "candidate_file_count": len(files),
        "candidate_files": files,
        "inaccessible_paths": inaccessible,
        "inaccessible_path_count": len(inaccessible),
        "missing_required_paths": missing,
        "over_100mb_files": oversized,
        "package_ready": not missing and not oversized and not inaccessible,
        "publication_actions": [
            "Review the exact candidate list before materializing the package.",
            "Run license/source audit for selected References or third-party code before inclusion.",
            "Run secret, path, and dependency checks on the final selected slice.",
            "Materialize and publish only after exact-path review; this manifest does not do so.",
        ],
        "claim_boundary": [
            "This is a package-boundary audit, not a final submission package.",
            "It does not copy, delete, stage, commit, push, or publish files.",
            "A package can contain blocked evidence as long as its status and claim ceiling are preserved.",
        ],
    }


def write_markdown(data: dict[str, Any], path: Path) -> None:
    lines = [
        "# Non-Frontend Submission Package Manifest",
        "",
        f"Status: `{data['status']}`",
        f"Candidate files: `{data['candidate_file_count']}`",
        f"Missing required paths: `{len(data['missing_required_paths'])}`",
        f"Files over 100 MB: `{len(data['over_100mb_files'])}`",
        f"Package boundary ready: `{data['package_ready']}`",
        "",
        "## Tracked Include Roots",
        "",
    ]
    lines.extend(f"- `{item}`" for item in data["scope"]["tracked_include_roots"])
    lines.extend(["", "## Exclude Roots", ""])
    lines.extend(f"- `{item}`" for item in data["scope"]["exclude_roots"])
    lines.extend(["", "## Required Paths", "", "| Path | Exists | Kind |", "|---|---|---|"])
    lines.extend(f"| `{item['path']}` | {item['exists']} | `{item['kind']}` |" for item in data["required_paths"])
    lines.extend(["", "## Publication Actions", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(data["publication_actions"], 1))
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in data["claim_boundary"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT.relative_to(ROOT)))
    args = parser.parse_args()
    output = repo_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = build()
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_markdown(data, output.with_suffix(".md"))
    print(json.dumps({"ok": True, "path": rel(output), "candidate_file_count": data["candidate_file_count"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
