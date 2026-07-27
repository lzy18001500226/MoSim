# 工程源码迁移工作流

> 状态：目标架构已确认。2026-07-27，用户授权以“只复制、不移动、不删除、不切换活动
> 入口”的方式启动首批单组件迁移；当前已复制 `diff_planner`、`fuel`、`uav_utils`、
> `quadrotor_msgs`、`livox_ros_driver_compat`、`fast_lio` 与
> `sunray_planner_utils`、`sunray_uav_control` 到目标目录，均仍由旧路径作为唯一活动路径。
> 本文件定义执行顺序、证据和停止条件；目录归属的唯一权威是
> [`Docs/Design/架构.md` 第 8.2 节](../Design/架构.md)。不得从本文件推断任何组件已经
> 激活、可构建或可运行。

## 1. 目的和边界

目标是使交付给用户的源码包不依赖 `References/` 中的克隆仓库、示例或调研材料：用户只需
获取项目源码、按 README 配置环境、运行预检并在可见终端执行命令，即可启动对应的 Gazebo、
PX4、ROS、规划或 QGC 工作流。

目录的目标归属、功能边界和组件映射不在这里重复定义，统一以 `架构.md` 第 8.2 节为准。
本工作流不负责重写控制算法、改变仿真行为、把 QGC 接管为 ROS 运行时，或把 MWORKS/UE
原生工程强行迁入 `src/`。

当前 `References/` 仍可能被既有脚本、Profile、测试或构建配置引用。因此在所有依赖审计和
组件迁移完成前，它只是现状来源，不能被批量删除、忽略或视为已经从交付链路移除。

## 2. 启动条件

只有用户显式重新授权具体迁移范围后，才能开始执行。每次迁移任务必须先冻结以下输入：

1. **组件所有权清单**：组件名、当前路径、目标功能目录、负责人、运行/构建/测试入口和
   依赖它的 Profile、launch、脚本、CMake 或 Python 配置。
2. **来源与完整性清单**：上游 URL、固定 commit/tag、许可证、项目补丁、必要资源以及源/
   目标目录的哈希或文件清单。迁入组件必须带有 `UPSTREAM.md` 与 `PATCHES.md`。
3. **路径注册方案**：一个稳定的项目根和组件路径配置，供脚本、Profile、launch 和构建配置
   读取；禁止继续以相对层级猜测仓库根目录。
4. **组件级验收方案**：静态路径检查、最小预检或构建检查、允许的烟测以及结果存放位置。
   未获运行授权时，只做静态检查和 dry-run。
5. **干净的变更边界**：只纳入本组件相关文件；现有无关工作区改动不可被重置、清理、暂存或
   一并提交。

`Models/` 与 `UE5/` 是原生项目根。除非路径注册、构建检查和专门烟测均已写入并获授权，
它们不属于早期迁移组件。

## 3. 迁移阶段

### 阶段 0：盘点，不移动

1. 对选定组件建立源文件、必要资产、生成目录、许可证和活动依赖清单。
2. 在 `Config/`、`Scripts/`、`src/`、`apps/`、测试、launch、CMake、Profile 和文档入口中
   检索该组件及 `References/` 的活动引用。
3. 区分源码/必要资产与 `build`、`devel`、`install`、缓存、历史日志和临时结果；后五类不迁入
   新源码目录。
4. 给出迁移顺序和回退方式。尚不能说明最小验证方式的组件不得进入下一阶段。

### 阶段 1：稳定路径配置，不移动

1. 先建立或扩展唯一的项目根/组件路径配置，并让一个最小消费者读取它。
2. 对 QGC、CMake、ROS launch、Profile 与脚本的项目根推导逐项审计；不得保留依赖
   `CMAKE_SOURCE_DIR` 相对回退层级的隐式路径假设。
3. 为当前路径和目标路径建立显式解析测试或 dry-run，确认错误信息能指出缺失组件而非默默
   回退到 `References/`。
4. 这一步完成前，不复制任何运行源码。

### 阶段 2：复制一个功能组件

