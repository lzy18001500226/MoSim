# MoSim ExperimentProfile与兼容性矩阵

> 状态：Profile Schema 与兼容性门禁设计，2026-06-24。
>
> 本文冻结实验配置、兼容性检查、Launch Plan 和运行证据之间的契约。它的目标
> 不是定义具体控制律，而是保证控制器、状态源、轨迹、规划器、故障扰动、显示
> 和评价可以受控组合，不能靠前端按钮或脚本直接拼运行命令。

## 1. 核心原则

MoSim 的实验入口只有一个：

```text
ExperimentProfile
```

前端、脚本、Agent 和自动测试都只能提交已注册的 `ExperimentProfile`，不能
直接拼裸 `sh`、`roslaunch`、MAVROS topic 或 Gazebo topic。

Orchestrator 必须按以下顺序工作：

```text
1. 读取 ExperimentProfile
2. 解析各子 Profile
3. 做 schema 检查
4. 做兼容性检查
5. 生成 Launch Plan
6. 执行 dry-run preflight
7. 生成 Results/runs/<run_id> 运行准备包
8. 启动 runtime
9. 锁定运行期 profile
10. 收集日志、截图、原始CSV和人工review
11. 归一化 tracking.csv
12. 按 evaluation_profile 计算 metrics.json
13. 执行 Metrics Threshold Gate
14. 执行 Run Evidence Gate
15. 输出最终 Run Packet
```

默认策略是拒绝错误组合，而不是启动后静默降级。

## 2. ExperimentProfile 最小结构

```yaml
experiment_profile:
  id: figure8_px4ctrl_px4_state_v1
  version: 1
  description: px4ctrl figure-eight baseline with PX4/MAVROS fused state

  scenario_profile: obstacle_figure8_v1
  plant_profile: sunray150_gazebo_v1
  sensor_profile: mid360_imu_height_camera_v1
  state_source_profile: px4_mavros_fused_v1
  localization_eval_profile: fastlio_eval_only_v1   # 可选，仅并行定位评价时出现
  height_source_profile: px4_or_gazebo_rangefinder_proxy_v1
  truth_profile: gazebo_truth_eval_only_v1
  frequency_profile: attitude_thrust_100hz_v1

  trajectory_profile: figure8_v1
  planner_profile: none
  controller_profile: px4ctrl_attitude_thrust_v1
  augmentation_profile: none
  safety_profile: basic_limiter_v1
  adapter_profile: mavros_attitude_thrust_v1

  fault_profile: none
  disturbance_profile: none
  display_profile: rviz_gazebo_v1
  evaluation_profile: tracking_metrics_v1

  runtime_profile: sunray_ros1_gazebo_classic_v1
  evidence_profile: standard_run_packet_v1
```

所有 profile id 必须可解析到项目内受控配置或明确的上游配置。`none` 是合法
Profile，也必须有语义，不能用空字符串或省略字段代替。

## 3. Profile 槽位定义

| 槽位 | 必填 | 负责内容 | 禁止混淆 |
| --- | --- | --- | --- |
| `scenario_profile` | 是 | 地图、障碍物、任务区域、车辆数量、初始位姿 | 不记录plant动力学 |
| `plant_profile` | 是 | 机体、质量、惯量、电机、桨叶、执行器、Gazebo/Sunray版本 | 不记录控制器参数 |
| `sensor_profile` | 是 | MID360、IMU、定高、摄像头、噪声、延迟、外参和频率 | 不替代state source |
| `state_source_profile` | 是 | 控制器实际使用的位置、速度、姿态和角速度来源 | 不静默混入truth |
| `localization_eval_profile` | 否 | 并行定位算法评价来源，例如FAST-LIO独立ATE/RPE | 不输入控制器，不替代state_source |
| `height_source_profile` | 是 | Z轴/定高来源 | 不冒充FAST-LIO完整三维定位 |
| `truth_profile` | 是 | 评价真值来源和是否允许输入控制 | 默认不得输入控制器 |
| `frequency_profile` | 是 | 控制、状态对齐、轨迹求值、规划、显示和日志频率 | 不靠topic实测反推配置 |
| `trajectory_profile` | 是 | 手写任务、样条、阶跃、8字、螺旋等参考轨迹 | 不直接发布MAVROS控制 |
| `planner_profile` | 是 | Diff-Planner当前入口、EGO/EGOv2/EGO-Swarm参考/后续对照、FUEL/RACER第二阶段探索及其地图输入 | 不拥有最终控制发布权 |
| `controller_profile` | 是 | 名义控制器core和参数 | 不包含SafetySupervisor和Adapter私有逻辑 |
| `augmentation_profile` | 是 | INDI、L1、DOB/ESO、ADRC、AWFF、NN/Fuzzy等补偿模块 | 不掩盖基准控制器问题 |
| `safety_profile` | 是 | 限幅、geofence、CBF、急停和发布前否决规则 | 不写入控制器内部状态 |
| `adapter_profile` | 是 | ATTITUDE_THRUST/BODY_RATE/WRENCH/ROTOR映射 | 不改变控制器数学输出语义 |
| `fault_profile` | 是 | 故障类型、对象、强度、开始时间、持续时间、随机种子 | 不通过改误差伪造物理故障 |
| `disturbance_profile` | 是 | 风扰、负载、地效、参数摄动、传感器退化 | 不和fault_profile混写 |
| `display_profile` | 是 | RViz、Gazebo GUI、UE、Web、QGC窗口和显示桥 | 不作为指标来源 |
| `evaluation_profile` | 是 | 指标、truth对照、排行榜分组和证据留存规则 | 不参与控制闭环 |
| `runtime_profile` | 是 | ROS/Gazebo/PX4/MAVROS/MWORKS/UE运行后端和版本 | 不替代plant或controller |
| `evidence_profile` | 是 | 结果目录结构、日志、截图、视频、manifest和review包 | 不定义算法 |

