from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "control_platform" / "build_cascade_pid_formal_adapter.py"


def load_module():
    spec = importlib.util.spec_from_file_location("cascade_pid_formal_adapter", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_native_serialization_equivalence_accepts_only_line_end_and_trailing_whitespace() -> None:
    module = load_module()
    expected = "model Example\n  Real input; \nend Example;\n"
    native = "model Example\r\n  Real input;\r\nend Example;\r\n"

    assert module.native_serialization_equivalence(expected, native) == "mworks_line_end_and_trailing_whitespace_only"
    assert module.native_serialization_equivalence(expected, expected) == "exact_bytes"
    assert module.native_serialization_equivalence(expected, "model Example\n  Integer input;\nend Example;\n") is None


def test_current_adapter_is_equivalent_to_the_historical_import() -> None:
    module = load_module()

    assert module.native_serialization_equivalence(
        module.materialized_text(),
        module.OUTPUT.read_text(encoding="utf-8"),
    ) == "mworks_line_end_and_trailing_whitespace_only"


def test_current_cascade_binding_matches_its_live_source_hashes() -> None:
    module = load_module()

    assert module.binding_hash_mismatches(module.current_binding()) == []


def test_cascade_binding_covers_the_shared_physical_closure() -> None:
    module = load_module()
    binding = module.current_binding()

    roles = {source["role"] for source in binding["source_bindings"]}
    assert {role for role, _ in module.SHARED_CLOSURE_SOURCES}.issubset(roles)
    assert binding["formal_adapter"]["implementation"] == {"kind": "direct_model_reference"}
