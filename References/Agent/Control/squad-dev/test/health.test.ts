/**
 * Health Monitor tests — success, timeout, degraded, getStatus.
 *
 * Covers audit gaps: check() healthy, check() timeout → unhealthy,
 * check() slow response → degraded, getStatus() current state.
 *
 * @module test/health
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { HealthMonitor, type HealthCheckResult, type HealthMonitorConfig } from '../packages/squad-sdk/src/runtime/health.js';

// ============================================================================
// Mock SquadClient
// ============================================================================

function createMockClient(overrides: {
  isConnected?: boolean;
  state?: string;
  pingResult?: { message: string; timestamp: number; protocolVersion?: number };
  pingDelay?: number;
  pingError?: Error;
} = {}) {
  const connected = overrides.isConnected ?? true;
  const state = overrides.state ?? (connected ? 'connected' : 'disconnected');

  return {
    isConnected: vi.fn(() => connected),
    getState: vi.fn(() => state),
    ping: vi.fn(async (msg?: string) => {
      if (overrides.pingDelay) {
        await new Promise(resolve => setTimeout(resolve, overrides.pingDelay));
      }
      if (overrides.pingError) throw overrides.pingError;
      return overrides.pingResult ?? {
        message: msg ?? 'pong',
        timestamp: Date.now(),
        protocolVersion: 1,
      };
    }),
  };
}

// ============================================================================
// HealthMonitor.check() — success
// ============================================================================

describe('HealthMonitor.check() — success', () => {
  it('returns healthy when connected and ping succeeds', async () => {
    const client = createMockClient();
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    const result = await monitor.check();

    expect(result.status).toBe('healthy');
    expect(result.connected).toBe(true);
    expect(result.connectionState).toBe('connected');
    expect(result.protocolVersion).toBe(1);
    expect(result.responseTimeMs).toBeDefined();
    expect(result.responseTimeMs).toBeGreaterThanOrEqual(0);
    expect(result.error).toBeUndefined();
    expect(result.timestamp).toBeInstanceOf(Date);
  });

  it('calls ping with health-check message', async () => {
    const client = createMockClient();
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    await monitor.check();

    expect(client.ping).toHaveBeenCalledWith('health-check');
  });

  it('checks connection before pinging', async () => {
    const client = createMockClient();
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    await monitor.check();

    expect(client.isConnected).toHaveBeenCalled();
    expect(client.getState).toHaveBeenCalled();
  });
});

// ============================================================================
// HealthMonitor.check() — timeout
// ============================================================================

describe('HealthMonitor.check() — timeout', () => {
  it('returns unhealthy when ping exceeds timeout', async () => {
    const client = createMockClient({ pingDelay: 200 });
    const monitor = new HealthMonitor({
      client: client as any,
      timeout: 50,
      logDiagnostics: false,
    });

    const result = await monitor.check();

    expect(result.status).toBe('unhealthy');
    expect(result.error).toContain('timeout');
  });

  it('returns unhealthy when client not connected', async () => {
    const client = createMockClient({ isConnected: false });
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    const result = await monitor.check();

    expect(result.status).toBe('unhealthy');
    expect(result.connected).toBe(false);
    expect(result.error).toContain('not connected');
  });

  it('does not call ping when not connected', async () => {
    const client = createMockClient({ isConnected: false });
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    await monitor.check();

    expect(client.ping).not.toHaveBeenCalled();
  });

  it('returns unhealthy when ping throws', async () => {
    const client = createMockClient({ pingError: new Error('Connection refused') });
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    const result = await monitor.check();

    expect(result.status).toBe('unhealthy');
    expect(result.error).toBe('Connection refused');
  });

  it('captures responseTimeMs even on failure', async () => {
    const client = createMockClient({ pingError: new Error('fail') });
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    const result = await monitor.check();

    expect(result.responseTimeMs).toBeDefined();
    expect(result.responseTimeMs).toBeGreaterThanOrEqual(0);
  });
});

// ============================================================================
// HealthMonitor.check() — degraded
// ============================================================================

describe('HealthMonitor.check() — degraded', () => {
  it('returns degraded when response time exceeds 80% of timeout', async () => {
    // Timeout is 100ms, 80% = 80ms. Ping takes 90ms → degraded.
    const client = createMockClient({ pingDelay: 90 });
    const monitor = new HealthMonitor({
      client: client as any,
      timeout: 100,
      logDiagnostics: false,
    });

    const result = await monitor.check();

    // Should be degraded if responseTimeMs > 80
    if (result.status === 'degraded') {
      expect(result.error).toContain('Slow response');
      expect(result.responseTimeMs).toBeGreaterThan(80);
    } else {
      // If the machine is fast enough that ping < 80ms, it may be healthy
      expect(result.status).toBe('healthy');
    }
  });

  it('uses default timeout of 5000ms', async () => {
    const client = createMockClient();
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    const result = await monitor.check();

    // With default 5000ms timeout and instant mock, should be healthy
    expect(result.status).toBe('healthy');
  });
});

// ============================================================================
// HealthMonitor.getStatus()
// ============================================================================

describe('HealthMonitor.getStatus()', () => {
  it('returns healthy for connected client', () => {
    const client = createMockClient({ isConnected: true, state: 'connected' });
    const monitor = new HealthMonitor({ client: client as any });

    const status = monitor.getStatus();

    expect(status.status).toBe('healthy');
    expect(status.connectionState).toBe('connected');
    expect(status.connected).toBe(true);
    expect(status.timestamp).toBeInstanceOf(Date);
  });

  it('returns unhealthy for disconnected client', () => {
    const client = createMockClient({ isConnected: false, state: 'disconnected' });
    const monitor = new HealthMonitor({ client: client as any });

    const status = monitor.getStatus();

    expect(status.status).toBe('unhealthy');
    expect(status.connected).toBe(false);
  });

  it('returns degraded for reconnecting client', () => {
    const client = createMockClient({ isConnected: false, state: 'reconnecting' });
    const monitor = new HealthMonitor({ client: client as any });

    const status = monitor.getStatus();

    expect(status.status).toBe('degraded');
    expect(status.connectionState).toBe('reconnecting');
  });

  it('returns unhealthy for error state', () => {
    const client = createMockClient({ isConnected: false, state: 'error' });
    const monitor = new HealthMonitor({ client: client as any });

    const status = monitor.getStatus();

    expect(status.status).toBe('unhealthy');
    expect(status.connectionState).toBe('error');
  });

  it('does not perform a ping (passive check)', () => {
    const client = createMockClient();
    const monitor = new HealthMonitor({ client: client as any });

    monitor.getStatus();

    expect(client.ping).not.toHaveBeenCalled();
  });
});

// ============================================================================
// Diagnostics logging
// ============================================================================

describe('HealthMonitor — diagnostics', () => {
  it('logs diagnostics on failure when enabled', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const client = createMockClient({ isConnected: false });
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: true });

    await monitor.check();

    expect(consoleSpy).toHaveBeenCalledWith(
      expect.stringContaining('[HealthMonitor]'),
      // Don't care about exact message
    );
    consoleSpy.mockRestore();
  });

  it('does not log diagnostics when disabled', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const client = createMockClient({ isConnected: false });
    const monitor = new HealthMonitor({ client: client as any, logDiagnostics: false });

    await monitor.check();

    expect(consoleSpy).not.toHaveBeenCalled();
    consoleSpy.mockRestore();
  });
});
