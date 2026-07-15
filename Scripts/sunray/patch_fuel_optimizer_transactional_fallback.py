#!/usr/bin/env python3
"""Make FUEL's NLopt-to-Eigen handoff transactional on solver failure.

The upstream optimizer reads best_variable_ after NLopt returns.  If NLopt
throws or performs no cost callback, that vector can be empty or stale and is
then indexed past its valid size.  Preserve the initial decision vector and
only commit a solver result with the expected dimension and finite values.
"""
from __future__ import annotations

import argparse
from pathlib import Path


OLD = """  vector<double> q(variable_num_);\n  // Variables for control points\n"""
OLD_INCLUDE = '#include "bspline_opt/bspline_optimizer.h"\n'
NEW_INCLUDE = '#include "bspline_opt/bspline_optimizer.h"\n#include <algorithm>\n#include <cmath>\n'
NEW = """  std::vector<double> q(variable_num_);\n  // Transaction fallback: a failed/empty NLopt solve must not expose stale\n  // best_variable_ memory to the Eigen control-point matrix below.\n  best_variable_.clear();\n  // Variables for control points\n"""

OLD_TRY = """  auto t1 = ros::Time::now();\n  try {\n    double final_cost;\n    nlopt::result result = opt.optimize(q, final_cost);\n  } catch (std::exception& e) {\n    cout << e.what() << endl;\n  }\n  for (int i = 0; i < point_num_; ++i)\n    for (int j = 0; j < dim_; ++j)\n      control_points_(i, j) = best_variable_[dim_ * i + j];\n  if (optimize_time_) knot_span_ = best_variable_[variable_num_ - 1];\n"""
NEW_TRY = """  auto t1 = ros::Time::now();\n  best_variable_ = q;\n  bool solver_returned = false;\n  try {\n    double final_cost = 0.0;\n    nlopt::result result = opt.optimize(q, final_cost);\n    solver_returned = true;\n    ROS_INFO(\"[FUEL_OPT] result=%d vars=%zu points=%d dim=%d dt=%.9f\",\n        static_cast<int>(result), q.size(), point_num_, dim_, knot_span_);\n  } catch (std::exception& e) {\n    ROS_ERROR(\"[FUEL_OPT] NLopt exception; retaining initial decision vector: %s\", e.what());\n  }\n  const bool valid_solution = solver_returned &&\n      best_variable_.size() == static_cast<size_t>(variable_num_) &&\n      std::all_of(best_variable_.begin(), best_variable_.end(),\n          [](double value) { return std::isfinite(value); });\n  if (!valid_solution) {\n    ROS_WARN(\"[FUEL_OPT] invalid solver result; retaining initial decision vector\");\n    best_variable_ = q;\n  }\n  for (int i = 0; i < point_num_; ++i)\n    for (int j = 0; j < dim_; ++j)\n      control_points_(i, j) = best_variable_[dim_ * i + j];\n  if (optimize_time_) knot_span_ = best_variable_[variable_num_ - 1];\n"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fuel_source_root", type=Path)
    path = parser.parse_args().fuel_source_root.resolve() / "bspline_opt/src/bspline_optimizer.cpp"
    text = path.read_text(encoding="utf-8")
    if "[FUEL_OPT] invalid solver result" in text:
        print("FUEL optimizer transactional fallback already applied")
        return 0
    if text.count(OLD) != 1:
        raise SystemExit(f"{path}: expected one optimizer decision-vector declaration")
    if text.count(OLD_TRY) != 1:
        raise SystemExit(f"{path}: expected one NLopt commit block")
    if text.count(OLD_INCLUDE) != 1:
        raise SystemExit(f"{path}: expected optimizer header include")
    text = text.replace(OLD_INCLUDE, NEW_INCLUDE, 1)
    text = text.replace(OLD, NEW, 1).replace(OLD_TRY, NEW_TRY, 1)
    path.write_text(text, encoding="utf-8")
    print("Applied FUEL optimizer transactional fallback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
