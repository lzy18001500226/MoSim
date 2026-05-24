import { describe, expect, it } from 'vitest';
import type { ITools } from '../../types/tool-interfaces.js';
import type { PipelineArgs } from '../../types/handler-types.js';
import { handlePipelineTools } from './pipeline-handlers.js';

const tools = {} as unknown as ITools;

function runUbt(args: Partial<PipelineArgs>) {
  return handlePipelineTools('run_ubt', {
    target: 'MCPtestEditor',
    platform: 'Linux',
    configuration: 'Development',
    ...args
  } as PipelineArgs, tools);
}

describe('handlePipelineTools run_ubt validation', () => {
  it('rejects switch-shaped positional fields before local or bridge execution', async () => {
    await expect(runUbt({ target: '-Project=/tmp/Evil.uproject' }))
      .rejects.toThrow(/positional UBT token/);
  });

  it('rejects platform and configuration values outside allowlists', async () => {
    await expect(runUbt({ platform: 'Windows' }))
      .rejects.toThrow(/platform is not allowed/);

    await expect(runUbt({ configuration: 'DevelopmentEditor' }))
      .rejects.toThrow(/configuration is not allowed/);
  });

  it('rejects extra arguments that override the managed invocation', async () => {
    await expect(runUbt({ arguments: '-Project=/tmp/Evil.uproject' }))
      .rejects.toThrow(/cannot override/);

    await expect(runUbt({ arguments: '--Project=/tmp/Evil.uproject' }))
      .rejects.toThrow(/cannot override/);

    await expect(runUbt({ arguments: '@/tmp/ubt.rsp' }))
      .rejects.toThrow(/response-file/);
  });
});
