import importlib.util
from pathlib import Path

import pytest


PATCH_PATH = Path(__file__).resolve().parents[1] / "sunray/patch_racer_grid_id_width.py"
SPEC = importlib.util.spec_from_file_location("patch_racer_grid_id_width", PATCH_PATH)
assert SPEC is not None and SPEC.loader is not None
PATCH_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCH_MODULE)
MESSAGE_FIELDS = PATCH_MODULE.MESSAGE_FIELDS
apply = PATCH_MODULE.apply


def make_source_tree(root: Path) -> None:
    declarations = {
        "exploration_manager/msg/DroneState.msg": "int32 drone_id\nint8[] grid_ids\n",
        "exploration_manager/msg/PairOpt.msg": (
            "int32 from_drone_id\nint8[] ego_ids\nint8[] other_ids\n"
        ),
        "exploration_manager/msg/GridIds.msg": "int8[] ids\n",
    }
    for relative_path, text in declarations.items():
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_patch_widens_all_grid_id_arrays_and_is_idempotent(tmp_path: Path) -> None:
    make_source_tree(tmp_path)

    assert apply(tmp_path) is True
    assert apply(tmp_path) is False

    for relative_path, fields in MESSAGE_FIELDS.items():
        text = (tmp_path / relative_path).read_text(encoding="utf-8")
        for field in fields:
            assert f"int32[] {field}" in text
            assert f"int8[] {field}" not in text


def test_patch_rejects_unknown_message_schema(tmp_path: Path) -> None:
    make_source_tree(tmp_path)
    path = tmp_path / "exploration_manager/msg/GridIds.msg"
    path.write_text("uint8[] ids\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="expected field declaration"):
        apply(tmp_path)
