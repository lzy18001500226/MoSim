"""Security tests: scope validation bypass attempts.

These tests verify that an attacker cannot manipulate target validation
to reach out-of-scope hosts through edge cases in IP/CIDR comparison logic.
"""

import pytest

from pentestagent.workspaces.validation import is_target_in_scope
from pentestagent.workspaces.manager import TargetManager, WorkspaceError


# ---------------------------------------------------------------------------
# IPv4 scope bypass attempts
# ---------------------------------------------------------------------------

class TestIPv4ScopeBypass:
    def test_zero_cidr_does_not_match_all(self):
        # /0 covers everything; candidate should only match if allowed list contains /0
        assert is_target_in_scope("8.8.8.8", ["192.168.1.0/24"]) is False

    def test_broadcast_outside_scope(self):
        assert is_target_in_scope("255.255.255.255", ["192.168.1.0/24"]) is False

    def test_loopback_not_in_private_scope(self):
        assert is_target_in_scope("127.0.0.1", ["10.0.0.0/8"]) is False

    def test_link_local_not_in_private_scope(self):
        assert is_target_in_scope("169.254.0.1", ["10.0.0.0/8"]) is False

    def test_multicast_not_in_private_scope(self):
        assert is_target_in_scope("224.0.0.1", ["10.0.0.0/8"]) is False

    def test_adjacent_cidr_does_not_bleed(self):
        # 192.168.2.1 is NOT in 192.168.1.0/24
        assert is_target_in_scope("192.168.2.1", ["192.168.1.0/24"]) is False

    def test_octet_boundary_exact(self):
        assert is_target_in_scope("192.168.1.1", ["192.168.1.0/32"]) is False
        assert is_target_in_scope("192.168.1.0", ["192.168.1.0/32"]) is True


# ---------------------------------------------------------------------------
# CIDR expansion bypass
# ---------------------------------------------------------------------------

class TestCIDRExpansionBypass:
    def test_larger_network_not_within_smaller_allowed(self):
        # Attacker requests a larger network that contains the allowed one
        assert is_target_in_scope("10.0.0.0/8", ["10.0.0.0/24"]) is False

    def test_supernet_containing_allowed_rejected(self):
        assert is_target_in_scope("0.0.0.0/0", ["192.168.1.0/24"]) is False

    def test_different_class_b_rejected(self):
        assert is_target_in_scope("172.16.0.0/12", ["10.0.0.0/8"]) is False


# ---------------------------------------------------------------------------
# Hostname bypass
# ---------------------------------------------------------------------------

class TestHostnameScopeBypass:
    def test_similar_hostname_rejected(self):
        # "targetexample.com" should not match "target.example.com"
        assert is_target_in_scope("targetexample.com", ["target.example.com"]) is False

    def test_subdomain_not_automatically_in_scope(self):
        assert is_target_in_scope("evil.example.com", ["example.com"]) is False

    def test_hostname_prefix_not_match(self):
        assert is_target_in_scope("target", ["target.example.com"]) is False

    def test_hostname_with_trailing_dot_normalized(self):
        # Trailing dots in DNS are stripped by normalize_target
        # If TargetManager rejects them, scope check returns False (also fine)
        result = is_target_in_scope("example.com.", ["example.com"])
        # Either True (if trailing dot is stripped) or False (if rejected) is acceptable,
        # but it must NOT crash
        assert isinstance(result, bool)

    def test_wildcard_not_supported(self):
        assert is_target_in_scope("*.example.com", ["example.com"]) is False


# ---------------------------------------------------------------------------
# Mixed IP/hostname scope
# ---------------------------------------------------------------------------

class TestMixedScopeEntries:
    def test_ip_against_hostname_scope(self):
        # IP address should not match hostname-only scope
        assert is_target_in_scope("192.168.1.1", ["example.com"]) is False

    def test_hostname_against_cidr_scope(self):
        # A hostname should not match a CIDR scope entry
        assert is_target_in_scope("example.com", ["192.168.1.0/24"]) is False

    def test_empty_allowed_list(self):
        assert is_target_in_scope("192.168.1.1", []) is False

    def test_none_like_strings_in_allowed(self):
        assert is_target_in_scope("192.168.1.1", ["None", "null", ""]) is False


# ---------------------------------------------------------------------------
# TargetManager path traversal via normalize
# ---------------------------------------------------------------------------

class TestTargetManagerPathTraversal:
    @pytest.mark.parametrize("payload", [
        "../etc/passwd",
        "../../root",
        "/etc/shadow",
        "c:\\windows\\system32",
        "%2e%2e/etc/passwd",
    ])
    def test_path_like_inputs_rejected(self, payload):
        with pytest.raises((WorkspaceError, Exception)):
            TargetManager.normalize_target(payload)
