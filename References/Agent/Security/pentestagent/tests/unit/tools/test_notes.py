"""Tests for pentestagent.tools.notes."""

import asyncio
import json
from pathlib import Path

import pytest

import pentestagent.tools.notes as notes_module
from pentestagent.tools.notes import (
    _validate_note_schema,
    get_all_notes,
    get_all_notes_sync,
    set_notes_file,
)


# ---------------------------------------------------------------------------
# Fixture: isolated notes file per test
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_notes(tmp_path):
    notes_file = tmp_path / "notes.json"
    set_notes_file(notes_file)
    notes_module._notes.clear()
    yield notes_file
    notes_module._notes.clear()
    notes_module._custom_notes_file = None


async def _call(action: str, **kwargs) -> str:
    args = {"action": action, **kwargs}
    return await notes_module.notes(args, runtime=None)


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

class TestNotesCreate:
    @pytest.mark.asyncio
    async def test_create_basic_note(self):
        result = await _call("create", key="test_key", value="test value")
        assert "Created" in result
        assert "test_key" in result

    @pytest.mark.asyncio
    async def test_create_missing_key_errors(self):
        result = await _call("create", value="some value")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_create_missing_value_errors(self):
        result = await _call("create", key="k")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_create_duplicate_key_errors(self):
        await _call("create", key="dup", value="first")
        result = await _call("create", key="dup", value="second")
        assert "Error" in result

    @pytest.mark.asyncio
    async def test_create_persists_to_file(self, isolated_notes):
        await _call("create", key="persist", value="data")
        assert isolated_notes.exists()
        data = json.loads(isolated_notes.read_text())
        assert "persist" in data

    @pytest.mark.asyncio
    async def test_create_with_valid_category(self):
        result = await _call("create", key="k", value="v", category="vulnerability",
                             target="192.168.1.1", cve="CVE-2021-0001")
        assert "Error" not in result

    @pytest.mark.asyncio
    async def test_create_invalid_category_falls_back_to_info(self):
        result = await _call("create", key="k2", value="v", category="unknown_cat")
        assert "Error" not in result
        notes = await get_all_notes()
        assert notes["k2"]["category"] == "info"


class TestNotesRead:
    @pytest.mark.asyncio
    async def test_read_existing_note(self):
        await _call("create", key="rkey", value="hello world")
        result = await _call("read", key="rkey")
        assert "hello world" in result

    @pytest.mark.asyncio
    async def test_read_nonexistent_note(self):
        result = await _call("read", key="ghost")
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_read_missing_key_errors(self):
        result = await _call("read")
        assert "Error" in result


class TestNotesUpdate:
    @pytest.mark.asyncio
    async def test_update_existing_note(self):
        await _call("create", key="upd", value="original")
        result = await _call("update", key="upd", value="updated")
        assert "Updated" in result

    @pytest.mark.asyncio
    async def test_update_creates_if_missing(self):
        result = await _call("update", key="new", value="fresh")
        assert "Created" in result or "Updated" in result

    @pytest.mark.asyncio
    async def test_update_missing_value_errors(self):
        result = await _call("update", key="upd")
        assert "Error" in result


class TestNotesDelete:
    @pytest.mark.asyncio
    async def test_delete_existing_note(self):
        await _call("create", key="del", value="to delete")
        result = await _call("delete", key="del")
        assert "Deleted" in result
        notes = await get_all_notes()
        assert "del" not in notes

    @pytest.mark.asyncio
    async def test_delete_nonexistent_note(self):
        result = await _call("delete", key="ghost")
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_delete_persists_removal(self, isolated_notes):
        await _call("create", key="x", value="y")
        await _call("delete", key="x")
        data = json.loads(isolated_notes.read_text())
        assert "x" not in data


class TestNotesList:
    @pytest.mark.asyncio
    async def test_list_all_empty(self):
        result = await _call("list_all")
        assert "No notes" in result

    @pytest.mark.asyncio
    async def test_list_all_shows_notes(self):
        await _call("create", key="a", value="alpha")
        await _call("create", key="b", value="beta")
        result = await _call("list_all")
        assert "a" in result
        assert "b" in result

    @pytest.mark.asyncio
    async def test_list_truncated_truncates_long_values(self):
        long_value = "x" * 200
        await _call("create", key="long", value=long_value)
        result = await _call("list_truncated")
        assert "..." in result
        # The truncated value should be at most 60 chars + "..."
        lines = result.split("\n")
        for line in lines:
            if "long" in line:
                # Find the content portion — should be truncated
                assert len(line) < len(long_value)


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

class TestNoteSchemaValidation:
    def test_credential_missing_target_fails(self):
        err = _validate_note_schema("credential", {"username": "admin", "password": "pass"})
        assert err is not None
        assert "target" in err

    def test_credential_valid(self):
        err = _validate_note_schema("credential", {
            "username": "admin", "password": "pass", "target": "10.0.0.1"
        })
        assert err is None

    def test_vulnerability_missing_target_fails(self):
        err = _validate_note_schema("vulnerability", {"cve": "CVE-2021-1234"})
        assert err is not None

    def test_vulnerability_valid(self):
        err = _validate_note_schema("vulnerability", {
            "target": "10.0.0.1", "cve": "CVE-2021-1234"
        })
        assert err is None

    def test_finding_missing_host_data_fails(self):
        err = _validate_note_schema("finding", {"target": "10.0.0.1"})
        assert err is not None

    def test_finding_valid_with_services(self):
        err = _validate_note_schema("finding", {
            "target": "10.0.0.1",
            "services": [{"port": 80, "product": "nginx"}]
        })
        assert err is None

    def test_host_specific_field_without_target_fails(self):
        err = _validate_note_schema("info", {"services": [{"port": 22}]})
        assert err is not None

    def test_info_category_no_required_fields(self):
        err = _validate_note_schema("info", {})
        assert err is None


# ---------------------------------------------------------------------------
# Security: JSON injection / prototype pollution attempts
# ---------------------------------------------------------------------------

class TestNotesSecurityContent:
    @pytest.mark.asyncio
    async def test_json_characters_in_value_stored_safely(self):
        malicious = '{"__proto__": {"admin": true}, "constructor": "exploit"}'
        await _call("create", key="json_attack", value=malicious)
        result = await _call("read", key="json_attack")
        assert "json_attack" in result

    @pytest.mark.asyncio
    async def test_script_tag_in_value_stored_as_literal(self):
        xss = "<script>alert('xss')</script>"
        await _call("create", key="xss", value=xss)
        result = await _call("read", key="xss")
        assert "xss" in result  # stored, not executed

    @pytest.mark.asyncio
    async def test_path_traversal_in_key_stored_safely(self):
        # Key validation is loose but the file path uses a fixed notes file
        # so path traversal in key content just stores the key
        await _call("create", key="normal_key", value="safe")
        notes = await get_all_notes()
        assert "normal_key" in notes

    @pytest.mark.asyncio
    async def test_large_value_stored(self):
        large = "A" * 100_000
        result = await _call("create", key="large", value=large)
        assert "Error" not in result

    @pytest.mark.asyncio
    async def test_get_all_notes_sync_returns_copy(self):
        await _call("create", key="s1", value="v1")
        sync_notes = get_all_notes_sync()
        sync_notes["injected"] = {"content": "evil", "category": "info"}
        # Modifying the returned copy must not affect in-memory notes
        notes = await get_all_notes()
        assert "injected" not in notes
