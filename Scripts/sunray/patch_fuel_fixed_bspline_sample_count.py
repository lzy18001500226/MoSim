#!/usr/bin/env python3
"""Keep FUEL B-spline point count consistent with seg_num."""
from __future__ import annotations
import argparse
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("fuel_source_root", type=Path)
    path = ap.parse_args().fuel_source_root.resolve() / "plan_manage/src/planner_manager.cpp"
    text = path.read_text(encoding="utf-8")
    old = "  for (double ts = 0.0; ts <= duration + 1e-4; ts += dt)\n    points.push_back(init_traj.evaluate(ts, 0));\n"
    new = "  for (int sample_idx = 0; sample_idx <= seg_num; ++sample_idx) {\n    const double sample_t = duration * double(sample_idx) / double(seg_num);\n    points.push_back(init_traj.evaluate(sample_t, 0));\n  }\n"
    if new in text:
        print("FUEL fixed B-spline sample-count patch already applied")
        return 0
    if text.count(old) != 1:
        raise SystemExit(f"{path}: expected exactly one variable-step sample loop")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print("Applied FUEL fixed B-spline sample-count patch")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
