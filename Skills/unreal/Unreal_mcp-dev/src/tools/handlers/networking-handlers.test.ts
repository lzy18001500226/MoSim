import { describe, expect, it, vi } from 'vitest';
import { handleNetworkingTools } from './networking-handlers.js';
import type { ITools } from '../../types/tool-interfaces.js';

function createTools() {
  const sendAutomationRequest = vi.fn(async () => ({ success: true }));
  const tools = {
    automationBridge: {
      isConnected: () => true,
      sendAutomationRequest
    }
  } as unknown as ITools;

  return { tools, sendAutomationRequest };
}

describe('handleNetworkingTools path normalization', () => {
  it('normalizes blueprint paths before dispatch', async () => {
    const { tools, sendAutomationRequest } = createTools();

    await handleNetworkingTools('set_property_replicated', {
      action: 'set_property_replicated',
      blueprintPath: 'Content\\Blueprints\\BP_NetActor',
      propertyName: 'Health'
    }, tools);

    expect(sendAutomationRequest).toHaveBeenCalledWith('manage_networking', {
      action: 'set_property_replicated',
      blueprintPath: '/Game/Blueprints/BP_NetActor',
      propertyName: 'Health',
      subAction: 'set_property_replicated'
    }, {
      timeoutMs: 120000
    });
  });

  it('honors per-call timeoutMs before dispatch', async () => {
    const { tools, sendAutomationRequest } = createTools();

    await handleNetworkingTools('set_property_replicated', {
      action: 'set_property_replicated',
      blueprintPath: '/Game/Blueprints/BP_NetActor',
      propertyName: 'Health',
      timeoutMs: 250000
    }, tools);

    expect(sendAutomationRequest).toHaveBeenCalledWith('manage_networking', {
      action: 'set_property_replicated',
      blueprintPath: '/Game/Blueprints/BP_NetActor',
      propertyName: 'Health',
      subAction: 'set_property_replicated'
    }, {
      timeoutMs: 250000
    });
  });

});
