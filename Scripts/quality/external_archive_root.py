"""Canonical destination validation shared by external MoSim archivers."""

from __future__ import annotations

from pathlib import Path


CANONICAL_EXTERNAL_ARCHIVE_ROOT = Path(r"E:\刘致远18001500226\MoSim_Archive")


def canonical_external_archive_root() -> Path:
    return CANONICAL_EXTERNAL_ARCHIVE_ROOT.expanduser().resolve(strict=False)


def validate_external_archive_destination(
    value: Path,
    *,
    repository_root: Path,
    must_exist: bool = False,
) -> Path:
    """Require one direct archive batch beneath the canonical external root."""

    destination = value.expanduser().resolve(strict=False)
    repository_root = repository_root.resolve()
    archive_root = canonical_external_archive_root()
    try:
        destination.relative_to(repository_root)
    except ValueError:
        pass
    else:
        raise ValueError("archive destination must be outside the repository")

    try:
        destination.relative_to(archive_root)
    except ValueError as exc:
        raise ValueError(f"archive destination must be under canonical root: {archive_root}") from exc
    if destination == archive_root or destination.parent != archive_root:
        raise ValueError(f"archive destination must be a direct batch under canonical root: {archive_root}")
    if must_exist:
        if not destination.is_dir():
            raise ValueError(f"existing archive destination does not exist: {destination}")
    elif destination.exists():
        raise ValueError(f"archive destination already exists: {destination}")
    return destination
