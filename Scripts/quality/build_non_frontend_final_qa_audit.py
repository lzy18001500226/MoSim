#!/usr/bin/env python3
"""Audit the exact non-frontend package selection before publication."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = ROOT / "Results" / "control_platform" / "non_frontend_evidence_index_20260718"
DEFAULT_PACKAGE = EVIDENCE_DIR / "NON_FRONTEND_SUBMISSION_PACKAGE_MANIFEST.json"
DEFAULT_OUTPUT = EVIDENCE_DIR / "NON_FRONTEND_FINAL_QA_AUDIT.json"
UPSTREAM_SOURCES = ROOT / "Config" / "control_platform" / "upstream_sources.json"
TEXT_SUFFIXES = {".c", ".cc", ".cpp", ".h", ".hpp", ".json", ".md", ".mo", ".ps1", ".py", ".sh", ".toml", ".txt", ".yaml", ".yml"}
SECRET_PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "named_credential": re.compile(
        r"(?i)(?:OPENAI_API_KEY|GITHUB_TOKEN|COMPOSIO_API_KEY|API_KEY|ACCESS_TOKEN|CLIENT_SECRET)"
        r"\s*[:=]\s*[\"']?(?!<|your[_-]|example|dummy|redacted|none|null|\$\{)[A-Za-z0-9_./+\-=]{16,}"
    ),
}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
URL_RE = re.compile(r"^https://github\.com/[^/]+/[^/]+/?$")


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def secret_findings(paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in paths:
        if path.suffix.lower() not in TEXT_SUFFIXES or path.stat().st_size > 2 * 1024 * 1024:
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, 1):
            for finding_type, pattern in SECRET_PATTERNS.items():
                if pattern.search(line):
                    findings.append({"path": rel(path), "line": line_number, "type": finding_type})
    return findings


def source_findings() -> tuple[int, list[dict[str, Any]]]:
    data = load_json(UPSTREAM_SOURCES)
    entries = data.get("selected", [])
    reference_only = data.get("reference_only", [])
    findings: list[dict[str, Any]] = []
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            findings.append({"index": index, "issue": "entry_not_object"})
            continue
        source_id = item.get("id", f"index_{index}")
        for field in ("repo", "url", "commit", "license", "role"):
            if not item.get(field):
                findings.append({"id": source_id, "issue": f"missing_{field}"})
        if item.get("url") and not URL_RE.fullmatch(str(item["url"])):
            findings.append({"id": source_id, "issue": "invalid_github_url"})
        if item.get("commit") and not COMMIT_RE.fullmatch(str(item["commit"])):
            findings.append({"id": source_id, "issue": "invalid_commit_pin"})
        if str(item.get("license", "")).lower() in {"", "unknown", "unlicensed"}:
            findings.append({"id": source_id, "issue": "unresolved_license"})
    for index, item in enumerate(reference_only):
        if not isinstance(item, dict):
            findings.append({"reference_only_index": index, "issue": "entry_not_object"})
            continue
        source_id = item.get("repo", f"reference_only_{index}")
        if item.get("source_copy_allowed") is not False:
            findings.append({"id": source_id, "issue": "reference_only_copy_not_forbidden"})
        if not item.get("reason"):
            findings.append({"id": source_id, "issue": "reference_only_reason_missing"})
    return len(entries) + len(reference_only), findings


def build(package_path: Path = DEFAULT_PACKAGE) -> dict[str, Any]:
    package = load_json(package_path)
    candidate_records = package.get("candidate_files", [])
    candidate_paths = [repo_path(item["path"]) for item in candidate_records if isinstance(item, dict) and item.get("path")]
    missing_candidates = [rel(path) for path in candidate_paths if not path.is_file()]
    oversized = [item["path"] for item in candidate_records if isinstance(item, dict) and item.get("over_100mb")]
    secrets = secret_findings([path for path in candidate_paths if path.is_file()])
    source_count, source_issues = source_findings()
    issues = []
    if package.get("package_ready") is not True:
        issues.append("package_manifest_not_ready")
    if missing_candidates:
        issues.append("selected_files_missing")
    if oversized:
        issues.append("selected_files_over_100mb")
    if secrets:
        issues.append("credential_like_content_detected")
    if source_issues:
        issues.append("upstream_source_registry_incomplete")
    return {
        "schema": "mosim.non_frontend_final_qa_audit.v1",
        "date": "2026-07-18",
        "status": "passed" if not issues else "blocked",
        "package_manifest": rel(package_path),
        "selected_file_count": len(candidate_records),
        "checks": {
            "package_boundary_ready": package.get("package_ready") is True,
            "missing_selected_files": missing_candidates,
            "over_100mb_files": oversized,
            "secret_findings": secrets,
            "upstream_source_count": source_count,
            "upstream_source_findings": source_issues,
            "frontend_excluded": package.get("scope", {}).get("frontend_excluded") is True,
        },
        "issues": issues,
        "claim_boundary": [
            "This audit validates the selected package boundary, credential patterns, file size, and source metadata.",
            "It does not replace runtime evidence, human PDF/video review, Git publication, or final competition acceptance.",
        ],
    }


def write_markdown(data: dict[str, Any], path: Path) -> None:
    checks = data["checks"]
    lines = [
        "# Non-Frontend Final QA Audit",
        "",
        f"Status: `{data['status']}`",
        f"Selected files: `{data['selected_file_count']}`",
        f"Package boundary ready: `{checks['package_boundary_ready']}`",
        f"Files over 100 MB: `{len(checks['over_100mb_files'])}`",
        f"Credential-like findings: `{len(checks['secret_findings'])}`",
        f"Upstream source entries: `{checks['upstream_source_count']}`",
        f"Upstream source findings: `{len(checks['upstream_source_findings'])}`",
        "",
        "## Claim Boundary",
        "",
    ]
    lines.extend(f"- {item}" for item in data["claim_boundary"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", default=str(DEFAULT_PACKAGE.relative_to(ROOT)))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT.relative_to(ROOT)))
    args = parser.parse_args()
    output = repo_path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = build(repo_path(args.package))
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_markdown(data, output.with_suffix(".md"))
    print(json.dumps({"ok": data["status"] == "passed", "path": rel(output), "issues": data["issues"]}, ensure_ascii=False))
    return 0 if data["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
