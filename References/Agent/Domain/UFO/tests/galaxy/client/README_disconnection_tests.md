# Device Disconnection and Reconnection Tests

## 📋 概述

这个测试套件全面验证了设备断连和重连的功能，包括：
- 断连检测和状态更新
- 自动重连机制
- 连接尝试计数管理
- 任务取消处理
- 事件通知
- 完整的集成测试

## 🎯 测试覆盖

### 功能覆盖

- ✅ **断连检测**: WebSocket ConnectionClosed 异常捕获
- ✅ **状态管理**: DISCONNECTED, CONNECTING, CONNECTED, IDLE, FAILED
- ✅ **自动重连**: 按照 `max_retries` 和 `reconnect_delay` 配置
- ✅ **连接计数**: 递增、重置、最大限制执行
- ✅ **任务处理**: 断连时取消正在执行的任务
- ✅ **事件通知**: 断连和重连事件
- ✅ **心跳管理**: 断连时停止心跳监控

### 测试统计

- **总测试数**: 15
- **单元测试**: 14
- **集成测试**: 1
- **通过率**: 100% ✅

## 🚀 快速开始

### 运行所有测试

```bash
# 方法 1: 使用 pytest 直接运行
python -m pytest tests/galaxy/client/test_device_disconnection_reconnection.py -v

# 方法 2: 使用测试脚本
python tests/galaxy/client/run_disconnection_tests.py
```

### 运行特定测试

```bash
# 运行单个测试
pytest tests/galaxy/client/test_device_disconnection_reconnection.py::TestDeviceDisconnectionReconnection::test_disconnection_updates_status -v

# 运行特定测试类
pytest tests/galaxy/client/test_device_disconnection_reconnection.py::TestDeviceDisconnectionReconnection -v

# 运行集成测试
pytest tests/galaxy/client/test_device_disconnection_reconnection.py::TestDisconnectionReconnectionIntegration -v
```

### 带详细输出运行

```bash
pytest tests/galaxy/client/test_device_disconnection_reconnection.py -v -s
```

## 📊 测试列表

### 单元测试 (TestDeviceDisconnectionReconnection)

1. **test_disconnection_updates_status**
   - 验证断连后状态更新为 DISCONNECTED

2. **test_message_processor_handles_connection_closed**
   - 验证 MessageProcessor 检测 ConnectionClosed 异常

3. **test_automatic_reconnection_scheduled**
   - 验证断连后自动调度重连

4. **test_reconnection_updates_status_to_idle**
   - 验证重连成功后状态更新为 IDLE

5. **test_connection_attempts_increment**
   - 验证每次连接尝试递增计数器

6. **test_connection_attempts_reset_on_success**
   - 验证成功重连后重置计数器

7. **test_max_retry_limit_stops_reconnection**
   - 验证达到最大重试次数后停止重连

8. **test_current_task_cancelled_on_disconnection**
   - 验证断连时取消正在执行的任务

9. **test_disconnection_event_notification**
   - 验证断连事件通知

10. **test_reconnection_event_notification**
    - 验证重连事件通知

11. **test_multiple_disconnection_reconnection_cycles**
    - 验证多次断连/重连循环

12. **test_heartbeat_stops_on_disconnection**
    - 验证断连时停止心跳

13. **test_disconnection_handler_with_unregistered_device**
    - 验证处理未注册设备的断连

14. **test_reconnection_attempts_tracking**
    - 验证重连尝试次数跟踪

### 集成测试 (TestDisconnectionReconnectionIntegration)

15. **test_full_disconnection_reconnection_flow**
    - 完整的端到端测试，涵盖整个断连和重连流程

## 🔧 测试配置

### Mock 组件

测试使用以下 Mock 策略：

- **WebSocket**: `MagicMock` 模拟连接和断连
- **ConnectionManager**: `AsyncMock` 模拟连接操作
- **EventManager**: `AsyncMock` 验证事件触发
- **HeartbeatManager**: `Mock` 验证心跳启停
- **TaskQueueManager**: `Mock` 验证任务失败处理

### 测试参数

- `reconnect_delay`: 0.5 秒（加快测试速度）
- `max_retries`: 3 次（测试重试逻辑）
- `heartbeat_interval`: 30 秒（标准配置）

## 📖 测试示例

### 示例 1: 基本断连测试

```python
@pytest.mark.asyncio
async def test_disconnection_updates_status(
    self, device_manager, setup_connected_device
):
    """测试断连后状态更新"""
    device_id = setup_connected_device

    # 验证初始状态
    device_info = device_manager.device_registry.get_device(device_id)
    assert device_info.status == DeviceStatus.IDLE

    # 触发断连
    await device_manager._handle_device_disconnection(device_id)

    # 验证状态更新
    device_info = device_manager.device_registry.get_device(device_id)
    assert device_info.status == DeviceStatus.DISCONNECTED
```

### 示例 2: 重连测试

```python
@pytest.mark.asyncio
async def test_automatic_reconnection_scheduled(
    self, device_manager, setup_connected_device
):
    """测试自动重连调度"""
    device_id = setup_connected_device

    # Mock connect_device
    connect_called = asyncio.Event()
    async def mock_connect(dev_id):
        connect_called.set()
        return True
    device_manager.connect_device = mock_connect

    # 触发断连
    await device_manager._handle_device_disconnection(device_id)

    # 等待重连（reconnect_delay = 0.5s）
    await asyncio.wait_for(connect_called.wait(), timeout=2.0)
```

### 示例 3: 集成测试

```python
@pytest.mark.asyncio
async def test_full_disconnection_reconnection_flow(self):
    """完整流程测试"""
    # 1. 注册并连接设备
    # 2. 分配任务
    # 3. 设备断连
    # 4. 任务被取消
    # 5. 自动重连
    # 6. 验证设备状态
```

## 📝 相关文档

- [设备断连处理实现文档](../../docs/device_disconnection_handling.md)
- [测试报告](../../docs/device_disconnection_test_report.md)

## 🐛 故障排除

### 测试失败

如果测试失败，请检查：

1. **环境配置**: 确保已激活虚拟环境
2. **依赖安装**: 确保安装了 `pytest` 和 `pytest-asyncio`
3. **代码同步**: 确保所有相关文件都已更新

### 运行缓慢

如果测试运行缓慢：

1. 检查 `reconnect_delay` 配置
2. 使用 `-n auto` 启用并行测试（需要 `pytest-xdist`）

```bash
pytest tests/galaxy/client/test_device_disconnection_reconnection.py -n auto
```

## 📞 联系方式

如有问题，请查看：
- 项目 README
- 相关文档
- GitHub Issues

---

**最后更新**: 2025-10-24
**测试状态**: ✅ 全部通过 (15/15)
