# Simulation

Sunray_yundrone 仿真相关功能包集合，包含 UAV 竞赛演示、评分脚本、Gazebo 插件、通用仿真工具与 Sunray 主仿真环境。

## 1. 目录说明

```text
Simulation/
├── 2025_uav_competition_demo/   # 2025 无人机竞赛示例（A*、APF、位置发布等）
├── future_2025_score/           # 比赛评分脚本
├── gazebo_plugin/               # Gazebo 插件集合（雷达、风场、随机障碍等）
├── simulator_utils/             # 通用仿真工具（地图、控制、可视化等）
├── sunray_simulator/            # Sunray 仿真主场景与启动文件
└── sysu_competition/            # 竞赛相关环境与源码
```

## 2. 环境依赖

- Ubuntu 20.04（推荐）
- ROS Noetic
- Gazebo（Noetic 默认版本）
- catkin 工具链（catkin_make 或 catkin build）
- 常用依赖：`mavros`、`rviz`、`tf`、`pcl`、`opencv`（按各包实际依赖安装）

> 提示：不同子目录为独立 ROS 包，建议先在工作空间执行 `rosdep` 补齐依赖。

## 3. 构建方式

将 `Simulation` 放入 Catkin 工作空间（例如 `~/catkin_ws/src/Simulation`）后执行：

```bash
cd ~/catkin_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make -DCMAKE_BUILD_TYPE=Release
source devel/setup.bash
```

若只想编译部分包，可在工作空间中使用白名单或 `catkin build <pkg_name>`。

## 4. 快速运行示例

### 4.1 运行 Sunray 基础仿真

```bash
roslaunch sunray_simulator sunray_px4_basic.launch
```

### 4.2 运行竞赛示例（A* / APF）

```bash
roslaunch 2025_uav_competition_demo Astar.launch
# 或
roslaunch 2025_uav_competition_demo APF.launch
```


## 5. 作为 Git 子模块使用

如果你希望将本目录作为独立仓库并在主工程中以子模块方式引用，可按以下流程：

### 5.1 在当前目录初始化并推送独立仓库

```bash
cd Simulation
git init
git add .
git commit -m "init Simulation repository"
git branch -M main
git remote add origin <your-simulation-repo-url>
git push -u origin main
```

### 5.2 在主仓库中添加子模块

```bash
cd <Sunray_yundrone_root>
git rm -r Simulation
git commit -m "remove local Simulation directory"
git submodule add <your-simulation-repo-url> Simulation
git commit -m "add Simulation as submodule"
```

团队成员拉取主仓库时：

```bash
git clone --recurse-submodules <main-repo-url>
# 或已有仓库执行
git submodule update --init --recursive
```

## 6. 常见问题

1. **找不到包或话题**
	- 确认已 `source devel/setup.bash`
	- 检查 `ROS_PACKAGE_PATH` 与工作空间层级是否正确

2. **Gazebo 模型加载失败**
	- 检查模型路径是否加入 `GAZEBO_MODEL_PATH`
	- 检查插件编译是否成功

3. **脚本无执行权限**
	- 执行 `chmod +x scripts/*.py`

## 7. 维护建议

- 新增功能优先放入对应子包，保持包边界清晰
- 启动配置变更时同步更新 `launch/` 与文档
- 若作为子模块使用，主仓库需及时更新子模块指针提交

