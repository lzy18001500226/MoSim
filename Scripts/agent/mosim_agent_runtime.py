#!/usr/bin/env python3
"""Compatibility entrypoint for the CoAgent runtime.

Core implementation lives in `CoAgent/runtime/mosim_agent_runtime.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime.mosim_agent_runtime import *  # noqa: F401,F403


if __name__ == "__main__":
    raise SystemExit(main())
