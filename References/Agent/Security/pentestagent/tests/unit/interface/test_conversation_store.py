"""Tests for pentestagent.interface.conversation_store (ConversationStore)."""

import json
from pathlib import Path

import pytest

from pentestagent.agents.base_agent import AgentMessage, ToolCall, ToolResult
from pentestagent.interface.conversation_store import ConversationMeta, ConversationStore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user(content: str) -> AgentMessage:
    return AgentMessage(role="user", content=content)


def _assistant(content: str) -> AgentMessage:
    return AgentMessage(role="assistant", content=content)


def _assistant_with_tool_call(content: str, call_id: str, tool_name: str, args: dict) -> AgentMessage:
    tc = ToolCall(id=call_id, name=tool_name, arguments=args)
    return AgentMessage(role="assistant", content=content, tool_calls=[tc])


def _tool_result(call_id: str, tool_name: str, result: str) -> AgentMessage:
    tr = ToolResult(tool_call_id=call_id, tool_name=tool_name, result=result, success=True)
    return AgentMessage(role="tool_result", content="", tool_results=[tr])


# Minimal conversation matching the Hello example from the JSON fixtures
_HELLO_MESSAGES = [
    _user("Hello"),
    _assistant("Hey! Ready when you are."),
    _user("Let's go with camera"),
    _assistant("Great — focusing on the camera (192.168.0.21:8086)."),
]

# Conversation with a tool call + tool result
_TOOL_MESSAGES = [
    _user("Try to detect what is behind the port 8086"),
    _assistant_with_tool_call(
        "Plan: run a small set of HTTPS probes.",
        call_id="call_vBw8IJhb3UrHXFH70s1rLFMS",
        tool_name="terminal",
        args={"command": "bash -lc 'echo DONE'", "timeout": 300},
    ),
    _tool_result(
        call_id="call_vBw8IJhb3UrHXFH70s1rLFMS",
        tool_name="terminal",
        result="Exit Code: 0\n--- stdout ---\nDONE\n",
    ),
    _assistant("Short readout: all probes returned HTTP status 000."),
]


# ---------------------------------------------------------------------------
# ConversationStore.save — new conversations
# ---------------------------------------------------------------------------

