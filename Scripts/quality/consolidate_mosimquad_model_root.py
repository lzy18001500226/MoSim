#!/usr/bin/env python3
"""Check that MoSim exposes one formal MWORKS Modelica root.

The project is reviewed and reproduced by loading exactly one package:
``Models/MoSimQuadrotorModel/package.mo``.  This check intentionally rejects
the former top-level facade packages and any active runner/config reference to
them.  It is source-only and does not claim MWORKS simulation success.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS = REPO_ROOT / "Models"
CANONICAL_ROOT = MODELS / "MoSimQuadrotorModel"
MANIFEST_PATH = REPO_ROOT / "Config" / "control_platform" / "model_namespace_migration.json"

REQUIRED_TOP_LEVEL = (
    "Plant",
    "Dynamics",
    "Parameters",
    "Missions",
    "Controllers",
    "Robustness",
    "Planning",
    "Formation",
    "ExperimentRunner",
    "LiveIntegration",
    "SceneTrace",
    "Support",
    "System",
)

RETIRED_MODEL_ROOTS = (
    MODELS / "QuadrotorExperiments",
    MODELS / "QuadrotorControllerBlocks",
    MODELS / "MworksLive",
    MODELS / "MoSimQuadrotorModel_backup",
)

LEGACY_REFERENCE = re.compile(
    r"(?:\b(?:QuadrotorExperiments|QuadrotorControllerBlocks|MworksLive)\.|"
    r"Models[\\/](?:QuadrotorExperiments|QuadrotorControllerBlocks|MworksLive)|"
    r"References[\\/]MWORKS[\\/]QuadrotorModel)"
)
EXTERNAL_PLANT_REFERENCE = re.compile(
    r"\b(?:within|extends|import)\s+QuadrotorModel(?:\.|\s|;)"
)
RETIRED_NAMESPACE_REFERENCE = re.compile(
    r"(?<![A-Za-z0-9_])QuadrotorModel(?:\.|[\\/])"
)
CANONICAL_RESOURCE_URI = re.compile(r"modelica://MoSimQuadrotorModel/([^\"'\s,)]+)")
PACKAGE_DECLARATION = re.compile(r"(?m)^\s*package\s+([A-Za-z_]\w*)\b")
PACKAGE_MEMBER_DECLARATION = re.compile(
    r"(?m)^\s*(?:package|model|block|record|function|connector|type|class)\s+([A-Za-z_]\w*)\b"
)


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def expected_within(path: Path) -> str:
    relative_parts = path.relative_to(CANONICAL_ROOT).parts
    if path.name == "package.mo":
        parent_parts = relative_parts[:-2]
    else:
        parent_parts = relative_parts[:-1]
    return ".".join(("MoSimQuadrotorModel", *parent_parts))


def has_within(text: str, namespace: str) -> bool:
    return bool(re.search(rf"(?m)^\s*within\s+{re.escape(namespace)}\s*;", text))


def package_order_entry_exists(package_path: Path, entry: str) -> bool:
    package_dir = package_path.parent
    if (package_dir / f"{entry}.mo").is_file():
        return True
    if (package_dir / entry / "package.mo").is_file():
        return True
    members = set(PACKAGE_MEMBER_DECLARATION.findall(read_text(package_path)))
    return entry in members


def check_package_integrity(errors: list[str]) -> None:
    for package_path in sorted(CANONICAL_ROOT.rglob("package.mo")):
        if package_path == CANONICAL_ROOT / "package.mo":
            continue
        text = read_text(package_path)
        expected_namespace = expected_within(package_path)
        relative = rel(package_path)
        if not has_within(text, expected_namespace):
            errors.append(
                f"nested package has wrong within namespace: {relative} -> {expected_namespace}"
            )
        expected_name = package_path.parent.name
        if expected_name not in PACKAGE_DECLARATION.findall(text):
            errors.append(f"nested package declaration is missing: {relative} -> {expected_name}")

        order_path = package_path.with_name("package.order")
        if not order_path.is_file():
            continue
        for entry in (line.strip() for line in read_text(order_path).splitlines()):
            if entry and not package_order_entry_exists(package_path, entry):
                errors.append(
                    f"package.order entry has no source: {rel(order_path)} -> {entry}"
                )

    for source in sorted(CANONICAL_ROOT.rglob("*.mo")):
        if source.name == "package.mo":
            continue
        expected_namespace = expected_within(source)
        if not has_within(read_text(source), expected_namespace):
            errors.append(
                f"model source has wrong within namespace: {rel(source)} -> {expected_namespace}"
            )


def active_reference_paths() -> list[Path]:
    paths: set[Path] = set()
    for root in (
        REPO_ROOT / "Config" / "scenarios",
        REPO_ROOT / "Config" / "control_platform",
        REPO_ROOT / "Scripts" / "mworks",
        REPO_ROOT / "Scripts" / "quality",
        REPO_ROOT / "Scripts" / "tests",
    ):
        if root.is_dir():
            paths.update(path for path in root.rglob("*") if path.suffix in {".json", ".yaml", ".yml", ".py"})

    paths.update(
        path
        for path in (
            REPO_ROOT / "Docs" / "Workflows" / "run_simulation.md",
            REPO_ROOT / "Docs" / "Workflows" / "controller_evidence_closeout.md",
            REPO_ROOT / "Docs" / "Workflows" / "project_structure_refactor.md",
            REPO_ROOT / "Docs" / "user_manual.md",
            REPO_ROOT / "Docs" / "Index" / "simulation_model_structure_index.md",
            REPO_ROOT / "Docs" / "Index" / "mworks_flight_animation_model_catalog.md",
            REPO_ROOT / "Docs" / "Design" / "架构" / "01_控制器平台" / "MWORKS控制器关系与组合架构.md",
            REPO_ROOT / "Models" / "README.md",
            REPO_ROOT / "README.md",
        )
        if path.is_file()
    )
    paths.difference_update(
        {
            MANIFEST_PATH,
            # This static migration audit names retired paths only to verify
            # that they are absent; it is not an MWORKS loading entry point.
            REPO_ROOT / "Scripts" / "mworks" / "validate_mosimquad_dynamics_batch_a_source_migration.py",
        }
    )
    return sorted(paths)


def check_manifest(errors: list[str]) -> None:
    if not MANIFEST_PATH.is_file():
        errors.append(f"missing canonical-root manifest: {rel(MANIFEST_PATH)}")
        return
    try:
        manifest = json.loads(read_text(MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid canonical-root manifest: {exc}")
        return

    expected = {
        "schema_version": 2,
        "status": "canonical_single_root",
        "canonical_model_root": "Models/MoSimQuadrotorModel",
        "formal_load_file": "Models/MoSimQuadrotorModel/package.mo",
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            errors.append(f"canonical-root manifest {key!r} must be {value!r}")


def check_canonical_root(errors: list[str]) -> None:
    package_path = CANONICAL_ROOT / "package.mo"
    order_path = CANONICAL_ROOT / "package.order"
    if not package_path.is_file():
        errors.append("canonical package.mo is missing")
        return
    package_text = read_text(package_path)
    if "package MoSimQuadrotorModel" not in package_text:
        errors.append("canonical package.mo does not declare MoSimQuadrotorModel")
    if EXTERNAL_PLANT_REFERENCE.search(package_text):
        errors.append("canonical package imports an external QuadrotorModel root")
    if RETIRED_NAMESPACE_REFERENCE.search(package_text):
        errors.append("canonical package retains a retired QuadrotorModel namespace")

    if not order_path.is_file():
        errors.append("canonical package.order is missing")
        return
    order = [line.strip() for line in read_text(order_path).splitlines() if line.strip()]
    for name in (*REQUIRED_TOP_LEVEL, "saturate"):
        if name not in order:
            errors.append(f"canonical package.order omits {name}")
    if "LegacyCompatibility" in order:
        errors.append("canonical package.order retains LegacyCompatibility")
    if "Baseline" in order:
        errors.append("canonical package.order retains the redundant Baseline facade")

    for name in REQUIRED_TOP_LEVEL:
        package = CANONICAL_ROOT / name / "package.mo"
        if not package.is_file():
            errors.append(f"canonical child package is missing: {rel(package)}")

    check_package_integrity(errors)

    for child in sorted(CANONICAL_ROOT.iterdir()):
        if child.is_dir() and child.name not in REQUIRED_TOP_LEVEL:
            errors.append(
                "canonical root retains an unregistered top-level directory: "
                f"{rel(child)}"
            )

    for source in CANONICAL_ROOT.rglob("*.mo"):
        text = read_text(source)
        if LEGACY_REFERENCE.search(text):
            errors.append(f"canonical source retains a retired root reference: {rel(source)}")
        if EXTERNAL_PLANT_REFERENCE.search(text):
            errors.append(f"canonical source retains an external plant reference: {rel(source)}")
        if RETIRED_NAMESPACE_REFERENCE.search(text):
            errors.append(f"canonical source retains a retired QuadrotorModel namespace: {rel(source)}")
        for resource_relative in CANONICAL_RESOURCE_URI.findall(text):
            resource = CANONICAL_ROOT / resource_relative
            if not resource.exists():
                errors.append(
                    "canonical source references a missing in-root resource: "
                    f"{rel(source)} -> {resource_relative}"
                )


def check_retirement(errors: list[str]) -> None:
    if MODELS.is_dir():
        for child in sorted(MODELS.iterdir()):
            if child.is_dir() and child != CANONICAL_ROOT:
                errors.append(f"unexpected second directory under Models: {rel(child)}")

    for root in RETIRED_MODEL_ROOTS:
        if root.exists():
            errors.append(f"retired Modelica root remains under Models: {rel(root)}")

    for path in active_reference_paths():
        text = read_text(path)
        if LEGACY_REFERENCE.search(text):
            errors.append(f"active file retains a retired model-root reference: {rel(path)}")
        if RETIRED_NAMESPACE_REFERENCE.search(text):
            errors.append(f"active file retains a retired QuadrotorModel namespace: {rel(path)}")


def validate() -> list[str]:
    errors: list[str] = []
    check_manifest(errors)
    check_canonical_root(errors)
    check_retirement(errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the canonical single-root layout")
    args = parser.parse_args()
    errors = validate()
    payload = {
        "status": "ok" if not errors else "failed",
        "formal_load_file": "Models/MoSimQuadrotorModel/package.mo",
        "source_only": True,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
