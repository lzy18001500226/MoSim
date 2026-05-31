import { describe, expect, it } from 'vitest';

import { applyProviderRuntimeEnv } from './providerRuntimeEnv';

describe('applyProviderRuntimeEnv', () => {
  it('preserves Bedrock as an Anthropic runtime backend', () => {
    const env: NodeJS.ProcessEnv = {
      CLAUDE_CODE_USE_BEDROCK: '1',
      AWS_PROFILE: 'cc',
      AWS_REGION: 'us-east-1',
    };

    applyProviderRuntimeEnv(env, 'anthropic');

    expect(env.CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST).toBe('1');
    expect(env.CLAUDE_CODE_ENTRY_PROVIDER).toBe('bedrock');
    expect(env.CLAUDE_CODE_USE_BEDROCK).toBe('1');
    expect(env.CLAUDE_CODE_USE_VERTEX).toBeUndefined();
    expect(env.CLAUDE_CODE_USE_FOUNDRY).toBeUndefined();
    expect(env.AWS_PROFILE).toBe('cc');
    expect(env.AWS_REGION).toBe('us-east-1');
  });

  it('preserves Vertex as an Anthropic runtime backend', () => {
    const env: NodeJS.ProcessEnv = {
      CLAUDE_CODE_USE_VERTEX: 'true',
      GOOGLE_CLOUD_PROJECT: 'project-1',
    };

    applyProviderRuntimeEnv(env, 'anthropic');

    expect(env.CLAUDE_CODE_ENTRY_PROVIDER).toBe('vertex');
    expect(env.CLAUDE_CODE_USE_VERTEX).toBe('1');
    expect(env.CLAUDE_CODE_USE_BEDROCK).toBeUndefined();
    expect(env.GOOGLE_CLOUD_PROJECT).toBe('project-1');
  });

  it('preserves Claude Platform on AWS as an Anthropic runtime backend', () => {
    const env: NodeJS.ProcessEnv = {
      ANTHROPIC_AWS_WORKSPACE_ID: 'wrkspc_123',
      AWS_PROFILE: 'cc',
      AWS_REGION: 'us-west-2',
    };

    applyProviderRuntimeEnv(env, 'anthropic');

    expect(env.CLAUDE_CODE_ENTRY_PROVIDER).toBe('claude-platform-aws');
    expect(env.ANTHROPIC_AWS_WORKSPACE_ID).toBe('wrkspc_123');
    expect(env.CLAUDE_CODE_USE_BEDROCK).toBeUndefined();
    expect(env.CLAUDE_CODE_USE_VERTEX).toBeUndefined();
    expect(env.CLAUDE_CODE_USE_FOUNDRY).toBeUndefined();
    expect(env.AWS_PROFILE).toBe('cc');
    expect(env.AWS_REGION).toBe('us-west-2');
  });

  it('does not infer Claude Platform on AWS from AWS profile and region alone', () => {
    const env: NodeJS.ProcessEnv = {
      AWS_PROFILE: 'cc',
      AWS_REGION: 'us-west-2',
    };

    applyProviderRuntimeEnv(env, 'anthropic');

    expect(env.CLAUDE_CODE_ENTRY_PROVIDER).toBe('anthropic');
    expect(env.CLAUDE_CODE_USE_BEDROCK).toBeUndefined();
    expect(env.AWS_PROFILE).toBe('cc');
    expect(env.AWS_REGION).toBe('us-west-2');
  });

  it('keeps Bedrock ahead of Claude Platform on AWS when both are configured', () => {
    const env: NodeJS.ProcessEnv = {
      CLAUDE_CODE_USE_BEDROCK: '1',
      ANTHROPIC_AWS_WORKSPACE_ID: 'wrkspc_123',
      AWS_PROFILE: 'cc',
      AWS_REGION: 'us-east-1',
    };

    applyProviderRuntimeEnv(env, 'anthropic');

    expect(env.CLAUDE_CODE_ENTRY_PROVIDER).toBe('bedrock');
    expect(env.CLAUDE_CODE_USE_BEDROCK).toBe('1');
    expect(env.ANTHROPIC_AWS_WORKSPACE_ID).toBe('wrkspc_123');
  });

  it('still strips Anthropic backend routing when Codex is selected', () => {
    const env: NodeJS.ProcessEnv = {
      CLAUDE_CODE_USE_BEDROCK: '1',
      ANTHROPIC_AWS_WORKSPACE_ID: 'wrkspc_123',
      AWS_PROFILE: 'cc',
    };

    applyProviderRuntimeEnv(env, 'codex');

    expect(env.CLAUDE_CODE_ENTRY_PROVIDER).toBe('codex');
    expect(env.CLAUDE_CODE_USE_BEDROCK).toBeUndefined();
    expect(env.ANTHROPIC_AWS_WORKSPACE_ID).toBe('wrkspc_123');
    expect(env.AWS_PROFILE).toBe('cc');
  });
});
