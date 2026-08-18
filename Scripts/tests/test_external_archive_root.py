"""Regression checks for canonical external archive destinations."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
QUALITY_ROOT = ROOT / "Scripts" / "quality"
if str(QUALITY_ROOT) not in sys.path:
    sys.path.insert(0, str(QUALITY_ROOT))

import external_archive_root


def _load_script(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, QUALITY_ROOT / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_active_archivers_require_one_direct_canonical_batch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repository = tmp_path / "repository"
    archive_root = tmp_path / "MoSim_Archive"
    repository.mkdir()
    archive_root.mkdir()
    monkeypatch.setattr(external_archive_root, "CANONICAL_EXTERNAL_ARCHIVE_ROOT", archive_root)

    materializer = _load_script("materialize_config_results_archive_test", "materialize_config_results_archive.py")
    result_archiver = _load_script("archive_unreferenced_results_test", "archive_unreferenced_results.py")
    valid = archive_root / "20260811_test_batch"

    assert materializer.external_destination(valid) == valid.resolve(strict=False)
    assert result_archiver.resolve_destination(valid) == valid.resolve(strict=False)

    for invalid in (archive_root, archive_root / "nested" / "batch", tmp_path / "legacy_c_root" / "batch"):
        with pytest.raises(ValueError, match="canonical root"):
            materializer.external_destination(invalid)
        with pytest.raises(ValueError, match="canonical root"):
            result_archiver.resolve_destination(invalid)


def test_materializer_requires_exact_lx_symlink_metadata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    materializer = _load_script("materialize_config_results_archive_reparse_test", "materialize_config_results_archive.py")
    source = ROOT / "Results" / "_quarantine" / "synthetic_lx_symlink"
    raw_payload = (2).to_bytes(4, "little") + b"/opt/ros/noetic/share/catkin/cmake/toplevel.cmake"
    raw_buffer = materializer.LX_SYMLINK_REPARSE_TAG.to_bytes(4, "little") + len(raw_payload).to_bytes(2, "little") + b"\0\0" + raw_payload
    monkeypatch.setattr(materializer, "read_reparse_buffer", lambda _: raw_buffer)

    expected = {
        "source_relpath": source.relative_to(ROOT).as_posix(),
        "reparse_tag": "0xa000001d",
        "reparse_data_sha256": "02a2c1a3c6eb8a22177b0a904cd69435703253e210886f84f469029686e1275d",
        "target": "/opt/ros/noetic/share/catkin/cmake/toplevel.cmake",
    }

    class Status:
        st_reparse_tag = materializer.LX_SYMLINK_REPARSE_TAG

    record = materializer.lx_symlink_metadata(source, Status(), expected)
    assert record["lx_symlink_version"] == 2
    assert record["target"] == expected["target"]

    expected["target"] = "/different-target"
    with pytest.raises(ValueError, match="approved declaration"):
        materializer.lx_symlink_metadata(source, Status(), expected)
