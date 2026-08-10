from Scripts.sunray.fastlio_fusion_evidence_contract import evaluate_goal3_gate


def _checks(**overrides):
    values = {
        "external_odom_valid_last": True,
        "armed_fusion_sample_count": 100,
        "armed_fusion_success_seen": True,
        "armed_fusion_success_last": True,
        "armed_fusion_success_ratio": 1.0,
        "negative_header_gaps": {"fastlio_aligned_odom": 0},
    }
    values.update(overrides)
    return values


def _comparisons(p95=0.04):
    return {"aligned_vs_truth_position_m": {"p95": p95}}


def test_goal3_gate_accepts_continuous_armed_fusion_within_truth_residual_limit():
    result = evaluate_goal3_gate(_checks(), _comparisons())

    assert result["gate_pass"] is True


def test_goal3_gate_rejects_a_lost_fusion_even_when_it_was_seen_earlier():
    result = evaluate_goal3_gate(
        _checks(
            armed_fusion_success_last=False,
            armed_fusion_success_ratio=0.45,
        ),
        _comparisons(),
    )

    assert result["armed_fusion_success_last"] is False
    assert result["armed_fusion_success_ratio_ok"] is False
    assert result["gate_pass"] is False


def test_goal3_gate_rejects_large_aligned_to_truth_drift():
    result = evaluate_goal3_gate(_checks(), _comparisons(p95=72.0))

    assert result["aligned_truth_position_p95_ok"] is False
    assert result["gate_pass"] is False
