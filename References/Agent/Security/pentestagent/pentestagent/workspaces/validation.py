"""Workspace target validation utilities.

Provides helpers to extract candidate targets from arbitrary tool arguments
and to determine whether a candidate target is covered by the allowed
workspace targets (IP, CIDR, hostname).
"""

import ipaddress
import logging
from typing import Any, List

from .manager import TargetManager


def gather_candidate_targets(obj: Any) -> List[str]:
    """
    Extract candidate target strings from arguments (shallow, non-recursive).

    This function inspects only the top-level of the provided object (str or dict)
    and collects values for common target keys (e.g., 'target', 'host', 'ip', etc.).
    It does NOT recurse into nested dictionaries or lists. If you need to extract
    targets from deeply nested structures, you must implement or call a recursive
    extractor separately.

    Rationale: Shallow extraction is fast and predictable for most tool argument
    schemas. For recursive extraction, see the project documentation or extend
    this function as needed.
    """
    candidates: List[str] = []
    if isinstance(obj, str):
        candidates.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in (
                "target",
                "host",
                "hostname",
                "ip",
                "address",
                "url",
                "hosts",
                "targets",
            ):
                if isinstance(v, (list, tuple)):
                    for it in v:
                        if isinstance(it, str):
                            candidates.append(it)
                elif isinstance(v, str):
                    candidates.append(v)
    return candidates


def is_target_in_scope(candidate: str, allowed: List[str]) -> bool:
    """Check whether `candidate` is covered by any entry in `allowed`.

    Allowed entries may be IPs, CIDRs, or hostnames/labels. Candidate may
    also be an IP, CIDR, or hostname. The function normalizes inputs and
    performs robust comparisons for networks and addresses.
    """
    try:
        norm = TargetManager.normalize_target(candidate)
    except Exception:
        return False

    # If candidate is a network (contains '/'), treat as network
    try:
        if "/" in norm:
            cand_net = ipaddress.ip_network(norm, strict=False)
            for a in allowed:
                try:
                    if "/" in a:
                        an = ipaddress.ip_network(a, strict=False)
                        if cand_net.subnet_of(an) or cand_net == an:
                            return True
                    else:
                        # allowed is IP or hostname; accept only when candidate
                        # network represents exactly one address equal to allowed IP
                        try:
                            allowed_ip = ipaddress.ip_address(a)
                        except Exception:
                            # not an IP (likely hostname) - skip
                            continue
                        if (
                            cand_net.num_addresses == 1
                            and cand_net.network_address == allowed_ip
                        ):
                            return True
                except Exception:
                    continue
            return False
        else:
            # candidate is a single IP/hostname
            try:
                cand_ip = ipaddress.ip_address(norm)
                for a in allowed:
                    try:
                        if "/" in a:
                            an = ipaddress.ip_network(a, strict=False)
                            if cand_ip in an:
                                return True
                        else:
                            if TargetManager.normalize_target(a) == norm:
                                return True
                    except Exception:
                        if isinstance(a, str) and a.lower() == norm.lower():
                            return True
                return False
            except Exception:
                # candidate is likely a hostname; compare case-insensitively
                for a in allowed:
                    try:
                        if a.lower() == norm.lower():
                            return True
                    except Exception:
                        continue
                return False
    except Exception as e:
        logging.getLogger(__name__).exception("Error checking target scope: %s", e)
        return False
