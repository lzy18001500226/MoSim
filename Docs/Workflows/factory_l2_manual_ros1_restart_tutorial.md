# Factory L2 ROS1 与 QGC 手工重启教程（PowerShell）

本教程只重新启动并检查 Factory L2 的单机基础链路：

```text
Windows PowerShell
  -> WSL Ubuntu-20.04 -> ROS1 Noetic -> Gazebo Classic -> PX4 SITL -> MAVROS
                                           |
                                           +-> UDP 14550 -> Windows MoSim Ground Control / QGC
```

QGC 在 Windows 上运行，Gazebo、PX4 和 MAVROS 在 WSL 的 Ubuntu-20.04 中运行。
本教程不启动 QGC 的任务 Profile，不启动 FAST-LIO、px4ctrl、规划器或 UE，也不执行
解锁、起飞、航点上传或自动任务。

## 0. 使用规则

1. 全部代码块都在 **Windows PowerShell** 中执行；不需要进入 Bash 提示符后再粘贴命令。
2. 需要四个 PowerShell 标签页：`停止/检查`、`终端 A`、`终端 B`、`终端 C`；QGC 可以使用第五个标签页。
3. 每次新的重试都改一次 `RUN_ID`，并在所有标签页使用同一个值。
4. PowerShell 代码里的 `@' ... '@` 是传给 WSL 的 Bash 内容。不要单独复制其中的行到
   PowerShell，也不要把普通 Bash 的 `export` 命令直接粘贴到 PowerShell。

在每个需要运行 WSL 命令的 PowerShell 标签页，先执行下面的公共准备块。它通过 Base64
传递 Bash 内容，避免 PowerShell 展开 Linux 变量。

```powershell
Set-Location C:\Users\HP\Desktop\MoSim

$RunId = 'factory_l2_manual_restart_20260809_02'

function Invoke-MoSimUbuntu20 {
    param([Parameter(Mandatory)][string]$BashScript)

    $encoded = [Convert]::ToBase64String(
        [System.Text.Encoding]::UTF8.GetBytes($BashScript)
    )
    & wsl.exe -d Ubuntu-20.04 --exec bash -lc "printf '%s' $encoded | base64 --decode | bash"
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "Ubuntu-20.04 command failed with exit code $exitCode."
    }
}
```

## 1. 先结束旧的 Factory L2 运行

优先回到原来正在显示 `roslaunch` 日志的 PowerShell 窗口，在该窗口按一次 `Ctrl+C`，等待它
返回 PowerShell 提示符。不要在 Gazebo 窗口、QGC 窗口或已经结束的检查窗口按 `Ctrl+C`。

随后在“停止/检查”PowerShell 标签页执行上节的公共准备块，再执行：

```powershell
$bash = @'
pgrep -af '[r]oslaunch .*factory_l2_sunray_px4_gazebo.launch|[g]zserver .*factoryenvironmentcollect_l2_static_review_clean|[p]x4 .*sitl_sunray150_with_mid360_0|[m]avros_node' || true
'@
Invoke-MoSimUbuntu20 $bash
```

通过条件：没有输出。此时旧的 Factory L2 `roslaunch`、Gazebo、PX4 和 MAVROS 都已结束。

若原来的启动窗口已经丢失，且上述检查仍显示
`factory_l2_sunray_px4_gazebo.launch`，在同一个“停止/检查”标签页执行下面的**定向**停止命令：

```powershell
$bash = @'
while read -r pid; do
  [[ -z "$pid" ]] || kill -INT "$pid"
done < <(pgrep -f '[r]oslaunch .*factory_l2_sunray_px4_gazebo.launch' || true)

sleep 5
pgrep -af '[r]oslaunch .*factory_l2_sunray_px4_gazebo.launch|[g]zserver .*factoryenvironmentcollect_l2_static_review_clean|[p]x4 .*sitl_sunray150_with_mid360_0|[m]avros_node' || true
'@
Invoke-MoSimUbuntu20 $bash
```

