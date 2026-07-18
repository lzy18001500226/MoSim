#!/usr/bin/env python3
"""Generate report-ready figures from current non-frontend authority JSON."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "control_platform" / "non_frontend_evidence_index_20260718" / "figures"
CONTROLLER = ROOT / "Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json"
AB = ROOT / "Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json"
LEARNING = ROOT / "Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json"

COLORS = {"accepted": "#287a4b", "executed_blocked": "#d9871c", "not_run": "#8a9099"}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> list[str]:
    paths = []
    for suffix in ("png", "svg"):
        path = output_dir / f"{stem}.{suffix}"
        fig.savefig(path, dpi=220, bbox_inches="tight")
        if suffix == "svg":
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"[ \t]+(?=\r?\n)", "", text).replace("\r\n", "\n")
            path.write_text(text, encoding="utf-8", newline="\n")
        paths.append(display_path(path))
    plt.close(fig)
    return paths


def controller_status_figure(data: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    counts = data["counts"]
    labels = ["Accepted", "Executed blocked", "Not run"]
    keys = ["accepted", "executed_blocked", "not_run"]
    values = [int(counts[key]) for key in keys]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    bars = ax.bar(labels, values, color=[COLORS[key] for key in keys], width=0.62)
    ax.set_ylabel("Controller-contract rows")
    ax.set_title("Controller-family final evidence status (67 rows)")
    ax.set_ylim(0, max(values) * 1.22)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.5, str(value), ha="center", va="bottom", fontweight="bold")
    return {"figure_id": "controller_status_counts", "files": save_figure(fig, output_dir, "controller_status_counts"), "values": dict(zip(keys, values)), "claim_ceiling": "Row visibility and status distribution only; not a claim that blocked/not-run controllers passed."}


def ab_figure(data: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    scenario_order = ["hover", "step", "figure8", "spiral", "wind", "parameter_mismatch", "motor_efficiency_fault"]
    profiles = ["official_pid", "gain_scheduled_pid"]
    lookup = {(row["profile"], row["scenario"]): row for row in data["rows"]}
    x = np.arange(len(scenario_order))
    width = 0.36
    fig, ax = plt.subplots(figsize=(11.5, 5.4))
    plotted: dict[str, list[float | None]] = {}
    for index, profile in enumerate(profiles):
        values: list[float] = []
        statuses: list[str] = []
        for scenario in scenario_order:
            row = lookup[(profile, scenario)]
            statuses.append(str(row["status"]))
            values.append(float(row["primary_rmse_m"]) if row["status"] != "not_run" and row.get("primary_rmse_m") is not None else np.nan)
        positions = x + (index - 0.5) * width
        bars = ax.bar(positions, values, width, label=profile.replace("_", " "), color="#36648b" if index == 0 else "#6f4c8b")
        for bar, status, value in zip(bars, statuses, values):
            if status == "executed_blocked":
                bar.set_hatch("///")
                bar.set_edgecolor("#d9871c")
                bar.set_linewidth(1.4)
            if not np.isnan(value):
                ax.text(bar.get_x() + bar.get_width() / 2, value + 0.004, f"{value:.3f}", ha="center", va="bottom", fontsize=7, rotation=90)
        plotted[profile] = [None if np.isnan(value) else value for value in values]
    for index, scenario in enumerate(scenario_order):
        if scenario == "motor_efficiency_fault":
            ax.text(index, 0.012, "not run\n(infrastructure blocker)", ha="center", va="bottom", fontsize=8, color=COLORS["not_run"])
    ax.set_xticks(x, ["Hover", "Step", "Figure 8", "Spiral", "Wind", "Parameter\nmismatch", "Motor\nfault"])
    ax.set_ylabel("Primary RMSE (m)")
    ax.set_title("Official PID vs gain-scheduled PID: observed seven-scenario A/B")
    ax.legend(frameon=False)
    fig.text(0.5, 0.01, "Hatched bars: executed-blocked; motor-fault rows: not run", ha="center", fontsize=9, color="#555555")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    return {"figure_id": "final_pid_ab_primary_rmse", "files": save_figure(fig, output_dir, "final_pid_ab_primary_rmse"), "values": plotted, "claim_ceiling": "Hatched bars are executed-blocked; motor-fault values are omitted because both rows are not-run. No general superiority claim."}


def learning_figure(data: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    routes = ["trained_neural_residual", "rl_gain_scheduler"]
    conditions = ["nominal", "wind", "parameter_mismatch"]
    x = np.arange(len(conditions))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    values_by_route: dict[str, list[float]] = {}
    for index, route in enumerate(routes):
        changes = data["routes"][route]["xyz_rmse_change_vs_cascade_fraction"]
        values = [100.0 * float(changes[condition]) for condition in conditions]
        values_by_route[route] = values
        ax.bar(x + (index - 0.5) * width, values, width, label=route.replace("_", " "), color="#2a7f9e" if index == 0 else "#a35d2d")
    ax.axhline(0.0, color="#333333", linewidth=1)
    ax.set_xticks(x, ["Nominal", "Wind", "Parameter mismatch"])
    ax.set_ylabel("XYZ RMSE change vs Cascade (%)")
    ax.set_title("Learning-control routes: observed change relative to Cascade")
    fig.text(0.5, 0.01, "Positive values indicate lower RMSE than Cascade", ha="center", fontsize=9, color="#555555")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    return {"figure_id": "learning_control_rmse_change", "files": save_figure(fig, output_dir, "learning_control_rmse_change"), "values_percent": values_by_route, "claim_ceiling": "Positive means lower RMSE than Cascade in that condition. Both routes remain selectable=false because strict matrix acceptance is blocked."}


def build(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    controller = read_json(CONTROLLER)
    ab = read_json(AB)
    learning = read_json(LEARNING)
    figures = [controller_status_figure(controller, output_dir), ab_figure(ab, output_dir), learning_figure(learning, output_dir)]
    return {
        "schema": "mosim.non_frontend_report_figure_manifest.v1",
        "date": "2026-07-18",
        "status": "report_figures_generated_with_claim_boundaries",
        "sources": [CONTROLLER.relative_to(ROOT).as_posix(), AB.relative_to(ROOT).as_posix(), LEARNING.relative_to(ROOT).as_posix()],
        "figures": figures,
        "claim_boundary": "Figures preserve authority status and are report assets, not independent acceptance evidence.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()
    output_dir = ROOT / args.output_dir
    manifest = build(output_dir)
    path = output_dir / "REPORT_FIGURE_MANIFEST.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"ok": True, "manifest": path.relative_to(ROOT).as_posix(), "figure_count": len(manifest["figures"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
