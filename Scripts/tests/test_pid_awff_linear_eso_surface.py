"""Focused static checks for the pid_awff_linear_eso source surface."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Scripts/mworks"))

from validate_pid_awff_linear_eso_surface import validate  # noqa: E402


class PidAwffLinearEsoSurfaceTest(unittest.TestCase):
    def test_surface_is_complete(self) -> None:
        result = validate()
        self.assertEqual(result["status"], "passed", result["errors"])

    def test_baseline_is_not_replaced_by_new_core(self) -> None:
        result = validate()
        self.assertTrue(result["checks"]["baseline_class_preserved"])


if __name__ == "__main__":
    unittest.main()