最后一行仍有进程输出时，不要运行广泛的 `pkill`、`kill -9` 或“停止所有仿真”脚本。保留该输出，
因为其他任务可能拥有别的 Sunray 运行实例。

## 2. 终端 A：准备并启动 Gazebo、PX4 与 MAVROS

在“终端 A”PowerShell 标签页先执行第 0 节的公共准备块，然后执行下面完整代码。它会保持前台、
显示 Gazebo/PX4/MAVROS 的实时输出，并打开 Gazebo 窗口。

```powershell
$bash = @'
set -o pipefail
cd /mnt/c/Users/HP/Desktop/MoSim

export PROJECT_ROOT=$PWD
export RUN_ID=__RUN_ID__
export MOSIM_RUNTIME_OVERLAY_ID=$RUN_ID
export RESULT_DIR="$PROJECT_ROOT/Results/sunray_ros1/$RUN_ID"
export WORLD_FILE="$PROJECT_ROOT/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf"
export FACTORY_MODEL_PATH="$PROJECT_ROOT/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models"

mkdir -p "$RESULT_DIR"
source Scripts/sunray/resolve_local_ros1_runtime.sh

bash Scripts/sunray/check_sunray_ros1_runtime_preflight.sh 2>&1 | tee "$RESULT_DIR/preflight.txt"
if [[ "${PIPESTATUS[0]}" -ne 0 ]]; then exit 1; fi

bash Scripts/sunray/prepare_local_ros1_runtime_overlay.sh --workspace "$SUNRAY_WS" 2>&1 | tee "$RESULT_DIR/runtime_overlay.txt"
if [[ "${PIPESTATUS[0]}" -ne 0 ]]; then exit 1; fi

[[ -e "$SUNRAY_WS/devel" ]] || ln -s "$LOCAL_ROS1_WS/devel" "$SUNRAY_WS/devel"
export SUNRAY_LIVOX_PLUGIN_FILENAME="$LOCAL_ROS1_WS/devel/lib/liblivox_laser_simulation.so"

python3 Scripts/sunray/sync_assembled_model_into_sunray_ros1.py \
  --project-root "$PROJECT_ROOT" \
  --sunray-ws "$SUNRAY_WS" \
  --manifest "$RESULT_DIR/assembled_model_sync.json" 2>&1 | tee "$RESULT_DIR/assembled_model_sync.txt"
if [[ "${PIPESTATUS[0]}" -ne 0 ]]; then exit 1; fi

source /usr/share/gazebo/setup.sh
source /opt/ros/noetic/setup.bash
source "$SUNRAY_PX4_DIR/Tools/simulation/gazebo-classic/setup_gazebo.bash" "$SUNRAY_PX4_DIR" "$PX4_BUILD_DIR"
source "$LOCAL_ROS1_WS/devel/setup.bash"
source "$SUNRAY_WS/devel/setup.bash"

export ROS_PACKAGE_PATH="$PX4_ROS1_OVERLAY_PKG:${SUNRAY_WS}/simulation:${SUNRAY_WS}/General_Module:${LOCAL_ROS1_WS}/src:${SUNRAY_PX4_DIR}:/opt/ros/noetic/share:${ROS_PACKAGE_PATH:-}"

roslaunch Scripts/sunray/factory_l2_sunray_px4_gazebo.launch \
  project_root:="$PROJECT_ROOT" \
  uav_num:=1 \
  vehicle:=sunray150_with_mid360 \
  gui:=true \
  world:="$WORLD_FILE" \
  factory_model_path:="$FACTORY_MODEL_PATH" \
  use_sim_time:=true \
  uav1_init_x:=-10.575025 \
  uav1_init_y:=-19.36313 \
  uav1_init_z:=0.2 \
  uav1_init_yaw:=0
'@

$bash = $bash.Replace('__RUN_ID__', $RunId)
Invoke-MoSimUbuntu20 $bash
```

不要单独启动 `roscore`；最后一行 `roslaunch` 会在没有 ROS master 时自行启动它。

