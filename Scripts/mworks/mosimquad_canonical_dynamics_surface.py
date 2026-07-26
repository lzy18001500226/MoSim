#!/usr/bin/env python3
"""Shared static checks for canonical MoSim dynamics source ownership."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
FORMAL_ROOT = ROOT / "Models" / "MoSimQuadrotorModel" / "Vehicle" / "Dynamics"
RETIRED_ROOTS = (
    ROOT / "Models" / "QuadrotorExperiments",
    ROOT / "Models" / "QuadrotorControllerBlocks",
    ROOT / "Models" / "MworksLive",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_order(path: Path) -> list[str]:
    return [line.strip() for line in read_text(path).splitlines() if line.strip()]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_finding(findings: list[dict[str, str]], code: str, message: str, target: Path) -> None:
    findings.append(
        {
            "severity": "error",
            "code": code,
            "message": message,
            "target": rel(target),
        }
    )


def anchor_rows(text: str, anchors: Iterable[str]) -> list[dict[str, Any]]:
    return [{"anchor": anchor, "present": anchor in text} for anchor in anchors]


def validate_component(
    *,
    formal_name: str,
    legacy_alias_name: str,
    legacy_file_name: str,
    legacy_file_model: str,
    primary_anchors: Iterable[str],
    related_sources: Iterable[tuple[str, Path, Iterable[str]]] = (),
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    formal_package = FORMAL_ROOT / "package.mo"
    formal_order = FORMAL_ROOT / "package.order"
    formal_source = FORMAL_ROOT / f"{formal_name}.mo"
    formal_package_text = read_text(formal_package) if formal_package.exists() else ""
    formal_order_entries = read_order(formal_order) if formal_order.exists() else []
    formal_text = read_text(formal_source) if formal_source.exists() else ""

    if not formal_source.is_file():
        add_finding(findings, "canonical_source_missing", "canonical Dynamics source file is missing", formal_source)
    if formal_name not in formal_order_entries:
        add_finding(findings, "canonical_order_missing", "canonical Dynamics package.order omits the model", formal_order)
    if f"model {formal_name}" in formal_package_text:
        add_finding(findings, "canonical_inline_duplicate", "canonical package.mo contains a duplicate inline model", formal_package)
    if f"within MoSimQuadrotorModel.Vehicle.Dynamics;" not in formal_text:
        add_finding(findings, "canonical_namespace_missing", "canonical source has the wrong namespace", formal_source)
    if f"model {formal_name}" not in formal_text:
        add_finding(findings, "canonical_model_missing", "canonical source lacks the model declaration", formal_source)
    if "QuadrotorExperiments" in formal_text or "Deprecated compatibility alias" in formal_text:
        add_finding(findings, "canonical_source_not_owned", "canonical source still carries a legacy implementation reference", formal_source)

    primary_rows = anchor_rows(formal_text, primary_anchors)
    for row in primary_rows:
        if not row["present"]:
            add_finding(findings, "canonical_anchor_missing", f"missing canonical source anchor {row['anchor']!r}", formal_source)

    for retired_root in RETIRED_ROOTS:
        if retired_root.exists():
            add_finding(
                findings,
                "retired_root_present",
                "a retired top-level Modelica root remains under Models",
                retired_root,
            )

    related_rows: list[dict[str, Any]] = []
    for label, source_path, anchors in related_sources:
        source_text = read_text(source_path) if source_path.exists() else ""
        if not source_path.is_file():
            add_finding(findings, "related_source_missing", f"related canonical source {label!r} is missing", source_path)
        for row in anchor_rows(source_text, anchors):
            row["source"] = rel(source_path)
            row["label"] = label
            related_rows.append(row)
            if not row["present"]:
                add_finding(
                    findings,
                    "related_anchor_missing",
                    f"related canonical source {label!r} lacks anchor {row['anchor']!r}",
                    source_path,
                )

    canonical_owned = (
        formal_source.is_file()
        and f"within MoSimQuadrotorModel.Vehicle.Dynamics;" in formal_text
        and f"model {formal_name}" in formal_text
        and "QuadrotorExperiments" not in formal_text
        and "Deprecated compatibility alias" not in formal_text
    )
    retired_roots_absent = all(not path.exists() for path in RETIRED_ROOTS)

    check = {
        "schema": "mosim.mworks.canonical_dynamics_surface_check.v2",
        "status": "passed_static" if not findings else "failed_static",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_target": f"MoSimQuadrotorModel.Vehicle.Dynamics.{formal_name}",
        "formal_source": rel(formal_source),
        "retired_predecessor": {
            "class_name": legacy_alias_name,
            "file_name": legacy_file_name,
            "model_name": legacy_file_model,
        },
        "source_authority": {
            "canonical_source_owns_implementation": canonical_owned,
            "retired_roots_absent": retired_roots_absent,
            "formal_package_order_contains_target": formal_name in formal_order_entries,
        },
        "canonical_anchors": primary_rows,
        "related_canonical_anchors": related_rows,
        "findings": findings,
    }
    return check, findings


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate_component(
    *,
    output_dir: Path,
    title: str,
    output_basename: str,
    formal_name: str,
    legacy_alias_name: str,
    legacy_file_name: str,
    legacy_file_model: str,
    primary_anchors: Iterable[str],
    related_sources: Iterable[tuple[str, Path, Iterable[str]]] = (),
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    check, _ = validate_component(
        formal_name=formal_name,
        legacy_alias_name=legacy_alias_name,
        legacy_file_name=legacy_file_name,
        legacy_file_model=legacy_file_model,
        primary_anchors=primary_anchors,
        related_sources=related_sources,
    )
    check_path = output_dir / f"{output_basename}.json"
    write_json(check_path, check)
    markdown_path = output_dir / f"{output_basename}.md"
    markdown_path.write_text(
        "\n".join(
            [
                f"# {title}",
                "",
                f"Status: `{check['status']}`",
                "",
                f"- Canonical implementation: `{check['formal_target']}`",
                f"- Canonical source: `{check['formal_source']}`",
                f"- Retired predecessor: `{check['retired_predecessor']['class_name']}`",
                "",
                "This is a static source-ownership check. It does not claim MWORKS load, simulation, graphical evidence, controller performance, or closed-loop success.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    summary = {
        "status": "passed" if check["status"] == "passed_static" else "failed",
        "static_only": True,
        "live_mworks_touched": False,
        "mworks_window_evidence_touched": False,
        "formal_source_materialized": check["source_authority"]["canonical_source_owns_implementation"],
        "canonical_implementation_owned": check["source_authority"]["canonical_source_owns_implementation"],
        "retired_predecessor_recorded": bool(check["retired_predecessor"]["class_name"]),
        "findings": check["findings"],
        "evidence_files": [rel(check_path), rel(markdown_path)],
    }
    write_json(output_dir / "static_validation_summary.json", summary)
    return summary
