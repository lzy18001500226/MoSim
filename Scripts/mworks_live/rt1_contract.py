#!/usr/bin/env python3
"""Fixed-size RT1 wire contract and fail-closed control-owner state machine."""

from __future__ import annotations

import enum
import math
import struct
from dataclasses import dataclass


PROTOCOL_VERSION = 1
STATE_REFERENCE_MAGIC = 0x4D525431  # MRT1
COMMAND_MAGIC = 0x4D524331  # MRC1
RUN_ID_SIZE = 64

# Header: magic, version, flags, sequence, related sequence, source stamp,
# produced/receive stamp, validity deadline, fixed-size run_id.
HEADER = struct.Struct(f"<IHHIIQQQ{RUN_ID_SIZE}s")
STATE_REFERENCE_VALUES = struct.Struct("<24d")
COMMAND_VALUES = struct.Struct("<5dII")

FLAG_ARMED = 1 << 0
FLAG_STATE_VALID = 1 << 1
FLAG_REFERENCE_VALID = 1 << 2
FLAG_OUTPUT_VALID = 1 << 3


class ControlState(str, enum.Enum):
    DISABLED = "DISABLED"
    SHADOW = "SHADOW"
    READY = "READY"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    FALLBACK_HOVER = "FALLBACK_HOVER"
    LANDING = "LANDING"
    SAFE_STOPPED = "SAFE_STOPPED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class StateReferenceFrame:
    run_id: str
    sequence: int
    source_stamp_ns: int
    receive_monotonic_ns: int
    valid_until_ns: int
    armed: bool
    state_valid: bool
    reference_valid: bool
    values: tuple[float, ...]

    def pack(self) -> bytes:
        if len(self.values) != 24 or not all(math.isfinite(value) for value in self.values):
            raise ValueError("invalid_state_reference_values")
        flags = (
            (FLAG_ARMED if self.armed else 0)
            | (FLAG_STATE_VALID if self.state_valid else 0)
            | (FLAG_REFERENCE_VALID if self.reference_valid else 0)
        )
        return HEADER.pack(
            STATE_REFERENCE_MAGIC,
            PROTOCOL_VERSION,
            flags,
            self.sequence,
            0,
            self.source_stamp_ns,
            self.receive_monotonic_ns,
            self.valid_until_ns,
            _encode_run_id(self.run_id),
        ) + STATE_REFERENCE_VALUES.pack(*self.values)

    @classmethod
    def unpack(cls, payload: bytes) -> "StateReferenceFrame":
        if len(payload) != HEADER.size + STATE_REFERENCE_VALUES.size:
            raise ValueError("invalid_state_reference_size")
        header = HEADER.unpack_from(payload)
        _validate_header(header, STATE_REFERENCE_MAGIC)
        flags = header[2]
        return cls(
            run_id=_decode_run_id(header[8]),
            sequence=header[3],
            source_stamp_ns=header[5],
            receive_monotonic_ns=header[6],
            valid_until_ns=header[7],
            armed=bool(flags & FLAG_ARMED),
            state_valid=bool(flags & FLAG_STATE_VALID),
            reference_valid=bool(flags & FLAG_REFERENCE_VALID),
            values=STATE_REFERENCE_VALUES.unpack_from(payload, HEADER.size),
        )


@dataclass(frozen=True)
class CommandFrame:
    run_id: str
    sequence: int
    state_sequence: int
    source_stamp_ns: int
    produced_monotonic_ns: int
    valid_until_ns: int
    q_enu_from_flu_des_xyzw: tuple[float, float, float, float]
    collective_thrust_n: float
    saturation_mask: int = 0
    controller_status: int = 1
    output_valid: bool = True

    def pack(self) -> bytes:
        values = (*self.q_enu_from_flu_des_xyzw, self.collective_thrust_n)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("non_finite_command")
        flags = FLAG_OUTPUT_VALID if self.output_valid else 0
        return HEADER.pack(
            COMMAND_MAGIC,
            PROTOCOL_VERSION,
            flags,
            self.sequence,
            self.state_sequence,
            self.source_stamp_ns,
            self.produced_monotonic_ns,
            self.valid_until_ns,
            _encode_run_id(self.run_id),
        ) + COMMAND_VALUES.pack(*values, self.saturation_mask, self.controller_status)

    @classmethod
    def unpack(cls, payload: bytes) -> "CommandFrame":
        if len(payload) != HEADER.size + COMMAND_VALUES.size:
            raise ValueError("invalid_command_size")
        header = HEADER.unpack_from(payload)
        _validate_header(header, COMMAND_MAGIC)
        values = COMMAND_VALUES.unpack_from(payload, HEADER.size)
        return cls(
            run_id=_decode_run_id(header[8]),
            sequence=header[3],
            state_sequence=header[4],
            source_stamp_ns=header[5],
            produced_monotonic_ns=header[6],
            valid_until_ns=header[7],
            q_enu_from_flu_des_xyzw=values[:4],
            collective_thrust_n=values[4],
            saturation_mask=values[5],
            controller_status=values[6],
            output_valid=bool(header[2] & FLAG_OUTPUT_VALID),
        )


@dataclass(frozen=True)
class CommandDecision:
    accepted: bool
    reason_code: str
    state: ControlState
    command_age_ms: float | None = None