1. 只选择一个可独立验证的功能组件，复制到 `架构.md` 第 8.2 节定义的目标目录。
2. 同步放入来源、许可证、固定版本与本项目补丁说明；必要小型资源与组件同行，生成物不同行。
3. 保留旧副本作为只读回退来源，不修改其行为，也不把两个路径同时作为正常运行入口。
4. 不跨组件“顺手整理”目录，不移动 `Models/`、`UE5/`，也不处理未列入清单的引用。

### 阶段 3：改写活动入口

1. 仅改写该组件清单中列出的运行、构建、测试和 Profile 引用，使其解析新路径。
2. 新的路径解析失败必须明确失败；不得隐藏性回退到旧 `References/` 副本。
3. `Scripts/` 保持用户入口、预检、构建、诊断和分析职责。可复用业务实现应归入对应的
   `src/` 功能目录。
4. QGC 的上游源码、MoSim 扩展和补丁应按 `src/ground_station/qgc/` 的约束分别可追溯；
   不在此阶段扩大 QGC 功能或修改飞控职责。

### 阶段 4：组件级验证

按阶段 0 冻结的验收方案执行，最少包括：

1. 目标路径、来源文件和补丁说明存在且与清单一致。
2. 该组件的构建配置、测试、launch、Profile 和入口脚本不再活动引用旧
   `References/` 路径。
3. 通过对应静态检查以及最小预检、build 或 dry-run；运行时烟测只有在单独授权时才执行。
4. 新路径错误时能够给出可诊断错误，不能静默从旧路径加载。
5. 记录检查命令、版本、哈希、输出摘要和未解决依赖，放在该迁移任务声明的正常证据路径。

### 阶段 5：旧副本归档与交付核验

仅在阶段 4 通过、依赖审计完整且用户授权后，才可将旧 `References/` 副本归档或从交付包
剔除。任何删除或移动前必须再次核对源/目标哈希、活动引用和回退说明。

整个迁移完成的交付验收为：当前构建、launch、QGC 构建、测试和运行 Profile 均不再引用
`References/`；每个迁入组件可追溯上游来源、固定版本、许可证和补丁；用户无需在
`References/` 中定位源码即可按 README 配置并完成预检和运行。

## 4. 明确禁止项

- 不得一次性剪切、批量移动或批量删除目录。
- 不得用正在运行的 Gazebo、PX4、UE、QGC 或 MWORKS 实例替代路径、构建和日志证据。
- 不得为了“兼容”保留新旧两个活动加载面，或允许新路径静默回退到旧路径。
- 不得将 `build`、`devel`、`install`、缓存、历史日志或临时结果迁入源码树。
- 不得因本迁移执行未经授权的控制器、规划器、仿真或桌面 GUI 复跑。
- 不得使用 `git add -A`、`git clean`、`git reset --hard` 或对无关改动做任何清理。

## 5. 单组件交付记录

每个完成的组件迁移应至少留下以下可审核信息：

```text
component_id
旧路径与新路径
上游来源、版本、许可证、补丁说明
活动引用审计结果
源/目标哈希或文件清单
路径配置变更
执行的静态检查、预检/build/dry-run及其结果
未执行的运行时检查和原因
归档或交付包剔除决定
```

提交时只暂存已审核的本组件路径，执行 `git diff --cached --check`，提交并推送后再报告完成。
本工作流只规定迁移方法；当前工程的主线控制器证据门禁仍由
`Docs/Workflows/mainline_operations_board.md` 决定。

### 5.1 Diff-Planner 首批复制记录（2026-07-27）

