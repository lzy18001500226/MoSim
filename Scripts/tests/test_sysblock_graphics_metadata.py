from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "Scripts" / "mworks" / "check_sysblock_graphics.py"
SYSBLOCKS = ROOT / "Models" / "MoSimQuadrotorModel" / "Control" / "Implementations" / "Sysblocks"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_sysblock_graphics", CHECKER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_sysblock_metadata_is_counted_by_class_and_has_no_missing_native_markers() -> None:
    audit = load_checker().sysblock_metadata_audit(SYSBLOCKS)

    assert audit["pass"] is True
    assert audit["missing_model_workspace"] == []
    assert audit["missing_base_workspace_import"] == []
    assert audit["duplicate_model_workspace_extends"] == []
    assert audit["duplicate_base_workspace_import"] == []
    assert audit["derived_sysblock_missing_own_metadata"] == []
    assert audit["awff_innovation_graphical_controllers_class_count"] == 18
    assert audit["sysblock_class_count"] >= 46
    assert audit["package_navigation_aliases_excluded"]


def test_duplicate_model_workspace_extends_fails_own_text_audit(tmp_path: Path) -> None:
    checker = load_checker()
    filename = "MoSim_PID_AWFF_LINEAR_ESO_GRAPHICAL_MIL.mo"
    source = (SYSBLOCKS / filename).read_text(encoding="utf-8")
    target = tmp_path / filename
    duplicate = source.replace(
        "  extends ModelWorkspace;\n",
        "  extends ModelWorkspace;\n  extends ModelWorkspace;\n",
        1,
    )
    assert duplicate != source
    target.write_text(duplicate, encoding="utf-8")

    duplicate_audit = checker.sysblock_metadata_audit(tmp_path)

    assert duplicate_audit["duplicate_model_workspace_extends"]
    assert duplicate_audit["pass"] is False

    target.write_text(source, encoding="utf-8")
    restored_audit = checker.sysblock_metadata_audit(tmp_path)

    assert restored_audit["duplicate_model_workspace_extends"] == []
    assert restored_audit["duplicate_base_workspace_import"] == []
    assert restored_audit["pass"] is True
