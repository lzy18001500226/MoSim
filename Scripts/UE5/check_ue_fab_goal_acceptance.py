#!/usr/bin/env python3
"""Audit current evidence for the MoSim UE/Fab tool-capability goal.

The goal is intentionally larger than one script can complete.  This checker
turns the goal into explicit evidence gates so current status is recoverable
from the worktree instead of chat memory.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENE_SOURCE_REGISTRY = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json"
DERELICT_TRUTH = (
    ROOT
    / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/"
    / "derelictcorridormegascans_collision_truth.json"
)
UNREAL_SKILL = ROOT / "Docs/Skills/Unreal/mosim-unreal/SKILL.md"
FAB_SKILL = ROOT / "Docs/Skills/Unreal/mosim-epic/SKILL.md"
UNREAL_WORKFLOW = ROOT / "Docs/Workflows/unreal_renderer.md"
EPIC_MCP = ROOT / "Docs/Skills/Unreal/mosim-epic/mcp/server.py"
EPIC_MCP_WRAPPER = ROOT / "Docs/Skills/Unreal/mosim-epic/wrappers/mosim-epic.sh"
UNREAL_WRAPPER = ROOT / "Docs/Skills/Unreal/mosim-unreal/wrappers/mosim-unreal.sh"
EDITOR_PROBE_DIR = ROOT / "Results/tmp"
RENDERER_MAP_LOAD_PROBE = ROOT / "Results/tmp/renderer_map_load_probe_latest.json"


@dataclass
class Gate:
    gate_id: str
    requirement: str
    status: str
    evidence: list[str]
    missing: list[str]

    @property
    def passed(self) -> bool:
        return self.status == "passed"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{rel(path)} must be a JSON object")
    return payload


def run_command(command: list[str], timeout: float = 60.0) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output


def source_by_id(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    sources = registry.get("local_editable_fallback", {}).get("scene_sources", [])
    if not isinstance(sources, list):
        return {}
    for source in sources:
        if isinstance(source, dict) and source.get("scene_source_id") == source_id:
            return source
    return {}


def gate_fab_inventory() -> Gate:
    ok, output = run_command([sys.executable, "Scripts/UE5/check_epic_library_inventory.py", "--json"], timeout=90)
    evidence: list[str] = []
    missing: list[str] = []
    if ok:
        payload = json.loads(output)
        summary = payload.get("baseline_summary", {})
        checks = payload.get("checks", {})
        evidence.append("Scripts/UE5/check_epic_library_inventory.py --json passed")
        evidence.append(f"summary={summary}")
        if not all(checks.values()):
            missing.append(f"inventory checks not all true: {checks}")
    else:
        missing.append("Epic/Fab inventory health check failed")
        missing.append(output[:1200])
    return Gate(
        "fab_inventory_visible",
        "mosim-epic can read sanitized Epic/Fab/Launcher inventory",
        "passed" if ok and not missing else "missing",
        evidence,
        missing,
    )


def gate_fab_acceptance(registry: dict[str, Any]) -> Gate:
    fab = registry.get("fab_route", {})
    status = fab.get("status") if isinstance(fab, dict) else None
    candidates = fab.get("candidate_entries", []) if isinstance(fab, dict) else []
    evidence = [
        f"{rel(SCENE_SOURCE_REGISTRY)} fab_route.status={status}",
        f"candidate_entries={len(candidates) if isinstance(candidates, list) else 'invalid'}",
    ]
    missing: list[str] = []
    if status != "accepted":
        missing.append(
            "No Fab asset is proven imported/reused inside the MoSim UE sim project with edit access and planning truth"
        )
    return Gate(
        "fab_route_acceptance",
        "Fab route must prove full import/reuse, UE editability, and planning-truth availability",
        "passed" if not missing else "partial",
        evidence,
        missing,
    )


def gate_local_fallback(registry: dict[str, Any]) -> Gate:
    policy = registry.get("policy", {})
    primary = str(policy.get("primary_scene_source_id", "")) if isinstance(policy, dict) else ""
    source = source_by_id(registry, primary)
    evidence = [f"primary_scene_source_id={primary}"]
    missing: list[str] = []
    if not source:
        missing.append("Primary local scene source is not present in scene_sources")
    else:
        evidence.append(f"source_status={source.get('status')}")
        for key in ["editable_candidate", "renderable_candidate", "planning_truth_ready"]:
            evidence.append(f"{key}={source.get(key)}")
            if source.get(key) is not True:
                missing.append(f"Primary local source missing true gate: {key}")
        truth_artifacts = source.get("truth_artifacts", [])
        evidence.append(f"truth_artifacts={truth_artifacts}")
        if not isinstance(truth_artifacts, list) or not truth_artifacts:
            missing.append("Primary local source has no truth artifacts")
    return Gate(
        "local_fallback_ready",
        "Fallback local editable scene source is available, renderable, and truth-backed",
        "passed" if not missing else "missing",
        evidence,
        missing,
    )


def gate_scene_truth() -> Gate:
    evidence: list[str] = []
    missing: list[str] = []
    if not DERELICT_TRUTH.exists():
        missing.append(f"Missing truth artifact: {rel(DERELICT_TRUTH)}")
    else:
        ok, output = run_command(
            [sys.executable, "Scripts/UE5/export_unreal_scene_truth.py", "validate", rel(DERELICT_TRUTH)],
            timeout=90,
        )
        if ok:
            payload = load_json(DERELICT_TRUTH)
            evidence.append(f"{rel(DERELICT_TRUTH)} validates")
            evidence.append(f"asset_count={len(payload.get('assets', []))}")
            evidence.append(f"collision_proxy_count={len(payload.get('collision_proxies', []))}")
        else:
            missing.append("Truth artifact validation failed")
            missing.append(output[:1200])
    return Gate(
        "scene_truth_valid",
        "Selected local fallback scene provides explicit collision/planning truth",
        "passed" if not missing else "missing",
        evidence,
        missing,
    )


def gate_udp_contract() -> Gate:
    ok, output = run_command([sys.executable, "Scripts/UE5/check_scene_source_udp_contract.py"], timeout=90)
    return Gate(
        "scene_source_udp_contract",
        "MWORKS UDP packets can select the primary scene-source id for UE bridge resolution",
        "passed" if ok else "missing",
        [output] if ok else [],
        [] if ok else ["Scene-source UDP contract check failed", output[:1200]],
    )


def latest_editor_probe() -> Path | None:
    if not EDITOR_PROBE_DIR.exists():
        return None
    probes = sorted(
        list(EDITOR_PROBE_DIR.glob("linked_scene_source_mcp_probe*.json"))
        + list(EDITOR_PROBE_DIR.glob("unreal_mcp_editor_probe*.json")),
        key=lambda path: path.stat().st_mtime,
    )
    return probes[-1] if probes else None


def gate_unreal_mcp_edit() -> Gate:
    probe = latest_editor_probe()
    evidence: list[str] = []
    missing: list[str] = []
    if probe is None:
        missing.append("No reversible Unreal editor MCP probe JSON found under Results/tmp")
    else:
        try:
            payload = load_json(probe)
        except Exception as exc:
            missing.append(f"Latest editor probe unreadable: {rel(probe)}: {exc}")
        else:
            evidence.append(f"latest_probe={rel(probe)}")
            evidence.append(f"ok={payload.get('ok')}")
            if payload.get("scene_source_id"):
                evidence.append(f"scene_source_id={payload.get('scene_source_id')}")
            steps = payload.get("steps", [])
            if isinstance(steps, list):
                evidence.append("steps=" + ",".join(str(step.get("step")) for step in steps if isinstance(step, dict)))
            if payload.get("ok") is not True:
                missing.append("Latest reversible editor MCP probe did not report ok=true")
            required = ["spawn probe actor", "modify probe transform", "delete probe actor"]
            step_names = {str(step.get("step")) for step in steps if isinstance(step, dict)}
            for step in required:
                if step not in step_names:
                    missing.append(f"Editor probe missing step: {step}")
            if probe.name.startswith("linked_scene_source_mcp_probe"):
                scene_source = payload.get("scene_source", {})
                if not isinstance(scene_source, dict) or not scene_source.get("renderer_map_asset"):
                    missing.append("Linked scene-source MCP probe missing renderer_map_asset evidence")
    return Gate(
        "mosim_unreal_edit_authority",
        "mosim-unreal MCP can modify a running UE project through reversible actor edit/delete, preferably with linked scene-source context",
        "passed" if not missing else "missing",
        evidence,
        missing,
    )


def gate_skills_and_workflow() -> Gate:
    required_files = [UNREAL_SKILL, FAB_SKILL, UNREAL_WORKFLOW, EPIC_MCP, EPIC_MCP_WRAPPER, UNREAL_WRAPPER]
    evidence: list[str] = []
    missing: list[str] = []
    for path in required_files:
        if path.exists():
            evidence.append(rel(path))
        else:
            missing.append(f"Missing required workflow/tool file: {rel(path)}")
    if FAB_SKILL.exists():
        text = FAB_SKILL.read_text(encoding="utf-8")
        for token in ["mosim-epic", "editable Unreal content", "planning truth"]:
            if token not in text:
                missing.append(f"Fab skill missing token: {token}")
    if UNREAL_SKILL.exists():
        text = UNREAL_SKILL.read_text(encoding="utf-8")
        for token in ["mosim-unreal", "reversible_actor_probe", "scene_source_status"]:
            if token not in text:
                missing.append(f"Unreal MCP skill missing token: {token}")
    return Gate(
        "skills_workflow_defined",
        "Minimal project-local Skills and workflow docs exist for UE MCP and Epic/Fab inventory MCP",
        "passed" if not missing else "missing",
        evidence,
        missing,
    )


def gate_visual_import(registry: dict[str, Any]) -> Gate:
    policy = registry.get("policy", {})
    primary = str(policy.get("primary_scene_source_id", "")) if isinstance(policy, dict) else ""
    source = source_by_id(registry, primary)
    evidence: list[str] = [f"primary_scene_source_id={primary}"]
    missing: list[str] = []
    imported = source.get("imported_into_renderer") if isinstance(source, dict) else None
    renderer_content_root = source.get("renderer_content_root") if isinstance(source, dict) else None
    renderer_map_asset = source.get("renderer_map_asset") if isinstance(source, dict) else None
    renderer_map_package = source.get("renderer_map_package") if isinstance(source, dict) else None
    renderer_reuse_kind = source.get("renderer_reuse_kind") if isinstance(source, dict) else None
    if imported is True:
        evidence.append("imported_into_renderer=true")
    else:
        missing.append("Primary source is not yet proven imported/reused inside MoSimSceneLibrary")
    if renderer_reuse_kind:
        evidence.append(f"renderer_reuse_kind={renderer_reuse_kind}")
    if renderer_content_root:
        evidence.append(f"renderer_content_root={renderer_content_root}")
        if not (ROOT / str(renderer_content_root)).exists():
            missing.append(f"Renderer content root does not exist: {renderer_content_root}")
    else:
        missing.append("No renderer_content_root recorded for the primary scene source")
    if renderer_map_asset:
        evidence.append(f"renderer_map_asset={renderer_map_asset}")
        if not (ROOT / str(renderer_map_asset)).exists():
            missing.append(f"Renderer map asset does not exist: {renderer_map_asset}")
    else:
        missing.append("No renderer_map_asset recorded for the primary scene source")
    if renderer_map_package:
        evidence.append(f"renderer_map_package={renderer_map_package}")
    else:
        missing.append("No renderer_map_package recorded for the primary scene source")
    if RENDERER_MAP_LOAD_PROBE.exists():
        try:
            probe = load_json(RENDERER_MAP_LOAD_PROBE)
        except Exception as exc:
            missing.append(f"Renderer map-load probe is unreadable: {rel(RENDERER_MAP_LOAD_PROBE)}: {exc}")
        else:
            evidence.append(f"renderer_map_load_probe={rel(RENDERER_MAP_LOAD_PROBE)}")
            evidence.append(f"map_load_ok={probe.get('ok')}")
            evidence.append(f"loaded_level={probe.get('level_name')}")
            evidence.append(f"actor_count={probe.get('actor_count')}")
            if probe.get("ok") is not True:
                missing.append("Renderer map-load probe did not report ok=true")
            if probe.get("scene_source_id") != primary:
                missing.append(
                    f"Renderer map-load probe scene_source_id mismatch: {probe.get('scene_source_id')} != {primary}"
                )
            if renderer_map_asset and probe.get("renderer_map_asset") != renderer_map_asset:
                missing.append(
                    f"Renderer map-load probe asset mismatch: {probe.get('renderer_map_asset')} != {renderer_map_asset}"
                )
            if renderer_map_package and probe.get("renderer_map_package") != renderer_map_package:
                missing.append(
                    "Renderer map-load probe package mismatch: "
                    f"{probe.get('renderer_map_package')} != {renderer_map_package}"
                )
            if int(probe.get("actor_count") or 0) <= 0:
                missing.append("Renderer map-load probe loaded no actors")
    else:
        missing.append(f"Missing renderer map-load proof: {rel(RENDERER_MAP_LOAD_PROBE)}")
    return Gate(
        "scene_visual_import_or_reuse",
        "Selected Fab/local scene is actually imported or reused by the MoSim UE sim project and loadable by the renderer",
        "passed" if not missing else "missing",
        evidence,
        missing,
    )


def build_report() -> dict[str, Any]:
    registry = load_json(SCENE_SOURCE_REGISTRY)
    gates = [
        gate_fab_inventory(),
        gate_fab_acceptance(registry),
        gate_local_fallback(registry),
        gate_scene_truth(),
        gate_udp_contract(),
        gate_unreal_mcp_edit(),
        gate_skills_and_workflow(),
        gate_visual_import(registry),
    ]
    passed = [gate for gate in gates if gate.passed]
    missing_actions = []
    by_id = {gate.gate_id: gate for gate in gates}
    fallback_route_ok = all(
        by_id[gate_id].passed
        for gate_id in [
            "fab_inventory_visible",
            "local_fallback_ready",
            "scene_truth_valid",
            "scene_source_udp_contract",
            "mosim_unreal_edit_authority",
            "skills_workflow_defined",
            "scene_visual_import_or_reuse",
        ]
    )
    fab_route_ok = by_id["fab_route_acceptance"].passed and fallback_route_ok
    goal_ok = fab_route_ok or fallback_route_ok
    if not by_id["fab_route_acceptance"].passed and fallback_route_ok:
        missing_actions.append(
            "Fab remains inventory-visible only, but fallback route is active and satisfies the current objective branch"
        )
    elif not by_id["fab_route_acceptance"].passed:
        missing_actions.append(
            "Fab remains inventory-visible only; keep the local editable fallback active unless a Fab asset is created/imported with truth"
        )
    if not by_id["scene_visual_import_or_reuse"].passed:
        missing_actions.append(
            "Prove scene_visual_import_or_reuse by linking/importing Derelict or an accepted Fab scene into MoSimSceneLibrary, then run probe_renderer_map_load.py"
        )
    if by_id["scene_visual_import_or_reuse"].passed and by_id["mosim_unreal_edit_authority"].passed:
        missing_actions.append(
            "Next strengthening gate: run a live UE MCP reversible modification while the linked Derelict map is loaded in the MoSim renderer"
        )

    return {
        "schema": "mosim.ue_fab_goal_acceptance.v1",
        "ok": goal_ok,
        "route": "fab" if fab_route_ok else "local_editable_fallback" if fallback_route_ok else "incomplete",
        "passed_count": len(passed),
        "gate_count": len(gates),
        "gates": [gate.__dict__ for gate in gates],
        "next_required_actions": missing_actions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON only.")
    parser.add_argument("--require-complete", action="store_true", help="Exit nonzero unless every gate passes.")
    return parser.parse_args()


def print_text(report: dict[str, Any]) -> None:
    print(f"ok: {report['ok']} ({report['passed_count']}/{report['gate_count']} gates passed)")
    for gate in report["gates"]:
        print(f"- {gate['gate_id']}: {gate['status']}")
        for item in gate["evidence"][:4]:
            print(f"  evidence: {item}")
        for item in gate["missing"][:4]:
            print(f"  missing: {item}")
    if not report["ok"]:
        print("next_required_actions:")
        for action in report["next_required_actions"]:
            print(f"- {action}")


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report)
    return 1 if args.require_complete and not report["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