```text
component_id: diff_planner
旧路径: References/Lab/planning_local/Diff-Planner
新路径: src/planning/diff_planner
活动路径: References/Lab/planning_local/Diff-Planner
迁移状态: copied_pending_activation
来源: https://github.com/DifferentialRobotics/Diff-Planner.git
固定版本: 旧导入快照未能恢复上游 commit；不得宣称已钉定版本
许可证: 根目录 GPL-3.0 已随副本保留；发布前仍需审计各 ROS 包许可证
项目补丁: 无算法、launch、CMake、参数或资源改动；仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照: 613 个文件，SHA-256 清单
          60f3ae2837c8b42f71c5e9892807ab5d40993fd50cb37053c86a496a7195daf1
交付负载: 排除 4 个本地 .vscode 配置和 1 个 Ogre 工具日志后，608 个文件与旧路径一致，
          bd9f049290b4ad38b7021869dad98a4be3a132fdd9c75d6f367f2222f65ffe62
静态检查: JSON 解析、注册表检查、Python 编译和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动 ROS/Gazebo/PX4/QGC/UE 或运行规划器
激活前置: 补齐上游 commit/submodule 身份、许可证审计、活动引用改写和受控 ROS1 验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.2 FUEL 复制记录（2026-07-27）

```text
component_id: fuel
旧路径: References/Lab/exploration_coverage/FUEL
新路径: src/planning/fuel
活动路径: References/Lab/exploration_coverage/FUEL
迁移状态: copied_pending_activation
来源: https://github.com/HKUST-Aerial-Robotics/FUEL.git
固定版本: 旧导入快照未能恢复上游 commit；不得宣称已钉定版本
许可证: 根目录 GPL-3.0 已随副本保留；发布前仍需审计内嵌 ROS 包和第三方资源许可证
项目补丁: 无算法、launch、CMake、参数、资源或资产改动；仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照: 1,541 个文件，SHA-256 清单
          ef7d5ac53f0f9ba98209f0468c49b9130a7965060c768dae123da13e724dcc27
交付负载: 排除 4 个本地 build 树及其中嵌套 devel 输出、3 个 Python bytecode、3 个本地 .so、
          3 个带绝对工作区路径的 LKH 运行时状态文件、2 个可由源码重建的 ELF、76 个
          Catkin/Dynamic Reconfigure 消息/配置生成物、6 个编辑器备份和 1 个 .cfgc
          动态配置字节码后，785 个文件与旧路径一致，
          b43afd26242b170e1b0f249b39d78fa751c0b2d83b320c544bc6e719ae402d25
静态检查: JSON 解析、复制载荷 SHA-256 比对、Python 编译和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动 ROS/Gazebo/PX4/QGC/UE 或运行 FUEL
激活前置: 补齐上游 commit/许可证、改写审计过的 FUEL 入口并完成受控 ROS1 验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.3 uav_utils 复制记录（2026-07-27）

```text
component_id: uav_utils
旧路径: References/Lab/planning_local/Fast-Drone-250/src/utils/uav_utils
新路径: src/common/utilities/ros1/uav_utils
活动路径: References/Lab/planning_local/Fast-Drone-250/src/utils/uav_utils
迁移状态: copied_pending_activation
来源: https://github.com/ZJU-FAST-Lab/Fast-Drone-250
固定版本: 旧导入快照未能恢复上游 commit；不得宣称已钉定版本
许可证: package.xml 声明 LGPLv3；旧组件未携带独立许可证文件，发布前仍需审计
项目补丁: 无源码、CMake、package.xml 或脚本改动；仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照与交付负载: 11 个文件，无 build、devel、install、缓存或编辑器本地文件，
                         SHA-256 清单 f00befb146bdb47cfb194d3dfa6a566c2d962f5d003d0704e8e9709a567e4aa8
静态检查: JSON 解析、复制载荷 SHA-256 比对和差异格式检查通过；4 个 Python 脚本中
          3 个可由当前 Python 3 编译，tf_assist.py 保留 Python 2 except 语法，未作修改
未执行项: 未改写入口，未构建、预检、启动 ROS/Gazebo/PX4/QGC/UE 或运行控制器
激活前置: 补齐上游 commit/许可证、改写审计过的消费者引用并完成受控 ROS1 验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.4 quadrotor_msgs 复制记录（2026-07-27）

```text
component_id: quadrotor_msgs
旧路径: References/Lab/planning_local/Fast-Drone-250/src/utils/quadrotor_msgs
新路径: src/integration/ros1_launch/quadrotor_msgs
活动路径: References/Lab/planning_local/Fast-Drone-250/src/utils/quadrotor_msgs
迁移状态: copied_pending_activation
来源: https://github.com/ZJU-FAST-Lab/Fast-Drone-250
固定版本: 旧导入快照未能恢复上游 commit；不得宣称已钉定版本
许可证: package.xml 声明 BSD；旧组件未携带独立许可证文件，发布前仍需审计
项目补丁: 无源码、CMake、package.xml、消息定义或库改动；仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照: 49 个文件，SHA-256 清单
          9eea29e626190d2eb007be41ac90020029994a9a7a89b24abef77c8924844112
