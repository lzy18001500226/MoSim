# RACER占用期间非Gazebo收口板

> 状态：当前可执行工作板，2026-07-15。
>
> 目标是在不干扰现有 RACER/ROS/Gazebo/PX4/MAVROS 共享运行资源的前提下，先把
> 赛题和扩展能力的模型、接口、Profile、离线仿真、指标和证据准备完成。本文不把
> 静态或 MWORKS 结果升级为 Gazebo 运行成功。

## 1. 资源等级

```text
L0 source_offline
  文件、schema、单元测试、代码生成离线门禁、历史结果审计；可立即执行。

L1 mworks_isolated
  MWORKS/Sysplorer/Syslab模型检查、仿真和结果查看；不接触ROS/Gazebo/PX4。
  进入前仍需通过当前MWORKS activation/window gate。

L2 replay_only
  使用已有run bundle做RViz/UE/MWORKS离线回放、指标和展示契约验证；不连接live runtime。

L3 gazebo_exclusive
  Gazebo/PX4/MAVROS/ROS master live运行；当前由RACER占用，暂不执行。
```

## 2. 立即收口顺序

### N0 接口和Profile基线

- 校验 `Config/profiles/catalog.json`、所有正式 experiment profile 和 candidate profile；
- 补齐 controller、trajectory、fault、disturbance、display、evaluation 和 evidence 槽位；
- 固化 DisplayFrame、FaultEvent、MetricsFrame、Run Manifest 和参数 lineage；
- 为不兼容组合保留明确 rejection packet。

完成条件：全量 profile validator 通过，或每个失败都有预期拒绝原因。

### N1 控制器离线门禁

- 保持六类 G9 generated-C 450-case 门禁可重复；
- 检查 controller registry、源码路径、ABI、adapter 和 generated provenance；
- 将 backlog/planned 控制器与正式可运行控制器严格分组；
- 神经残差、强化学习和 YOPO 只先定义接口、训练/推理契约和 fallback，不升级状态。

完成条件：离线一致性、ABI、来源和静态 adapter 门禁全部有可追溯结果。

### N2 MWORKS图形化仿真矩阵

按相同 plant 和指标顺序完成：

```text
official PID baseline
improved/enhanced PID
PID-INDI或现有增强控制器
Linear MPC/NMPC候选
SE3/DFBC/SMC等已实现控制器
```

任务矩阵：

```text
起飞-悬停-降落
阶跃
8字
螺旋
```

完成条件：每次运行有 scenario/config、MWORKS result/raw、metrics、figure 和 manifest。

### N3 鲁棒性和故障的MWORKS矩阵

先执行已存在场景的最小正交矩阵：

```text
nominal
wind gust
mass +20%
rotor 1 efficiency -15%
wind gust + rotor 1 efficiency -15%
```

对比至少包含 official PID 与一个当前最强已实现控制器。其他转子和控制器组合在
最小矩阵稳定后再扩展，避免把已有大量 YAML/Modelica 文件全部无差别重跑。

完成条件：故障事件时间、检测/响应、恢复时间、约束违规和前后指标可追溯。

### N4 调参与参数优化闭环

- 冻结 plant/state/frequency/trajectory；
- 建立参数版本和父子 run lineage；
- 先做 MWORKS 批量候选筛选；
- 输出失败类别、候选参数、目标函数和安全拒绝原因；
- 只将少量候选排入后续 Gazebo 确认队列。

完成条件：能够从一个失败 run 生成候选、重跑、比较、promote/rollback，且不覆盖历史。

### N5 离线显示与嵌入契约

- 使用已有 run bundle 生成统一 DisplayFrame；
- 验证 RViz/UE replay 的 run id、坐标、时间和事件一致；
- 实现/验证显示会话 mock、attach/detach/reset 和延迟字段；
- 不启动 live Gazebo，不把 replay 画面当作新运行证据。

完成条件：T0 replay 可复现、跨 run 无残留、延迟字段完整。

### N6 官方要求到证据矩阵

- 为每项官方要求登记 `implemented/measured/accepted`；
- 固定最终控制器对比表和图表清单；
- 统一报告、用户手册和演示视频所引用的 run id；
- 缺失结果保持空缺或 blocker，不填造数据。

完成条件：每个报告结论都能定位到 profile、raw、metrics、figure 和 manifest。

## 3. 当前禁止并发的工作

在 RACER 明确释放共享资源前，禁止：

```text
启动新的Gazebo world或PX4 SITL；
重启ROS master、MAVROS、FAST-LIO、RACER或共享bridge；
运行G9真实ROS/Gazebo回灌；
运行Gazebo风扰/转子故障验收；
以端口冲突为由杀共享进程；
修改RACER当前运行所依赖的profile、launch或参数。
```

## 4. 资源释放后的最短运行队列

```text
GZ1 official_pid完整起飞-悬停-降落
GZ2 official_pid 8字/螺旋统一指标
GZ3 MWORKS筛选出的最佳增强控制器A/B
GZ4 风扰 nominal vs disturbed
GZ5 rotor1 -15%与故障恢复
GZ6 其余G9控制器按门禁逐个回灌
GZ7 编队和多机故障单独验收
```

先跑最小代表场景，失败时回到对应离线层修复；不批量占用运行资源制造大量无效日志。

## 5. 状态边界

| 完成层级 | 允许声明 |
| --- | --- |
| L0 | schema/source/static/offline gate通过 |
| L1 | MWORKS模型级仿真和指标通过 |
| L2 | 历史数据回放/显示契约通过 |
| L3 | 当前Gazebo/PX4运行回灌通过 |

L0-L2 均不能替代 L3。当前目标是把 L0-L2 做到只剩明确、最小的 L3 运行队列。

## 6. 建板时静态基线

2026-07-15 已在不启动任何 live runtime 的条件下验证：

```text
python Scripts/quality/check_experiment_profile.py --all
  ok=true, checked_count=21

python Scripts/quality/build_experiment_preflight.py --all
  ok=true, checked_count=21

python -m pytest -q \
  Scripts/tests/test_experiment_profile_validator.py \
  Scripts/tests/test_trajectory_dynamics.py \
  Scripts/tests/test_metrics.py \
  Scripts/tests/test_metric_threshold_gate.py
  38 passed
```

该结果关闭 N0 的现有正式 Profile 基线检查，不代表 candidate、blocked profile、
MWORKS live 仿真或 Gazebo/PX4 运行通过。N0 后续只处理新接口字段、预期拒绝和新增
实验 Profile，不需要重复重建整个 Profile 体系。