终端 A 不能关闭。其最终返回 PowerShell 提示符只会发生在你按 `Ctrl+C` 结束整套运行之后。

## 3. 终端 B：确认 Gazebo 已生成 `uav1`

终端 A 已开始持续输出后，在“终端 B”PowerShell 标签页先执行第 0 节的公共准备块，再执行：

```powershell
$bash = @'
cd /mnt/c/Users/HP/Desktop/MoSim

export RUN_ID=__RUN_ID__
export RESULT_DIR="$PWD/Results/sunray_ros1/$RUN_ID"
export ROS_MASTER_URI=http://localhost:11311

source /opt/ros/noetic/setup.bash
source build/ros1/local_source_ws/devel/setup.bash
mkdir -p "$RESULT_DIR"

python3 Scripts/sunray/wait_for_gazebo_model.py \
  --model uav1 \
  --timeout-s 240 \
  --output "$RESULT_DIR/gazebo_uav1.txt"

cat "$RESULT_DIR/gazebo_uav1.txt"
'@

$bash = $bash.Replace('__RUN_ID__', $RunId)
Invoke-MoSimUbuntu20 $bash
```

通过条件：

```text
model: uav1
status: ready
```

若结果是 `status: timeout`，不要启动终端 C。保留终端 A 最后 80 行以及
`Results\sunray_ros1\<RUN_ID>\gazebo_uav1.txt`。

## 4. 终端 C：确认 MAVROS 已连接 PX4

只有终端 B 显示 `status: ready` 后，才在“终端 C”PowerShell 标签页执行第 0 节的公共准备块，
然后执行：

```powershell
$bash = @'
cd /mnt/c/Users/HP/Desktop/MoSim

export RUN_ID=__RUN_ID__
export RESULT_DIR="$PWD/Results/sunray_ros1/$RUN_ID"
export ROS_MASTER_URI=http://localhost:11311

source /opt/ros/noetic/setup.bash
source build/ros1/local_source_ws/devel/setup.bash
mkdir -p "$RESULT_DIR"

python3 Scripts/sunray/wait_for_mavros_state.py \
  --topic /uav1/mavros/state \
  --timeout-s 180 \
  --output "$RESULT_DIR/mavros_state.txt"

cat "$RESULT_DIR/mavros_state.txt"
'@

$bash = $bash.Replace('__RUN_ID__', $RunId)
Invoke-MoSimUbuntu20 $bash
```

通过条件是：

```text
connected: True
```

此阶段 `armed: False` 是预期状态，`AUTO.LOITER` 等模式也可以接受。这只证明
Gazebo/PX4/MAVROS 启动和遥测链路已经就绪，不证明起飞、控制器、定位、规划或闭环飞行。

## 5. 启动 Windows 端 QGC

在独立的“QGC”PowerShell 标签页运行：

```powershell
Set-Location C:\Users\HP\Desktop\MoSim
& .\Scripts\cmd\启动MoSim地面站.cmd
```

该入口只启动 Windows 端的 MoSim Ground Control/QGC。它成功的最低条件是 PowerShell 输出
`main window ready`，且出现 MoSim Ground Control 主窗口。它不会启动或重启 Gazebo、PX4、
MAVROS、ROS、控制器或规划器。

如果已经有一个 MoSim Ground Control 窗口，启动器会复用它。需要真正重开 QGC 时，先正常关闭该
窗口，再重新运行上面的 PowerShell 命令。

## 6. 在 QGC 中连接 PX4

当前项目的端口合同是：PX4 的 GCS MAVLink 链路默认把远端 UDP 端口设为 `14550`，QGC 的
`UDP Link (AutoConnect)` 默认也监听 `14550`。因此在终端 C 已通过后，QGC 应先尝试自动发现
该飞机。