交付负载: 排除 Catkin 自动生成的 src/quadrotor_msgs Python 消息输出目录和 2 个 *.msg~ 编辑器备份后，
          34 个文件与旧路径一致，d45bbfe4d83ebf1cbf5b95a8941c5b7a4548e00bf17b23b8a752dad712c3be41
静态检查: JSON 解析、复制载荷 SHA-256 比对和差异格式检查通过
未执行项: 未改写入口，未生成消息、构建、预检、启动 ROS/Gazebo/PX4/QGC/UE 或运行控制器
激活前置: 补齐上游 commit/许可证、改写审计过的 overlay 与消费者引用、生成消息并完成受控 ROS1 验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.5 livox_ros_driver_compat 复制记录（2026-07-27）

```text
component_id: livox_ros_driver_compat
旧路径: References/Lab/localization_slam/livox_ros_driver_compat
新路径: src/perception/livox_ros_driver_compat
活动路径: References/Lab/localization_slam/livox_ros_driver_compat
迁移状态: copied_pending_activation
来源: 项目本地 FAST-LIO ROS1 消息兼容包；不是完整的外部 Livox 驱动仓库
固定版本: 不适用；无外部上游 commit 可钉定
许可证: package.xml 声明 BSD；旧组件未携带独立许可证文件，发布前仍需审计
项目补丁: 无源码、CMake、package.xml 或消息定义改动；仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照与交付负载: 4 个文件，无 build、devel、install、缓存或编辑器本地文件，
                         SHA-256 清单 c2946a7188009abdd0aa22d1e9496ce1a2dc05af748703fbf819fe668ee63cb4
静态检查: JSON 解析、复制载荷 SHA-256 比对和差异格式检查通过
未执行项: 未改写入口，未生成消息、构建、预检、启动 ROS/Gazebo/PX4/QGC/UE 或运行 FAST-LIO
激活前置: 审计包名/消息契约、改写审计过的 FAST-LIO 消费者引用、生成消息并完成受控 ROS1 验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.6 FAST-LIO 复制记录（2026-07-27）

```text
component_id: fast_lio
旧路径: References/Lab/localization_slam/FAST_LIO
新路径: src/perception/fast_lio
活动路径: References/Lab/localization_slam/FAST_LIO
迁移状态: copied_pending_activation
来源: https://github.com/hku-mars/FAST_LIO.git
固定版本: 旧导入快照未能恢复上游 FAST-LIO 与 ikd-Tree commit；不得宣称已钉定版本
许可证: 根 LICENSE 为 GPL-2.0 文本，而 package.xml 声明 BSD；发布前必须完成冲突审计
项目补丁: 无源码、CMake、package.xml、launch、配置或传感器文件改动；仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照: 85 个文件，SHA-256 清单
          a4931b9ce91f98384a9c785ac7aa5b5103acb056e4cf1c3ec5c3ccb33918aa1d
交付负载: 排除 doc 演示媒体、Log 历史运行输出和 PCD 输出后，49 个文件与旧路径一致，
          6f830a3fbd685e84894e646e29a16222996a7f24743432dc0fee0f04ac5e8bfe；新路径保留 Log/、PCD/ 空占位目录
静态检查: JSON 解析、复制载荷 SHA-256 比对和差异格式检查通过
未执行项: 未改写入口，未初始化子模块、构建、预检、启动 ROS/Gazebo/PX4/QGC/UE、FAST-LIO 或 RViz
激活前置: 补齐 FAST-LIO/ikd-Tree 版本和许可证、改写审计过的入口、完成 ROS1 MID360/Sunray 受控验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.7 sunray_planner_utils 复制记录（2026-07-27）

