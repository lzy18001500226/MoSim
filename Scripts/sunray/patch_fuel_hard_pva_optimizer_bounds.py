#!/usr/bin/env python3
"""Add opt-in hard endpoint bounds to FUEL's B-spline optimizer."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, path: Path) -> str:
    if new in text:
        return text
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected one patch anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    root = parser.parse_args().fuel_source_root.resolve()
    header = root / "bspline_opt/include/bspline_opt/bspline_optimizer.h"
    source = root / "bspline_opt/src/bspline_optimizer.cpp"

    h = header.read_text(encoding="utf-8")
    h = replace_once(
        h,
        "  void setBoundaryStates(const vector<Eigen::Vector3d>& start, const vector<Eigen::Vector3d>& end);\n",
        "  void setBoundaryStates(const vector<Eigen::Vector3d>& start, const vector<Eigen::Vector3d>& end);\n"
        "  void setHardBoundaryBounds(bool start, bool end);\n",
        header,
    )
    h = replace_once(
        h,
        "  int variable_num_;  // optimization variables\n",
        "  int variable_num_;  // optimization variables\n"
        "  bool hard_start_boundary_{false};\n"
        "  bool hard_end_boundary_{false};\n",
        header,
    )
    header.write_text(h, encoding="utf-8")

    s = source.read_text(encoding="utf-8")
    s = replace_once(
        s,
        "void BsplineOptimizer::setTimeLowerBound(const double& lb) {\n",
        "void BsplineOptimizer::setHardBoundaryBounds(bool start, bool end) {\n"
        "  hard_start_boundary_ = start;\n"
        "  hard_end_boundary_ = end;\n"
        "}\n\n"
        "void BsplineOptimizer::setTimeLowerBound(const double& lb) {\n",
        source,
    )
    s = replace_once(
        s,
        "    if (optimize_time_) {\n"
        "      lb[variable_num_ - 1] = 0.0;\n"
        "      ub[variable_num_ - 1] = 5.0;\n"
        "    }\n"
        "    opt.set_lower_bounds(lb);\n",
        "    if (hard_start_boundary_) {\n"
        "      for (int i = 0; i < min(3, point_num_); ++i)\n"
        "        for (int j = 0; j < dim_; ++j) lb[dim_ * i + j] = ub[dim_ * i + j] = q[dim_ * i + j];\n"
        "    }\n"
        "    if (hard_end_boundary_) {\n"
        "      for (int i = max(0, point_num_ - 3); i < point_num_; ++i)\n"
        "        for (int j = 0; j < dim_; ++j) lb[dim_ * i + j] = ub[dim_ * i + j] = q[dim_ * i + j];\n"
        "    }\n"
        "    if (optimize_time_) {\n"
        "      lb[variable_num_ - 1] = 0.0;\n"
        "      ub[variable_num_ - 1] = 5.0;\n"
        "    }\n"
        "    opt.set_lower_bounds(lb);\n",
        source,
    )
    s = replace_once(
        s,
        "  start_state_.clear();\n  time_lb_ = -1;\n",
        "  start_state_.clear();\n"
        "  hard_start_boundary_ = false;\n"
        "  hard_end_boundary_ = false;\n"
        "  time_lb_ = -1;\n",
        source,
    )
    source.write_text(s, encoding="utf-8")
    print("Applied opt-in hard P/V/A optimizer boundary bounds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
