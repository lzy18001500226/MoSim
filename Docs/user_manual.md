# 用户手册

本文档说明如何检查项目结构、复现官方案例参考轨迹、处理 MWORKS/MCP 导出的仿真结果、生成指标和报告素材。

## 1. 环境要求

必需环境：

```text
Python 3.10+
MWORKS.Sysplorer 2026
MWORKS.Sysblock 2026
MWORKS.Syslab 2026
Codex MCP: syslab, sysplorer, unreal_engine
```

可选环境：

```text
Julia / Syslab Julia runtime
Sysplorer plot_manager / Syslab plotting APIs
```

当前 WSL 自动化优先使用 Python 脚本；当 Syslab/Julia 不可用时，仍可完成 QA、参考轨迹、指标和 SVG 图表生成。

当 Sysplorer / Syslab MCP 状态正常时，交互式模型加载、检查、仿真、曲线查看和三维动画审核必须直接通过 MCP 工具完成。不要用项目脚本封装交互式 MCP 操作。项目脚本只用于批量执行、结果导出、指标汇总和回归自动化。

## 2. 快速检查

在项目根目录运行：

```bash
python3 Scripts/quality/qa_check.py
python3 Scripts/quality/check_reference_outputs.py
```

通过标准：

```text
Required project structure passed
MCP wrapper scripts found
official_example1/2/3 reference checks OK
```

## 3. 官方案例入口

官方模型包：

```text
References/MWORKS/QuadrotorModel/package.mo
```

官方场景配置：

```text
Config/scenarios/official/example1_pid_baseline.yaml  阶梯爬升，50 s
Config/scenarios/official/example2_pid_baseline.yaml  螺旋爬升，50 s
Config/scenarios/official/example3_pid_baseline.yaml  8字形运动，120 s
```

对应模型：

```text
QuadrotorModel.Examples.Example1
QuadrotorModel.Examples.Example2
QuadrotorModel.Examples.Example3
QuadrotorExperiments.Example1ImprovedPID
QuadrotorExperiments.Example2ImprovedPID
QuadrotorExperiments.Example3ImprovedPID
```

项目本地实验模型包：

```text
Models/QuadrotorExperiments/package.mo
```

该包通过 `extends QuadrotorModel.Examples.*` 派生官方模型，只覆盖 `controller3_2.PID*` 参数，不修改官方 `References/MWORKS/QuadrotorModel/package.mo`。

## 4. 参考轨迹与 replay JSON

生成官方参考轨迹和回放 JSON：

```bash
python3 Scripts/results/generate_reference.py --scene all
python3 Scripts/quality/check_reference_outputs.py
```

输出：

```text
Results/official/example1_step/reference_official_example1/raw/reference_official_example1.csv
Results/official/example2_helix/reference_official_example2/raw/reference_official_example2.csv
Results/official/example3_figure8/reference_official_example3/raw/reference_official_example3.csv
Results/official/example1_step/reference_official_example1/replay/reference_official_example1.json
Results/official/example2_helix/reference_official_example2/replay/reference_official_example2.json
Results/official/example3_figure8/reference_official_example3/replay/reference_official_example3.json
```

`Results/{group}/{scene}/{experiment}/replay/*.json` 是从参考轨迹或真实 raw CSV 导出的展示素材输入，不参与控制闭环，也不作为在线仿真证据。正式控制器仿真证据以 MWORKS/Sysplorer 模型检查、仿真日志、raw CSV、metrics JSON/CSV 和 SVG 图表为准。

从真实 MCP raw CSV 生成实际轨迹回放：

```bash
python3 Scripts/results/generate_replay_from_raw.py \
  Results/official/example1_step/official_example1_improved_pid/raw/official_example1_improved_pid.csv \
  Results/official/example1_step/official_example1_improved_pid/replay/official_example1_improved_pid.json \
  --scene-id official_example1_improved_pid \
  --model-name QuadrotorExperiments.Example1ImprovedPID \
  --description 'Example1 MCP 参数搜索型 Improved PID 真实轨迹'
```

正式 replay JSON 文件：

