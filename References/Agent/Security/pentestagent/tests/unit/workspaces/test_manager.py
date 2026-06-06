"""Tests for pentestagent.workspaces.manager (WorkspaceManager, TargetManager)."""

import pytest

from pentestagent.workspaces.manager import (
    TargetManager,
    WorkspaceError,
    WorkspaceManager,
)


# ---------------------------------------------------------------------------
# TargetManager.normalize_target
# ---------------------------------------------------------------------------

class TestTargetManagerNormalize:
    def test_valid_ipv4(self):
        assert TargetManager.normalize_target("192.168.1.1") == "192.168.1.1"

    def test_valid_ipv4_with_whitespace(self):
        assert TargetManager.normalize_target("  10.0.0.1  ") == "10.0.0.1"

    def test_valid_cidr(self):
        result = TargetManager.normalize_target("192.168.1.0/24")
        assert "192.168.1.0/24" in result

    def test_valid_hostname(self):
        assert TargetManager.normalize_target("example.com") == "example.com"

    def test_hostname_lowercased(self):
        assert TargetManager.normalize_target("Example.COM") == "example.com"

    def test_ipv6_accepted(self):
        result = TargetManager.normalize_target("::1")
        assert result is not None

    def test_invalid_target_raises(self):
        with pytest.raises(WorkspaceError):
            TargetManager.normalize_target("not a valid target!@#")

    def test_double_dot_hostname_raises(self):
        with pytest.raises(WorkspaceError):
            TargetManager.normalize_target("evil..com")

    def test_path_traversal_raises(self):
        with pytest.raises(WorkspaceError):
            TargetManager.normalize_target("../etc/passwd")

    def test_special_chars_raise(self):
        with pytest.raises(WorkspaceError):
            TargetManager.normalize_target("<script>alert(1)</script>")


class TestTargetManagerValidate:
    def test_valid_ip_returns_true(self):
        assert TargetManager.validate("192.168.1.1") is True

    def test_valid_hostname_returns_true(self):
        assert TargetManager.validate("target.local") is True

    def test_invalid_target_returns_false(self):
        assert TargetManager.validate("not valid!") is False

    def test_empty_string_returns_false(self):
        assert TargetManager.validate("") is False


# ---------------------------------------------------------------------------
# WorkspaceManager — name validation (path traversal security)
# ---------------------------------------------------------------------------

class TestWorkspaceNameValidation:
    def test_valid_name(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.validate_name("my-workspace")

    def test_valid_name_with_dots(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.validate_name("workspace.v2")

    def test_path_traversal_dot_dot_raises(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        with pytest.raises(WorkspaceError):
            mgr.validate_name("../../etc/passwd")

    def test_slash_in_name_raises(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        with pytest.raises(WorkspaceError):
            mgr.validate_name("a/b")

    def test_special_chars_raise(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        with pytest.raises(WorkspaceError):
            mgr.validate_name("name with spaces")

    def test_too_long_name_raises(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        with pytest.raises(WorkspaceError):
            mgr.validate_name("a" * 65)

    def test_empty_name_raises(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        with pytest.raises(WorkspaceError):
            mgr.validate_name("")


# ---------------------------------------------------------------------------
# WorkspaceManager — CRUD
# ---------------------------------------------------------------------------

class TestWorkspaceManagerCreate:
    def test_create_workspace(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        meta = mgr.create("test")
        assert meta["name"] == "test"

    def test_create_creates_required_directories(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ops")
        ws_path = tmp_path / "workspaces" / "ops"
        assert (ws_path / "loot").is_dir()
        assert (ws_path / "notes").is_dir()
        assert (ws_path / "memory").is_dir()

    def test_create_writes_meta_yaml(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("proj")
        assert (tmp_path / "workspaces" / "proj" / "meta.yaml").exists()

    def test_create_idempotent(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("dup")
        mgr.create("dup")
        assert len(mgr.list_workspaces()) == 1

    def test_create_targets_default_empty(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        meta = mgr.create("empty")
        assert meta["targets"] == []


class TestWorkspaceManagerActive:
    def test_get_active_empty_when_none(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        assert mgr.get_active() == ""

    def test_set_and_get_active(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws1")
        mgr.set_active("ws1")
        assert mgr.get_active() == "ws1"

    def test_set_active_creates_workspace_if_needed(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.set_active("newws")
        assert "newws" in mgr.list_workspaces()


class TestWorkspaceManagerTargets:
    def test_add_valid_target(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("scan")
        targets = mgr.add_targets("scan", ["192.168.1.1"])
        assert "192.168.1.1" in targets

    def test_add_cidr_target(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("scan")
        targets = mgr.add_targets("scan", ["10.0.0.0/8"])
        assert any("10.0.0.0" in t for t in targets)

    def test_add_duplicate_target_ignored(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("scan")
        mgr.add_targets("scan", ["192.168.1.1"])
        targets = mgr.add_targets("scan", ["192.168.1.1"])
        assert targets.count("192.168.1.1") == 1

    def test_add_invalid_target_raises(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("scan")
        with pytest.raises(WorkspaceError):
            mgr.add_targets("scan", ["not-valid!!"])

    def test_remove_target(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("scan")
        mgr.add_targets("scan", ["192.168.1.1"])
        remaining = mgr.remove_target("scan", "192.168.1.1")
        assert "192.168.1.1" not in remaining

    def test_list_targets_empty(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("empty")
        assert mgr.list_targets("empty") == []

    def test_list_workspaces(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("a")
        mgr.create("b")
        ws_list = mgr.list_workspaces()
        assert "a" in ws_list
        assert "b" in ws_list


class TestWorkspaceManagerMeta:
    def test_get_meta_returns_dict(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws")
        meta = mgr.get_meta("ws")
        assert isinstance(meta, dict)
        assert meta["name"] == "ws"

    def test_set_and_get_operator_note(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws")
        mgr.set_operator_note("ws", "initial note")
        note = mgr.get_meta_field("ws", "operator_notes")
        assert "initial note" in note

    def test_operator_note_appends(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws")
        mgr.set_operator_note("ws", "first")
        mgr.set_operator_note("ws", "second")
        note = mgr.get_meta_field("ws", "operator_notes")
        assert "first" in note
        assert "second" in note

    def test_set_last_target(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws")
        result = mgr.set_last_target("ws", "10.0.0.1")
        assert result == "10.0.0.1"
        assert "10.0.0.1" in mgr.list_targets("ws")

    def test_corrupted_meta_yaml_raises_workspace_error(self, tmp_path):
        mgr = WorkspaceManager(root=tmp_path)
        mgr.create("ws")
        meta_path = tmp_path / "workspaces" / "ws" / "meta.yaml"
        meta_path.write_text("{ invalid yaml: [unclosed", encoding="utf-8")
        with pytest.raises(WorkspaceError):
            mgr.get_meta("ws")
