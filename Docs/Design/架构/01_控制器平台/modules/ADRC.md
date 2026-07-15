# ADRC / Active Disturbance Rejection Control

> Status: BACKLOG / augmentation semantics must be frozen before integration.

## 链路位置

ADRC 在 MoSim 中优先作为扰动观测和补偿增强模块，不作为第一阶段独立主控制器
抢占 px4ctrl 基线。其核心组件通常包括：

```text
Tracking Differentiator
Extended State Observer / ESO
Nonlinear State Error Feedback
Disturbance Compensation
```

第一阶段可先实现 ESO / disturbance compensation 子集，并明确标注为
`ESO-based augmentation`，不得直接宣称完整 ADRC。

## 输入

```text
state_error
nominal_control_output
model_output
measured_state
observer_params
sample_time
```

## 输出

```text
disturbance_estimate
bounded_control_compensation
diagnostics
```

ADRC 模块不直接发布 MAVROS setpoint；必须经过名义控制器或 SafetySupervisor。

## Simulink/MWORKS路线

```text
nominal controller
  -> ESO / ADRC observer
  -> disturbance estimate
  -> bounded compensation
  -> SafetySupervisor
  -> ATTITUDE_THRUST Adapter
```

实现时必须冻结：

```text
观测器阶次
带宽参数
采样周期
补偿限幅
噪声敏感性
reset语义
```

## Gazebo接入

首选作为 augmentation profile：

```text
controller_profile: px4ctrl / PID / SE3
augmentation_profile: eso_adrc_v1
adapter_profile: mavros_attitude_thrust_v1
```

## 证据门禁

| Gate | 要求 |
| --- | --- |
| E1 | 有论文、教材、官方示例或开源实现 |
| E2 | MWORKS/Simulink观测器在噪声和扰动下稳定 |
| E3 | 补偿项有界、可复现、可离线测试 |
| E4 | Gazebo风扰/参数摄动下比无增强基线改善，且无振荡放大 |

## 禁止声明

```text
不得把只有ESO的实现称为完整ADRC。
不得绕过SafetySupervisor直接叠加无限补偿。
不得用ADRC补偿状态源坐标系错误或基础控制器发散。
```
