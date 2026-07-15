#!/usr/bin/env python3
"""Legacy durable agent runtime tests are retired in single-thread mode."""

from __future__ import annotations

import pytest


pytest.skip(
    "Retired durable agent runtime is not part of current single-thread MoSim workflow.",
    allow_module_level=True,
)
