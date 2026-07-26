from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


def load_module(relative_path: str, name: str):
    source = ROOT / relative_path
    source_parent = str(source.parent)
    if source_parent not in sys.path:
        sys.path.insert(0, source_parent)
    spec = importlib.util.spec_from_file_location(name, source)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_matrix_builder_accepts_a_new_project_results_root() -> None:
    module = load_module(
        "Scripts/quality/build_g6_controller_execution_matrix.py", "g6_matrix_builder_current_root"
    )
    output_root = Path("Results/model_library_refactor/controller_route_execution_current")

    module.configure_output_root(output_root)

    assert module.OUTPUT_ROOT == (ROOT / output_root).resolve()
    assert module.OUTPUT_PATH == module.OUTPUT_ROOT / "G6_EXECUTION_MATRIX.json"
    assert module.STATUS_PATH == module.OUTPUT_ROOT / "G6_EXECUTION_STATUS.json"


def test_executor_and_auditor_bind_the_same_new_matrix_root() -> None:
    executor = load_module("Scripts/mworks/run_g6_controller_execution.py", "g6_executor_current_root")
    auditor = load_module(
        "Scripts/quality/check_g6_controller_execution_evidence.py", "g6_auditor_current_root"
    )
    output_root = Path("Results/model_library_refactor/controller_route_execution_current")
    matrix = output_root / "G6_EXECUTION_MATRIX.json"

    executor.configure_matrix_path(matrix)
    auditor.configure_output_root(output_root)

    expected_matrix = (ROOT / matrix).resolve()
    assert executor.MATRIX_PATH == expected_matrix
    assert executor.STATUS_PATH == expected_matrix.parent / "G6_EXECUTION_STATUS.json"
    assert auditor.MATRIX_PATH == expected_matrix


def test_current_matrix_paths_reject_writes_outside_results() -> None:
    builder = load_module(
        "Scripts/quality/build_g6_controller_execution_matrix.py", "g6_matrix_builder_outside_results"
    )
    executor = load_module("Scripts/mworks/run_g6_controller_execution.py", "g6_executor_outside_results")

    with pytest.raises(ValueError, match="below Results"):
        builder.configure_output_root(ROOT / "Docs")
    with pytest.raises(ValueError, match="below Results"):
        executor.configure_matrix_path(ROOT / "Docs" / "G6_EXECUTION_MATRIX.json")


def test_formal_harness_map_binds_an_explicit_current_status_path() -> None:
    module = load_module(
        "Scripts/quality/build_formal_closed_loop_harness_map.py", "formal_harness_map_current_status"
    )

    with pytest.raises(module.HarnessMapError, match="below Results"):
        module.configure_g6_status_path(ROOT / "Docs" / "G6_EXECUTION_STATUS.json")
