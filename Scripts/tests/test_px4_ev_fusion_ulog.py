import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "sunray" / "analyze_px4_ev_fusion_ulog.py"


def load_module():
    spec = importlib.util.spec_from_file_location("px4_ev_fusion_ulog", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_selected_ev_requirements_follow_the_requested_bitmask() -> None:
    module = load_module()

    assert module.selected_ev_requirements(15) == (
        ("estimator_aid_src_ev_pos", "cs_ev_pos"),
        ("estimator_aid_src_ev_hgt", "cs_ev_hgt"),
        ("estimator_aid_src_ev_vel", "cs_ev_vel"),
    )
    assert module.selected_ev_requirements(11) == (
        ("estimator_aid_src_ev_pos", "cs_ev_pos"),
        ("estimator_aid_src_ev_hgt", "cs_ev_hgt"),
    )
