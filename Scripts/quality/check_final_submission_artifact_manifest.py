#!/usr/bin/env python3
"""Check final submission artifact presence and minimum metadata.

This checker verifies final output artifacts if they exist. Missing artifacts
are reported as blockers. It never creates PDFs, videos, or acceptance packets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_artifacts_20260610"
    / "final_submission_artifact_manifest_check.json"
)

FINAL_ARTIFACTS = {
    "user_manual_pdf": {
        "path": "Results/submission/user_manual.pdf",
        "kind": "pdf",
        "min_size_bytes": 1024,
    },
    "simulation_analysis_report_pdf": {
        "path": "Results/submission/simulation_analysis_report.pdf",
        "kind": "pdf",
        "min_size_bytes": 1024,
    },
    "demo_video": {
        "path": "Results/submission/demo_video.mp4",
        "kind": "mp4",
        "min_size_bytes": 1024,
    },
    "final_acceptance_packet": {
        "path": "Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json",
        "kind": "json",
        "min_size_bytes": 20,
    },
}

REQUIRED_ACCEPTANCE_TERMS = [
    "final_submission",
    "accepted",
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def artifact_record(name: str, spec: dict[str, Any]) -> dict[str, Any]:
    path_value = str(spec["path"])
    path = repo_path(path_value)
    exists = path.exists()
    size = path.stat().st_size if path.is_file() else 0
    issues: list[str] = []
    if not exists:
        issues.append("missing")
    elif not path.is_file():
        issues.append("not_a_file")
    elif size < int(spec["min_size_bytes"]):
        issues.append(f"too_small<{spec['min_size_bytes']}")
    suffix = path.suffix.lower()
    kind = str(spec["kind"])
    if exists and kind == "pdf" and suffix != ".pdf":
        issues.append("wrong_extension")
    if exists and kind == "mp4" and suffix != ".mp4":
        issues.append("wrong_extension")
    if exists and kind == "json":
        if suffix != ".json":
            issues.append("wrong_extension")
        elif path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                issues.append(f"invalid_json:{type(exc).__name__}")
            else:
                text = json.dumps(data, ensure_ascii=False).lower()
                for term in REQUIRED_ACCEPTANCE_TERMS:
                    if term not in text:
                        issues.append(f"acceptance_packet_missing_term:{term}")
    return {
        "artifact_id": name,
        "path": path_value,
        "kind": kind,
        "exists": exists,
        "size_bytes": size,
        "ok": not issues,
        "issues": issues,
    }


def validate() -> dict[str, Any]:
    artifacts = {
        name: artifact_record(name, spec)
        for name, spec in FINAL_ARTIFACTS.items()
    }
    missing = [name for name, item in artifacts.items() if not item["exists"]]
    failing = [name for name, item in artifacts.items() if not item["ok"]]
    return {
        "manifest_id": "final_submission_artifact_manifest_20260610",
        "status": "final_artifacts_missing_not_final_submission",
        "summary": {
            "artifact_count": len(artifacts),
            "missing_artifact_count": len(missing),
            "failing_artifact_count": len(failing),
            "final_submission_artifacts_ready": not failing,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "artifacts": artifacts,
        "missing_artifacts": missing,
        "failing_artifacts": failing,
        "claim_boundary": [
            "This checker validates final artifacts only if they exist.",
            "It does not create PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "Missing artifacts mean final submission is not ready.",
        ],
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# Final Submission Artifact Manifest Check, 2026-06-10",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- Artifacts: `{summary['artifact_count']}`",
        f"- Missing artifacts: `{summary['missing_artifact_count']}`",
        f"- Failing artifacts: `{summary['failing_artifact_count']}`",
        f"- Final submission artifacts ready: `{summary['final_submission_artifacts_ready']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in result["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Artifacts", "", "| Artifact | OK | Exists | Size | Issues | Path |", "|---|---|---|---:|---|---|"])
    for name, item in result["artifacts"].items():
        lines.append(
            f"| {name} | {item['ok']} | {item['exists']} | {item['size_bytes']} | {', '.join(item['issues'])} | `{item['path']}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    parser.add_argument("--output-md", default="")
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args()

    result = validate()
    output_json = repo_path(args.output_json)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md = repo_path(args.output_md) if args.output_md else output_json.with_suffix(".md")
    write_markdown(result, output_md)

    print(json.dumps({"ok": result["summary"]["final_submission_artifacts_ready"], "path": rel(output_json)}, ensure_ascii=False))
    if args.allow_missing:
        return 0
    return 0 if result["summary"]["final_submission_artifacts_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
