from __future__ import annotations

import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_checker():
    path = ROOT / "Scripts/sunray/check_pid_attitude_thrust_generated_runtime_provenance.py"
    spec = importlib.util.spec_from_file_location("pid_runtime_provenance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load provenance checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_contract_constants_and_profiles() -> None:
    checker = load_checker()
    assert checker.BACKEND == "pid_attitude_thrust"
    assert checker.BACKEND_DEFINITION == "MOSIM_PX4CTRL_GENERATED_BACKEND_PID_ATTITUDE_THRUST"
    assert checker.CONTROLLERS == {
        "cascade_pid": 1,
        "gain_scheduled_pid": 2,
        "fuzzy_pid": 3,
        "neural_pid": 4,
        "anti_windup": 5,
        "feedforward_profile": 6,
    }
    source = (ROOT / "Scripts/sunray/check_pid_attitude_thrust_generated_runtime_provenance.py").read_text(encoding="utf-8")
    assert '"build_only"' in source
    assert '"runtime_acknowledged"' in source


def test_generated_bundle_is_content_stable(tmp_path: Path) -> None:
    checker = load_checker()
    code_dir = tmp_path / checker.MODEL
    for relative in checker.REQUIRED_GENERATED_FILES:
        path = code_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(relative + "\n", encoding="utf-8")
    first, hashes, missing = checker.generated_bundle(code_dir)
    second, _, _ = checker.generated_bundle(code_dir)
    assert first == second
    assert len(hashes) == len(checker.REQUIRED_GENERATED_FILES)
    assert missing == []
    (code_dir / checker.REQUIRED_GENERATED_FILES[0]).write_text("changed\n", encoding="utf-8")
    changed, _, _ = checker.generated_bundle(code_dir)
    assert changed != first


def test_cache_and_windows_path_helpers() -> None:
    checker = load_checker()
    text = "MOSIM_PX4CTRL_GENERATED_BACKEND:STRING=pid_attitude_thrust\n"
    assert checker.cache_value(text, "MOSIM_PX4CTRL_GENERATED_BACKEND") == "pid_attitude_thrust"
    path = checker.normalized_path(r"C:\Users\HP\Desktop\MoSim\Results\control_platform")
    if os.name == "posix" and Path("/mnt/c").is_dir():
        assert str(path).startswith("/mnt/c/Users/HP/Desktop/MoSim/Results/control_platform")
    else:
        assert "C:/Users/HP/Desktop/MoSim/Results/control_platform" in str(path).replace("\\", "/")


def test_first_existing_supports_nested_catkin_package_layout(tmp_path: Path) -> None:
    checker = load_checker()
    flat = tmp_path / "build/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make"
    nested = tmp_path / "build/realflight_modules/px4ctrl/CMakeFiles/px4ctrl_node.dir/flags.make"
    nested.parent.mkdir(parents=True)
    nested.write_text("flags\n", encoding="utf-8")
    assert checker.first_existing((flat, nested)) == nested