class ControlOwnerArbiter:
    """Pure state machine used by the ROS adapter and unit tests."""

    def __init__(
        self,
        run_id: str,
        *,
        deadline_ms: float = 10.0,
        stale_ms: float = 50.0,
        escalation_ms: float = 100.0,
        consecutive_misses: int = 3,
    ) -> None:
        _encode_run_id(run_id)
        self.run_id = run_id
        self.deadline_ns = round(deadline_ms * 1e6)
        self.stale_ns = round(stale_ms * 1e6)
        self.escalation_ns = round(escalation_ms * 1e6)
        self.consecutive_misses_limit = consecutive_misses
        self.state = ControlState.DISABLED
        self.last_command_sequence = -1
        self.consecutive_deadline_misses = 0
        self.fallback_started_ns: int | None = None

    def enable_shadow(self) -> None:
        if self.state not in {ControlState.DISABLED, ControlState.SAFE_STOPPED}:
            raise ValueError("shadow_transition_rejected")
        self.state = ControlState.SHADOW
        self.last_command_sequence = -1
        self.consecutive_deadline_misses = 0
        self.fallback_started_ns = None

    def mark_ready(self) -> None:
        if self.state != ControlState.SHADOW:
            raise ValueError("ready_requires_shadow")
        self.state = ControlState.READY

    def activate(self, *, airborne: bool) -> None:
        if self.state != ControlState.READY:
            raise ValueError("active_requires_ready")
        if airborne:
            raise ValueError("airborne_backend_switch_forbidden")
        self.state = ControlState.ACTIVE

    def observe(self, command: CommandFrame, *, now_ns: int, latest_state_sequence: int) -> CommandDecision:
        reason = self._validate(command, now_ns=now_ns, latest_state_sequence=latest_state_sequence)
        if reason is not None:
            if self.state == ControlState.ACTIVE:
                self._fallback(now_ns)
            return CommandDecision(False, reason, self.state, self._age_ms(command, now_ns))

        # source_stamp_ns is echoed from this adapter's monotonic clock. The
        # MWORKS produced timestamp is a different clock domain and is only
        # diagnostic unless clock synchronization evidence exists.
        latency_ns = now_ns - command.source_stamp_ns
        if latency_ns > self.deadline_ns:
            self.consecutive_deadline_misses += 1
        else:
            self.consecutive_deadline_misses = 0
        self.last_command_sequence = command.sequence

        if (
            self.state == ControlState.ACTIVE
            and self.consecutive_deadline_misses >= self.consecutive_misses_limit
        ):
            self._fallback(now_ns)
            return CommandDecision(False, "consecutive_deadline_miss", self.state, self._age_ms(command, now_ns))
        return CommandDecision(True, "command_accepted", self.state, self._age_ms(command, now_ns))

    def tick(self, *, now_ns: int) -> ControlState:
        if (
            self.state == ControlState.FALLBACK_HOVER
            and self.fallback_started_ns is not None
            and now_ns - self.fallback_started_ns >= self.escalation_ns
        ):
            self.state = ControlState.DEGRADED
        return self.state

    def observe_timeout(self, *, now_ns: int, last_command_receive_ns: int | None) -> ControlState:
        if (
            self.state == ControlState.ACTIVE
            and (last_command_receive_ns is None or now_ns - last_command_receive_ns > self.stale_ns)
        ):
            self._fallback(now_ns)
        return self.state

    def begin_landing(self) -> None:
        if self.state not in {ControlState.ACTIVE, ControlState.FALLBACK_HOVER, ControlState.DEGRADED}:
            raise ValueError("landing_transition_rejected")
        self.state = ControlState.LANDING

    def safe_stop(self) -> None:
        self.state = ControlState.SAFE_STOPPED

    def fail(self) -> None:
        self.state = ControlState.FAILED

    def _fallback(self, now_ns: int) -> None:
        self.state = ControlState.FALLBACK_HOVER
        if self.fallback_started_ns is None:
            self.fallback_started_ns = now_ns

    def _validate(self, command: CommandFrame, *, now_ns: int, latest_state_sequence: int) -> str | None:
        if command.run_id != self.run_id:
            return "run_id_mismatch"
        if command.sequence <= self.last_command_sequence:
            return "sequence_regression"
        # RT1 is an asynchronous request/response pipeline. A valid command
        # normally references an earlier state than the newest frame already
        # sent by the adapter. Sequence monotonicity prevents replay and the
        # validity/age checks below reject commands that are too old.
        if command.state_sequence > latest_state_sequence:
            return "state_sequence_ahead"
        if not command.output_valid or command.controller_status != 1:
            return "controller_output_invalid"
        values = (*command.q_enu_from_flu_des_xyzw, command.collective_thrust_n)
        if not all(math.isfinite(value) for value in values):
            return "non_finite_output"
        norm = math.sqrt(sum(value * value for value in command.q_enu_from_flu_des_xyzw))
        if abs(norm - 1.0) > 1e-6:
            return "quaternion_not_normalized"
        if command.collective_thrust_n <= 0.0:
            return "command_out_of_bounds"
        if now_ns > command.valid_until_ns or now_ns - command.source_stamp_ns > self.stale_ns:
            return "output_stale"
        return None

    @staticmethod
    def _age_ms(command: CommandFrame, now_ns: int) -> float:
        return (now_ns - command.source_stamp_ns) / 1e6


def _encode_run_id(run_id: str) -> bytes:
    encoded = run_id.encode("ascii")
    if not encoded or len(encoded) >= RUN_ID_SIZE or b"\0" in encoded:
        raise ValueError("invalid_run_id")
    return encoded.ljust(RUN_ID_SIZE, b"\0")


def _decode_run_id(value: bytes) -> str:
    try:
        return value.split(b"\0", 1)[0].decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("invalid_run_id") from exc


def _validate_header(header: tuple[object, ...], magic: int) -> None:
    if header[0] != magic:
        raise ValueError("invalid_magic")
    if header[1] != PROTOCOL_VERSION:
        raise ValueError("unsupported_protocol_version")
    _decode_run_id(header[8])