```text
Results/official/example1_step/official_example1_pid_baseline/replay/official_example1_pid_baseline.json
Results/official/example1_step/official_example1_improved_pid/replay/official_example1_improved_pid.json
Results/official/example1_step/official_example1_enhanced_pid/replay/official_example1_enhanced_pid.json
Results/official/example1_step/official_example1_awff_pid/replay/official_example1_awff_pid.json
Results/official/example2_helix/official_example2_pid_baseline/replay/official_example2_pid_baseline.json
Results/official/example2_helix/official_example2_improved_pid/replay/official_example2_improved_pid.json
Results/official/example3_figure8/official_example3_pid_baseline/replay/official_example3_pid_baseline.json
Results/official/example3_figure8/official_example3_improved_pid/replay/official_example3_improved_pid.json
```

如需临时制作浏览器回放素材，可手动执行 `Scripts/results/generate_replay_html.py`。仓库默认流程不再生成或提交 HTML 文件。

## 5. 官方仿真流程

使用 Sysplorer MCP 时按以下顺序执行：

```text
session_manager
→ model_manager load References/MWORKS/QuadrotorModel/package.mo
→ check_model
→ simulate_model
→ result_manager list/read variables
→ native_result / GUI result viewer for manual review
→ export raw CSV
→ calc metrics
→ generate figures/replay
```

变量映射见：

```text
Docs/Index/variable_mapping.md
```

完整官方 baseline 结果应写入：

```text
Results/official/example1_step/official_example1_pid_baseline/raw/official_example1_pid_baseline.csv
Results/official/example2_helix/official_example2_pid_baseline/raw/official_example2_pid_baseline.csv
Results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv
Results/official/example1_step/official_example1_pid_baseline/metrics/official_example1_pid_baseline.json
Results/official/example2_helix/official_example2_pid_baseline/metrics/official_example2_pid_baseline.json
Results/official/example3_figure8/official_example3_pid_baseline/metrics/official_example3_pid_baseline.json
```

`qa_check.py` 会检查这些正式结果的时长，Example1/2 不得短于 50 s，Example3 不得短于 120 s。

`Scripts/mworks/run_sysplorer_mcp_smoke.py` 当前会导出以下标准字段：

```text
time,x,y,z,x_ref,y_ref,z_ref,roll,pitch,yaw,u1,u2,u3,u4
```

其中 `roll/pitch/yaw` 来自 `sensors1_1.AngleMea[1..3]`，`u1-u4` 来自 `controller3_2.y/y1/y2/y3`。这组 `u1-u4` 是控制器原始输出，不是 0-1 归一化电机占空比；因此 `calc_metrics.py` 只在控制命令整体位于 0-1 范围内时计算 `saturation_ratio`，否则将其留空，并记录 `control_command_min/max` 与 `control_command_normalized=false`。

复现完整官方 PID baseline：

```bash
python3 Scripts/mworks/run_sysplorer_mcp_smoke.py \
  --target-time 0,50 \
  --raw-output Results/official/example1_step/official_example1_pid_baseline/raw/official_example1_pid_baseline.csv \
  --metrics-json Results/official/example1_step/official_example1_pid_baseline/metrics/official_example1_pid_baseline.json \
  --metrics-csv Results/official/example1_step/official_example1_pid_baseline/metrics/official_example1_pid_baseline.csv \
  --log-output Results/official/example1_step/official_example1_pid_baseline/logs/sysplorer_example1_pid_baseline_full_20260509.jsonl \
  --scene-id official_example1 \
  --controller-id pid_baseline \
  --evidence-level real_sysplorer_mcp_full_baseline

python3 Scripts/mworks/run_sysplorer_mcp_smoke.py \
  --model-name QuadrotorModel.Examples.Example2 \
  --target-time 0,50 \
  --raw-output Results/official/example2_helix/official_example2_pid_baseline/raw/official_example2_pid_baseline.csv \
  --metrics-json Results/official/example2_helix/official_example2_pid_baseline/metrics/official_example2_pid_baseline.json \
  --metrics-csv Results/official/example2_helix/official_example2_pid_baseline/metrics/official_example2_pid_baseline.csv \
  --log-output Results/official/example2_helix/official_example2_pid_baseline/logs/sysplorer_example2_pid_baseline_full_20260509.jsonl \
  --scene-id official_example2 \
  --controller-id pid_baseline \
  --evidence-level real_sysplorer_mcp_full_baseline

python3 Scripts/mworks/run_sysplorer_mcp_smoke.py \
  --model-name QuadrotorModel.Examples.Example3 \
  --target-time 0,120 \
  --raw-output Results/official/example3_figure8/official_example3_pid_baseline/raw/official_example3_pid_baseline.csv \
  --metrics-json Results/official/example3_figure8/official_example3_pid_baseline/metrics/official_example3_pid_baseline.json \
  --metrics-csv Results/official/example3_figure8/official_example3_pid_baseline/metrics/official_example3_pid_baseline.csv \
  --log-output Results/official/example3_figure8/official_example3_pid_baseline/logs/sysplorer_example3_pid_baseline_full_20260509.jsonl \
  --scene-id official_example3 \
  --controller-id pid_baseline \
  --evidence-level real_sysplorer_mcp_full_baseline
```

