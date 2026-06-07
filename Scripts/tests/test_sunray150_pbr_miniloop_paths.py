from pathlib import Path

import pytest

from Scripts.UE5.check_sunray150_pbr_miniloop import PROJECT_ROOT, assert_project_path


def test_assert_project_path_accepts_project_relative_path() -> None:
    path = assert_project_path("UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/example.png")

    assert path == PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Textures" / "example.png"


def test_assert_project_path_accepts_wsl_mount_for_project_root() -> None:
    project_root_posix = PROJECT_ROOT.as_posix()
    drive = project_root_posix[0].lower()
    tail = project_root_posix[3:]
    wsl_path = f"/mnt/{drive}/{tail}/UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures/example.png"

    path = assert_project_path(wsl_path)

    assert path == PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Textures" / "example.png"


def test_assert_project_path_rejects_wsl_mount_outside_project() -> None:
    project_root_posix = PROJECT_ROOT.as_posix()
    drive = project_root_posix[0].lower()
    outside = f"/mnt/{drive}/Users/HP/Desktop/OtherProject/example.png"

    with pytest.raises(AssertionError, match="path outside project"):
        assert_project_path(outside)


def test_assert_project_path_rejects_absolute_outside_project() -> None:
    outside = Path(PROJECT_ROOT.anchor) / "Users" / "HP" / "Desktop" / "OtherProject" / "example.png"

    with pytest.raises(AssertionError, match="path outside project"):
        assert_project_path(str(outside))
