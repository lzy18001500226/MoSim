"""Ensure the ``webeval`` and ``fara`` source trees are importable when
running pytest from the repo root without an editable install.

``webeval.benchmarks.webtailbench.webtailbench`` imports
``FARA_ACTION_DEFINITIONS`` from the top-level ``fara`` package, so we
prepend both source trees to ``sys.path``.
"""

from __future__ import annotations

import sys
from pathlib import Path

_WEBEVAL_SRC = Path(__file__).resolve().parent.parent / "src"
_FARA_SRC = Path(__file__).resolve().parent.parent.parent / "src"

for _p in (_WEBEVAL_SRC, _FARA_SRC):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