## 4. 子Profile最低字段

### 4.1 ControllerProfile

```yaml
controller_profile:
  id: px4ctrl_attitude_thrust_v1
  controller_id: px4ctrl
  implementation: cpp
  output_interface: ATTITUDE_THRUST
  rate_hz: 100
  params_id: px4ctrl_sunray_baseline_v1
  required_state:
    - position
    - velocity
    - attitude
    - angular_velocity
  required_reference:
    - position
    - velocity
    - acceleration
    - yaw
  optional_reference:
    - yaw_rate
  compatible_adapters:
    - mavros_attitude_thrust_v1
  compatible_augmentations:
    - none
    - awff_v1
  compatible_safety:
    - basic_limiter_v1
  evidence_level: E4
```

### 4.2 StateSourceProfile

```yaml
state_source_profile:
  id: px4_mavros_fused_v1
  group: A
  pose_velocity_topic: /uav1/mavros/local_position/odom
  angular_velocity_topic: /uav1/mavros/imu/data
  system_status_topic: /uav1/sunray/uav_state
  allowed_for_control: true
  requires_truth_label: false
  timeout_s: 0.05
  frame_semantics: ENU_local_to_base_link
```

FAST-LIO 相关状态源必须明确分组：

```text
A: PX4/MAVROS融合状态，正式基准
B: Gazebo truth debug state，只能debug
C: FAST-LIO直接输出，只能定位评价
D: FAST-LIO -> PX4 EKF -> MAVROS，闭环对比
E: FAST-LIO XY/Yaw + Gazebo/Laser Z替身，Hybrid-Z单独榜
```

其中 `state_source_profile` 和 `localization_eval_profile` 必须分清：

```text
state_source_profile
  = 控制器实际闭环状态输入

localization_eval_profile
  = 只给评价器、RViz审查和FAST-LIO定位指标使用
  = 不允许发布控制状态
  = 不允许改变px4ctrl输入
```

例如 `fastlio_independent_eval_figure8_v1` 中，px4ctrl 仍然使用
`px4_mavros_fused_v1` 控制状态；FAST-LIO 只作为
`localization_eval_profile=fastlio_eval_only_v1` 计算 ATE/RPE、延迟、丢帧和
地图完整性。该实验可以评价 FAST-LIO 定位质量，但不能宣称“FAST-LIO闭环入控”。
FAST-LIO 独立定位评价的正式指标不从 `tracking.csv` 推导；`tracking.csv`
仍用于本次飞行轨迹/控制状态回放，ATE/RPE、姿态/速度误差、延迟、丢帧和
地图完整性必须来自 `raw/localization.csv` 与 `raw/map_summary.json`。

### 4.3 TrajectoryProfile

```yaml
trajectory_profile:
  id: figure8_v1
  source_type: analytic
  required_reference_order:
    position: true
    velocity: true
    acceleration: true
    jerk: false
    snap: false
  duration_s: 30.0
  continuity_required:
    position: true
    velocity: true
    acceleration: true
  constraints:
    max_velocity_mps: 2.0
    max_acceleration_mps2: 3.0
    max_yaw_rate_radps: 1.0
```

### 4.4 PlannerProfile

```yaml
planner_profile:
  id: ego_single_v1
  planner_id: ego_planner
  output_type: bspline_or_position_cmd
  nominal_rate_hz: 10
  map_input_profile: livox_world_grid_v1
  trajectory_adapter: ego_to_reference_v1
  owns_mavros_control: false
```

### 4.5 AdapterProfile

```yaml
adapter_profile:
  id: mavros_attitude_thrust_v1
  input_interface: ATTITUDE_THRUST
  output_backend: mavros_setpoint_raw_attitude
  thrust_input_unit: N
  thrust_mapping_profile: sunray_px4ctrl_original_or_mosim_v1
  quaternion_order: wxyz
  publishes_final_command: true
```

### 4.6 EvaluationProfile

```yaml
evaluation_profile:
  id: tracking_metrics_v1
  truth_profile: gazebo_truth_eval_only_v1
  metrics:
    - rmse
    - max_error
    - steady_state_error
    - overshoot
    - settling_time
    - saturation_ratio
  leaderboard_group: px4_mavros_fused
  required_artifacts:
    - RUN_MANIFEST.json
    - runtime_log_manifest.json
    - metrics.json
    - threshold_report.json
    - tracking.csv
    - review.md
```

