import { describe, expect, it, vi } from 'vitest';
import { HealthMonitor } from './health-monitor.js';
import { Logger } from '../utils/logger.js';
import type { UnrealBridge } from '../unreal-bridge.js';

function createLogger(): Logger {
  return new Logger('HealthMonitorTest', 'error');
}

describe('HealthMonitor', () => {
  it('marks the bridge disconnected without sending a ping', async () => {
    const monitor = new HealthMonitor(createLogger());
    monitor.metrics.connectionStatus = 'connected';
    const executeConsoleCommand = vi.fn();
    const bridge = {
      isConnected: false,
      executeConsoleCommand
    } as unknown as UnrealBridge;

    const healthy = await monitor.performHealthCheck(bridge);

    expect(healthy).toBe(false);
    expect(monitor.metrics.connectionStatus).toBe('disconnected');
    expect(executeConsoleCommand).not.toHaveBeenCalled();
  });
});
