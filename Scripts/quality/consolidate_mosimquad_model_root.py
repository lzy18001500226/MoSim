#!/usr/bin/env python3
"""Consolidate MoSim's active Modelica implementation under one formal root.

The operation is intentionally namespace-preserving for callers: canonical
implementations are copied into ``MoSimQuadrotorModel`` and the former roots
become thin hidden aliases.  It is safe to re-run after a successful apply and
refuses unknown class declarations or target collisions.

This script is a source/static migration tool.  It does not invoke MWORKS,
check a graphical layout, or claim simulation success.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS = REPO_ROOT / "Models"
CANONICAL_ROOT = MODELS / "MoSimQuadrotorModel"
QEXP_ROOT = MODELS / "QuadrotorExperiments"
CONTROLLER_ROOT = MODELS / "QuadrotorControllerBlocks"
LIVE_ROOT = MODELS / "MworksLive"
MANIFEST_PATH = REPO_ROOT / "Config" / "control_platform" / "model_namespace_migration.json"


@dataclass(frozen=True)
class CategoryRoute:
    legacy_name: str
    target_relative: Path
    target_namespace: str


CATEGORY_ROUTES = (
    CategoryRoute(
        "ControllerBaselines",
        Path("Controllers/Baselines"),
        "MoSimQuadrotorModel.Controllers.Baselines",
    ),
    CategoryRoute(
        "FormationScenarios",
        Path("Formation/Scenarios"),
        "MoSimQuadrotorModel.Formation.Scenarios",
    ),
    CategoryRoute(
        "OfficialScenarios",
        Path("Missions/Official"),
        "MoSimQuadrotorModel.Missions.Official",
    ),
    CategoryRoute(
        "PlanningScenarios",
        Path("Planning/Scenarios"),
        "MoSimQuadrotorModel.Planning.Scenarios",
    ),
    CategoryRoute(
        "RobustFaultScenarios",
        Path("Robustness/Scenarios"),
        "MoSimQuadrotorModel.Robustness.Scenarios",
    ),
    CategoryRoute(
        "SceneTraceScenarios",
        Path("SceneTrace/Scenarios"),
        "MoSimQuadrotorModel.SceneTrace.Scenarios",
    ),
    CategoryRoute(
        "TraceIsolation",
        Path("SceneTrace/Diagnostics"),
        "MoSimQuadrotorModel.SceneTrace.Diagnostics",
    ),
    CategoryRoute(
        "SupportModels",
        Path("Support/Models"),
        "MoSimQuadrotorModel.Support.Models",
    ),
    CategoryRoute(
        "SystemArchitecture",
        Path("System/Architecture"),
        "MoSimQuadrotorModel.System.Architecture",
    ),
    CategoryRoute(
        "SystemModules",
        Path("System/Modules"),
        "MoSimQuadrotorModel.System.Modules",
    ),
)

CATEGORY_BY_NAME = {route.legacy_name: route for route in CATEGORY_ROUTES}

# Dynamics class names are deliberately concise in the canonical package.
# Both raw historical names and former curated aliases resolve to these names.
DYNAMICS_CLASS_NAMES = {
    "Sunray150ActuatorCommandMapper": "ActuatorCommandMapper",
    "ActuatorCommandMapper": "ActuatorCommandMapper",
    "Sunray150ActuatorMappedWrapperSurface": "ActuatorMappedWrapperSurface",
    "ActuatorMappedWrapperSurface": "ActuatorMappedWrapperSurface",
    "Sunray150DynamicsUpgradeHoverSmoke": "HoverSmoke",
    "RotorHoverSmoke": "HoverSmoke",
    "Sunray150DynamicsUpgradeYawStepSmoke": "YawStepSmoke",
    "RotorYawStepSmoke": "YawStepSmoke",
    "Sunray150DynamicsWrapperHoverSmoke": "WrapperHoverSmoke",
    "WrapperHoverSmoke": "WrapperHoverSmoke",
    "Sunray150DynamicsWrapperSurface": "WrapperSurface",
    "WrapperSurface": "WrapperSurface",
    "Sunray150DynamicsWrapperYawStepSmoke": "WrapperYawStepSmoke",
    "WrapperYawStepSmoke": "WrapperYawStepSmoke",
    "Sunray150OptionalDampingGyroLayer": "OptionalDampingGyroLayer",
    "OptionalDampingGyroLayer": "OptionalDampingGyroLayer",
    "Sunray150PhysicalWrenchFrameAdapter": "PhysicalWrenchAdapter",
    "PhysicalWrenchAdapter": "PhysicalWrenchAdapter",
    "Sunray150PhysicalWrenchHoverSmoke": "PhysicalWrenchHoverSmoke",
    "PhysicalWrenchHoverSmoke": "PhysicalWrenchHoverSmoke",
    "Sunray150PhysicalWrenchYawStepSmoke": "PhysicalWrenchYawStepSmoke",
    "PhysicalWrenchYawStepSmoke": "PhysicalWrenchYawStepSmoke",
    "Sunray150RflyStyleRotorDynamics": "RotorActuatorCore",
    "RotorDynamicsCore": "RotorActuatorCore",
    "Sunray150RotorEffectivenessSmoke": "RotorEffectivenessSmoke",
    "RotorEffectivenessSmoke": "RotorEffectivenessSmoke",
}

# Historical scenario metadata used both ``GPS`` and ``Gps`` in an otherwise
# identical class name. Modelica is case-sensitive, so retain this exact
# compatibility spelling in the config migration map instead of leaving a
# legacy root reference behind.
HISTORICAL_MODEL_CLASS_ALIASES = {
    "QuadrotorExperiments.Sunray150CompleteSystemGpsDropoutSysblock": (
        "MoSimQuadrotorModel.System.Architecture."
        "Sunray150CompleteSystemGPSDropoutSysblock"
    ),
}

NAMESPACE_REPLACEMENTS = {
    "QuadrotorExperiments.saturate": "MoSimQuadrotorModel.saturate",
    "QuadrotorExperiments.ControllerBaselines": "MoSimQuadrotorModel.Controllers.Baselines",
    "QuadrotorExperiments.FormationScenarios": "MoSimQuadrotorModel.Formation.Scenarios",
    "QuadrotorExperiments.OfficialScenarios": "MoSimQuadrotorModel.Missions.Official",
    "QuadrotorExperiments.PlanningScenarios": "MoSimQuadrotorModel.Planning.Scenarios",
    "QuadrotorExperiments.RobustFaultScenarios": "MoSimQuadrotorModel.Robustness.Scenarios",
    "QuadrotorExperiments.SceneTraceScenarios": "MoSimQuadrotorModel.SceneTrace.Scenarios",
    "QuadrotorExperiments.TraceIsolation": "MoSimQuadrotorModel.SceneTrace.Diagnostics",
    "QuadrotorExperiments.SupportModels": "MoSimQuadrotorModel.Support.Models",
    "QuadrotorExperiments.SystemArchitecture": "MoSimQuadrotorModel.System.Architecture",
    "QuadrotorExperiments.SystemModules": "MoSimQuadrotorModel.System.Modules",
    "QuadrotorControllerBlocks": "MoSimQuadrotorModel.Controllers.Sysblocks",
    "MworksLive": "MoSimQuadrotorModel.LiveIntegration",
}

CLASS_DECLARATION = re.compile(
    r"(?m)^\s*(model|block|record|function)\s+([A-Za-z_][A-Za-z0-9_]*)\b"
)
WITHIN_DECLARATION = re.compile(r"(?m)^\s*within\s+([^;]+);\s*$")
LEGACY_NAMESPACE_TOKEN = re.compile(
    r"\b(?:QuadrotorExperiments|QuadrotorControllerBlocks|MworksLive)\b"
)
ROOT_SATURATE = re.compile(
    r"(?ms)^[ \t]*function\s+saturate\b.*?^[ \t]*end\s+saturate;\s*"
)

CANONICAL_PARENT_ORDERS: dict[Path, tuple[str, ...]] = {
    Path("Controllers"): ("Baselines", "Sysblocks", "GraphicalMIL", "IntegratedChains"),
    Path("Missions"): ("Official",),
    Path("Robustness"): ("Scenarios",),
    Path("Planning"): ("Scenarios",),
    Path("Formation"): ("Scenarios",),
    Path("SceneTrace"): ("Scenarios", "Diagnostics"),
    Path("Support"): ("Models",),
    Path("System"): ("Architecture", "Modules"),
}


def rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def declared_class(path: Path) -> tuple[str, str]:
    match = CLASS_DECLARATION.search(read_text(path))
    if not match:
        raise ValueError(f"Cannot find a supported Modelica class declaration: {rel(path)}")
    return match.group(1), match.group(2)


def declared_within(path: Path) -> str | None:
    match = WITHIN_DECLARATION.search(read_text(path))
    return match.group(1).strip() if match else None


def replace_namespace(text: str, old: str, new: str) -> str:
    pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?=[.\s;,(){{}}])")
    return pattern.sub(new, text)


def replace_qualified_namespace(text: str, old: str, new: str) -> str:
    pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?=\.)")
    return pattern.sub(new, text)


def rewrite_references(text: str) -> str:
    for legacy_name, canonical_name in sorted(
        DYNAMICS_CLASS_NAMES.items(), key=lambda item: len(item[0]), reverse=True
    ):
        text = replace_namespace(
            text,
            f"QuadrotorExperiments.DynamicsUpgrade.{legacy_name}",
            f"MoSimQuadrotorModel.Dynamics.{canonical_name}",
        )

    for old, new in sorted(NAMESPACE_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        if old in {"QuadrotorControllerBlocks", "MworksLive"}:
            text = replace_qualified_namespace(text, old, new)
        else:
            text = replace_namespace(text, old, new)

    text = text.replace(
        "modelica://MoSimQuadrotorModel/LiveIntegration/",
        "modelica://MoSimQuadrotorModel/LiveIntegration/",
    )
    return text


def update_root_package_declaration(text: str, source_name: str, target_name: str) -> str:
    pattern = re.compile(rf"(?m)^package\s+{re.escape(source_name)}\b")
    updated, count = pattern.subn(f"package {target_name}", text, count=1)
    if count != 1:
        raise ValueError(f"Cannot rename package {source_name} to {target_name}")
    terminator = re.compile(rf"(?m)^(\s*)end\s+{re.escape(source_name)};\s*$")
    updated, count = terminator.subn(rf"\1end {target_name};", updated, count=1)
    if count != 1:
        raise ValueError(f"Cannot rename package terminator {source_name} to {target_name}")
    return updated


def normalize_outer_package_terminator(text: str) -> str:
    """Make a package.mo outer terminator match its declared package name."""
    declaration = re.search(r"(?m)^\s*package\s+([A-Za-z_][A-Za-z0-9_]*)\b", text)
    if not declaration:
        return text
    terminators = list(
        re.finditer(r"(?m)^(\s*)end\s+([A-Za-z_][A-Za-z0-9_]*)\s*;\s*$", text)
    )
    if not terminators:
        raise ValueError("Cannot find outer package terminator")
    outer = terminators[-1]
    package_name = declaration.group(1)
    if outer.group(2) == package_name:
        return text
    return text[: outer.start(2)] + package_name + text[outer.end(2) :]

def make_wrapper(source_path: Path, canonical_fqn: str) -> str:
    kind, class_name = declared_class(source_path)
    within = declared_within(source_path)
    prefix = f"within {within};\n" if within else ""
    return (
        f"{prefix}{kind} {class_name}\n"
        f"  \"Deprecated compatibility alias; canonical implementation is {canonical_fqn}\"\n"
        f"  extends {canonical_fqn};\n"
        "  annotation(__MWORKS(hide=true));\n"
        f"end {class_name};\n"
    )


def qexp_target_for_file(source_path: Path) -> tuple[Path, str]:
    relative_path = source_path.relative_to(QEXP_ROOT)
    category = relative_path.parts[0]
    kind, class_name = declared_class(source_path)
    del kind

    if category == "DynamicsUpgrade":
        canonical_name = DYNAMICS_CLASS_NAMES.get(class_name)
        if not canonical_name:
            raise ValueError(f"Missing dynamics mapping for {rel(source_path)}")
        target = CANONICAL_ROOT / "Dynamics" / f"{canonical_name}.mo"
        return target, f"MoSimQuadrotorModel.Dynamics.{canonical_name}"

    route = CATEGORY_BY_NAME.get(category)
    if not route:
        raise ValueError(f"Missing category route for {rel(source_path)}")

    nested = Path(*relative_path.parts[1:-1])
    target = CANONICAL_ROOT / route.target_relative / nested / source_path.name
    namespace = route.target_namespace
    if nested.parts:
        namespace = f"{namespace}.{'.'.join(nested.parts)}"
    return target, f"{namespace}.{class_name}"


def controller_target_for_file(source_path: Path) -> tuple[Path, str]:
    _, class_name = declared_class(source_path)
    target = CANONICAL_ROOT / "Controllers" / "Sysblocks" / source_path.name
    return target, f"MoSimQuadrotorModel.Controllers.Sysblocks.{class_name}"


def live_target_for_file(source_path: Path) -> tuple[Path, str]:
    _, class_name = declared_class(source_path)
    target = CANONICAL_ROOT / "LiveIntegration" / source_path.name
    return target, f"MoSimQuadrotorModel.LiveIntegration.{class_name}"


def copy_file_if_compatible(source: Path, target: Path, content: str, apply: bool) -> None:
    if target.exists():
        current = read_text(target)
        if current != content:
            raise ValueError(f"Target collision with different content: {rel(target)}")
        return
    if apply:
        write_text(target, content)


def copy_binary_if_compatible(source: Path, target: Path, apply: bool) -> None:
    if target.exists():
        if source.read_bytes() != target.read_bytes():
            raise ValueError(f"Resource collision with different content: {rel(target)}")
        return
    if apply:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def migrate_qexp_category(route: CategoryRoute, apply: bool, operations: list[str]) -> None:
    source_root = QEXP_ROOT / route.legacy_name
    target_root = CANONICAL_ROOT / route.target_relative
    if not source_root.is_dir():
        raise ValueError(f"Missing source category: {rel(source_root)}")

    for source in sorted(source_root.rglob("*.mo")):
        source_relative = source.relative_to(source_root)
        target = target_root / source_relative
        text = rewrite_references(read_text(source))

        if source.name == "package.mo" and source_relative.parent == Path("."):
            target_parent = route.target_namespace.rsplit(".", 1)[0]
            text = re.sub(
                rf"(?m)^\s*within\s+{re.escape('QuadrotorExperiments')};\s*$",
                f"within {target_parent};",
                text,
                count=1,
            )
            text = update_root_package_declaration(text, route.legacy_name, target_root.name)

        copy_file_if_compatible(source, target, text, apply)
        operations.append(f"canonical-copy {rel(source)} -> {rel(target)}")

    for source in sorted(source_root.rglob("package.order")):
        target = target_root / source.relative_to(source_root)
        copy_binary_if_compatible(source, target, apply)
        operations.append(f"order-copy {rel(source)} -> {rel(target)}")


def migrate_controller_blocks(apply: bool, operations: list[str]) -> None:
    target_root = CANONICAL_ROOT / "Controllers" / "Sysblocks"
    for source in sorted(CONTROLLER_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        text = rewrite_references(read_text(source))
        if not declared_within(source):
            text = f"within MoSimQuadrotorModel.Controllers.Sysblocks;\n{text}"
        target, _ = controller_target_for_file(source)
        copy_file_if_compatible(source, target, text, apply)
        operations.append(f"canonical-copy {rel(source)} -> {rel(target)}")

    source_package = CONTROLLER_ROOT / "package.mo"
    package_text = rewrite_references(read_text(source_package))
    package_text = update_root_package_declaration(
        package_text, "QuadrotorControllerBlocks", "Sysblocks"
    )
    package_text = f"within MoSimQuadrotorModel.Controllers;\n{package_text}"
    copy_file_if_compatible(source_package, target_root / "package.mo", package_text, apply)
    copy_binary_if_compatible(
        CONTROLLER_ROOT / "package.order", target_root / "package.order", apply
    )
    operations.append(f"canonical-copy {rel(source_package)} -> {rel(target_root / 'package.mo')}")


def migrate_live_package(apply: bool, operations: list[str]) -> None:
    target_root = CANONICAL_ROOT / "LiveIntegration"
    for source in sorted(LIVE_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        text = rewrite_references(read_text(source))
        text = re.sub(
            r"(?m)^\s*within\s+MworksLive;\s*$",
            "within MoSimQuadrotorModel.LiveIntegration;",
            text,
            count=1,
        )
        target, _ = live_target_for_file(source)
        copy_file_if_compatible(source, target, text, apply)
        operations.append(f"canonical-copy {rel(source)} -> {rel(target)}")

    source_package = LIVE_ROOT / "package.mo"
    package_text = rewrite_references(read_text(source_package))
    package_text = update_root_package_declaration(package_text, "MworksLive", "LiveIntegration")
    package_text = f"within MoSimQuadrotorModel;\n{package_text}"
    copy_file_if_compatible(source_package, target_root / "package.mo", package_text, apply)
    copy_binary_if_compatible(LIVE_ROOT / "package.order", target_root / "package.order", apply)
    operations.append(f"canonical-copy {rel(source_package)} -> {rel(target_root / 'package.mo')}")

    resource_root = LIVE_ROOT / "Resources"
    for source in sorted(resource_root.rglob("*")):
        if source.is_file():
            target = target_root / "Resources" / source.relative_to(resource_root)
            copy_binary_if_compatible(source, target, apply)
            operations.append(f"resource-copy {rel(source)} -> {rel(target)}")


def update_canonical_references(apply: bool, operations: list[str]) -> None:
    for path in sorted(CANONICAL_ROOT.rglob("*.mo")):
        before = read_text(path)
        after = rewrite_references(before)
        after = after.replace(
            "Formal public alias; source implementation remains in QuadrotorExperiments",
            "Canonical scenario composition alias",
        )
        if after != before:
            if apply:
                write_text(path, after)
            operations.append(f"canonical-reference {rel(path)}")

def update_root_package_order(apply: bool, operations: list[str]) -> None:
    package_order = CANONICAL_ROOT / "package.order"
    lines = package_order.read_text(encoding="utf-8").splitlines()
    if "LiveIntegration" not in lines:
        insertion_after = "ExperimentRunner"
        index = lines.index(insertion_after) + 1 if insertion_after in lines else len(lines)
        lines.insert(index, "LiveIntegration")
        if apply:
            write_text(package_order, "\n".join(lines) + "\n")
        operations.append(f"package-order {rel(package_order)} + LiveIntegration")


def rewrite_legacy_implementations(apply: bool, operations: list[str]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []

    for source in sorted(QEXP_ROOT.rglob("*.mo")):
        if source.name == "package.mo":
            continue
        _, canonical = qexp_target_for_file(source)
        wrapper = make_wrapper(source, canonical)
        if apply:
            write_text(source, wrapper)
        operations.append(f"legacy-wrapper {rel(source)} -> {canonical}")
        entries.append(
            {
                "legacy_class": f"{declared_within(source)}.{declared_class(source)[1]}",
                "canonical_class": canonical,
                "legacy_file": rel(source),
                "canonical_file": rel(qexp_target_for_file(source)[0]),
            }
        )

    for source in sorted(CONTROLLER_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        _, canonical = controller_target_for_file(source)
        wrapper = make_wrapper(source, canonical)
        if apply:
            write_text(source, wrapper)
        operations.append(f"legacy-wrapper {rel(source)} -> {canonical}")
        entries.append(
            {
                "legacy_class": f"QuadrotorControllerBlocks.{declared_class(source)[1]}",
                "canonical_class": canonical,
                "legacy_file": rel(source),
                "canonical_file": rel(controller_target_for_file(source)[0]),
            }
        )

    for source in sorted(LIVE_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        _, canonical = live_target_for_file(source)
        wrapper = make_wrapper(source, canonical)
        if apply:
            write_text(source, wrapper)
        operations.append(f"legacy-wrapper {rel(source)} -> {canonical}")
        entries.append(
            {
                "legacy_class": f"{declared_within(source)}.{declared_class(source)[1]}",
                "canonical_class": canonical,
                "legacy_file": rel(source),
                "canonical_file": rel(live_target_for_file(source)[0]),
            }
        )

    return entries


def manifest_payload(entries: list[dict[str, str]]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": "static_namespace_consolidation",
        "canonical_model_root": "Models/MoSimQuadrotorModel",
        "active_implementation_namespaces": [
            "MoSimQuadrotorModel.Controllers",
            "MoSimQuadrotorModel.Dynamics",
            "MoSimQuadrotorModel.Missions",
            "MoSimQuadrotorModel.Robustness",
            "MoSimQuadrotorModel.Planning",
            "MoSimQuadrotorModel.Formation",
            "MoSimQuadrotorModel.System",
            "MoSimQuadrotorModel.SceneTrace",
            "MoSimQuadrotorModel.Support",
            "MoSimQuadrotorModel.ExperimentRunner",
            "MoSimQuadrotorModel.LiveIntegration",
        ],
        "legacy_compatibility_roots": [
            "Models/QuadrotorExperiments",
            "Models/QuadrotorControllerBlocks",
            "Models/MworksLive",
        ],
        "historical_snapshot": {
            "path": "Docs/Cache/model_legacy/MworksLive_backup_20260722",
            "role": "archive_only_not_an_active_model_root",
            "required_disposition": "archived_after_static_reference_audit",
        },
        "entries": sorted(entries, key=lambda entry: entry["legacy_class"]),
    }


def write_manifest(entries: list[dict[str, str]], apply: bool, operations: list[str]) -> None:
    content = json.dumps(manifest_payload(entries), ensure_ascii=False, indent=2) + "\n"
    if MANIFEST_PATH.exists() and read_text(MANIFEST_PATH) == content:
        return
    if apply:
        write_text(MANIFEST_PATH, content)
    operations.append(f"manifest {rel(MANIFEST_PATH)}")


def expected_entries() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for source in sorted(QEXP_ROOT.rglob("*.mo")):
        if source.name == "package.mo":
            continue
        target, canonical = qexp_target_for_file(source)
        within = declared_within(source)
        entries.append(
            {
                "legacy_class": f"{within}.{declared_class(source)[1]}",
                "canonical_class": canonical,
                "legacy_file": rel(source),
                "canonical_file": rel(target),
            }
        )
    for source in sorted(CONTROLLER_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        target, canonical = controller_target_for_file(source)
        entries.append(
            {
                "legacy_class": f"QuadrotorControllerBlocks.{declared_class(source)[1]}",
                "canonical_class": canonical,
                "legacy_file": rel(source),
                "canonical_file": rel(target),
            }
        )
    for source in sorted(LIVE_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        target, canonical = live_target_for_file(source)
        within = declared_within(source)
        entries.append(
            {
                "legacy_class": f"{within}.{declared_class(source)[1]}",
                "canonical_class": canonical,
                "legacy_file": rel(source),
                "canonical_file": rel(target),
            }
        )
    return sorted(entries, key=lambda entry: entry["legacy_class"])


def validate_static_state() -> list[str]:
    errors: list[str] = []
    if not MANIFEST_PATH.is_file():
        return [f"Missing migration manifest: {rel(MANIFEST_PATH)}"]

    try:
        manifest = json.loads(read_text(MANIFEST_PATH))
    except json.JSONDecodeError as exc:
        return [f"Invalid migration manifest: {exc}"]

    expected = expected_entries()
    if manifest.get("entries") != expected:
        errors.append("Migration manifest does not match the current legacy-source inventory")

    if "LiveIntegration" not in (CANONICAL_ROOT / "package.order").read_text(encoding="utf-8").splitlines():
        errors.append("MoSimQuadrotorModel/package.order does not include LiveIntegration")

    for entry in expected:
        canonical_path = REPO_ROOT / entry["canonical_file"]
        legacy_path = REPO_ROOT / entry["legacy_file"]
        if not canonical_path.is_file():
            errors.append(f"Missing canonical implementation: {entry['canonical_file']}")
            continue
        if not legacy_path.is_file():
            errors.append(f"Missing legacy compatibility file: {entry['legacy_file']}")
            continue
        legacy_text = read_text(legacy_path)
        if f"extends {entry['canonical_class']};" not in legacy_text:
            errors.append(f"Legacy class is not a canonical alias: {entry['legacy_file']}")
        if "__MWORKS(hide=true)" not in legacy_text:
            errors.append(f"Legacy alias is not hidden: {entry['legacy_file']}")

    for path in CANONICAL_ROOT.rglob("*.mo"):
        if "LegacyCompatibility" in path.parts:
            continue
        text = read_text(path)
        if LEGACY_NAMESPACE_TOKEN.search(text):
            errors.append(f"Canonical source retains a legacy namespace token: {rel(path)}")

    live_include = CANONICAL_ROOT / "LiveIntegration" / "Resources" / "Include"
    if not live_include.is_dir():
        errors.append("LiveIntegration resource include directory is missing")

    return errors


def changed_paths() -> set[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {Path(line.strip()) for line in result.stdout.splitlines() if line.strip()}


def model_reference_alias_maps() -> tuple[dict[str, str], dict[str, str]]:
    """Build exact old-entry aliases for active config migration.

    Historical scenario YAMLs often referenced a class as
    ``QuadrotorExperiments.<ClassName>`` even when its source file lived in a
    category directory. Namespace-only replacement cannot safely recover that
    form, so derive every alias from the canonical migration inventory and fail
    closed on an ambiguous class name.
    """

    fqn_aliases: dict[str, str] = {}
    path_aliases: dict[str, str] = {
        "Models/QuadrotorExperiments/package.mo": "Models/MoSimQuadrotorModel/package.mo",
        "Models/QuadrotorControllerBlocks/package.mo": "Models/MoSimQuadrotorModel/package.mo",
        "Models/MworksLive/package.mo": "Models/MoSimQuadrotorModel/package.mo",
    }
    canonical_by_simple_name: dict[str, str] = {}

    def register(mapping: dict[str, str], legacy: str, canonical: str, kind: str) -> None:
        previous = mapping.get(legacy)
        if previous is not None and previous != canonical:
            raise ValueError(
                f"Ambiguous {kind} migration alias `{legacy}`: {previous} versus {canonical}"
            )
        mapping[legacy] = canonical

    for entry in expected_entries():
        legacy_class = entry["legacy_class"]
        canonical_class = entry["canonical_class"]
        class_name = canonical_class.rsplit(".", 1)[1]
        existing = canonical_by_simple_name.get(class_name)
        if existing is not None and existing != canonical_class:
            raise ValueError(
                f"Ambiguous Modelica class name `{class_name}`: {existing} versus {canonical_class}"
            )
        canonical_by_simple_name[class_name] = canonical_class

        legacy_root = legacy_class.split(".", 1)[0]
        register(fqn_aliases, legacy_class, canonical_class, "Modelica class")
        register(fqn_aliases, f"{legacy_root}.{class_name}", canonical_class, "Modelica class")

        canonical_file = entry["canonical_file"]
        legacy_file = entry["legacy_file"]
        register(path_aliases, legacy_file, canonical_file, "model path")
        register(
            path_aliases,
            f"Models/{legacy_root}/{class_name}.mo",
            canonical_file,
            "model path",
        )

    for legacy_class, canonical_class in HISTORICAL_MODEL_CLASS_ALIASES.items():
        register(fqn_aliases, legacy_class, canonical_class, "Modelica class")

    return fqn_aliases, path_aliases


def replace_exact_tokens(text: str, replacements: dict[str, str]) -> str:
    """Replace only complete identifier/path tokens, longest aliases first."""

    for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
        pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])")
        text = pattern.sub(new, text)
    return text


def rewrite_source_package_values(text: str) -> str:
    """Promote model source-package fields without rewriting historical prose."""

    package_aliases = {
        "QuadrotorExperiments": "MoSimQuadrotorModel",
        "QuadrotorControllerBlocks": "MoSimQuadrotorModel",
        "MworksLive": "MoSimQuadrotorModel",
    }
    for old, new in package_aliases.items():
        yaml_pattern = re.compile(
            rf"(?m)^(\s*source_package\s*:\s*)([\"']?){re.escape(old)}\2(?=\s*(?:#.*)?$)"
        )
        json_pattern = re.compile(
            rf"(\"source_package\"\s*:\s*\"){re.escape(old)}(?=\")"
        )
        text = yaml_pattern.sub(rf"\1\2{new}", text)
        text = json_pattern.sub(rf"\1{new}", text)
    return text


def active_config_paths() -> list[Path]:
    suffixes = {".json", ".yaml", ".yml"}
    return sorted(
        path
        for path in (REPO_ROOT / "Config").rglob("*")
        if path.is_file()
        and path.suffix in suffixes
        and path.resolve() != MANIFEST_PATH.resolve()
    )


def validate_active_config_references() -> list[str]:
    errors: list[str] = []
    for path in active_config_paths():
        if LEGACY_NAMESPACE_TOKEN.search(read_text(path)):
            errors.append(f"Active config retains a legacy model-root reference: {rel(path)}")
    return errors


def rewrite_active_references(apply: bool, operations: list[str]) -> list[str]:
    """Rewrite active scenario/profile entry references using exact known aliases.

    The transform always reads the current file content and modifies only an
    exact legacy Modelica FQN, source-package value, or model path. That makes
    it safe to compose with unrelated user edits instead of discarding a dirty
    config wholesale. Scripts and compatibility validators are migrated at
    their owning entrypoints rather than by a repository-wide text pass.
    """

    fqn_aliases, path_aliases = model_reference_alias_maps()

    directory_aliases = {
        "Models/QuadrotorExperiments/ControllerBaselines": "Models/MoSimQuadrotorModel/Controllers/Baselines",
        "Models/QuadrotorExperiments/FormationScenarios": "Models/MoSimQuadrotorModel/Formation/Scenarios",
        "Models/QuadrotorExperiments/OfficialScenarios": "Models/MoSimQuadrotorModel/Missions/Official",
        "Models/QuadrotorExperiments/PlanningScenarios": "Models/MoSimQuadrotorModel/Planning/Scenarios",
        "Models/QuadrotorExperiments/RobustFaultScenarios": "Models/MoSimQuadrotorModel/Robustness/Scenarios",
        "Models/QuadrotorExperiments/SceneTraceScenarios": "Models/MoSimQuadrotorModel/SceneTrace/Scenarios",
        "Models/QuadrotorExperiments/TraceIsolation": "Models/MoSimQuadrotorModel/SceneTrace/Diagnostics",
        "Models/QuadrotorExperiments/SupportModels": "Models/MoSimQuadrotorModel/Support/Models",
        "Models/QuadrotorExperiments/SystemArchitecture": "Models/MoSimQuadrotorModel/System/Architecture",
        "Models/QuadrotorExperiments/SystemModules": "Models/MoSimQuadrotorModel/System/Modules",
        "Models/QuadrotorExperiments/DynamicsUpgrade": "Models/MoSimQuadrotorModel/Dynamics",
        "Models/QuadrotorControllerBlocks": "Models/MoSimQuadrotorModel/Controllers/Sysblocks",
        "Models/MworksLive": "Models/MoSimQuadrotorModel/LiveIntegration",
    }
    for legacy_name, canonical_name in DYNAMICS_CLASS_NAMES.items():
        directory_aliases[
            f"Models/QuadrotorExperiments/DynamicsUpgrade/{legacy_name}.mo"
        ] = f"Models/MoSimQuadrotorModel/Dynamics/{canonical_name}.mo"

    for path in active_config_paths():
        before = read_text(path)
        after = replace_exact_tokens(before, fqn_aliases)
        after = rewrite_references(after)
        after = rewrite_source_package_values(after)
        for replacements in (path_aliases, directory_aliases):
            for old, new in sorted(replacements.items(), key=lambda item: len(item[0]), reverse=True):
                after = after.replace(old, new)
                after = after.replace(old.replace("/", "\\"), new.replace("/", "\\"))
        if after == before:
            continue
        if apply:
            write_text(path, after)
        operations.append(f"active-reference {rel(path)}")

    return []


COMPLETE_FACADE_MARKER = "Deprecated compatibility facade; active implementation lives under MoSimQuadrotorModel."


def path_is_dirty(path: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", rel(path)],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())


def write_managed_text(
    target: Path, content: str, apply: bool, operations: list[str], operation: str
) -> None:
    if target.exists() and read_text(target) == content:
        return
    if target.exists() and path_is_dirty(target):
        raise ValueError(f"Refusing to overwrite dirty canonical target: {rel(target)}")
    if apply:
        write_text(target, content)
    operations.append(operation)


def write_legacy_facade_text(
    target: Path, content: str, apply: bool, operations: list[str], operation: str
) -> None:
    if read_text(target) == content:
        return
    if apply:
        write_text(target, content)
    operations.append(operation)


def legacy_alias_points_to(text: str, canonical_fqn: str) -> bool:
    return f"extends {canonical_fqn};" in text and "__MWORKS(hide=true)" in text


def copy_canonical_text(
    target: Path,
    content: str,
    apply: bool,
    operations: list[str],
    operation: str,
    *,
    replace_legacy_proxy: bool = False,
) -> None:
    if target.exists():
        current = read_text(target)
        if current == content:
            return
        is_proxy = bool(LEGACY_NAMESPACE_TOKEN.search(current)) and "extends" in current
        if is_proxy and not path_is_dirty(target):
            if apply:
                write_text(target, content)
            operations.append(operation)
            return
        raise ValueError(f"Target collision with different content: {rel(target)}")
    if apply:
        write_text(target, content)
    operations.append(operation)


def simple_package(
    within: str | None, name: str, description: str, *, hidden: bool = False
) -> str:
    prefix = f"within {within};\n" if within else ""
    annotation = "\n  annotation(__MWORKS(hide=true));" if hidden else ""
    return (
        f'{prefix}package {name}\n'
        f'  "{description}"\n\n'
        "  extends Modelica.Icons.Package;"
        f"{annotation}\n"
        f"end {name};\n"
    )


def prepare_canonical_surface(apply: bool, operations: list[str]) -> None:
    root_text = (
        "package MoSimQuadrotorModel\n"
        '  "MoSim formal quadrotor implementation root"\n\n'
        "  extends Modelica.Icons.Package;\n"
        "  annotation(uses(\n"
        '    Modelica(version = "4.0.0.TY.1"),\n'
        "    QuadrotorModel));\n"
        "end MoSimQuadrotorModel;\n"
    )
    write_managed_text(
        CANONICAL_ROOT / "package.mo",
        root_text,
        apply,
        operations,
        f"canonical-package {rel(CANONICAL_ROOT / 'package.mo')}",
    )

    package_specs = (
        ("Controllers", "MoSimQuadrotorModel", "controller implementations and graphical MIL entries", False),
        ("Missions", "MoSimQuadrotorModel", "official task scenarios", False),
        ("Robustness", "MoSimQuadrotorModel", "robustness, safety, and fault scenarios", False),
        ("Planning", "MoSimQuadrotorModel", "planning and obstacle-scene scenarios", False),
        ("Formation", "MoSimQuadrotorModel", "formation scenarios", False),
        ("SceneTrace", "MoSimQuadrotorModel", "scene trace scenarios and diagnostics", False),
        ("Support", "MoSimQuadrotorModel", "support models and references", False),
        ("System", "MoSimQuadrotorModel", "system architecture and hardware abstractions", False),
        ("LegacyCompatibility", "MoSimQuadrotorModel", "deprecated compatibility metadata; do not use as a new entry", True),
    )
    for relative, within, description, hidden in package_specs:
        target = CANONICAL_ROOT / relative / "package.mo"
        write_managed_text(
            target,
            simple_package(within, relative, description, hidden=hidden),
            apply,
            operations,
            f"canonical-package {rel(target)}",
        )

    root_order_path = CANONICAL_ROOT / "package.order"
    root_order = root_order_path.read_text(encoding="utf-8").splitlines()
    root_order = [name for name in root_order if name not in {"LiveIntegration", "saturate"}]
    insertion = root_order.index("ExperimentRunner") + 1 if "ExperimentRunner" in root_order else len(root_order)
    root_order.insert(insertion, "LiveIntegration")
    root_order.append("saturate")
    write_managed_text(
        root_order_path,
        "\n".join(root_order) + "\n",
        apply,
        operations,
        f"package-order {rel(root_order_path)}",
    )

    for relative, entries in CANONICAL_PARENT_ORDERS.items():
        target = CANONICAL_ROOT / relative / "package.order"
        write_managed_text(
            target,
            "\n".join(entries) + "\n",
            apply,
            operations,
            f"package-order {rel(target)}",
        )



def normalize_canonical_package_terminators(apply: bool, operations: list[str]) -> None:
    for target in sorted(CANONICAL_ROOT.rglob("package.mo")):
        before = read_text(target)
        after = normalize_outer_package_terminator(before)
        if after == before:
            continue
        if apply:
            write_text(target, after)
        operations.append(f"canonical-package-terminator {rel(target)}")

def migrate_root_saturate(apply: bool, operations: list[str]) -> None:
    source = QEXP_ROOT / "package.mo"
    source_text = read_text(source)
    match = ROOT_SATURATE.search(source_text)
    if not match:
        raise ValueError("Cannot locate QuadrotorExperiments.saturate")
    target = CANONICAL_ROOT / "saturate.mo"
    source_body = textwrap.dedent(match.group(0)).strip() + "\n"
    if legacy_alias_points_to(source_body, "MoSimQuadrotorModel.saturate"):
        if not target.is_file():
            raise ValueError("Legacy saturate wrapper exists without canonical implementation")
        return
    canonical_text = "within MoSimQuadrotorModel;\n" + source_body
    copy_canonical_text(
        target,
        canonical_text,
        apply,
        operations,
        f"canonical-copy {rel(source)}::saturate -> {rel(target)}",
    )


def migrate_qexp_category_complete(
    route: CategoryRoute, apply: bool, operations: list[str]
) -> None:
    source_root = QEXP_ROOT / route.legacy_name
    target_root = CANONICAL_ROOT / route.target_relative
    if not source_root.is_dir():
        raise ValueError(f"Missing source category: {rel(source_root)}")

    for source in sorted(source_root.rglob("*.mo")):
        source_relative = source.relative_to(source_root)
        source_text = read_text(source)
        target = target_root / source_relative
        if source.name == "package.mo" and COMPLETE_FACADE_MARKER in source_text:
            if not target.is_file():
                raise ValueError(f"Legacy package facade has no canonical target: {rel(source)}")
            continue
        if source.name != "package.mo":
            _, canonical = qexp_target_for_file(source)
            if legacy_alias_points_to(source_text, canonical):
                if not target.is_file():
                    raise ValueError(f"Legacy alias has no canonical target: {rel(source)}")
                continue

        text = rewrite_references(source_text)
        if source.name == "package.mo" and source_relative.parent == Path("."):
            target_parent = route.target_namespace.rsplit(".", 1)[0]
            text = re.sub(
                rf"(?m)^\s*within\s+{re.escape('QuadrotorExperiments')};\s*$",
                f"within {target_parent};",
                text,
                count=1,
            )
            text = update_root_package_declaration(text, route.legacy_name, target_root.name)
        copy_canonical_text(
            target,
            text,
            apply,
            operations,
            f"canonical-copy {rel(source)} -> {rel(target)}",
        )

    for source in sorted(source_root.rglob("package.order")):
        target = target_root / source.relative_to(source_root)
        copy_binary_if_compatible(source, target, apply)
        operations.append(f"order-copy {rel(source)} -> {rel(target)}")


def canonicalize_dynamics_definition(source: Path) -> tuple[Path, str]:
    kind, source_name = declared_class(source)
    canonical_name = DYNAMICS_CLASS_NAMES.get(source_name)
    if not canonical_name:
        raise ValueError(f"Missing dynamics mapping for {rel(source)}")
    text = rewrite_references(read_text(source))
    text = re.sub(
        r"(?m)^\s*within\s+QuadrotorExperiments\.DynamicsUpgrade;\s*$",
        "within MoSimQuadrotorModel.Dynamics;",
        text,
        count=1,
    )
    declaration = re.compile(
        rf"(?m)^(\s*{re.escape(kind)}\s+){re.escape(source_name)}\b"
    )
    text, count = declaration.subn(rf"\1{canonical_name}", text, count=1)
    if count != 1:
        raise ValueError(f"Cannot rename dynamics class declaration: {rel(source)}")
    text, count = re.subn(
        rf"(?m)^(\s*)end\s+{re.escape(source_name)};\s*$",
        rf"\1end {canonical_name};",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError(f"Cannot rename dynamics class terminator: {rel(source)}")
    return CANONICAL_ROOT / "Dynamics" / f"{canonical_name}.mo", text


def migrate_dynamics_complete(apply: bool, operations: list[str]) -> None:
    source_root = QEXP_ROOT / "DynamicsUpgrade"
    for source in sorted(source_root.glob("*.mo")):
        if source.name == "package.mo":
            continue
        target, canonical = qexp_target_for_file(source)
        source_text = read_text(source)
        if legacy_alias_points_to(source_text, canonical):
            if not target.is_file():
                raise ValueError(f"Legacy dynamics alias has no canonical target: {rel(source)}")
            continue
        target, text = canonicalize_dynamics_definition(source)
        copy_canonical_text(
            target,
            text,
            apply,
            operations,
            f"canonical-copy {rel(source)} -> {rel(target)}",
            replace_legacy_proxy=True,
        )


def migrate_controller_blocks_complete(apply: bool, operations: list[str]) -> None:
    target_root = CANONICAL_ROOT / "Controllers" / "Sysblocks"
    for source in sorted(CONTROLLER_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        target, canonical = controller_target_for_file(source)
        source_text = read_text(source)
        if legacy_alias_points_to(source_text, canonical):
            if not target.is_file():
                raise ValueError(f"Legacy controller alias has no canonical target: {rel(source)}")
            continue
        text = rewrite_references(source_text)
        if not declared_within(source):
            text = f"within MoSimQuadrotorModel.Controllers.Sysblocks;\n{text}"
        copy_canonical_text(
            target,
            text,
            apply,
            operations,
            f"canonical-copy {rel(source)} -> {rel(target)}",
        )

    source_package = CONTROLLER_ROOT / "package.mo"
    source_text = read_text(source_package)
    target = target_root / "package.mo"
    if COMPLETE_FACADE_MARKER not in source_text:
        text = rewrite_references(source_text)
        text = update_root_package_declaration(text, "QuadrotorControllerBlocks", "Sysblocks")
        text = f"within MoSimQuadrotorModel.Controllers;\n{text}"
        copy_canonical_text(
            target,
            text,
            apply,
            operations,
            f"canonical-copy {rel(source_package)} -> {rel(target)}",
        )
    elif not target.is_file():
        raise ValueError("Legacy controller facade has no canonical package")
    copy_binary_if_compatible(CONTROLLER_ROOT / "package.order", target_root / "package.order", apply)
    operations.append(f"order-copy {rel(CONTROLLER_ROOT / 'package.order')} -> {rel(target_root / 'package.order')}")


def migrate_live_package_complete(apply: bool, operations: list[str]) -> None:
    target_root = CANONICAL_ROOT / "LiveIntegration"
    for source in sorted(LIVE_ROOT.glob("*.mo")):
        if source.name == "package.mo":
            continue
        target, canonical = live_target_for_file(source)
        source_text = read_text(source)
        if legacy_alias_points_to(source_text, canonical):
            if not target.is_file():
                raise ValueError(f"Legacy live alias has no canonical target: {rel(source)}")
            continue
        text = rewrite_references(source_text)
        text = re.sub(
            r"(?m)^\s*within\s+MworksLive;\s*$",
            "within MoSimQuadrotorModel.LiveIntegration;",
            text,
            count=1,
        )
        copy_canonical_text(
            target,
            text,
            apply,
            operations,
            f"canonical-copy {rel(source)} -> {rel(target)}",
        )

    source_package = LIVE_ROOT / "package.mo"
    source_text = read_text(source_package)
    target = target_root / "package.mo"
    if COMPLETE_FACADE_MARKER not in source_text:
        text = rewrite_references(source_text)
        text = update_root_package_declaration(text, "MworksLive", "LiveIntegration")
        text = f"within MoSimQuadrotorModel;\n{text}"
        copy_canonical_text(
            target,
            text,
            apply,
            operations,
            f"canonical-copy {rel(source_package)} -> {rel(target)}",
        )
    elif not target.is_file():
        raise ValueError("Legacy live facade has no canonical package")
    copy_binary_if_compatible(LIVE_ROOT / "package.order", target_root / "package.order", apply)
    operations.append(f"order-copy {rel(LIVE_ROOT / 'package.order')} -> {rel(target_root / 'package.order')}")

    resource_root = LIVE_ROOT / "Resources"
    for source in sorted(resource_root.rglob("*")):
        if source.is_file():
            target = target_root / "Resources" / source.relative_to(resource_root)
            copy_binary_if_compatible(source, target, apply)
            operations.append(f"resource-copy {rel(source)} -> {rel(target)}")


def legacy_package_facade_text(text: str, package_name: str) -> str:
    text = rewrite_references(text)
    text = text.replace("__MWORKS(hide=false)", "__MWORKS(hide=true)")
    if COMPLETE_FACADE_MARKER not in text:
        declaration = re.compile(rf"(?m)^(\s*package\s+{re.escape(package_name)}\b[^\n]*\n)")
        text, count = declaration.subn(
            lambda match: match.group(1) + f"  // {COMPLETE_FACADE_MARKER}\n",
            text,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Cannot mark legacy package facade: {package_name}")
    outer_annotation = re.compile(
        rf"(?m)^\s*annotation\(__MWORKS\(hide=true\)\);\s*\n\s*end\s+{re.escape(package_name)};\s*$"
    )
    if not outer_annotation.search(text):
        terminator = re.compile(rf"(?m)^(\s*)end\s+{re.escape(package_name)};\s*$")
        text, count = terminator.subn(
            lambda match: f"  annotation(__MWORKS(hide=true));\n{match.group(1)}end {package_name};",
            text,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Cannot hide legacy package facade: {package_name}")
    return text


def root_qexp_facade_text(text: str) -> str:
    match = ROOT_SATURATE.search(text)
    if not match:
        raise ValueError("Cannot locate MoSimQuadrotorModel.saturate for facade rewrite")
    source_body = match.group(0)
    if not legacy_alias_points_to(source_body, "MoSimQuadrotorModel.saturate"):
        wrapper = (
            "  function saturate\n"
            '    "Deprecated compatibility alias; canonical implementation is MoSimQuadrotorModel.saturate"\n'
            "    extends MoSimQuadrotorModel.saturate;\n"
            "    annotation(__MWORKS(hide=true));\n"
            "  end saturate;\n"
        )
        text = text[: match.start()] + wrapper + text[match.end() :]
    return legacy_package_facade_text(text, "QuadrotorExperiments")


def rewrite_legacy_package_facades(apply: bool, operations: list[str]) -> None:
    root_package = QEXP_ROOT / "package.mo"
    write_legacy_facade_text(
        root_package,
        root_qexp_facade_text(read_text(root_package)),
        apply,
        operations,
        f"legacy-package-facade {rel(root_package)}",
    )
    for package_path in sorted(QEXP_ROOT.rglob("package.mo")):
        if package_path == root_package:
            continue
        package_name = re.search(r"(?m)^\s*package\s+([A-Za-z_][A-Za-z0-9_]*)\b", read_text(package_path))
        if not package_name:
            raise ValueError(f"Cannot find package declaration: {rel(package_path)}")
        write_legacy_facade_text(
            package_path,
            legacy_package_facade_text(read_text(package_path), package_name.group(1)),
            apply,
            operations,
            f"legacy-package-facade {rel(package_path)}",
        )
    for package_path, package_name in (
        (CONTROLLER_ROOT / "package.mo", "QuadrotorControllerBlocks"),
        (LIVE_ROOT / "package.mo", "MworksLive"),
    ):
        write_legacy_facade_text(
            package_path,
            legacy_package_facade_text(read_text(package_path), package_name),
            apply,
            operations,
            f"legacy-package-facade {rel(package_path)}",
        )


def validate_complete_static_state() -> list[str]:
    errors = validate_static_state()
    errors.extend(validate_active_config_references())
    root_text = read_text(CANONICAL_ROOT / "package.mo")
    if LEGACY_NAMESPACE_TOKEN.search(root_text):
        errors.append("Formal root package still imports a legacy model namespace")

    root_order = (CANONICAL_ROOT / "package.order").read_text(encoding="utf-8").splitlines()
    for required in ("LiveIntegration", "saturate"):
        if required not in root_order:
            errors.append(f"MoSimQuadrotorModel/package.order missing {required}")
    for relative, entries in CANONICAL_PARENT_ORDERS.items():
        order_path = CANONICAL_ROOT / relative / "package.order"
        if not order_path.is_file() or order_path.read_text(encoding="utf-8").splitlines() != list(entries):
            errors.append(f"Canonical package order is not normalized: {rel(order_path)}")

    for source in sorted((QEXP_ROOT / "DynamicsUpgrade").glob("*.mo")):
        if source.name == "package.mo":
            continue
        target, canonical = qexp_target_for_file(source)
        if not target.is_file():
            errors.append(f"Missing canonical dynamics implementation: {rel(target)}")
            continue
        if declared_within(target) != "MoSimQuadrotorModel.Dynamics":
            errors.append(f"Canonical dynamics namespace is wrong: {rel(target)}")
        if declared_class(target)[1] != canonical.rsplit(".", 1)[1]:
            errors.append(f"Canonical dynamics class name is wrong: {rel(target)}")
        if legacy_alias_points_to(read_text(target), canonical):
            errors.append(f"Canonical dynamics remains a legacy wrapper: {rel(target)}")

    saturate_path = CANONICAL_ROOT / "saturate.mo"
    if not saturate_path.is_file() or declared_within(saturate_path) != "MoSimQuadrotorModel":
        errors.append("Canonical root saturate utility is missing or in the wrong namespace")
    root_legacy = read_text(QEXP_ROOT / "package.mo")
    if not legacy_alias_points_to(root_legacy, "MoSimQuadrotorModel.saturate"):
        errors.append("MoSimQuadrotorModel.saturate is not a canonical compatibility alias")

    legacy_packages = list(QEXP_ROOT.rglob("package.mo")) + [
        CONTROLLER_ROOT / "package.mo",
        LIVE_ROOT / "package.mo",
    ]
    for package_path in legacy_packages:
        text = read_text(package_path)
        if COMPLETE_FACADE_MARKER not in text:
            errors.append(f"Legacy package is not marked as a compatibility facade: {rel(package_path)}")
        if re.search(r"(?m)^\s*(equation|algorithm)\b", text):
            errors.append(f"Legacy package retains direct implementation logic: {rel(package_path)}")

    for path in CANONICAL_ROOT.rglob("*.mo"):
        if LEGACY_NAMESPACE_TOKEN.search(read_text(path)):
            errors.append(f"Canonical source retains a legacy namespace token: {rel(path)}")
    for package_path in CANONICAL_ROOT.rglob("package.mo"):
        package_text = read_text(package_path)
        if normalize_outer_package_terminator(package_text) != package_text:
            errors.append(f"Canonical package terminator is inconsistent: {rel(package_path)}")
    return errors
def run(apply: bool) -> int:
    operations: list[str] = []
    prepare_canonical_surface(apply, operations)
    migrate_root_saturate(apply, operations)
    for route in CATEGORY_ROUTES:
        migrate_qexp_category_complete(route, apply, operations)
    migrate_dynamics_complete(apply, operations)
    migrate_controller_blocks_complete(apply, operations)
    migrate_live_package_complete(apply, operations)
    normalize_canonical_package_terminators(apply, operations)
    update_canonical_references(apply, operations)
    entries = rewrite_legacy_implementations(apply, operations)
    rewrite_legacy_package_facades(apply, operations)
    skipped = rewrite_active_references(apply, operations)
    write_manifest(entries, apply, operations)

    if not apply:
        print(json.dumps({"status": "dry_run_ok", "operations": operations, "operation_count": len(operations)}, ensure_ascii=False, indent=2))
        return 0

    errors = validate_complete_static_state()
    payload = {
        "status": "ok" if not errors else "failed_static_validation",
        "operation_count": len(operations),
        "dirty_reference_files_skipped": skipped,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the namespace migration")
    parser.add_argument("--check", action="store_true", help="validate an already-applied migration")
    args = parser.parse_args()
    if args.apply and args.check:
        parser.error("use either --apply or --check")
    if args.check:
        errors = validate_complete_static_state()
        print(json.dumps({"status": "ok" if not errors else "failed", "errors": errors}, ensure_ascii=False, indent=2))
        return 0 if not errors else 1
    return run(apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
