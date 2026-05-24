import { afterEach, describe, expect, it, vi } from 'vitest';
import { AssetResources } from './assets.js';
import type { AutomationBridge } from '../automation/index.js';
import type { UnrealBridge } from '../unreal-bridge.js';

function createAssetResources() {
  const sendAutomationRequest = vi.fn(async () => ({
    success: true,
    result: {
      folders_list: [],
      assets: []
    }
  }));

  const automationBridge = {
    isConnected: () => true,
    sendAutomationRequest
  } as unknown as AutomationBridge;

  const unrealBridge = {
    isConnected: true,
    getAutomationBridge: () => automationBridge
  } as unknown as UnrealBridge;

  return { resources: new AssetResources(unrealBridge), sendAutomationRequest };
}

describe('AssetResources cache TTL parsing', () => {
  const originalTtl = process.env.ASSET_LIST_TTL_MS;

  afterEach(() => {
    if (originalTtl === undefined) {
      delete process.env.ASSET_LIST_TTL_MS;
    } else {
      process.env.ASSET_LIST_TTL_MS = originalTtl;
    }
  });

  it('falls back to the default TTL for invalid env strings', async () => {
    for (const value of ['5000ms', '5e3', '0x2710', '-1']) {
      process.env.ASSET_LIST_TTL_MS = value;
      const { resources, sendAutomationRequest } = createAssetResources();

      await resources.list('/Game');
      await resources.list('/Game');

      expect(sendAutomationRequest).toHaveBeenCalledTimes(1);
    }
  });

  it('keeps zero as an explicit cache disable value', async () => {
    process.env.ASSET_LIST_TTL_MS = '0';
    const { resources, sendAutomationRequest } = createAssetResources();

    await resources.list('/Game');
    await resources.list('/Game');

    expect(sendAutomationRequest).toHaveBeenCalledTimes(2);
  });
});