```text
component_id: sunray_planner_utils
旧路径: References/Sunray/General_Module/sunray_planner_utils
新路径: src/integration/ros1_launch/sunray_planner_utils
活动路径: References/Sunray/General_Module/sunray_planner_utils
迁移状态: copied_pending_activation
来源: 保留的 YunDrone Sunray 本地导入包；上游仓库和 commit 均未能从快照恢复
固定版本: 不可恢复；不得宣称已钉定上游 Git commit
许可证: package.xml 声明 TODO，且组件不携带独立许可证文件；发布前必须完成审计
项目补丁: 无源码、CMake、package.xml、launch、配置或脚本改动；仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照与交付负载: 40 个文件，无 build、devel、install、缓存、媒体或编辑器备份排除项，
                         SHA-256 清单 ea21ddffacb2f555eb68d1ae38fd8c5be3f622e1ca1e5a8a35bda6ee3105e697
静态检查: JSON 解析、复制载荷 SHA-256 比对和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动 ROS/Gazebo/PX4/QGC/UE、规划器或 RViz
激活前置: 审计上游/许可证；处理 CMake 中对 ../sunray_common/common_lib 的相邻路径依赖；
          改写审计过的入口并完成受控 ROS1 验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.8 sunray_uav_control 复制记录（2026-07-27）

```text
component_id: sunray_uav_control
旧路径: References/Sunray/General_Module/sunray_uav_control
新路径: src/flight_stack/mavros/sunray_uav_control
活动路径: References/Sunray/General_Module/sunray_uav_control
迁移状态: copied_pending_activation
来源: 保留的 YunDrone Sunray 本地导入包；上游仓库和 commit 均未能从快照恢复
固定版本: 不可恢复；不得宣称已钉定上游 Git commit
许可证: package.xml 声明 TODO，且组件不携带独立许可证文件；内嵌 MAVLink 快照也需发布前审计
项目补丁: 无源码、CMake、package.xml、launch、MAVLink、配置、脚本、mesh 或 RViz 文件改动；
          仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照: 587 个文件，SHA-256 清单
          847699b0a94457610dda738d22cb411a3920c79a1e53ae04cda3cd6dd6c5d3f2
交付负载: 排除 20 个 launch/sunray_control_node.launch.bak_mosim_* 历史备份后，
          567 个文件与旧路径一致，2d723ac1e96c310b0d9ece1c830d7c9613ea014c9ff3363f15478ad1d9c192d8；
          保留 CMake 直接引用的内嵌 MAVLink 头文件快照和 uav.mesh 运行时资产
静态检查: JSON 解析、复制载荷 SHA-256 比对和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动 ROS/Gazebo/PX4/MAVROS/QGC/UE、控制器或 RViz
激活前置: 审计 Sunray/MAVLink 上游和许可证；处理 ../sunray_common/common_lib 相邻路径依赖；
          审计 generate_messages()/sunray_control_gencpp 契约，改写审计过的入口并完成受控 ROS1 验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.9 sunray_common 复制记录（2026-07-27）

