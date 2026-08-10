#!/usr/bin/env python3
"""Legacy durable agent runtime tests are retired in task-local mode."""

from __future__ import annotations

import pytest


pytest.skip(
    "Retired durable agent runtime is not part of current task-local MoSim workflow.",
    allow_module_level=True,
)
