#!/usr/bin/env python3
"""Pure acceptance rules for FAST-LIO to PX4 EKF fusion evidence."""

from __future__ import annotations

import math
from typing import Any


DEFAULT_MIN_ARMED_FUSION_SUCCESS_RATIO = 0.99
DEFAULT_MAX_ALIGNED_TRUTH_POSITION_P95_M = 0.15


def _finite_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _p95_within_limit(stats: Any, limit: float) -> bool:
    if not isinstance(stats, dict):
        return False
    value = _finite_number(stats.get("p95"))
    return value is not None and value <= limit


def evaluate_goal3_gate(
    checks: dict[str, Any],
    comparisons: dict[str, Any],
    *,
    min_armed_fusion_success_ratio: float = DEFAULT_MIN_ARMED_FUSION_SUCCESS_RATIO,
    max_aligned_truth_position_p95_m: float = DEFAULT_MAX_ALIGNED_TRUTH_POSITION_P95_M,
) -> dict[str, bool]:
    """Evaluate continuous in-flight fusion and simulation alignment evidence.

    The recorder can observe expected pre-arm settling states.  Fusion is
    therefore evaluated only while the PX4 state reports the vehicle armed.
    """

    ratio = _finite_number(checks.get("armed_fusion_success_ratio"))
    threshold = _finite_number(min_armed_fusion_success_ratio)
    residual_limit = _finite_number(max_aligned_truth_position_p95_m)
    negative_gaps = checks.get("negative_header_gaps", {})
    no_negative_gaps = isinstance(negative_gaps, dict) and all(
        int(count or 0) == 0 for count in negative_gaps.values()
    )

    outcome = {
        "external_odom_valid_last": bool(checks.get("external_odom_valid_last")),
        "armed_fusion_samples_present": int(checks.get("armed_fusion_sample_count", 0) or 0) > 0,
        "armed_fusion_success_seen": bool(checks.get("armed_fusion_success_seen")),
        "armed_fusion_success_last": bool(checks.get("armed_fusion_success_last")),
        "armed_fusion_success_ratio_ok": (
            ratio is not None and threshold is not None and ratio >= threshold
        ),
        "aligned_truth_position_p95_ok": (
            residual_limit is not None
            and _p95_within_limit(
                comparisons.get("aligned_vs_truth_position_m"), residual_limit
            )
        ),
        "no_negative_header_gaps": no_negative_gaps,
    }
    outcome["gate_pass"] = all(outcome.values())
    return outcome