## 5. Profile Hash 规则

每次实验必须生成：

```text
experiment_profile_hash
profile_hashes
launch_plan_hash
runtime_source_hashes
```

建议规则：

```text
1. 先将Profile展开为完整JSON对象；
2. 按key排序；
3. 去掉注释和非语义空白；
4. 使用UTF-8编码；
5. 计算SHA256；
6. 写入RUN_MANIFEST.json和metrics.json。
```

Profile hash 不是 Git commit 的替代品。正式 run manifest 还必须记录：

```text
git_commit_or_dirty_state
source_hashes
upstream_commit
local_patch_hash
runtime_version
```

## 5.1 Dry-Run Preflight

Profile Validator 只回答“实验组合是否允许”。Dry-run preflight 进一步回答：

```text
这个ExperimentProfile是否已经能展开成可执行前契约。
```

当前入口：

```powershell
python Scripts/quality/build_experiment_preflight.py --all --emit-artifacts-dir Results/profile_validation/px4ctrl_baseline_static
```

Preflight 必须发生在 ROS/Gazebo/PX4/MAVROS/RViz 启动之前。它检查：

```text
1. ExperimentProfile静态兼容性；
2. LaunchPlan是否能绑定run_id；
3. 每个LaunchPlan template是否在runtime_bindings中有项目本地路径；
4. 每个runtime required_path是否存在；
5. evaluation_profile声明的metrics是否在metrics_schema中定义；
6. FAST-LIO PX4 EKF分支是否声明PX4外部里程计融合；
7. Hybrid-Z分支是否声明混合高度来源；
8. localization_eval_profile是否仍保持非入控语义。
```

当前配置落点：

```text
Config/profiles/runtime_bindings.json
Config/profiles/metrics_schema.json
Config/profiles/tracking_sources.json
Config/profiles/runtime_log_exports.json
Scripts/quality/build_experiment_preflight.py
```

Preflight 通过只证明“可以进入运行前人工/自动启动阶段”，不证明闭环成功。
Preflight 失败时禁止启动 runtime，必须先修 Profile、runtime binding 或 metrics
schema。

## 5.2 Run Packet Materialization

Dry-run preflight 通过后，必须先将单个 ExperimentProfile 物化成正式运行目录，
再进入人工或自动启动阶段。当前入口：

```powershell
python Scripts/quality/prepare_experiment_run.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id>
```

该工具只生成运行前准备包：

```text
Results/runs/<run_id>/LaunchPlan.json
Results/runs/<run_id>/RUN_MANIFEST.json
Results/runs/<run_id>/preflight.json
Results/runs/<run_id>/source_hashes.json
Results/runs/<run_id>/operator_checklist.md
Results/runs/<run_id>/commands.md
Results/runs/<run_id>/review.template.md
Results/runs/<run_id>/screenshots/
Results/runs/<run_id>/logs/
Results/runs/<run_id>/raw/
```

它明确不启动：

```text
ROS
Gazebo
PX4
MAVROS
RViz
UE
MWORKS
```

它也不得生成会被误认为“运行完成”的证据：

```text
tracking.csv
metrics.json
review.md
非空 screenshots/
非空 logs/
```

因此 Run Packet Materialization 通过只证明：

```text
本次实验已经有唯一run_id、固定LaunchPlan、固定RUN_MANIFEST、当前source_state
和待填证据目录。
```

它不证明 runtime 已经启动，不证明闭环成功，也不证明指标达标。

`RUN_MANIFEST.json` 中不得长期保留 `<commit-or-dirty>`、
`<source_hashes.json>` 等模板占位。`prepare_experiment_run.py` 必须将当前
`git_commit`、`git_dirty`、`source_hashes.json` 路径和 source hash 摘要写入
`source_state`，并把 `runtime_bindings.json`、`metrics_schema.json`、
`runtime_log_exports.json` 和 `tracking_sources.json` 纳入可追溯源集合。
后续正式 Evidence Gate 必须复核这些字段，保证同一次 run 的 Profile、
runtime binding、日志导出语义、tracking语义和关键源码可追溯。

## 6. 兼容性检查矩阵

### 6.1 必须拒绝启动

