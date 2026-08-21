from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_strict_graphical_sysblock_registry.py"


def load_module():
    spec = importlib.util.spec_from_file_location("strict_graphical_sysblock_registry", BUILDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registry_covers_active_catalog_and_preserves_explicit_boundaries() -> None:
    registry_builder = load_module()
    registry = registry_builder.build_registry()
    schemes = {row["scheme_id"]: row for row in registry["schemes"]}

    assert registry["summary"]["active_entry_count"] == 48
    assert len(schemes) == 48
    assert schemes["official_pid"]["strict_graphical_status"] == "blocked_native_sysblock_modelica_embedding"
    assert schemes["official_pid"]["strict_targets"]["strict_core_class"].endswith(
        ".OfficialPidNativeSysblockCore"
    )
    assert schemes["awff_pid"]["strict_graphical_status"] == "blocked_mworks_compiler_internal_error"
    assert schemes["awff_l1_residual"]["strict_graphical_status"] == "strict_core_rebuild_required"
    assert schemes["awff_l1_indi"]["strict_graphical_status"] == "strict_core_rebuild_required"
    assert schemes["linear_mpc_l1_indi"]["strict_graphical_status"] == "strict_core_rebuild_required"
    assert schemes["qp_nmpc_l1_indi_cbf"]["strict_graphical_status"] == "strict_core_rebuild_required"
    assert schemes["px4ctrl"]["strict_graphical_status"] == "explicit_exception_pending_mworks_equivalent_core"
    assert schemes["awff_l1_residual"]["strict_targets"]["owner_directory"].endswith(
        "/Graphical/ProjectOwned"
    )
