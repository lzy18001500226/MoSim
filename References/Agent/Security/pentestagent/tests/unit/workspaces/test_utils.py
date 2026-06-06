"""Tests for pentestagent.workspaces.utils (get_conversations_base, get_loot_base)."""

from pathlib import Path

import pytest

from pentestagent.workspaces.manager import WorkspaceManager
import pentestagent.workspaces.utils as ws_utils


@pytest.fixture(autouse=True)
def reset_warn_flags():
    """Reset module-level warning-once flags so tests are independent."""
    ws_utils._WARNED = False
    ws_utils._WARNED_CONV = False
    yield
    ws_utils._WARNED = False
    ws_utils._WARNED_CONV = False


# ---------------------------------------------------------------------------
# get_conversations_base — with active workspace
# ---------------------------------------------------------------------------

class TestGetConversationsBaseWithWorkspace:
    def test_returns_workspace_memory_conversations_path(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("hola")
        mgr.set_active("hola")

        result = ws_utils.get_conversations_base(root=tmp_path)

        expected = tmp_path / "workspaces" / "hola" / "memory" / "conversations"
        assert result == expected

    def test_creates_directory_if_not_exists(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("proj")
        mgr.set_active("proj")

        result = ws_utils.get_conversations_base(root=tmp_path)

        assert result.is_dir()

    def test_returns_path_object(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws")
        mgr.set_active("ws")

        result = ws_utils.get_conversations_base(root=tmp_path)

        assert isinstance(result, Path)

    def test_nested_under_memory_not_loot(self, tmp_path):
        """Conversations must live under memory/, not loot/."""
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("pen")
        mgr.set_active("pen")

        result = ws_utils.get_conversations_base(root=tmp_path)

        assert "memory" in result.parts
        assert "loot" not in result.parts

    def test_matches_fixture_workspace_path(self, tmp_path):
        """Path must match the format seen in the workspace fixture:
        workspaces/hola/memory/conversations/"""
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("hola")
        mgr.set_active("hola")

        result = ws_utils.get_conversations_base(root=tmp_path)

        # Replicate the path seen in the JSON fixtures under workspaces/hola/memory/conversations/
        assert result.relative_to(tmp_path) == Path("workspaces/hola/memory/conversations")


# ---------------------------------------------------------------------------
# get_conversations_base — without active workspace
# ---------------------------------------------------------------------------

class TestGetConversationsBaseWithoutWorkspace:
    def test_returns_global_conversations_directory(self, tmp_path):
        result = ws_utils.get_conversations_base(root=tmp_path)

        assert result == tmp_path / "conversations"

    def test_creates_global_directory(self, tmp_path):
        result = ws_utils.get_conversations_base(root=tmp_path)

        assert result.is_dir()

    def test_emits_warning_once(self, tmp_path, caplog):
        import logging

        with caplog.at_level(logging.WARNING):
            ws_utils.get_conversations_base(root=tmp_path)
            ws_utils.get_conversations_base(root=tmp_path)

        warning_msgs = [r for r in caplog.records if "conversations" in r.message.lower()]
        assert len(warning_msgs) == 1

    def test_not_nested_under_workspaces(self, tmp_path):
        result = ws_utils.get_conversations_base(root=tmp_path)

        assert "workspaces" not in result.parts


# ---------------------------------------------------------------------------
# get_conversations_base — switching workspace changes path
# ---------------------------------------------------------------------------

class TestGetConversationsBaseSwitchWorkspace:
    def test_different_workspaces_produce_different_paths(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws1")
        mgr.create("ws2")

        mgr.set_active("ws1")
        path_ws1 = ws_utils.get_conversations_base(root=tmp_path)

        mgr.set_active("ws2")
        path_ws2 = ws_utils.get_conversations_base(root=tmp_path)

        assert path_ws1 != path_ws2
        assert "ws1" in str(path_ws1)
        assert "ws2" in str(path_ws2)