| 编号 | 条件 | 原因 | 建议替代 |
| --- | --- | --- | --- |
| C-REF-01 | 控制器要求 `jerk/snap`，轨迹只提供 `p/v/a` | 参考阶次不足 | 换Basic控制器或换TrajectoryProfile |
| C-OUT-01 | 控制器输出 `BODY_RATE_THRUST`，Adapter只支持 `ATTITUDE_THRUST` | 输出接口不匹配 | 换Adapter或换控制器输出层级 |
| C-STATE-01 | FAST-LIO未过定位门禁却被选为controller_state | 状态源未验收 | 切回`px4_mavros_fused_v1`或只做评价 |
| C-TRUTH-01 | Gazebo truth完整位姿被选为正式控制状态 | 正式榜单污染 | 改为debug profile |
| C-HYBRID-01 | 混合Z状态未声明height_source_profile | 无法追踪误差来源 | 使用Hybrid-Z profile |
| C-MPC-01 | NMPC缺失plant/constraint/solver profile | 优化问题不完整 | 补齐约束和求解器profile |
| C-SAFE-01 | safety_profile要求geofence但scenario无边界 | 安全约束不可判定 | 增加场景边界或关闭对应profile并标注 |
| C-SWARM-01 | 多机实验缺少namespace/topic/log隔离 | 实例互相污染 | 使用swarm隔离profile |
| C-DISPLAY-01 | display profile要求UE bridge但runtime无DisplayFrame bridge | 显示依赖不存在 | 降级到RViz/Gazebo display profile |
| C-EVAL-01 | evaluation profile缺truth/log | 无法形成指标 | 只允许debug，不进排行榜 |
| C-LOG-01/02/03/04 | RuntimeExportProfile绑定的RuntimeLogProfile未注册、不兼容实验、tracking_source不一致或缺少必需artifact slot | 运行后证据收集语义不可复现 | 修正`runtime_log_exports.json`或RuntimeExportProfile绑定 |
| C-TRACK-01/02/03/04/05/06/07/08 | TrackingSourceProfile未注册、不兼容实验、状态源/高度源/leaderboard/localization语义不一致，或FAST-LIO eval-only/Hybrid-Z语义错误 | tracking.csv无法代表声明的控制/评价状态 | 修正`tracking_sources.json`或切换匹配的RuntimeExportProfile |

### 6.2 允许但必须显式标注

| 条件 | 必须标注 | 禁止声明 |
| --- | --- | --- |
| Gazebo truth debug state进入控制器 | `state_group=B`、`debug_only=true` | 正式定位控制结果 |
| Gazebo Z作为定高替身 | `height_source=gazebo_rangefinder_surrogate` | 纯FAST-LIO全状态定位 |
| FAST-LIO直接输出进入评价器 | `state_group=C`、`control_input_allowed=false` | FAST-LIO闭环入控 |
| FAST-LIO经PX4 EKF融合 | `state_group=D`、EKF参数和外部观测profile | 与PX4融合基线混表 |
| UE truth用于显示 | `display_only=true` 或 `control_input_allowed=false` | 规划器偷读全局地图 |
| display降级 | `display_degraded=true`、原因码 | 控制成功或失败结论 |

### 6.3 可自动降级的条件

自动降级只允许发生在控制权尚未发布之前，且必须写入 run packet。

| 条件 | 可降级到 | 约束 |
| --- | --- | --- |
| 显示Profile缺UE依赖 | RViz/Gazebo显示Profile | 控制和评价继续，display标 degraded |
| Planner不可用 | 手写轨迹Profile | 只能做控制器基线，不得宣称planner通过 |
| FAST-LIO评价失败 | PX4/MAVROS融合状态 | 只能继续非FAST-LIO基线 |
| 高级控制器未注册 | px4ctrl或official PID | 只能作为fallback run，不能替代原实验 |

运行开始后，除人工停止和Safety回退外，不允许在线切换：

```text
controller_profile
state_source_profile
plant_profile
adapter_profile
truth_profile
```

## 7. Profile Rejection Packet

兼容性失败必须输出结构化记录：

```yaml
profile_rejection:
  planned_run_id: 20260624_figure8_nmpc
  rejected_stage: compatibility_check
  rejected_profile: nmpc_attitude_thrust_v1
  reason_code: C-MPC-01
  human_reason: NMPC缺失plant constraint和solver profile
  safe_alternative_profile: px4ctrl_attitude_thrust_v1
  control_started: false
```

拒绝不是失败实验；它是防止错误组合进入飞行闭环的安全门禁。

## 8. Launch Plan 契约

Launch Plan 由 Orchestrator 生成，不由用户手写。最小字段：

```yaml
launch_plan:
  run_id: 20260624_figure8_px4ctrl
  experiment_profile_id: figure8_px4ctrl_px4_state_v1
  experiment_profile_hash: <sha256>
  steps:
    - id: gazebo
      template: sunray_gazebo.launch
      profile: sunray150_gazebo_v1
      expected_topics:
        - /uav1/sunray/gazebo_pose
    - id: mavros
      template: mavros_px4.launch
      profile: px4_mavros_v1
    - id: controller
      template: controller_host.launch
      profile: px4ctrl_attitude_thrust_v1
    - id: rviz
      template: rviz_review.launch
      profile: rviz_gazebo_v1
  forbidden_claims:
    - FAST-LIO closed-loop localization
    - MWORKS generated controller
```

裸命令只能作为模板内部实现细节。正式证据引用 Launch Plan，不引用人工命令。

## 9. Run Manifest 最小结构

