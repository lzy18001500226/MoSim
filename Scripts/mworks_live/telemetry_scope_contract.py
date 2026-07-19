#!/usr/bin/env python3
"""Fixed-size contract for ROS1 telemetry displayed by MWORKS Scope."""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass


PROTOCOL_VERSION = 1
TELEMETRY_MAGIC = 0x4D545331  # MTS1
ACK_MAGIC = 0x4D544131  # MTA1
RUN_ID_SIZE = 64

HEADER = struct.Struct(f"<IHHIIQQQ{RUN_ID_SIZE}s")
TELEMETRY_VALUES = struct.Struct("<32d")
ACK_VALUES = struct.Struct("<Q")

FLAG_ARMED = 1 << 0
FLAG_STATE_VALID = 1 << 1
FLAG_REFERENCE_VALID = 1 << 2
FLAG_COMMAND_VALID = 1 << 3


@dataclass(frozen=True)
class TelemetryScopeFrame:
    run_id: str
    sequence: int
    source_stamp_ns: int
    produced_monotonic_ns: int
    valid_until_ns: int
    armed: bool
    state_valid: bool
    reference_valid: bool
    command_valid: bool
    values: tuple[float, ...]

    def pack(self) -> bytes:
        if len(self.values) != 32 or not all(math.isfinite(value) for value in self.values):
            raise ValueError("invalid_telemetry_scope_values")
        flags = (
            (FLAG_ARMED if self.armed else 0)
            | (FLAG_STATE_VALID if self.state_valid else 0)
            | (FLAG_REFERENCE_VALID if self.reference_valid else 0)
            | (FLAG_COMMAND_VALID if self.command_valid else 0)
        )
        return HEADER.pack(
            TELEMETRY_MAGIC,
            PROTOCOL_VERSION,
            flags,
            self.sequence,
            0,
            self.source_stamp_ns,
            self.produced_monotonic_ns,
            self.valid_until_ns,
            _encode_run_id(self.run_id),
        ) + TELEMETRY_VALUES.pack(*self.values)

    @classmethod
    def unpack(cls, payload: bytes) -> "TelemetryScopeFrame":
        if len(payload) != HEADER.size + TELEMETRY_VALUES.size:
            raise ValueError("invalid_telemetry_scope_size")
        header = HEADER.unpack_from(payload)
        _validate_header(header, TELEMETRY_MAGIC)
        flags = header[2]
        return cls(
            run_id=_decode_run_id(header[8]),
            sequence=header[3],
            source_stamp_ns=header[5],
            produced_monotonic_ns=header[6],
            valid_until_ns=header[7],
            armed=bool(flags & FLAG_ARMED),
            state_valid=bool(flags & FLAG_STATE_VALID),
            reference_valid=bool(flags & FLAG_REFERENCE_VALID),
            command_valid=bool(flags & FLAG_COMMAND_VALID),
            values=TELEMETRY_VALUES.unpack_from(payload, HEADER.size),
        )


@dataclass(frozen=True)
class TelemetryScopeAck:
    run_id: str
    sequence: int
    related_sequence: int
    receiver_monotonic_ns: int
    echoed_sender_monotonic_ns: int

    def pack(self) -> bytes:
        return HEADER.pack(
            ACK_MAGIC,
            PROTOCOL_VERSION,
            0,
            self.sequence,
            self.related_sequence,
            self.receiver_monotonic_ns,
            self.receiver_monotonic_ns,
            0,
            _encode_run_id(self.run_id),
        ) + ACK_VALUES.pack(self.echoed_sender_monotonic_ns)

    @classmethod
    def unpack(cls, payload: bytes) -> "TelemetryScopeAck":
        if len(payload) != HEADER.size + ACK_VALUES.size:
            raise ValueError("invalid_telemetry_scope_ack_size")
        header = HEADER.unpack_from(payload)
        _validate_header(header, ACK_MAGIC)
        return cls(
            run_id=_decode_run_id(header[8]),
            sequence=header[3],
            related_sequence=header[4],
            receiver_monotonic_ns=header[5],
            echoed_sender_monotonic_ns=ACK_VALUES.unpack_from(payload, HEADER.size)[0],
        )


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
