import { describe, it, expect } from 'vitest'
import { buildAgentfileLayer } from '../agentfile-layer'

describe('buildAgentfileLayer', () => {
  it('generates MODE for non-pty interaction mode', () => {
    const result = buildAgentfileLayer({ configValues: {}, interactionMode: 'acp' })
    expect(result).toContain('MODE acp')
  })

  it('omits MODE for pty (default)', () => {
    const result = buildAgentfileLayer({ configValues: {}, interactionMode: 'pty' })
    expect(result).not.toContain('MODE')
  })

  it('generates PROMPT declaration', () => {
    const result = buildAgentfileLayer({ configValues: {}, prompt: 'fix bug' })
    expect(result).toContain('PROMPT "fix bug"')
  })

  it('escapes PROMPT special characters', () => {
    const result = buildAgentfileLayer({
      configValues: {},
      prompt: 'say "hello" and use \\ backslash',
    })
    expect(result).toContain('PROMPT "say \\"hello\\" and use \\\\ backslash"')
  })

  it('generates REPO slug', () => {
    const result = buildAgentfileLayer({
      configValues: {},
      repositorySlug: 'dev-org/demo-api',
    })
    expect(result).toContain('REPO "dev-org/demo-api"')
  })

  it('generates BRANCH', () => {
    const result = buildAgentfileLayer({ configValues: {}, branchName: 'develop' })
    expect(result).toContain('BRANCH "develop"')
  })

  it('generates CONFIG declarations', () => {
    const result = buildAgentfileLayer({ configValues: { model: 'opus' } })
    expect(result).toContain('CONFIG model = "opus"')
  })

  it('emits USE_ENV_BUNDLE for the credential bundle', () => {
    const result = buildAgentfileLayer({
      configValues: {},
      credentialBundleName: 'my-profile',
    })
    expect(result).toContain('USE_ENV_BUNDLE "my-profile"')
  })

  it('emits credential first then runtime bundles in selection order', () => {
    const result = buildAgentfileLayer({
      configValues: {},
      credentialBundleName: 'creds-work',
      runtimeBundleNames: ['runtime-debug', 'shared-proxy'],
    })
    const lines = result.split('\n').filter((l) => l.startsWith('USE_ENV_BUNDLE'))
    expect(lines).toEqual([
      'USE_ENV_BUNDLE "creds-work"',
      'USE_ENV_BUNDLE "runtime-debug"',
      'USE_ENV_BUNDLE "shared-proxy"',
    ])
  })

  it('emits only runtime bundles when no credential is provided', () => {
    const result = buildAgentfileLayer({
      configValues: {},
      runtimeBundleNames: ['runtime-debug', 'shared-proxy'],
    })
    const lines = result.split('\n').filter((l) => l.startsWith('USE_ENV_BUNDLE'))
    expect(lines).toEqual([
      'USE_ENV_BUNDLE "runtime-debug"',
      'USE_ENV_BUNDLE "shared-proxy"',
    ])
  })

  it('omits USE_ENV_BUNDLE entirely when nothing is selected', () => {
    expect(buildAgentfileLayer({ configValues: {} })).not.toContain('USE_ENV_BUNDLE')
    expect(
      buildAgentfileLayer({ configValues: {}, credentialBundleName: '', runtimeBundleNames: [] }),
    ).not.toContain('USE_ENV_BUNDLE')
  })

  it('returns empty string when all params are empty', () => {
    const result = buildAgentfileLayer({ configValues: {} })
    expect(result).toBe('')
  })

  it('generates full output with all fields', () => {
    const result = buildAgentfileLayer({
      configValues: { model: 'opus', permission_mode: 'plan' },
      interactionMode: 'acp',
      credentialBundleName: 'my-creds',
      runtimeBundleNames: ['dev-preferences'],
      prompt: 'fix the bug',
      repositorySlug: 'dev-org/demo-api',
      branchName: 'develop',
    })
    expect(result).toContain('MODE acp')
    expect(result).toContain('USE_ENV_BUNDLE "my-creds"')
    expect(result).toContain('USE_ENV_BUNDLE "dev-preferences"')
    expect(result).toContain('PROMPT "fix the bug"')
    expect(result).toContain('CONFIG model = "opus"')
    expect(result).toContain('CONFIG permission_mode = "plan"')
    expect(result).toContain('REPO "dev-org/demo-api"')
    expect(result).toContain('BRANCH "develop"')
  })

  it('skips CONFIG entries with empty string values', () => {
    const result = buildAgentfileLayer({ configValues: { model: '', other: 'val' } })
    expect(result).not.toContain('CONFIG model')
    expect(result).toContain('CONFIG other = "val"')
  })

  it('handles CONFIG with boolean values', () => {
    const result = buildAgentfileLayer({ configValues: { mcp_enabled: true } })
    expect(result).toContain('CONFIG mcp_enabled = true')
  })

  it('handles CONFIG with numeric values', () => {
    const result = buildAgentfileLayer({ configValues: { timeout: 30 } })
    expect(result).toContain('CONFIG timeout = 30')
  })
})