```yaml
run_manifest:
  run_id: 20260624_figure8_px4ctrl
  experiment_profile_id: figure8_px4ctrl_px4_state_v1
  experiment_profile_hash: <sha256>
  launch_plan_hash: <sha256>
  profile_hashes:
    controller_profile: <sha256>
    state_source_profile: <sha256>
    localization_eval_profile: <sha256>  # 可选，仅并行定位评价实验出现
    trajectory_profile: <sha256>
  source_state:
    git_commit: <commit-or-dirty>
    source_hashes: <path>
  runtime:
    os: ubuntu-20.04
    ros: noetic
    gazebo: classic
    px4: <version-or-commit>
  runtime_bindings: Config/profiles/runtime_bindings.json
  metrics_schema: Config/profiles/metrics_schema.json
  evidence:
    result_root: Results/runs/<run_id>
    launch_plan: LaunchPlan.json
    run_manifest: RUN_MANIFEST.json
    metrics: metrics.json
    threshold_report: threshold_report.json
    runtime_log_manifest: runtime_log_manifest.json
    tracking_log: tracking.csv
    screenshots: screenshots/
    logs: logs/
    review: review.md
  forbidden_claims:
    - not_fastlio_closed_loop
```

## 9.1 Run Evidence Gate

Dry-run preflight 只允许实验进入启动阶段。实验跑完后，还必须通过 Run Evidence
Gate，才能用于审核、对比、排行榜或报告结论。

当前入口：

```powershell
python Scripts/quality/check_run_evidence.py Results/runs/<run_id>
```

如果需要先从标准跟踪日志生成 tracking metrics：

```powershell
python Scripts/quality/compute_tracking_metrics.py Results/runs/<run_id>/tracking.csv --manifest Results/runs/<run_id>/RUN_MANIFEST.json --out Results/runs/<run_id>/metrics.json
```

如果是 FAST-LIO eval-only 定位评价，必须使用定位对照日志生成 localization
metrics，而不是把轨迹参考误差冒充定位误差：

```powershell
python Scripts/quality/compute_tracking_metrics.py --localization-csv Results/runs/<run_id>/raw/localization.csv --map-summary-json Results/runs/<run_id>/raw/map_summary.json --manifest Results/runs/<run_id>/RUN_MANIFEST.json --out Results/runs/<run_id>/metrics.json
```

指标生成后，必须先执行 Metrics Threshold Gate，再进入人工审核：

```powershell
python Scripts/quality/check_metric_thresholds.py Results/runs/<run_id>/metrics.json --manifest Results/runs/<run_id>/RUN_MANIFEST.json --report Results/runs/<run_id>/threshold_report.json
```

第一版 px4ctrl PX4/MAVROS 融合状态基线阈值固定为：

```text
rmse <= 0.02 m
steady_state_error <= 0.02 m
max_error <= 0.05 m
overshoot <= 0.05 m
saturation_ratio <= 0.05
settling_time <= 5.0 s
```

这些阈值是“可审核目标”，不是算法已经达成的结论。若指标未通过，Run Packet
仍可保留为失败证据，但不能进入 accepted baseline、排行榜或报告成功结论。

如果真实日志不是标准列名，必须先归一化成统一 `tracking.csv`：

```powershell
python Scripts/quality/normalize_tracking_csv.py raw_tracking.csv --out Results/runs/<run_id>/tracking.csv --map time_s=stamp --map ref_x_m=ref_x --map ref_y_m=ref_y --map ref_z_m=ref_z --map truth_x_m=truth_x --map truth_y_m=truth_y --map truth_z_m=truth_z --default phase=unknown --default saturated=0
```

如果参考轨迹和状态/真值来自两个CSV日志，优先使用已注册的
`TrackingSourceProfile`，不要在正式命令里手工堆列名：

```powershell
python Scripts/quality/build_tracking_csv.py --reference-csv reference.csv --state-csv state.csv --out Results/runs/<run_id>/tracking.csv --tracking-source-profile px4_mavros_fused_reference_state_csv_v1
```

完整 Run Gate 中同样使用该 profile，并由 `RUN_MANIFEST.json` 中的
`experiment_profile_id` 检查兼容性：

```powershell
python Scripts/quality/run_experiment_gate.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id> --reference-csv <reference.csv> --state-csv <state.csv> --runtime-log-profile px4ctrl_runtime_log_export_v1 --tracking-source-profile px4_mavros_fused_reference_state_csv_v1 --review-file <review.md> --screenshot <rviz.png> --log <ros.log>
```

`TrackingSourceProfile` 只描述日志列契约、相位/饱和字段来源和时间对齐容差。
它不做坐标系转换、状态源融合、重采样滤波或控制状态切换。

真实运行结束后，先按 `RuntimeExportProfile` 导出真实运行产物，再使用
`RuntimeLogProfile` 把日志、截图、review 和 CSV 收进同一个 run packet。
三者边界固定为：

```text
RuntimeExportProfile
  真实运行后必须导出什么；
  artifact slot来自哪个producer；
  目标标准路径是什么；
  导出的CSV至少应包含哪些列；
  RViz/地图/轨迹审核必须看见什么。

RuntimeLogProfile
  已导出的文件怎么复制进Results/runs/<run_id>；
  每个slot的packet目标路径、大小和sha256如何记录；
  是否调用TrackingSourceProfile生成tracking.csv。

TrackingSourceProfile
  reference/state CSV列名如何映射；
  时间戳如何对齐；
  phase和saturated字段来自哪份日志；
  该tracking数据对应哪个state_source_profile、height_source_profile、
  localization_eval_profile和leaderboard_group。

LocalizationEvidence
  FAST-LIO eval-only必须额外导出raw/localization.csv和raw/map_summary.json；
  localization.csv表达FAST-LIO估计与Gazebo truth的时间对齐对照；
  map_summary.json表达累计地图覆盖完整性；
  二者只服务定位评价，不改变控制器state_source_profile。
```