1. 在 QGC 主窗口打开 Fly View，等待出现一架 PX4 车辆及持续更新的姿态、模式或电池字段。
2. 打开 QGC 的 Application Settings，确认“UDP 自动连接”已启用，监听端口为 `14550`。
3. 打开 Comm Links，若已存在 `UDP Link (AutoConnect)`，保持它连接，不要再添加第二个相同端口的
   UDP 链路。
4. 只有在自动 UDP 链路不存在或已经被明确禁用时，才在 Comm Links 新建一个 UDP 链路，监听端口填
   `14550`，然后连接该链路。

可在 QGC PowerShell 标签页检查 Windows 是否已由 QGC 监听端口：

```powershell
$endpoint = Get-NetUDPEndpoint -LocalPort 14550 -ErrorAction SilentlyContinue
if ($null -eq $endpoint) {
    Write-Warning 'Windows 上没有进程监听 UDP 14550。先在 QGC 中启用 UDP 自动连接或创建一个 UDP 14550 链路。'
} else {
    $endpoint | Select-Object LocalAddress, LocalPort, OwningProcess
    $endpoint |
        ForEach-Object { Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue } |
        Select-Object Id, ProcessName, MainWindowTitle
}
```

这个 PowerShell 检查只证明 Windows 正在监听端口，不证明已经接收到 MAVLink 数据。真正的连接
通过条件是 QGC Fly View 中出现活动 PX4 车辆并持续更新遥测，且终端 C 仍是 `connected: True`。

QGC 的 Factory L2 底图上暂时没有动态飞机、航迹或任务边界是正常的：手工启动链没有创建 QGC
`RunManifest` 和地图 sidecar。不要把底图可见或端口被监听当成飞控、任务或地图运行成功。

## 7. QGC 连接失败时的顺序

先不要重启全部进程，也不要在 QGC 中尝试解锁或起飞。按下面顺序判断：

1. 终端 B 必须先是 `uav1 / ready`，终端 C 必须先是 `connected: True`。
2. QGC 必须已打开，且第 6 节的 `Get-NetUDPEndpoint` 能看到 UDP `14550` 的监听者。
3. 若 QGC 自动 UDP 已禁用，在 QGC 内启用它并确认监听端口为 `14550`；不要与同端口的自动链路
   同时新增一个重复的手工 UDP 链路。
4. 若窗口已打开、端口也被监听，但 Fly View 仍没有活动车辆，保存 QGC 的连接错误文本、终端 A
   最后 80 行、`gazebo_uav1.txt` 与 `mavros_state.txt`。这时是 QGC-MAVLink/WSL 网络边界的
   明确排查点，不能通过改控制器、改地图或重复启动第二套 Gazebo 来掩盖。

本手工 Factory L2 会话已经有自己的 `roslaunch`。在 QGC 中不要点击“复制启动命令”，也不要运行
`Scripts\ui\start_flight_simulation.ps1`，否则会启动另一条受管运行路径并与当前 ROS/Gazebo/PX4
实例竞争端口和控制权。

## 8. 本教程的完成条件与停止方式

这次“启动并连接”检查通过，必须同时满足：

```text
终端 A：roslaunch 持续运行，未出现持续性致命错误。
终端 B：model: uav1 / status: ready。
终端 C：connected: True。
QGC：Fly View 中出现一架活动 PX4 车辆，遥测持续更新。
```

这不是飞行验收。没有单独授权时，不要在 QGC 中解锁、起飞、上传任务、执行航点或启动自动任务。

停止本次手工会话时，先回到终端 A 按一次 `Ctrl+C`，再使用第 1 节的进程检查确认清理完成。QGC
窗口可在确认 PX4 已停止后正常关闭。

若失败，只提供以下信息即可继续定位：

```text
1. 终端 A 最后 80 行。
2. Results\sunray_ros1\<RUN_ID>\preflight.txt。
3. Results\sunray_ros1\<RUN_ID>\gazebo_uav1.txt。
4. Results\sunray_ros1\<RUN_ID>\mavros_state.txt。
5. QGC 的连接错误文本，以及 Get-NetUDPEndpoint 的输出。
```
