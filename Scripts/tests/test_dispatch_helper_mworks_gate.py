#!/usr/bin/env python3
"""Legacy MWORKS dispatch helper tests are retired in task-local mode."""

from __future__ import annotations

import pytest


pytest.skip(
    "Retired multi-thread dispatch helper is not part of current task-local MoSim workflow.",
    allow_module_level=True,
)