当前分成四类TrackingSourceProfile：

```text
px4_mavros_fused_reference_state_csv_v1
  PX4/MAVROS融合状态基线；

fastlio_eval_reference_state_csv_v1
  FAST-LIO只做并行定位评价，控制状态仍来自PX4/MAVROS；
  tracking.csv只保留飞行回放/控制上下文，正式FAST-LIO指标来自raw/localization.csv和raw/map_summary.json；

fastlio_px4_ekf_fused_reference_state_csv_v1
  FAST-LIO外部里程计经PX4 EKF融合后，再由MAVROS local state输出；

fastlio_xy_yaw_gazebo_z_reference_state_csv_v1
  FAST-LIO XY/Yaw + Gazebo定高替身的Hybrid-Z状态源。
```

当前推荐入口是 RuntimeExportProfile exporter：

```powershell
python Scripts/quality/export_runtime_sources.py Results/runs/<run_id> --runtime-export-profile sunray_px4ctrl_runtime_export_v1 --artifact reference_csv=<reference.csv> --artifact state_csv=<state.csv> --artifact rviz_screenshot=<rviz.png> --artifact ros_log=<ros.log> --review-file <review.md> --build-tracking
```

FAST-LIO eval-only 运行必须额外导出定位对照和地图覆盖摘要：

```powershell
python Scripts/quality/export_runtime_sources.py Results/runs/<run_id> --runtime-export-profile sunray_fastlio_eval_runtime_export_v1 --artifact reference_csv=<reference.csv> --artifact state_csv=<state.csv> --artifact localization_csv=<localization.csv> --artifact map_summary_json=<map_summary.json> --artifact rviz_screenshot=<rviz.png> --artifact ros_log=<ros.log> --review-file <review.md> --build-tracking
```

该脚本先检查 `RUN_MANIFEST.json` 中的 `runtime_export_profile`、runtime绑定、
required slot、标准目标路径和 CSV 列契约，再调用底层 `RuntimeLogProfile`
收集器写入 `runtime_log_manifest.json` 与 `tracking.csv`。

`RuntimeLogProfile` 负责回答：

```text
本次实验收集哪些已导出的artifact；
每个artifact是什么角色；
artifact复制到run packet的哪个标准位置；
是否需要用TrackingSourceProfile生成tracking.csv；
该artifact profile兼容哪些ExperimentProfile。
```

`RuntimeExportProfile`、`runtime_export_manifest.json` 和 `RuntimeLogProfile`
都不证明 runtime 已经成功，只证明运行后的证据导出和收集过程有可追溯契约。
真正的控制效果仍由 metrics、截图、日志和人工审核共同判定。

标准 `tracking.csv` 至少必须表达：

```text
time_s
phase
ref_x_m / ref_y_m / ref_z_m
truth_x_m / truth_y_m / truth_z_m
saturated
```

`normalize_tracking_csv.py` 只做列名映射、默认值填充和数值检查，不做坐标系转换、
状态源融合、重采样或滤波。坐标系、频率和状态源选择必须在 Profile、Adapter 或
运行日志导出阶段解决，不能在指标归一化阶段偷偷修正。

Run Evidence Gate 检查：

```text
1. RUN_MANIFEST.json存在且包含run_manifest对象；
2. LaunchPlan.json存在，且内容hash等于launch_plan_hash；
3. run_id在目录名、LaunchPlan、RunManifest和metrics中一致；
4. RUN_MANIFEST.json不含模板占位值；
5. source_state和source_hashes.json存在且hash一致；
6. evidence_profile声明的required_artifacts全部存在；
7. RUN_MANIFEST.json声明的RuntimeExportProfile与本次运行路线一致；
8. runtime_export_manifest.json存在，且run_id、experiment_profile_id、runtime_profile、
   RuntimeExportProfile、RuntimeLogProfile和TrackingSourceProfile与RUN_MANIFEST一致；
9. runtime_export_manifest.json声明的required_artifact_slots、required_topics和
   review_requirements与RuntimeExportProfile一致；
10. runtime_export_manifest.json声明的source_artifacts覆盖全部必需slot，且source文件、
    复制后的destination文件、bytes和sha256一致；
11. runtime_export_manifest.json中的runtime_log_manifest路径和sha256与
    runtime_log_manifest.json一致；
12. runtime_log_manifest.json中的run_id、experiment_profile_id和RuntimeLogProfile兼容；
13. runtime_log_manifest.json声明的artifact目标文件存在、非空、大小和sha256一致；
14. runtime_log_manifest.json中的tracking_source_profile与RuntimeLogProfile一致；
15. tracking.csv包含标准参考/真值列且非空；
16. metrics.json包含evaluation.required_metrics声明的指标；
17. metrics.json中的指标名和单位与metrics_schema一致；
18. threshold_report.json存在且run_id一致，并包含accepted布尔字段；
19. review.md非空且不包含forbidden_claims；
20. screenshots/和logs/目录存在且至少包含可用非空文件。
```

