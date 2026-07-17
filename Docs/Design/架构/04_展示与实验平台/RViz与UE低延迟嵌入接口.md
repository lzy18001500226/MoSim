# RViz与UE低延迟嵌入接口

> 状态：接口设计冻结草案，2026-07-15。
>
> 本文只定义未来 MoSim Frontend 如何低延迟接入 RViz 和 UE，以及如何复用已启动
> 的显示进程。当前阶段不实现前端，也不改变 ROS1/Sunray/Gazebo/PX4/RACER 运行链。

## 1. 目标

解决两个不同问题：

```text
嵌入：用户在一个MoSim工作台中看到RViz和UE，不需要手工切换窗口。
复用：重复实验不反复冷启动RViz、UE和重载大场景，缩短等待时间。
```

显示复用不得造成跨 run 数据污染，也不得让 RViz/UE 进入控制闭环。

## 2. 设计原则

1. 控制进程、显示进程和前端进程解耦。
2. RViz/UE只消费带 `run_id` 和时间戳的只读显示流。
3. 优先复用暖进程和已加载资源，再切换数据源与布局。
4. 显示断开、卡顿、丢帧或重启不能阻塞控制器、PX4、Gazebo或日志。
5. 每次 attach 前清空上一 run 的可变轨迹、事件和缓存。
6. 前端只能调用 Orchestrator API，不能直接执行任意 shell、roslaunch 或控制话题。

## 3. 显示会话状态机

```text
cold
  -> warming
  -> ready_detached
  -> attaching
  -> attached_live | attached_replay
  -> detaching
  -> ready_detached

任意状态 -> degraded -> recovering | failed
ready_detached -> shutdown -> cold
```

状态最少包含：

```json
{
  "display_session_id": "display_20260715_001",
  "backend": "rviz_ros1 | unreal",
  "state": "ready_detached",
  "process_id": 0,
  "run_id": null,
  "profile_hash": null,
  "ready_at": null,
  "last_frame_at": null,
  "last_heartbeat_at": null,
  "stale": false,
  "restart_count": 0
}
```

## 4. Orchestrator接口

未来前端只依赖以下语义接口。第一版正式IPC冻结为仅绑定`127.0.0.1`的本机Loopback通道：
低频控制请求使用HTTP/JSON请求响应，实时遥测与状态事件使用版本化WebSocket，UE位姿/
渲染更新使用带`run_id`、时间戳和序号的独立单向低延迟流，证据和大体积结果继续落文件。
HTTP在这里是Windows、WSL和不同语言进程间的IPC协议，不代表网页、浏览器或外网服务。
现有JSON文件队列只保留为契约测试、恢复和诊断回退，不作为实时显示主链。

| 接口 | 用途 | 关键返回 |
| --- | --- | --- |
| `prepare_display_session` | 冷启动或复用RViz/UE暖进程 | session id、状态、启动阶段、耗时 |
| `attach_display` | 将指定run/profile绑定到显示会话 |绑定结果、首帧时间、数据源摘要 |
| `detach_display` | 解除当前run并清理可变缓存 |清理证明、保留进程状态 |
| `set_display_layout` | 切换RViz config、UE视角和面板布局 |布局hash、缺失面板 |
| `display_health` | 查询进程、心跳、帧年龄和数据延迟 |health、stale原因、恢复建议 |
| `capture_display_evidence` | 截图或录制已声明视图 |文件、时间戳、run id、窗口信息 |
| `shutdown_display_session` | 显式关闭暖进程 |退出码、残留检查 |

`prepare_display_session` 必须是幂等的。已有兼容暖进程时返回复用结果，不再次
启动；版本、场景或渲染后端不兼容时才允许新建显示会话。

## 5. ViewDescriptor

每个可嵌入视图由统一描述符注册：

```yaml
view_id: rviz_primary
backend: rviz_ros1
integration_mode: managed_external
runtime_os: ubuntu_20_04_wsl
process_identity:
  executable: rviz
  expected_window_title: MoSim RViz
  expected_window_class: null
native_window_handle: null
stream_endpoint: null
control_endpoint: orchestrator_only
data_profile: rviz_sunray_ros1_v1
layout_profile: rviz_trajectory_pointcloud_v1
target_fps: 30
control_input_allowed: false
```

`native_window_handle` 和 `stream_endpoint` 至少一个可用时，前端才能声明真正
嵌入；否则只能声明受控外部窗口。

## 6. 嵌入模式与优先级

### 6.1 RViz