```text
component_id: sunray_common
旧路径: References/Sunray/General_Module/sunray_common
新路径: src/common/utilities/ros1/sunray_common
活动路径: References/Sunray/General_Module/sunray_common
迁移状态: copied_pending_activation
来源: 保留的YunDrone Sunray本地导入包；上游仓库和commit均未能从快照恢复
固定版本: 不可恢复；不得宣称已钉定上游Git commit
许可证: sunray_msgs/package.xml声明TODO，且组件不携带独立许可证文件；发布前必须完成审计
项目补丁: 无公共头文件、消息、CMake、package.xml、launch、配置或脚本改动；
          仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照与交付负载: 40个文件，无build、devel、install、缓存、媒体或编辑器备份排除项，
                         SHA-256清单 25fdafec215f7fdd5d023dd8383b39f22d2eda43125afa91ada1d922123bb213
静态检查: JSON解析、复制负载SHA-256比对和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动ROS/Gazebo/PX4/MAVROS/QGC/UE、生成sunray_msgs消息或运行控制器
激活前置: 审计Sunray上游/许可证；处理sunray_uav_control与sunray_planner_utils
          对 ../sunray_common/common_lib 的相邻路径依赖；审计sunray_msgs消息生成契约；
          改写审计过的入口并完成受控ROS1验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.10 sunray_tutorial 复制记录（2026-07-27）

```text
component_id: sunray_tutorial
旧路径: References/Sunray/General_Module/sunray_tutorial
新路径: src/planning/mission_adapters/sunray_tutorial
活动路径: References/Sunray/General_Module/sunray_tutorial
迁移状态: copied_pending_activation
来源: 保留的YunDrone Sunray本地导入包；上游仓库和commit均未能从快照恢复
固定版本: 不可恢复；不得宣称已钉定上游Git commit
许可证: package.xml声明TODO，且组件不携带独立许可证文件；发布前必须完成审计
项目补丁: 无任务发布器、CMake、package.xml、launch、配置或脚本改动；
          仅新增 .gitattributes、UPSTREAM.md、PATCHES.md
原始快照与交付负载: 61个文件，无build、devel、install、缓存、媒体或编辑器备份排除项，
                         SHA-256清单 6bf007f55c91660154afb4fd22ffbcd6114218b2ee4f907d7f674ef703dd65dc
静态检查: JSON解析、复制负载SHA-256比对和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动ROS/Gazebo/PX4/MAVROS/QGC/UE、生成消息或运行任务
激活前置: 审计Sunray上游/许可证；处理对 ../sunray_common/common_lib 的相邻路径依赖；
          审计sunray_msgs、OpenCV、Boost与本地消息生成契约；改写审计过的run_demo.launch消费者并完成受控ROS1验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.11 px4ctrl 复制记录（2026-07-27）

```text
component_id: px4ctrl
旧路径: References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl
新路径: src/control/runtime_adapters/px4ctrl
活动路径: References/Lab/planning_local/Fast-Drone-250/src/realflight_modules/px4ctrl
迁移状态: copied_pending_activation
来源: https://github.com/ZJU-FAST-Lab/Fast-Drone-250；保留快照未能恢复确切上游commit
固定版本: 不可恢复；不得宣称已钉定上游Git commit
许可证: LICENSE保留GPL-3.0正文，package.xml声明GPLv3
项目补丁: 复制前活动工作树已含CMakeLists.txt与src/controller.cpp的P10后端改动；
          已作为当前源码快照原样保留，迁移仅新增.gitattributes、UPSTREAM.md、PATCHES.md
原始快照与交付负载: 17个文件，无build、devel、install、缓存、媒体或编辑器备份排除项，
                         SHA-256清单 c293274d4f02168e22a682bba6243aa255a6ff6a5f5f4c1f2831327ceed86dcd
静态检查: JSON解析、复制负载SHA-256比对和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动ROS/Gazebo/PX4/MAVROS/QGC/UE、生成代码或运行控制器
激活前置: 审计Fast-Drone-250上游/GPL义务；单独审核并提交P10工作树补丁；
          改写审计过的脚本、Profile和ROS overlay路径；验证生成C/C++契约、后端选择器并完成受控ROS1验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.12 fixed_formation 复制记录（2026-07-27）

```text
component_id: fixed_formation
旧路径: References/Lab/swarm_coordination/Swarm-Formation
新路径: src/planning/fixed_formation
活动路径: References/Lab/swarm_coordination/Swarm-Formation
迁移状态: copied_pending_activation
来源: https://github.com/ZJU-FAST-Lab/Swarm-Formation.git；保留快照未能恢复确切上游commit
固定版本: 不可恢复；不得宣称已钉定上游Git commit
许可证: LICENSE保留GPL-3.0正文
项目补丁: 复制前活动工作树已含6个规划源/头文件的碰撞与重规划改动；
          已作为当前源码快照原样保留，迁移仅新增.gitattributes、UPSTREAM.md、PATCHES.md
