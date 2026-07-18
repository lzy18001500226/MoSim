from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_builder():
    path = ROOT / "Scripts/quality/build_non_frontend_report_figures.py"
    spec = importlib.util.spec_from_file_location("non_frontend_report_figures", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load report figure builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_report_figures_preserve_not_run_and_learning_boundaries(tmp_path: Path) -> None:
    builder = load_builder()
    manifest = builder.build(tmp_path)
    assert len(manifest["figures"]) == 3
    by_id = {item["figure_id"]: item for item in manifest["figures"]}
    ab = by_id["final_pid_ab_primary_rmse"]
    assert ab["values"]["official_pid"][-1] is None
    assert ab["values"]["gain_scheduled_pid"][-1] is None
    learning = by_id["learning_control_rmse_change"]
    assert "selectable=false" in learning["claim_ceiling"]
    for figure in manifest["figures"]:
        assert len(figure["files"]) == 2
