"""Pure fixed-size transforms shared by the P7 FTC runtime and tests."""

from __future__ import annotations


def wrench_from_motors(motor: list[float]) -> tuple[float, float, float, float]:
    if len(motor) != 4:
        raise ValueError("exactly four motor commands are required")
    m0, m1, m2, m3 = motor
    return (
        m0 + m1 + m2 + m3,
        0.5 * (-m0 + m1 + m2 - m3),
        0.5 * (m0 + m1 - m2 - m3),
        m0 - m1 + m2 - m3,
    )
