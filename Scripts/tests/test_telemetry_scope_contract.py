from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts" / "mworks_live"))

from telemetry_scope_contract import TelemetryScopeAck, TelemetryScopeFrame


def test_telemetry_scope_frame_round_trip() -> None:
    frame = TelemetryScopeFrame(
        run_id="scope-run-001",
        sequence=42,
        source_stamp_ns=100,
        produced_monotonic_ns=200,
        valid_until_ns=300,
        armed=True,
        state_valid=True,
        reference_valid=True,
        command_valid=False,
        values=tuple(float(index) for index in range(32)),
    )

    assert TelemetryScopeFrame.unpack(frame.pack()) == frame


def test_telemetry_scope_ack_round_trip() -> None:
    ack = TelemetryScopeAck(
        run_id="scope-run-001",
        sequence=8,
        related_sequence=42,
        receiver_monotonic_ns=500,
        echoed_sender_monotonic_ns=200,
    )

    assert TelemetryScopeAck.unpack(ack.pack()) == ack


def test_telemetry_scope_rejects_non_finite_values() -> None:
    values = [0.0] * 32
    values[5] = float("nan")
    frame = TelemetryScopeFrame(
        run_id="scope-run-001",
        sequence=0,
        source_stamp_ns=0,
        produced_monotonic_ns=0,
        valid_until_ns=1,
        armed=False,
        state_valid=True,
        reference_valid=False,
        command_valid=False,
        values=tuple(values),
    )

    with pytest.raises(ValueError, match="invalid_telemetry_scope_values"):
        frame.pack()
