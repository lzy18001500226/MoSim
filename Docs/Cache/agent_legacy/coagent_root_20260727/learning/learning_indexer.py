#!/usr/bin/env python3
"""Build and validate a structured index of CoAgent learning audit records."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = ROOT / "CoAgent" / "learning" / "audits"
INDEX_PATH = ROOT / "Results" / "coagent_learning" / "learning_index.json"
REQUIRED_SECTIONS = [
    "source_slice",
    "read_files_or_urls",
    "architecture_claims",
    "adopt_now",
    "adapt_later",
    "portable_only",
    "reject",
    "unknowns",
    "required_patch",
    "verification",
    "next_trigger",
]
OUTCOME_SECTIONS = ["adopt_now", "adapt_later", "portable_only", "reject", "unknowns"]
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
SOURCE_FAMILIES = [
    {
        "family": "anthropic_engineering",
        "required": True,
        "needles": ["anthropic.com/engineering"],
        "description": "Anthropic/Claude official engineering articles",
    },
    {
        "family": "anthropic_sdk_beta",
        "required": True,
        "needles": ["References/Agent/anthropic-sdk-python/src/anthropic/resources/beta"],
        "description": "Anthropic SDK beta agent/session/thread/memory/resource boundaries",
    },
    {
        "family": "hermes",
        "required": True,
        "needles": ["References/Agent/hermes-agent", "References/Agent/hermes-desktop"],
        "description": "Hermes runtime, desktop, scheduler, memory, transport, and guardrails",
    },
    {
        "family": "codex",
        "required": True,
        "needles": ["References/Agent/codex"],
        "description": "Codex app-server, thread store, rollout/event trace, sandbox, and skills",
    },
    {
        "family": "agent_skills",
        "required": True,
        "needles": ["References/Agent"],
        "description": "Local agent skills and context/harness/verification patterns",
    },
    {
        "family": "official_multi_agent_sources",
        "required": True,
        "needles": [
            "anthropic.com/engineering/built-multi-agent-research-system",
            "openai.github.io/openai-agents-python/multi_agent",
            "google.github.io/adk-docs/workflows",
            "a2aproject/A2A",
            "semantic-kernel/frameworks/agent/agent-orchestration",
        ],
        "description": "Official multi-agent, handoff, workflow, hook, and context sources",
    },
    {
        "family": "multi_agent_frameworks",
        "required": True,
        "needles": [
            "References/Agent/autogen",
            "References/Agent/ag2",
            "References/Agent/crewAI",
            "References/Agent/camel",
            "References/Agent/MetaGPT",
            "References/Agent/langgraph",
            "References/Agent/llama-agents",
        ],
        "description": "Role, graph, crew, society, and framework-level multi-agent patterns",
    },
    {
        "family": "coding_agents",
        "required": True,
        "needles": [
            "References/Agent/OpenHands",
            "References/Agent/openclaw",
            "References/Agent/claw-code",
            "References/Agent/CowAgent",
        ],
        "description": "Repository coding-agent runtimes and execution boundaries",
    },
    {
        "family": "workflow_runtimes",
        "required": True,
        "needles": [
            "References/Agent/temporal",
            "References/Agent/TaskWeaver",
            "References/Agent/OpenSpec",
            "References/Agent/okwinds",
        ],
        "description": "Durable workflow, WAL, replay, spec-first, and planner/executor references",
    },
    {
        "family": "knowledge_search",
        "required": True,
        "needles": ["References/Agent/haystack", "References/Agent/langchain"],
        "description": "Retrieval, pipeline, indexing, and memory/search references",
    },
    {
        "family": "technical_enterprise_operating_system",
        "required": True,
        "needles": [
            "handbook.gitlab.com",
            "sre.google",
            "dora.dev",
            "Team Topologies",
            "architecture-decision-record",
            "Working Backwards",
        ],
        "description": "Technical enterprise management, accountability, delivery, incident, and decision systems",
    },
    {
        "family": "portable_product_architecture",
        "required": False,
        "needles": ["References/Agent/AFFiNE-canary"],
        "description": "Product/app architecture references useful for future CoAgent reuse",
    },
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def section_key(title: str) -> str:
    return title.strip().lower().replace(" ", "_").replace("-", "_")


def parse_sections(text: str) -> dict[str, str]:
    matches = list(HEADING_RE.finditer(text))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[section_key(match.group(1))] = text[start:end].strip()
    return sections


def parse_bullets(section: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.rstrip()
        if line.startswith("- "):
            if current:
                items.append(" ".join(current).strip())
            current = [line[2:].strip()]
        elif current and line.startswith("  "):
            current.append(line.strip())
    if current:
        items.append(" ".join(current).strip())
    return items


def parse_numbered(section: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.rstrip()
        if re.match(r"^\d+\.\s+", line):
            if current:
                items.append(" ".join(current).strip())
            current = [re.sub(r"^\d+\.\s+", "", line).strip()]
        elif current and line.startswith("   "):
            current.append(line.strip())
    if current:
        items.append(" ".join(current).strip())
    return items


def parse_code_commands(section: str) -> list[str]:
    in_fence = False
    commands: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence and line:
            commands.append(line)
    return commands


def parse_audit(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip() if text.splitlines() else path.stem
    sections = parse_sections(text)
    missing = [name for name in REQUIRED_SECTIONS if name not in sections or not sections[name]]
    outcomes = {name: parse_bullets(sections.get(name, "")) for name in OUTCOME_SECTIONS}
    return {
        "audit_id": path.stem,
        "title": title,
        "path": rel(path),
        "missing_sections": missing,
        "source_slice": parse_bullets(sections.get("source_slice", "")),
        "read_files_or_urls": parse_bullets(sections.get("read_files_or_urls", "")),
        "architecture_claims": parse_numbered(sections.get("architecture_claims", "")),
        "outcomes": outcomes,
        "required_patch": parse_bullets(sections.get("required_patch", "")),
        "verification_commands": parse_code_commands(sections.get("verification", "")),
        "next_trigger": parse_bullets(sections.get("next_trigger", "")),
    }


def iter_audits(audit_dir: Path = AUDIT_DIR) -> list[Path]:
    if not audit_dir.exists():
        return []
    return sorted(audit_dir.glob("*.md"))


def build_index(args: argparse.Namespace) -> dict[str, Any]:
    audits = [parse_audit(path) for path in iter_audits(args.audit_dir)]
    outcome_counts = {name: 0 for name in OUTCOME_SECTIONS}
    for audit in audits:
        for name, items in audit["outcomes"].items():
            outcome_counts[name] += len(items)
    result = {
        "count": len(audits),
        "outcome_counts": outcome_counts,
        "audits": audits,
    }
    if args.output:
        output = args.output if args.output.is_absolute() else ROOT / args.output
    else:
        output = INDEX_PATH
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["index_path"] = rel(output)
    return result


def validate_index(args: argparse.Namespace) -> dict[str, Any]:
    result = build_index(args)
    invalid = [audit for audit in result["audits"] if audit["missing_sections"]]
    if invalid:
        result["ok"] = False
        if args.strict:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            raise SystemExit(1)
        return result
    result["ok"] = True
    return result


def search_index(args: argparse.Namespace) -> dict[str, Any]:
    index_path = args.index if args.index.is_absolute() else ROOT / args.index
    if not index_path.exists():
        raise SystemExit("learning index does not exist; run build first")
    data = json.loads(index_path.read_text(encoding="utf-8"))
    needle = args.query.lower()
    hits = []
    for audit in data["audits"]:
        text = json.dumps(audit, ensure_ascii=False).lower()
        if needle not in text and needle not in audit["path"].lower():
            continue
        score = text.count(needle)
        if needle in audit["path"].lower():
            score += 10
        hits.append(
            {
                "score": score,
                "audit_id": audit["audit_id"],
                "path": audit["path"],
                "title": audit["title"],
                "outcomes": {key: len(value) for key, value in audit["outcomes"].items()},
            }
        )
    hits.sort(key=lambda item: (-item["score"], item["path"]))
    return {"query": args.query, "count": len(hits[: args.limit]), "hits": hits[: args.limit]}


def coverage_report(args: argparse.Namespace) -> dict[str, Any]:
    result = build_index(args)
    rows = []
    for family in SOURCE_FAMILIES:
        matched = []
        needles = [needle.lower() for needle in family["needles"]]
        for audit in result["audits"]:
            haystack = json.dumps(
                {
                    "path": audit["path"],
                    "source_slice": audit["source_slice"],
                    "read_files_or_urls": audit["read_files_or_urls"],
                    "architecture_claims": audit["architecture_claims"],
                    "outcomes": audit["outcomes"],
                },
                ensure_ascii=False,
            ).lower()
            if any(needle.lower() in haystack for needle in needles):
                matched.append(
                    {
                        "audit_id": audit["audit_id"],
                        "path": audit["path"],
                        "title": audit["title"],
                    }
                )
        status = "covered" if matched else "missing"
        rows.append(
            {
                "family": family["family"],
                "required": family["required"],
                "status": status,
                "description": family["description"],
                "matched_audits": matched,
            }
        )
    required_missing = [row["family"] for row in rows if row["required"] and row["status"] == "missing"]
    report = {
        "audit_count": result["count"],
        "required_family_count": sum(1 for row in rows if row["required"]),
        "covered_required_count": sum(
            1 for row in rows if row["required"] and row["status"] == "covered"
        ),
        "missing_required": required_missing,
        "ok": not required_missing,
        "families": rows,
    }
    if args.strict and required_missing:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("--audit-dir", type=Path, default=AUDIT_DIR)
    build.add_argument("--output", type=Path, default=INDEX_PATH)
    build.set_defaults(func=build_index)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--audit-dir", type=Path, default=AUDIT_DIR)
    validate.add_argument("--output", type=Path, default=INDEX_PATH)
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(func=validate_index)

    search = subparsers.add_parser("search")
    search.add_argument("--index", type=Path, default=INDEX_PATH)
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=20)
    search.set_defaults(func=search_index)

    coverage = subparsers.add_parser("coverage")
    coverage.add_argument("--audit-dir", type=Path, default=AUDIT_DIR)
    coverage.add_argument("--output", type=Path, default=INDEX_PATH)
    coverage.add_argument("--strict", action="store_true")
    coverage.set_defaults(func=coverage_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