复现 MCP 参数搜索型 Improved PID 对比：

```bash
python3 Scripts/mworks/run_sysplorer_mcp_smoke.py \
  --extra-model-file 'C:\Users\HP\Desktop\MoSim\Models\QuadrotorExperiments\package.mo' \
  --model-name QuadrotorExperiments.Example1ImprovedPID \
  --target-time 0,50 \
  --raw-output Results/official/example1_step/official_example1_improved_pid/raw/official_example1_improved_pid.csv \
  --metrics-json Results/official/example1_step/official_example1_improved_pid/metrics/official_example1_improved_pid.json \
  --metrics-csv Results/official/example1_step/official_example1_improved_pid/metrics/official_example1_improved_pid.csv \
  --log-output Results/official/example1_step/official_example1_improved_pid/logs/sysplorer_example1_improved_pid_full_20260509.jsonl \
  --scene-id official_example1 \
  --controller-id improved_pid \
  --evidence-level real_sysplorer_mcp_full_improved_pid

python3 Scripts/mworks/run_sysplorer_mcp_smoke.py \
  --extra-model-file 'C:\Users\HP\Desktop\MoSim\Models\QuadrotorExperiments\package.mo' \
  --model-name QuadrotorExperiments.Example2ImprovedPID \
  --target-time 0,50 \
  --raw-output Results/official/example2_helix/official_example2_improved_pid/raw/official_example2_improved_pid.csv \
  --metrics-json Results/official/example2_helix/official_example2_improved_pid/metrics/official_example2_improved_pid.json \
  --metrics-csv Results/official/example2_helix/official_example2_improved_pid/metrics/official_example2_improved_pid.csv \
  --log-output Results/official/example2_helix/official_example2_improved_pid/logs/sysplorer_example2_improved_pid_full_20260509.jsonl \
  --scene-id official_example2 \
  --controller-id improved_pid \
  --evidence-level real_sysplorer_mcp_full_improved_pid

python3 Scripts/mworks/run_sysplorer_mcp_smoke.py \
  --extra-model-file 'C:\Users\HP\Desktop\MoSim\Models\QuadrotorExperiments\package.mo' \
  --model-name QuadrotorExperiments.Example3ImprovedPID \
  --target-time 0,120 \
  --raw-output Results/official/example3_figure8/official_example3_improved_pid/raw/official_example3_improved_pid.csv \
  --metrics-json Results/official/example3_figure8/official_example3_improved_pid/metrics/official_example3_improved_pid.json \
  --metrics-csv Results/official/example3_figure8/official_example3_improved_pid/metrics/official_example3_improved_pid.csv \
  --log-output Results/official/example3_figure8/official_example3_improved_pid/logs/sysplorer_example3_improved_pid_full_20260509.jsonl \
  --scene-id official_example3 \
  --controller-id improved_pid \
  --evidence-level real_sysplorer_mcp_full_improved_pid
```

默认情况下，`Scripts/mworks/run_sysplorer_mcp_smoke.py` 会保留 Sysplorer GUI/session，避免连续仿真时反复启动。只有需要显式清理时才添加：

```bash
--shutdown-session
```

复现 Improved PID 参数搜索：

```bash
python3 Scripts/mworks/tune_improved_pid_mcp.py --examples 1 3 --timeout-s 900
```

该脚本会生成临时 Modelica 派生包、串行调用真实 Sysplorer MCP 仿真候选参数，并输出：

```text
Results/tuning/pid_search/summary/pid_tuning_summary.csv
Results/tuning/pid_search/summary/pid_tuning_summary.md
```

正式 improved PID 当前采用候选 `pos_kp_165_att_170`，对应 `PID3/PID4.KP=1.65`、`PID5/PID6.KD=1.70`。

## 6. 正式场景复现