对 `fastlio_independent_metrics_v1`，`metrics.json` 必须由
`raw/localization.csv` 与 `raw/map_summary.json` 生成，指标包括 `ate`、`rpe`、
`pose_error`、`velocity_error`、`delay`、`drop_rate` 和 `map_completeness`。
`tracking.csv` 不能单独证明 FAST-LIO 定位质量。

Run Evidence Gate 通过也只证明“本次运行证据包结构完整、指标可复算、声明未越界”，
不自动证明控制器达到最终指标。控制性能仍由 `metrics.json` 和人工审核结论决定。

## 10. 最小实现顺序

Profile系统按以下顺序落地，避免一次性做成大而空的配置平台：

```text
P1-0: 固定schema和兼容性矩阵
P1-1: 为px4ctrl起飞/悬停/降落建立首个ExperimentProfile
P1-2: 为8字、螺旋、阶跃建立TrajectoryProfile
P1-3: 为FAST-LIO A/B/C/D/E实验组建立StateSourceProfile
P1-4: 先为Diff-Planner单机和Diff-Planner swarm三机建立PlannerProfile；EGO/EGOv2/EGO-Swarm作为参考/后续对照补充；FUEL/RACER进入第二阶段探索Profile
P1-5: 建Profile Validator最小脚本
P1-6: 建dry-run preflight，检查runtime binding和metrics schema
P1-7: 建正式Run准备包物化器，生成Results/runs/<run_id>骨架
P1-8: 建source_state/source_hashes绑定，消除RunManifest模板占位
P1-9: 建tracking.csv归一化器，接真实日志列名
P1-10: 建RuntimeExportProfile，固定真实运行后的导出契约
P1-10a: 建RuntimeLogProfile和运行后证据收集器
P1-11: 建tracking metrics计算器
P1-11a: 建FAST-LIO independent localization metrics计算路径
P1-12: 建Metrics Threshold Gate，判定指标是否达标
P1-13: 建Run Evidence Gate，检查运行后证据包
P1-14: 将Launch Plan和Run Manifest接入正式run packet
P1-15: 前端只提交ExperimentProfile，不直接运行命令
```

当前已建立最小可检查入口：

```text
Config/profiles/catalog.json
Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json
Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json
Config/profiles/experiments/px4ctrl_spiral_baseline_v1.json
Config/profiles/experiments/px4ctrl_step_baseline_v1.json
Config/profiles/experiments/fastlio_independent_eval_figure8_v1.json
Config/profiles/experiments/fastlio_px4_ekf_ab_figure8_v1.json
Config/profiles/experiments/fastlio_hybrid_z_figure8_v1.json
Config/profiles/tracking_sources.json
Config/profiles/runtime_log_exports.json
Scripts/quality/check_experiment_profile.py
Scripts/quality/build_experiment_preflight.py
Scripts/quality/prepare_experiment_run.py
Scripts/quality/normalize_tracking_csv.py
Scripts/quality/build_tracking_csv.py
Scripts/quality/export_runtime_sources.py
Scripts/quality/collect_runtime_evidence.py
Scripts/quality/compute_tracking_metrics.py
Scripts/quality/check_metric_thresholds.py
Scripts/quality/check_run_evidence.py
Scripts/quality/run_experiment_gate.py
```

检查命令：

```powershell
python Scripts/quality/check_experiment_profile.py --all
```

生成 Launch Plan / Run Manifest / rejection skeleton：

```powershell
python Scripts/quality/check_experiment_profile.py --all --emit-artifacts-dir Results/profile_validation/px4ctrl_baseline_static
```

生成 dry-run preflight / LaunchPlan / RunManifest template：

```powershell
python Scripts/quality/build_experiment_preflight.py --all --emit-artifacts-dir Results/profile_validation/px4ctrl_baseline_static
```

生成单个正式运行准备目录：

```powershell
python Scripts/quality/prepare_experiment_run.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id>
```

执行单个完整离线Run Gate：

```powershell
python Scripts/quality/run_experiment_gate.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id> --tracking-csv <standard_tracking.csv> --review-file <review.md> --screenshot <rviz.png> --log <ros.log>
```

上述 `--tracking-csv` 形式只适合诊断或已有完整 runtime manifest 的情况。正式
accepted 路径必须通过 RuntimeLogProfile 生成 `runtime_log_manifest.json`：

```powershell
python Scripts/quality/run_experiment_gate.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id> --reference-csv <reference.csv> --state-csv <state.csv> --runtime-log-profile px4ctrl_runtime_log_export_v1 --tracking-source-profile px4_mavros_fused_reference_state_csv_v1 --review-file <review.md> --screenshot <rviz.png> --log <ros.log>
```

如果reference和state/truth来自两个CSV日志，Run Gate必须显式声明
`--tracking-source-profile`，并与 `RuntimeLogProfile` 绑定使用；不要在正式
验收命令里手工堆列名参数。

