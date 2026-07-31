#!/usr/bin/env julia
# awff 负性能样本详图 driver —— TyPlot 原生绘图（Syslab 产物）
#
# 为什么单独跑：
#   正文 10.6「G3跑通控制器完整轨迹图集」以 awff 作为"跑通但未达标"的负性能样本
#   列出（终端位置误差 48.8183 m，门限 5 m）。该节其余控制器均为 status=pass，
#   主脚本清单唯一来自 G3 status=="pass" 且带 @assert !("awff" in passed)，
#   因此 awff 必须走主脚本的负样本模式，而不是塞进达标清单。
#
# 为什么不复用归档图：
#   Docs/报告/图/归档/awff负性能样本_20260731/ 下 4 张 SVG 是 Python 产物
#   （mosim.plot_results.v1，见该目录 README 第 29-30 行），按图件口径不能作为
#   Syslab 绘图证据。本 driver 用 TyPlot 重出，规格与其余控制器一致（7 张 @600）。
#
# 输出：Docs/报告/figures/第10章/awff/ 下 7 张 PNG + figure_manifest.typlot.json
#   manifest 打 negative_sample=true 并保留 failure_class，防止被读成达标控制器。
#
# 数据源：Results/control_platform/phase2_full_48_climbpath/awff/raw/climbpath50s.csv
#   25001 点，dt=0.002 s，50 s，与本批主流 25 条采样一致。

DETAIL_NEGATIVE_SAMPLE_IDS = ["awff"]

include(joinpath(@__DIR__, "plot_28_passed_detail_typlot.jl"))