仓库已清理历史 0-1 s smoke 数据，当前复现和评审均以 `Config/scenarios/official/` 与 `Config/scenarios/robustness/` 下的正式场景为准。

复现任一正式场景时使用同一入口，直接替换 YAML 路径：

```bash
python3 Scripts/mworks/run_mworks_scenario.py Config/scenarios/official/example1_pid_baseline.yaml
python3 Scripts/mworks/run_mworks_scenario.py Config/scenarios/official/example1_improved_pid.yaml
```

不要用短时参数覆盖正式 `Config/scenarios/official/*.yaml`。如需临时链路诊断，应写入 `Results/diagnostics/`，不要覆盖正式证据。

批量复现已有场景：

```bash
python3 Scripts/mworks/run_mworks_batch.py --skip-existing Config/scenarios/official/*.yaml
```

`run_mworks_scenario.py` 和 `run_mworks_batch.py` 默认会在仿真、后处理之后执行质量门禁：

```bash
python3 Scripts/results/evaluate_result_quality.py Config/scenarios/official/example3_awff_sysblock.yaml --write-metrics
```

`quality_status=pass` 才能作为完整性能结论；`quality_status=smoke_only` 只能证明链路可用；`quality_status=needs_iteration` 表示需要保留当前证据并继续调控制器或场景。MWORKS 没有报错只代表仿真执行完成，不代表轨迹形状、RMSE、健康分或消融对比达标。

如果只想检查批量计划而不启动 MWORKS/MCP 仿真：

```bash
python3 Scripts/mworks/run_mworks_batch.py --dry-run Config/scenarios/official/*.yaml
```

## 7. 指标、图表与汇总

计算指标：

```bash
python3 Scripts/results/calc_metrics.py \
  Results/official/example1_step/official_example1_improved_pid/raw/official_example1_improved_pid.csv \
  Results/official/example1_step/official_example1_improved_pid/metrics/official_example1_improved_pid.json \
  official_example1 \
  improved_pid
```

指标输出包含：

```text
position_rmse_m
max_position_error_m
steady_state_error_m
settling_time_s
overshoot_x_pct / overshoot_y_pct / overshoot_z_pct / overshoot_max_pct
roll_rmse_rad / pitch_rmse_rad / yaw_rmse_rad / max_tilt_rad
minimum_altitude_m
constraint_violation_count
control_energy
control_smoothness
control_command_min / control_command_max / control_command_normalized
saturation_ratio
tracking_score / robustness_score / safety_score / energy_score / smoothness_score / fault_tolerance_score / total_health_score
```

生成 SVG 图表：

```bash
python3 Scripts/results/plot_results.py \
  Results/official/example1_step/official_example1_improved_pid/raw/official_example1_improved_pid.csv \
  Results/official/example1_step/official_example1_improved_pid/figures \
  --metrics Results/official/example1_step/official_example1_improved_pid/metrics/official_example1_improved_pid.json \
  --file-prefix official_example1_improved_pid
```

生成实验汇总时只纳入真实 MWORKS/MCP 结果：

```bash
python3 Scripts/results/summarize_experiments.py \
  --include-metrics-glob 'Results/official/**/metrics/*pid_baseline.json' \
  --include-metrics-glob 'Results/official/**/metrics/*improved_pid.json'
```

输出：

```text
Results/summaries/experiment_summary/experiment_summary.csv
Results/summaries/experiment_summary/experiment_summary.md
```

说明：项目不再生成或保留 Python/Julia 离线仿真结果。风扰、质量变化、故障、规划、编队等扩展场景必须通过 MWORKS/Sysplorer/MCP 或手动 MWORKS GUI 形成 `source=MWORKS_MCP` / `source=MWORKS_GUI` 证据后，才能进入正式实验汇总和报告结论。

