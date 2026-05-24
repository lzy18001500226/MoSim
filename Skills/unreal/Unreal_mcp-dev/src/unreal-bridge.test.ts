import { EventEmitter } from 'node:events';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { AutomationBridge } from './automation/index.js';
import { UnrealBridge } from './unreal-bridge.js';

function createDisconnectedAutomationBridge(): AutomationBridge {
  const emitter = new EventEmitter() as EventEmitter & { isConnected: () => boolean };
  emitter.isConnected = () => false;
  return emitter as unknown as AutomationBridge;
}

describe('UnrealBridge timeout env parsing', () => {
  const originalTimeout = process.env.UNREAL_CONNECTION_TIMEOUT;

  afterEach(() => {
    if (originalTimeout === undefined) {
      delete process.env.UNREAL_CONNECTION_TIMEOUT;
    } else {
      process.env.UNREAL_CONNECTION_TIMEOUT = originalTimeout;
    }
    vi.restoreAllMocks();
  });

  it('rejects partial numeric connection timeout strings', async () => {
    process.env.UNREAL_CONNECTION_TIMEOUT = '5000ms';
    const bridge = new UnrealBridge();
    bridge.setAutomationBridge(createDisconnectedAutomationBridge());
    const connect = vi.spyOn(bridge, 'connect').mockResolvedValue(undefined);

    await bridge.tryConnect(1, 1234, 1);

    expect(connect).toHaveBeenCalledWith(1234);
  });

  it('accepts positive decimal integer connection timeout strings', async () => {
    process.env.UNREAL_CONNECTION_TIMEOUT = '5000';
    const bridge = new UnrealBridge();
    bridge.setAutomationBridge(createDisconnectedAutomationBridge());
    const connect = vi.spyOn(bridge, 'connect').mockResolvedValue(undefined);

    await bridge.tryConnect(1, 1234, 1);

    expect(connect).toHaveBeenCalledWith(5000);
  });
});