优先级：

```text
R1 同一Linux/Qt进程内使用RViz RenderPanel/插件
R2 独立RViz进程，通过稳定的远程/流式视图嵌入
R3 受控外部窗口：自动启动、定位、缩放和恢复
R4 Windows宿主强行重挂WSL窗口句柄，只作实验，不作为正式基线
```

当前 ROS1/RViz 在 Ubuntu-20.04 WSL，未来前端大概率运行于 Windows。跨操作系统
原生窗口重挂存在 DPI、焦点、输入、窗口重建和 WSLg 生命周期风险，因此第一版
必须保留 `managed_external` 回退路径。

### 6.2 UE

第一版产品要求UE真正嵌入Flight Console主窗口。实现优先级：

```text
U1 Qt容器接管Windows原生UE渲染窗口
U2 GPU共享纹理接入
U3 UE Pixel Streaming/WebRTC嵌入
U4 受控外部UE窗口，仅调试和故障降级
```

U1必须通过窗口生命周期、DPI、缩放、焦点、输入、闪烁和重连门禁。若U1无法达到稳定
验收，转U2共享纹理；不能退回外部窗口并声称正式嵌入完成。Pixel Streaming更容易嵌入
Qt WebEngine，但增加编码/解码延迟，不作为当前比赛电脑默认路线。U4不满足正式产品验收，
但必须保留，确保嵌入层失败不会阻断Gazebo/PX4运行与证据保存。

## 7. DisplayFrame数据契约

RViz和UE必须从同一语义帧派生显示，但允许不同频率和格式：

```json
{
  "schema": "mosim.display_frame.v1",
  "run_id": "run_001",
  "profile_hash": "sha256:...",
  "source_id": "mavros_fused",
  "sequence": 1,
  "timestamp_source": 0.0,
  "timestamp_bridge": 0.0,
  "timestamp_display": 0.0,
  "frame_id": "world",
  "child_frame_id": "base_link",
  "vehicle_pose": {},
  "reference_pose": {},
  "vehicle_path_delta": [],
  "reference_path_delta": [],
  "controller_status": {},
  "mission_status": {},
  "events": [],
  "valid": true
}
```

延迟必须可分解为：

```text
source_to_bridge_ms
bridge_queue_ms
bridge_to_display_ms
display_frame_age_ms
```

只记录总延迟不足以定位 ROS、桥接、渲染还是前端造成的卡顿。

## 8. 暖启动与缓存策略

### RViz

- 复用固定 RViz 进程和已加载 display config；
- 通过 namespace/data profile 切换本次 run；
- attach 前执行 reset，清空旧 Path、Marker、PointCloud 和 TF诊断状态；
- 不因一次 topic 暂时缺失就重启 RViz；先进入 `ready_detached` 等待数据。

### UE

- 优先使用 packaged runtime 或稳定 Editor play surface；
- 预加载公共 Factory 场景、材质和机体资源；
- 空闲时保持 standby map，不维持上一 run 的 actor 状态；
- attach 时只绑定新的 stream、run id、初始位姿和视角；
- 场景版本或坐标契约变化时才重新加载完整场景。

### 缓存身份

暖进程只能在以下键一致时复用：

```text
backend_version
scene_profile_hash
display_schema_version
coordinate_contract_hash
layout_profile_compatibility
```

## 9. 延迟与启动基准

第一版先采集基线，不提前伪造达标结论。每次 PoC 输出：

```text
cold_process_start_ms
asset_or_layout_load_ms
ready_detached_ms
attach_to_first_frame_ms
warm_reattach_ms
source_to_display_p50_ms
source_to_display_p95_ms
frame_drop_ratio
stale_frame_count
```

建议的初始工程目标，需实测后冻结：

```text
暖会话重新attach到首帧：<= 2 s
RViz/UE显示帧过期告警：> 500 ms
显示故障对控制/日志的阻塞：0
跨run残留轨迹或事件：0
```

## 10. 当前非实现边界

- 本文不启动、关闭或修改当前 RACER/Gazebo/PX4/MAVROS 进程。
- 本文不决定最终前端采用 Qt/QML、Web 还是混合技术栈。
- 本文不承诺 Windows 可以稳定原生嵌入 WSL RViz。
- 本文不将 RViz/UE 首帧或流畅画面升级为控制、规划或定位成功。
- 当前可以先完成 schema、mock、replay、生命周期状态机和延迟记录工具；真实 live
  attach 必须等共享运行资源释放后再验收。
