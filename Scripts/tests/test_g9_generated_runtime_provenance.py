#!/usr/bin/env python3
"""Unit checks for G9 generated-runtime provenance helpers."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_checker():
    path = ROOT / "Scripts/sunray/check_g9_generated_runtime_provenance.py"
    spec = importlib.util.spec_from_file_location("g9_runtime_provenance", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load provenance checker")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cache_value() -> None:
    checker = load_checker()
    text = "A:STRING=x\nMOSIM_PX4CTRL_GENERATED_BACKEND:STRING=g9_family\n"
    assert checker.cache_value(text, "MOSIM_PX4CTRL_GENERATED_BACKEND") == "g9_family"
    assert checker.cache_value(text, "MISSING") is None


def test_generated_bundle_is_path_and_content_stable(tmp_path: Path) -> None:
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


def test_normalized_path_accepts_windows_manifest_path() -> None:
    checker = load_checker()
    path = checker.normalized_path(r"C:\Users\HP\Desktop\MoSim\Results\g9")
    if os.name == "posix" and Path("/mnt/c").is_dir():
        assert str(path).startswith("/mnt/c/Users/HP/Desktop/MoSim/Results/g9")
    else:
        assert "C:/Users/HP/Desktop/MoSim/Results/g9" in str(path).replace("\\", "/")
