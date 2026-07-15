# ILC / Iterative Learning Control

> Status: BACKLOG / reference and model route required.

## 链路位置

ILC 更适合作为重复轨迹任务的学习增强层，而不是第一阶段直接替代
px4ctrl 的名义控制器。它可以作用于：

```text
trajectory_profile / reference shaper
或
nominal controller augmentation
```

典型用途是对 8 字、圆形、螺旋等可重复轨迹，根据上一轮跟踪误差修正下一轮
参考或前馈项。

## 输入

```text
previous_run_reference
previous_run_tracking_error
current_reference
state_source_profile
learning_gain
filter / regularization
```

## 输出

第一阶段建议输出：

```text
corrected_reference
或
feedforward_correction
```

不建议第一版直接输出姿态、推力或电机命令。

## Simulink/MWORKS路线

```text
重复轨迹日志
  -> 误差对齐
  -> 学习律更新
  -> 修正参考/前馈
  -> 同一px4ctrl或代表控制器跟踪
```

ILC 可以先在 Simulink/MWORKS 中做离线重复轨迹学习；进入 Gazebo 前必须固定：

```text
轨迹周期
时间对齐方式
误差滤波
学习增益
饱和和安全限幅
```

## Gazebo接入

首选不改变控制器输出层级：

```text
ILC Reference Shaper
  -> Trajectory Server
  -> px4ctrl / SE3 / PID
  -> ATTITUDE_THRUST Adapter
```

## 证据门禁

| Gate | 要求 |
| --- | --- |
| E1 | 有官方示例、论文或开源实现 |
| E2 | MWORKS/Simulink中重复轨迹误差逐轮下降 |
| E3 | 修正参考或前馈项可离线复现 |
| E4 | Gazebo中同一轨迹多轮误差下降，且不违反安全约束 |

## 禁止声明

```text
不得把单轮调参结果说成ILC。
不得用ILC掩盖基础控制器不稳定。
不得在没有时间对齐和限幅时直接叠加学习修正。
```