如果只需要生成正式运行准备目录，必须显式使用：

```powershell
python Scripts/quality/run_experiment_gate.py Config/profiles/experiments/px4ctrl_takeoff_hover_land_v1.json --run-id <run_id> --prepare-only
```

归一化真实 tracking 日志：

```powershell
python Scripts/quality/normalize_tracking_csv.py raw_tracking.csv --out Results/runs/<run_id>/tracking.csv --map time_s=stamp --map ref_x_m=ref_x --map ref_y_m=ref_y --map ref_z_m=ref_z --map truth_x_m=truth_x --map truth_y_m=truth_y --map truth_z_m=truth_z
```

从独立reference/state日志构造标准tracking.csv：

```powershell
python Scripts/quality/build_tracking_csv.py --reference-csv reference.csv --state-csv state.csv --out Results/runs/<run_id>/tracking.csv --tracking-source-profile px4_mavros_fused_reference_state_csv_v1
```

将运行后的真实日志、截图和review收进正式run packet：

```powershell
python Scripts/quality/export_runtime_sources.py Results/runs/<run_id> --runtime-export-profile sunray_px4ctrl_runtime_export_v1 --artifact reference_csv=<reference.csv> --artifact state_csv=<state.csv> --artifact rviz_screenshot=<rviz.png> --artifact ros_log=<ros.log> --review-file <review.md> --build-tracking
```

执行指标阈值门禁：

```powershell
python Scripts/quality/check_metric_thresholds.py Results/runs/<run_id>/metrics.json --manifest Results/runs/<run_id>/RUN_MANIFEST.json --report Results/runs/<run_id>/threshold_report.json
```

回归测试：

```powershell
python -m pytest Scripts/tests/test_experiment_profile_validator.py Scripts/tests/test_experiment_preflight.py Scripts/tests/test_prepare_experiment_run.py Scripts/tests/test_tracking_normalizer.py Scripts/tests/test_build_tracking_csv.py Scripts/tests/test_export_runtime_sources.py Scripts/tests/test_collect_runtime_evidence.py Scripts/tests/test_metric_threshold_gate.py Scripts/tests/test_run_evidence_gate.py Scripts/tests/test_run_experiment_gate.py -q
```

模板位置：

```text
Config/profiles/templates/launch_plan.skeleton.template.json
Config/profiles/templates/RUN_MANIFEST.skeleton.template.json
Config/profiles/templates/profile_rejection.template.json
```

该检查只证明实验意图满足静态Profile契约，不证明ROS/Gazebo/PX4闭环已经运行。
生成的 skeleton 也只作为运行前审查材料，不能替代真实日志、指标、截图和
review packet。
回归测试必须保留典型负例，证明兼容性矩阵不仅能接受正确Profile，也能拒绝
错误Profile。

## 11. 禁止事项

```text
不得没有Profile就启动正式实验。
不得把Profile字段省略后靠默认值猜测。
不得运行后静默换状态源、控制器、Adapter或truth。
不得把debug profile的指标放进正式排行榜。
不得把显示Profile失败解释成控制失败。
不得把前端按钮能启动说成实验平台完成。
不得把Launch Plan生成成功说成闭环成功。
```

## 12. 后续落点

| 后续工作 | 落点 |
| --- | --- |
| Profile JSON/YAML schema | `Config/profiles/` |
| Profile Validator | `Scripts/quality/check_experiment_profile.py` |
| Dry-run Preflight | `Scripts/quality/build_experiment_preflight.py` |
| Run准备包物化器 | `Scripts/quality/prepare_experiment_run.py` |
| Runtime绑定表 | `Config/profiles/runtime_bindings.json` |
| Metrics定义表 | `Config/profiles/metrics_schema.json` |
| TrackingSourceProfile表 | `Config/profiles/tracking_sources.json` |
| RuntimeLogProfile表 | `Config/profiles/runtime_log_exports.json` |
| Tracking CSV归一化器 | `Scripts/quality/normalize_tracking_csv.py` |
| Reference/State日志对齐器 | `Scripts/quality/build_tracking_csv.py` |
| RuntimeExportProfile导出入口 | `Scripts/quality/export_runtime_sources.py` |
| RuntimeLogProfile底层收集器 | `Scripts/quality/collect_runtime_evidence.py` |
| Tracking metrics计算器 | `Scripts/quality/compute_tracking_metrics.py` |
| Metrics Threshold Gate | `Scripts/quality/check_metric_thresholds.py` |
| Run Evidence Gate | `Scripts/quality/check_run_evidence.py` |
| Run Gate一键封装 | `Scripts/quality/run_experiment_gate.py` |
| Run Manifest模板 | `Config/profiles/templates/RUN_MANIFEST.skeleton.template.json`，实际运行落点为 `Results/runs/<run_id>/RUN_MANIFEST.json` |
| 前端ExperimentProfile入口 | `Docs/Design/架构/04_展示与实验平台/展示与实验平台接口.md` |
| 指标和排行榜分组 | `Docs/Design/架构/03_测试调参与证据/测试与评价.md` |
