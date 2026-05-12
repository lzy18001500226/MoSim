#!/usr/bin/env python3
"""Regression checks for evidence bundle audit rules."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_audit_module():
    path = ROOT / "scripts" / "audit_evidence_bundle.py"
    spec = importlib.util.spec_from_file_location("audit_evidence_bundle", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load audit_evidence_bundle.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sysblock_scenarios_declare_graphical_counterparts() -> None:
    module = load_audit_module()
    scenarios = sorted((ROOT / "scenarios").glob("**/*sysblock*.yaml"))
    missing: list[str] = []
    for scenario in scenarios:
        if "/smoke/" in scenario.as_posix():
            continue
        config = module.read_yaml(scenario)
        controller = config.get("controller", {})
        if not isinstance(controller, dict) or not controller.get("sysblock_controller_file"):
            continue
        if not controller.get("graphical_sysblock_model") or not controller.get("graphical_sysblock_file"):
            missing.append(scenario.relative_to(ROOT).as_posix())
            continue
        graph_file = module.repo_path(controller["graphical_sysblock_file"])
        if not module.graphical_model_declared(graph_file, str(controller["graphical_sysblock_model"])):
            missing.append(scenario.relative_to(ROOT).as_posix())
    if missing:
        raise AssertionError("Missing graphical Sysblock counterparts: " + ", ".join(missing))


def test_active_sysblock_evidence_audit_has_no_blocking_issues() -> None:
    module = load_audit_module()
    scenarios = sorted((ROOT / "scenarios").glob("**/*sysblock*.yaml"))
    failures: list[str] = []
    for scenario in scenarios:
        if "/smoke/" in scenario.as_posix():
            continue
        config = module.read_yaml(scenario)
        if config.get("active", True) is False:
            continue
        result = module.audit_one(scenario)
        if result["issues"]:
            failures.append(f"{scenario.relative_to(ROOT).as_posix()}: {'; '.join(result['issues'])}")
    if failures:
        raise AssertionError("Evidence audit failures: " + " | ".join(failures))

