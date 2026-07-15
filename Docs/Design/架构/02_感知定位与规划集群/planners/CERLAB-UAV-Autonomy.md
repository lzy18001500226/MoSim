# CERLAB-UAV-Autonomy

## 定位

CERLAB-UAV-Autonomy 位于
`References/Lab/exploration_coverage/CERLAB-UAV-Autonomy`。上游是 CMU
CERLAB 的 UAV autonomy framework，README 声明覆盖 simulator、perception、
mapping、planning、control，并包含 navigation、unknown exploration 和
inspection demo。

它是 HighStar/FUEL/FALCON 后的 source-backed 候选，不是当前已接入的
MoSim runtime 主线。

## 上游边界

README 声明：

```text
tested on ROS Melodic / ROS Noetic
depends on octomap, mavros, vision_msgs
simulation demo uses uav_simulator
exploration demo uses dynamic_exploration.launch
real/PX4 route requires robot pose/odometry and depth image
```

这意味着 CERLAB 与当前 MoSim 有两个潜在优势：

1. ROS Noetic 与 MAVROS/PX4 路线相对接近；
2. exploration 明确以 UAV autonomy 为目标，而不是地面机器人 frontier-only
   demo。

同时也有两个适配风险：

1. 上游默认 simulator、topic、frame 和 depth image 契约与 Sunray/MID360
   不同；
2. 其 tracking_controller / trajectory_planner 不能直接替换 MoSim 的
   px4ctrl 权威控制链，必须通过 Planner Adapter 输出中间规划命令。

## MoSim 接入门禁

```text
CERLAB-C0 source audit:
  识别 autonomous_flight、map_manager、trajectory_planner、tracking_controller
  的输入/输出/topic/frame/launch分支，确认 simulation/px4 分支状态。

CERLAB-C1 build preflight:
  在隔离 ROS1 Noetic workspace 中做最小 catkin build，不污染当前 Sunray
  runtime workspace。

CERLAB-C2 topic bridge dry-run:
  MoSim odom + MID360/depth adapter -> CERLAB mapping/planning input；
  CERLAB exploration output -> MoSim Planner Adapter；
  dry-run 不允许直接发布 MAVROS 控制。

CERLAB-C3 Factory single-UAV runtime:
  使用 Factory L2 clean world、PX4/MAVROS/px4ctrl/RViz/log/coverage packet
  运行，记录 coverage、轨迹、命令、Z安全和终态。
```

## 当前状态

当前只完成入库，尚未完成 C0-C3。不得声明 CERLAB 已解决 Factory 室内自主探索。

## 禁止声明

不得因为 CERLAB 上游 demo 可运行，就声称 MoSim Factory L2 可运行。不得直接
切换到 CERLAB controller 或 simulator 来绕过当前 Sunray/PX4/px4ctrl 证据链。
