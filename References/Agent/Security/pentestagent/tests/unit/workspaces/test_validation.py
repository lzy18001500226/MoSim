"""Tests for pentestagent.workspaces.validation."""

import pytest

from pentestagent.workspaces.validation import gather_candidate_targets, is_target_in_scope


# ---------------------------------------------------------------------------
# gather_candidate_targets
# ---------------------------------------------------------------------------

class TestGatherCandidateTargets:
    def test_string_input_returns_itself(self):
        result = gather_candidate_targets("192.168.1.1")
        assert "192.168.1.1" in result

    def test_dict_with_target_key(self):
        result = gather_candidate_targets({"target": "10.0.0.1"})
        assert "10.0.0.1" in result

    def test_dict_with_host_key(self):
        result = gather_candidate_targets({"host": "example.com"})
        assert "example.com" in result

    def test_dict_with_hostname_key(self):
        result = gather_candidate_targets({"hostname": "db.internal"})
        assert "db.internal" in result

    def test_dict_with_ip_key(self):
        result = gather_candidate_targets({"ip": "172.16.0.1"})
        assert "172.16.0.1" in result

    def test_dict_with_address_key(self):
        result = gather_candidate_targets({"address": "192.168.0.1"})
        assert "192.168.0.1" in result

    def test_dict_with_url_key(self):
        result = gather_candidate_targets({"url": "http://target.com"})
        assert "http://target.com" in result

    def test_dict_with_hosts_list(self):
        result = gather_candidate_targets({"hosts": ["1.1.1.1", "2.2.2.2"]})
        assert "1.1.1.1" in result
        assert "2.2.2.2" in result

    def test_dict_with_targets_list(self):
        result = gather_candidate_targets({"targets": ["a.com", "b.com"]})
        assert "a.com" in result
        assert "b.com" in result

    def test_irrelevant_key_ignored(self):
        result = gather_candidate_targets({"command": "nmap -sV 10.0.0.1", "port": "80"})
        assert result == []

    def test_empty_dict_returns_empty(self):
        assert gather_candidate_targets({}) == []

    def test_none_values_ignored(self):
        result = gather_candidate_targets({"target": None})
        assert result == []

    def test_case_insensitive_key_matching(self):
        result = gather_candidate_targets({"TARGET": "1.2.3.4"})
        assert "1.2.3.4" in result


# ---------------------------------------------------------------------------
# is_target_in_scope — IPs
# ---------------------------------------------------------------------------

class TestIsTargetInScopeIPs:
    def test_exact_ip_in_scope(self):
        assert is_target_in_scope("192.168.1.1", ["192.168.1.1"]) is True

    def test_ip_not_in_scope(self):
        assert is_target_in_scope("10.0.0.1", ["192.168.1.1"]) is False

    def test_ip_in_cidr(self):
        assert is_target_in_scope("192.168.1.100", ["192.168.1.0/24"]) is True

    def test_ip_outside_cidr(self):
        assert is_target_in_scope("10.0.0.1", ["192.168.1.0/24"]) is False

    def test_ip_at_network_boundary(self):
        assert is_target_in_scope("192.168.1.0", ["192.168.1.0/24"]) is True

    def test_ip_at_broadcast(self):
        assert is_target_in_scope("192.168.1.255", ["192.168.1.0/24"]) is True

    def test_empty_allowed_returns_false(self):
        assert is_target_in_scope("192.168.1.1", []) is False

    def test_multiple_allowed_ranges(self):
        allowed = ["10.0.0.0/8", "172.16.0.0/12"]
        assert is_target_in_scope("10.10.10.10", allowed) is True
        assert is_target_in_scope("172.20.0.1", allowed) is True
        assert is_target_in_scope("192.168.1.1", allowed) is False


# ---------------------------------------------------------------------------
# is_target_in_scope — CIDRs as candidate
# ---------------------------------------------------------------------------

class TestIsTargetInScopeCIDRs:
    def test_subnet_within_allowed_network(self):
        assert is_target_in_scope("192.168.1.0/24", ["192.168.0.0/16"]) is True

    def test_exact_cidr_match(self):
        assert is_target_in_scope("10.0.0.0/8", ["10.0.0.0/8"]) is True

    def test_larger_cidr_not_in_smaller_allowed(self):
        assert is_target_in_scope("10.0.0.0/8", ["10.0.0.0/24"]) is False

    def test_disjoint_cidrs(self):
        assert is_target_in_scope("172.16.0.0/12", ["10.0.0.0/8"]) is False


# ---------------------------------------------------------------------------
# is_target_in_scope — hostnames
# ---------------------------------------------------------------------------

class TestIsTargetInScopeHostnames:
    def test_exact_hostname_match(self):
        assert is_target_in_scope("target.example.com", ["target.example.com"]) is True

    def test_hostname_case_insensitive(self):
        assert is_target_in_scope("TARGET.EXAMPLE.COM", ["target.example.com"]) is True

    def test_hostname_not_in_scope(self):
        assert is_target_in_scope("evil.com", ["target.example.com"]) is False

    def test_subdomain_not_automatically_in_scope(self):
        # "sub.example.com" should NOT match "example.com" unless explicitly allowed
        assert is_target_in_scope("sub.example.com", ["example.com"]) is False


# ---------------------------------------------------------------------------
# is_target_in_scope — security: bypass attempts
# ---------------------------------------------------------------------------

class TestScopeBypassAttempts:
    """These tests verify that scope validation cannot be trivially bypassed."""

    def test_ip_outside_any_cidr_is_rejected(self):
        allowed = ["192.168.1.0/24"]
        assert is_target_in_scope("8.8.8.8", allowed) is False

    def test_loopback_not_in_scope_if_not_listed(self):
        assert is_target_in_scope("127.0.0.1", ["192.168.1.0/24"]) is False

    def test_private_range_not_in_public_cidr(self):
        assert is_target_in_scope("10.0.0.1", ["8.8.8.0/24"]) is False

    def test_invalid_ip_returns_false(self):
        assert is_target_in_scope("999.999.999.999", ["192.168.1.0/24"]) is False

    def test_empty_string_returns_false(self):
        assert is_target_in_scope("", ["192.168.1.0/24"]) is False

    def test_malformed_cidr_candidate_returns_false(self):
        assert is_target_in_scope("192.168.1.1/999", ["192.168.1.0/24"]) is False

    def test_dotdot_hostname_rejected(self):
        # ".." in hostname should be invalid
        assert is_target_in_scope("..evil.com", ["evil.com"]) is False

    def test_path_traversal_in_hostname_rejected(self):
        assert is_target_in_scope("../etc/passwd", ["192.168.1.0/24"]) is False
