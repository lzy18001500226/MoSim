from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_helper():
    path = ROOT / "Scripts/sunray/prepare_px4_ram_dataman_rcs.py"
    spec = importlib.util.spec_from_file_location("prepare_px4_ram_dataman_rcs", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load PX4 rcS helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_transform_inserts_ram_backend_immediately_before_dataman() -> None:
    helper = load_helper()
    source = "#!/bin/sh\nparam select parameters.bson\ndataman start\ncommander start\n"
    output = helper.transform(source)
    assert output.count("dataman start -r") == 1
    assert "param set SYS_DM_BACKEND 1\ndataman start -r\ncommander start" in output


def test_transform_rejects_missing_or_duplicate_dataman_start() -> None:
    helper = load_helper()
    for source in ("#!/bin/sh\n", "dataman start\ndataman start\n"):
        try:
            helper.transform(source)
        except ValueError:
            continue
        raise AssertionError("invalid rcS source was accepted")
