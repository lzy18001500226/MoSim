from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "mworks" / "resume_offline_profile_animation.py"


def load_module():
    spec = importlib.util.spec_from_file_location("resume_offline_profile_animation", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.closed = False

    def call_tool(self, *_args, **_kwargs):
        return self.response

    def close(self):
        self.closed = True


@pytest.mark.parametrize(
    "response, expected_ok",
    [
        ({"ok": True, "run_script_result": {"create_animation": True}}, True),
        ({"ok": True, "run_script_result": {"create_animation": False}}, False),
    ],
)
def test_resume_animation_requires_bound_result(monkeypatch, capsys, response, expected_ok):
    module = load_module()
    client = FakeClient(response)
    monkeypatch.setattr(module.mcp, "resolve_wrapper", lambda _value: "wrapper")
    monkeypatch.setattr(module.mcp, "wrapper_command", lambda _value: ["wrapper"])
    monkeypatch.setattr(module.mcp, "initialize_mcp_client", lambda _client: {"driver_ready": True})
    monkeypatch.setattr(module.mcp, "JsonlMcpClient", lambda *_args: client)

    if expected_ok:
        assert module.main() == 0
        assert json.loads(capsys.readouterr().out)["ok"] is True
    else:
        with pytest.raises(RuntimeError, match="no_bound_result_in_current_session"):
            module.main()
    assert client.closed is True