class TestSaveNewConversation:
    def test_returns_conv_id(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        assert conv_id is not None
        assert isinstance(conv_id, str)
        assert len(conv_id) == 32  # uuid4().hex

    def test_creates_json_file(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        assert (tmp_path / f"{conv_id}.json").exists()

    def test_json_file_structure(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        data = json.loads((tmp_path / f"{conv_id}.json").read_text())
        assert data["id"] == conv_id
        assert "title" in data
        assert "created_at" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) == len(_HELLO_MESSAGES)

    def test_title_comes_from_first_user_message(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        data = json.loads((tmp_path / f"{conv_id}.json").read_text())
        assert data["title"] == "Hello"

    def test_title_truncated_to_80_chars(self, tmp_path):
        long_content = "A" * 200
        messages = [_user(long_content), _assistant("ok")]
        store = ConversationStore(tmp_path)
        conv_id = store.save(messages)
        data = json.loads((tmp_path / f"{conv_id}.json").read_text())
        assert len(data["title"]) <= 80

    def test_fallback_title_when_no_user_message(self, tmp_path):
        messages = [_assistant("only an assistant message")]
        store = ConversationStore(tmp_path)
        conv_id = store.save(messages)
        data = json.loads((tmp_path / f"{conv_id}.json").read_text())
        assert data["title"].startswith("Conversation")

    def test_creates_index_entry(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        index = json.loads((tmp_path / "index.json").read_text())
        assert len(index) == 1
        assert index[0]["id"] == conv_id
        assert index[0]["message_count"] == len(_HELLO_MESSAGES)

    def test_returns_none_for_empty_messages(self, tmp_path):
        store = ConversationStore(tmp_path)
        result = store.save([])
        assert result is None

    def test_new_conversations_prepended_to_index(self, tmp_path):
        store = ConversationStore(tmp_path)
        id1 = store.save([_user("first")])
        id2 = store.save([_user("second")])
        index = json.loads((tmp_path / "index.json").read_text())
        assert index[0]["id"] == id2
        assert index[1]["id"] == id1


# ---------------------------------------------------------------------------
# ConversationStore.save — update in-place (existing conv_id)
# ---------------------------------------------------------------------------

class TestSaveUpdateInPlace:
    def test_overwrites_file_same_id(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        extended = _HELLO_MESSAGES + [_user("one more")]
        returned_id = store.save(extended, conv_id=conv_id)
        assert returned_id == conv_id

    def test_index_not_duplicated(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        store.save(_HELLO_MESSAGES + [_user("extra")], conv_id=conv_id)
        index = json.loads((tmp_path / "index.json").read_text())
        assert len(index) == 1

    def test_message_count_updated(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        extended = _HELLO_MESSAGES + [_user("new")]
        store.save(extended, conv_id=conv_id)
        index = json.loads((tmp_path / "index.json").read_text())
        assert index[0]["message_count"] == len(extended)

    def test_created_at_preserved(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        original_data = json.loads((tmp_path / f"{conv_id}.json").read_text())
        original_ts = original_data["created_at"]
        store.save(_HELLO_MESSAGES + [_user("extra")], conv_id=conv_id)
        updated_data = json.loads((tmp_path / f"{conv_id}.json").read_text())
        assert updated_data["created_at"] == original_ts

    def test_unknown_conv_id_creates_new(self, tmp_path):
        store = ConversationStore(tmp_path)
        new_id = store.save(_HELLO_MESSAGES, conv_id="nonexistentid123")
        assert new_id != "nonexistentid123"
        index = json.loads((tmp_path / "index.json").read_text())
        assert len(index) == 1
        assert index[0]["id"] == new_id


# ---------------------------------------------------------------------------
# ConversationStore.load
# ---------------------------------------------------------------------------

class TestLoad:
    def test_roundtrip_simple_messages(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_HELLO_MESSAGES)
        loaded = store.load(conv_id)
        assert len(loaded) == len(_HELLO_MESSAGES)
        for orig, restored in zip(_HELLO_MESSAGES, loaded):
            assert restored.role == orig.role
            assert restored.content == orig.content

    def test_roundtrip_with_tool_calls_and_results(self, tmp_path):
        store = ConversationStore(tmp_path)
        conv_id = store.save(_TOOL_MESSAGES)
        loaded = store.load(conv_id)
        assert len(loaded) == len(_TOOL_MESSAGES)

        # assistant message with tool_calls
        assistant_msg = loaded[1]
        assert assistant_msg.role == "assistant"
        assert assistant_msg.tool_calls is not None
        assert len(assistant_msg.tool_calls) == 1
        tc = assistant_msg.tool_calls[0]
        assert tc.id == "call_vBw8IJhb3UrHXFH70s1rLFMS"
        assert tc.name == "terminal"
        assert tc.arguments["timeout"] == 300

        # tool_result message
        result_msg = loaded[2]
        assert result_msg.role == "tool_result"
        assert result_msg.tool_results is not None
        tr = result_msg.tool_results[0]
        assert tr.tool_call_id == "call_vBw8IJhb3UrHXFH70s1rLFMS"
        assert tr.tool_name == "terminal"
        assert tr.success is True
        assert "DONE" in tr.result

    def test_load_missing_returns_empty(self, tmp_path):
        store = ConversationStore(tmp_path)
        result = store.load("doesnotexist")
        assert result == []

    def test_load_from_fixture_json(self, tmp_path):
        """Load a conversation from the exact JSON format used in the file store."""
        fixture = {
            "id": "836537b948284454a3ba9d6fa25a9574",
            "title": "Hello",
            "created_at": "2026-05-11T20:51:37.556372+00:00",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                    "tool_calls": None,
                    "tool_results": None,
                    "metadata": {},
                    "usage": None,
                },
                {
                    "role": "assistant",
                    "content": "Hey! Ready when you are.",
                    "tool_calls": None,
                    "tool_results": None,
                    "metadata": {},
                    "usage": None,
                },
                {
                    "role": "user",
                    "content": "Let's go with camera",
                    "tool_calls": None,
                    "tool_results": None,
                    "metadata": {},
                    "usage": None,
                },
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_vBw8IJhb3UrHXFH70s1rLFMS",
                            "name": "terminal",
                            "arguments": {
                                "command": "bash -lc 'echo DONE'",
                                "timeout": 300,
                            },
                        }
                    ],
                    "tool_results": None,
                    "metadata": {},
                    "usage": None,
                },
                {
                    "role": "tool_result",
                    "content": "",
                    "tool_calls": None,
                    "tool_results": [
                        {
                            "tool_call_id": "call_vBw8IJhb3UrHXFH70s1rLFMS",
                            "tool_name": "terminal",
                            "result": "Exit Code: 0\n--- stdout ---\nDONE\n",
                            "error": None,
                            "success": True,
                        }
                    ],
                    "metadata": {},
                    "usage": None,
                },
            ],
        }
        conv_id = fixture["id"]
        (tmp_path / f"{conv_id}.json").write_text(json.dumps(fixture), encoding="utf-8")

        store = ConversationStore(tmp_path)
        messages = store.load(conv_id)

        assert len(messages) == 5
        assert messages[0].role == "user"
        assert messages[0].content == "Hello"
        assert messages[1].role == "assistant"
        assert messages[3].tool_calls[0].name == "terminal"
        assert messages[4].tool_results[0].success is True


# ---------------------------------------------------------------------------
# ConversationStore.list_conversations
# ---------------------------------------------------------------------------

class TestListConversations:
    def test_empty_when_no_index(self, tmp_path):
        store = ConversationStore(tmp_path)
        assert store.list_conversations() == []

    def test_returns_conversation_meta(self, tmp_path):
        store = ConversationStore(tmp_path)
        store.save(_HELLO_MESSAGES)
        convs = store.list_conversations()
        assert len(convs) == 1
        assert isinstance(convs[0], ConversationMeta)
        assert convs[0].title == "Hello"
        assert convs[0].message_count == len(_HELLO_MESSAGES)

    def test_multiple_conversations_ordered_newest_first(self, tmp_path):
        store = ConversationStore(tmp_path)
        store.save([_user("first conversation")])
        store.save([_user("second conversation")])
        convs = store.list_conversations()
        assert convs[0].title == "second conversation"
        assert convs[1].title == "first conversation"

    def test_list_from_fixture_index(self, tmp_path):
        """Use the exact index.json format from the workspace fixture."""
        index = [
            {
                "id": "a8d43447bddf4c7d81dc9c6dde702f3c",
                "title": "Hola",
                "created_at": "2026-05-11T20:52:17.052017+00:00",
                "message_count": 2,
            },
            {
                "id": "836537b948284454a3ba9d6fa25a9574",
                "title": "Hello",
                "created_at": "2026-05-11T20:51:37.556372+00:00",
                "message_count": 14,
            },
        ]
        (tmp_path / "index.json").write_text(json.dumps(index), encoding="utf-8")
        store = ConversationStore(tmp_path)
        convs = store.list_conversations()
        assert len(convs) == 2
        assert convs[0].id == "a8d43447bddf4c7d81dc9c6dde702f3c"
        assert convs[0].title == "Hola"
        assert convs[0].message_count == 2
        assert convs[1].id == "836537b948284454a3ba9d6fa25a9574"
        assert convs[1].message_count == 14


# ---------------------------------------------------------------------------
# ConversationStore._prune
# ---------------------------------------------------------------------------

class TestPrune:
    def test_prune_removes_oldest_files(self, tmp_path):
        store = ConversationStore(tmp_path)
        store.MAX_CONVERSATIONS = 3

        ids = []
        for i in range(5):
            cid = store.save([_user(f"message {i}")])
            ids.append(cid)

        # After saving 5 with MAX=3, the 2 oldest should be deleted
        assert not (tmp_path / f"{ids[0]}.json").exists()
        assert not (tmp_path / f"{ids[1]}.json").exists()
        assert (tmp_path / f"{ids[2]}.json").exists()
        assert (tmp_path / f"{ids[3]}.json").exists()
        assert (tmp_path / f"{ids[4]}.json").exists()

    def test_prune_keeps_index_within_limit(self, tmp_path):
        store = ConversationStore(tmp_path)
        store.MAX_CONVERSATIONS = 3
        for i in range(5):
            store.save([_user(f"message {i}")])
        index = json.loads((tmp_path / "index.json").read_text())
        assert len(index) == 3

    def test_no_prune_when_under_limit(self, tmp_path):
        store = ConversationStore(tmp_path)
        for i in range(3):
            store.save([_user(f"message {i}")])
        index = json.loads((tmp_path / "index.json").read_text())
        assert len(index) == 3
