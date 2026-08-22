# -*- coding: utf-8 -*-
"""绘制阶跃响应时域指标图（超调量 / 调节时间 / 稳态误差）。

数据源: Results/control_platform/controller_pair_seven_scenario_repaired_current_20260817
        {official_pid,px4ctrl}/step_response/raw/result.csv + metrics/METRICS.json

输出:   Docs/报告/figures/第11章/阶跃响应指标/
        - step_response_annotated.png   带指标标注的响应曲线（答辩主图）
        - step_response_metrics_bar.png 双控制器三指标对比条形图
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "Results/control_platform/controller_pair_seven_scenario_repaired_current_20260817"
OUT = ROOT / "Docs/报告/figures/第11章/阶跃响应指标"
OUT.mkdir(parents=True, exist_ok=True)

CTRLS = [
    ("official_pid", "官方 PID 基线", "#1C7293"),
    ("px4ctrl", "自研 px4ctrl", "#B85042"),
]
STEP_T = 15.0          # 阶跃施加时刻 (s)
BAND = 0.05            # ±5% 调节时间带
WIN = (13.0, 30.0)     # 绘图时间窗


def load(cid: str):
    df = pd.read_csv(RUN / cid / "step_response/raw/result.csv")
    met = json.loads((RUN / cid / "step_response/metrics/METRICS.json").read_text(encoding="utf-8"))
    return df, met


def plot_annotated() -> Path:
    """x 通道阶跃响应曲线，标注 σ% / ts / ess。"""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)

    for ax, (cid, label, color) in zip(axes, CTRLS):
        df, met = load(cid)
        m = (df.time >= WIN[0]) & (df.time <= WIN[1])
        t, x, xr = df.time[m].values, df.x[m].values, df.x_ref[m].values
        final = 1.0  # 阶跃终值

        # ±5% 调节带
        ax.axhspan(final * (1 - BAND), final * (1 + BAND), color="#97BC62", alpha=0.22,
                   label=f"±{int(BAND*100)}% 调节带")
        ax.plot(t, xr, color="#36454F", lw=1.6, ls="--", label="参考指令 $x_{ref}$")
        ax.plot(t, x, color=color, lw=2.4, label=f"实际响应 $x$（{label}）")

        # 峰值 → 超调量
        post = t >= STEP_T
        pk = np.argmax(x[post])
        t_pk, x_pk = t[post][pk], x[post][pk]
        sigma = met["overshoot_x_pct"]
        ax.plot([t_pk], [x_pk], "o", color=color, ms=8, mec="white", mew=1.4, zorder=5)
        ax.annotate(f"超调量 $\\sigma$ = {sigma:.2f}%",
                    xy=(t_pk, x_pk), xytext=(t_pk + 2.6, x_pk + 0.16),
                    fontsize=11, color=color, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.4))
        ax.annotate("", xy=(t_pk, x_pk), xytext=(t_pk, final),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.2, alpha=0.8))

        # 调节时间
        ts = met["settling_time_s"]
        if ts and np.isfinite(ts):
            t_set = STEP_T + ts
            ax.axvline(t_set, color="#6D2E46", lw=1.5, ls=":")
            ax.annotate(f"调节时间 $t_s$ = {ts:.2f} s",
                        xy=(t_set, 0.30), xytext=(t_set + 0.35, 0.24),
                        fontsize=11, color="#6D2E46", fontweight="bold")
            ax.annotate("", xy=(STEP_T, 0.14), xytext=(t_set, 0.14),
                        arrowprops=dict(arrowstyle="<->", color="#6D2E46", lw=1.2))

        # 稳态误差
        ess = met["steady_state_error_m"]
        ax.annotate(f"稳态误差 $e_{{ss}}$ = {ess*1000:.2f} mm",
                    xy=(WIN[1] - 0.4, final), xytext=(WIN[1] - 0.4, final - 0.30),
                    fontsize=11, color="#36454F", ha="right", fontweight="bold")

        ax.axvline(STEP_T, color="#999999", lw=1.0, ls="-.")
        ax.text(STEP_T - 0.2, 1.42, "阶跃施加\nt = 15 s", fontsize=9.5,
                color="#666666", ha="right", va="top")

        ax.set_xlim(*WIN)
        ax.set_ylim(-0.12, 1.52)
        ax.set_xlabel("时间 t / s", fontsize=12)
        ax.set_title(label, fontsize=14, fontweight="bold", color=color, pad=10)
        ax.grid(axis="y", color="#DDDDDD", lw=0.8)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.legend(loc="lower right", fontsize=9.5, framealpha=0.92)

    axes[0].set_ylabel("X 向位置 / m", fontsize=12)
    fig.suptitle("阶跃响应时域性能指标对比（step_response 场景，1 m 水平阶跃）",
                 fontsize=15, fontweight="bold", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    p = OUT / "step_response_annotated.png"
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def plot_bars() -> Path:
    """三项指标 + RMSE 的双控制器条形对比。"""
    data = {cid: load(cid)[1] for cid, _, _ in CTRLS}
    items = [
        ("超调量 $\\sigma$（X 通道）/ %", lambda m: m["overshoot_x_pct"], "{:.2f}"),
        ("超调量 $\\sigma$（三轴最大）/ %", lambda m: m["overshoot_max_pct"], "{:.2f}"),
        ("调节时间 $t_s$ / s", lambda m: m["settling_time_s"], "{:.2f}"),
        ("稳态误差 $e_{ss}$ / mm", lambda m: m["steady_state_error_m"] * 1000, "{:.2f}"),
        ("跟踪精度 RMSE / m", lambda m: m["position_rmse_m"], "{:.4f}"),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(17, 4.4))
    labels = [lb for _, lb, _ in CTRLS]
    colors = [c for _, _, c in CTRLS]

    for ax, (title, getter, fmt) in zip(axes, items):
        vals = [getter(data[cid]) for cid, _, _ in CTRLS]
        bars = ax.bar(labels, vals, color=colors, width=0.55)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v * 1.02, fmt.format(v),
                    ha="center", va="bottom", fontsize=12, fontweight="bold")
        ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
        ax.set_ylim(0, max(vals) * 1.28)
        ax.grid(axis="y", color="#E5E5E5", lw=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="x", labelsize=11)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0, labelsize=9, colors="#888888")

    fig.suptitle("官方 PID 基线 vs 自研 px4ctrl —— 阶跃响应五项指标",
                 fontsize=15, fontweight="bold", y=1.0)
    fig.text(0.5, -0.035,
             "注：超调量分 X 通道与三轴最大值两列并列给出——px4ctrl 在 X 通道显著优于基线（8.92% vs 23.99%），"
             "但 Y 通道两者接近（22.95% vs 24.14%），单看一个通道会得出片面结论。",
             ha="center", fontsize=10, color="#666666")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    p = OUT / "step_response_metrics_bar.png"
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


if __name__ == "__main__":
    for p in (plot_annotated(), plot_bars()):
        print(f"[OK] {p}")