原始快照: 534个文件，SHA-256清单 8269c172068e8d9dc41ea9a654f34e9dede12659ca5cd795e847069213caea6d
交付负载: 排除fig/文档演示媒体与所有.vscode/本地编辑器配置后，525个文件，
          SHA-256清单 c3950cc62a2063243997dc4b7e7897a783f512f5682e9178c47aa148d91cf605
静态检查: JSON解析、复制负载SHA-256比对和差异格式检查通过
未执行项: 未改写入口，未构建、预检、启动ROS/Gazebo/PX4/MAVROS/QGC/UE或运行规划器
激活前置: 审计Swarm-Formation上游/GPL义务；单独审核并提交碰撞/重规划工作树补丁；
          改写审计过的Factory脚本、Profile和ROS overlay路径；验证工作区补丁假设并完成受控ROS1验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.13 QGroundControl 上游快照复制记录（2026-07-27）

```text
component_id: qgroundcontrol
旧路径: apps/flight_console/vendor/qgroundcontrol
新路径: src/ground_station/qgc/qgroundcontrol
活动路径: apps/flight_console/vendor/qgroundcontrol
迁移状态: copied_pending_activation
来源: https://github.com/mavlink/qgroundcontrol；保留目录不是嵌套Git仓库，确切上游commit不可恢复
固定版本: 不可恢复；本地基线为22224f94079bb85a5de6f6856d5fd157bb68eee6，不得宣称为QGC上游版本
许可证: 同时保留LICENSE-APACHE与LICENSE-GPL，发布与构建许可证选择尚需审计
项目补丁: 复制前活动工作树已含src/UI/MainWindow.qml本地改动；已作为当前源码快照原样保留，
          迁移仅新增UPSTREAM.md、PATCHES.md
交付负载: 排除android/.gradle/缓存与custom/生成覆盖层后，2,638个文件、325,541,737字节，
          SHA-256清单 a8c7231105f1469ed703d45e33498c91562daa48f09755f07f6903bcc7a8e29c
覆盖层边界: custom/由apps/flight_console/mosim物化，权威源码另存为qgc_mosim_extension；
          custom-example/仍作为QGC上游源码保留
静态检查: JSON解析、源/目标SHA-256比对、缓存与生成覆盖层排除检查通过
未执行项: 未改写入口，未构建、预检、启动QGC、ROS、Gazebo、PX4、MAVROS、UE或RViz
激活前置: 恢复或固定QGC上游版本与许可证选择；处理cmake/Git.cmake对父Git仓库的版本推导；
          审计生成覆盖层物化流程、改写审计过的构建/启动入口并完成受控QGC构建验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```

### 5.14 MoSim QGC 扩展快照复制记录（2026-07-27）

```text
component_id: qgc_mosim_extension
旧路径: apps/flight_console/mosim
新路径: src/ground_station/qgc/mosim_extension
活动路径: apps/flight_console/mosim
迁移状态: copied_pending_activation
来源: 项目自有QGC custom-build源码，不是独立上游克隆仓库
固定版本: 不适用；以本项目工作树快照为准
许可证: 未发现独立许可证文件；与QGC双许可证源码的交付关系需在发布前审计
项目补丁: 复制前活动工作树含5个QML/C++修改与3个Factory地图数据文件；
          已作为当前源码快照原样保留，迁移仅新增UPSTREAM.md、PATCHES.md
原始快照与交付负载: 15个文件、12,086,470字节，
                         SHA-256清单 2b98e1588ef5636000cb6f310ce13c16d1079448a11d3a60f720f77bfa79d857
静态检查: JSON解析、源/目标SHA-256比对和Factory地图资产存在检查通过
未执行项: 未改写物化脚本，未构建、预检、启动QGC、ROS、Gazebo、PX4、MAVROS、UE或RViz
激活前置: 审计Scripts/ui/materialize_qgc_custom_overlay.py的输入/输出边界；
          将其改为受控消费canonical扩展路径，验证工厂地图资源路径并完成受控QGC构建验证
旧副本处置: 保留且不修改；无归档、删除或交付包剔除决定
```