默认情况下，正式场景运行会生成 Sysplorer 原生结果目录 `native_result/{ModelName}/Result.msr`，并在当前仿真会话中尝试打开模型窗口、结果曲线和四旋翼三维动画，便于人工审核。GUI 审核链路使用 `ModelingPy.SimulateModel(..., path=...)` 生成原生结果，并在创建曲线前显式 `OpenResult(Result.msr)`；不要把 MCP `simulate_model ext_res_path` 生成的结果当作可 GUI 审核结果，因为它可能可被脚本读取但无法被 Sysplorer 结果查看器绑定。`Result.msr` 作为人工兜底审查文件保留在本地。人工审核目标是“真实四旋翼三维动画 + 关键跟踪曲线”；只看到桨叶静态/局部旋转、空白结果查看器或单独参数曲线，不能算完成可视化审核。脚本默认不自动调用阻塞式播放命令，动画窗口打开后由人工在 GUI 中点击播放。该目录只用于本地 GUI 审查，已被 Git 忽略。若原生结果路径对 `OpenResult/CreatePlot` 不可靠，脚本会自动改写到 `Results/native_result_cache/{experiment}/{ModelName}/Result.msr`，并在实验目录的 `native_result/native_result_manifest.json` 记录映射。批量回归、无界面环境或授权状态不稳定时可添加 `--no-gui-result-viewer` 跳过原生结果和动画窗口；若仍需保留 `Result.msr` 但不自动弹曲线/动画窗口，可添加 `--no-gui-open`。QP/NMPC-style、安全投影、故障隔离等模型可能明显慢于普通 PID/LinearMPC 场景，不能仅凭长时间无输出判断卡死；只有 MCP health 无响应、授权/登录/激活错误、进程异常退出或日志出现明确错误时，才中止该 MCP 序列。若出现无法解释的授权、登录、激活或大批量库加载失败，应先保存当前代码改动并停止 MCP 重试，等待人工重新登录/激活。

GUI 人工审查时通常会看到三类窗口：模型/图形结构窗口用于确认 Sysblock 或整机连接，曲线窗口用于查看高度、位置误差和控制量，三维动画窗口用于播放四旋翼运动。只有三维动画窗口能判断“无人机是否跑出视野”；模型结构窗口和曲线窗口不能作为三维展示效果结论。如果播放后无人机很快离开视野，先检查对应 metrics 中的 RMSE、最大误差和质量门；若质量门已通过，则优先调整动画视角/缩放后再审查，不把“视角没跟上”直接判定为控制失败。若质量门失败且动画中确实飞离轨迹，应保留该结果为负样本并继续迭代控制器或场景参数。每次正式仿真结束后，需要人工确认当前打开的窗口属于哪一个 experiment，不能把旧窗口的动画当作新场景证据。单个场景人工审查时建议使用 `--gui-reset-windows`，脚本会先关闭旧曲线/动画窗口，再用当前 `Result.msr` 显式创建曲线窗口并创建当前动画窗口；批量回归仍使用 `--no-gui-result-viewer`。

视频级展示允许接入 Unreal 外部渲染器。此时 MWORKS/Sysplorer 仍是唯一仿真源，Unreal 只读取 raw CSV、native result 或实时 TCP/UDP 状态帧，用于无人机上色、桨叶材质、地形/障碍物材质、雷达扇形、局部地图、轨迹留痕、跟随相机和录屏。外部渲染不能改写控制器输出、规划路径、碰撞验收或指标结果。若 Unreal 画面和 Sysplorer/metrics 不一致，先检查坐标转换、单位、材质可见性和资源版本，不允许用渲染画面覆盖仿真结论。

## 8. 下一阶段真实仿真入口

扩展功能保留在 `Docs/Design/` 中作为实现规格，但不再用离线脚本冒充仿真。新增场景时按以下流程推进：

```text
Docs/Design/*.md 明确接口和验收
→ 在 MWORKS/Sysplorer 中建立或派生模型
→ check_model
→ simulate_model
→ result_manager 导出 raw CSV
→ calc_metrics.py 计算指标
→ evaluate_result_quality.py 写入 quality_status
→ plot_results.py / generate_replay_from_raw.py 生成图表和回放
→ summarize_experiments.py 纳入真实证据汇总
```

优先建议：

1. 将 Improved PID 从参数搜索升级为真实的抗饱和、导数滤波和参考前馈实现。
2. 选一个风扰或质量变化场景，接入官方模型并形成真实 MWORKS/MCP 证据。
3. 再推进 INDI / MPC / L1-inspired 模块，不保留无法复现的离线结果。

## 12. 提交前检查

提交前运行：

```bash
python3 Scripts/quality/qa_check.py
python3 Scripts/quality/check_reference_outputs.py
python3 Scripts/tests/test_metrics.py
python3 Scripts/tests/test_summary.py
python3 -m py_compile Scripts/*.py Scripts/tests/*.py
git diff --check
```

若生成了新的二进制或官方资料文件，还需确认没有超过 GitHub 限制的大文件。
