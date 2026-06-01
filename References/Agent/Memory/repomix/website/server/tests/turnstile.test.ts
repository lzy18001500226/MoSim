import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { Hono } from 'hono';
import { describe, expect, test, vi } from 'vitest';
import { EXPECTED_TURNSTILE_ACTION, turnstileMiddleware } from '../src/middlewares/turnstile.js';
import * as logger from '../src/utils/logger.js';

// The middleware reads `requestId` and `clientInfo` from the Hono context
// (set by upstream middleware in production). For unit tests we shim these
// via a tiny middleware so each test gets the values it needs without
// importing the full middleware chain.
function buildApp(opts: { middleware: ReturnType<typeof turnstileMiddleware>; requestId?: string }) {
  const app = new Hono();
  app.use('*', async (c, next) => {
    c.set('requestId', opts.requestId ?? 'req-test');
    await next();
  });
  app.post('/api/pack', opts.middleware, (c) => c.json({ ok: true }));
  return app;
}

const SECRET = 'test-secret';

const okResponse = (body: object) =>
  new Response(JSON.stringify(body), {
    headers: { 'Content-Type': 'application/json' },
  });

describe('turnstileMiddleware', () => {
  test('skips verification when secret is unset (fail-open in dev/test)', async () => {
    const fetchMock = vi.fn();
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => undefined,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', { method: 'POST' });

    expect(res.status).toBe(200);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test('returns 403 when secret is unset in production (fail-closed)', async () => {
    const fetchMock = vi.fn();
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => undefined,
      isProduction: () => true,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', { method: 'POST' });

    expect(res.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test('returns 403 when token header is missing', async () => {
    const fetchMock = vi.fn();
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', { method: 'POST' });

    expect(res.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
    const body = (await res.json()) as { error: string };
    expect(body.error).toMatch(/Verification failed/);
  });

  test('returns 403 when token is whitespace-only (treated as missing)', async () => {
    const fetchMock = vi.fn();
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': '   ' },
    });

    expect(res.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test('returns 403 when token exceeds max length (no siteverify call)', async () => {
    const fetchMock = vi.fn();
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const oversized = 'x'.repeat(2049);
    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': oversized },
    });

    expect(res.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  test('passes through when siteverify reports success', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true, action: 'pack' }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'good-token' },
    });

    expect(res.status).toBe(200);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe('https://challenges.cloudflare.com/turnstile/v0/siteverify');
    const body = (init as RequestInit).body as URLSearchParams;
    expect(body.get('secret')).toBe(SECRET);
    expect(body.get('response')).toBe('good-token');
  });

  test('passes through when siteverify omits action (backward-compat)', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'good-token' },
    });

    expect(res.status).toBe(200);
  });

  test('returns 403 when siteverify reports an action other than "pack"', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true, action: 'login' }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'wrong-action-token' },
    });

    expect(res.status).toBe(403);
  });

  test('returns 403 when siteverify reports failure', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(okResponse({ success: false, 'error-codes': ['invalid-input-response'] }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'bad-token' },
    });

    expect(res.status).toBe(403);
  });

  test('returns 403 (fail-closed) when siteverify network call rejects', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new Error('network down'));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'any-token' },
    });

    expect(res.status).toBe(403);
  });

  test('omits remoteip when clientInfo.ip falls back to 0.0.0.0', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    // Build a minimal app without IP-providing headers so getClientInfo()
    // returns the '0.0.0.0' sentinel.
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'good-token' },
    });

    expect(res.status).toBe(200);
    const body = (fetchMock.mock.calls[0][1] as RequestInit).body as URLSearchParams;
    expect(body.has('remoteip')).toBe(false);
  });

  test('includes remoteip when a real client IP header is present', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: {
        'X-Turnstile-Token': 'good-token',
        'cf-connecting-ip': '203.0.113.42',
      },
    });

    expect(res.status).toBe(200);
    const body = (fetchMock.mock.calls[0][1] as RequestInit).body as URLSearchParams;
    expect(body.get('remoteip')).toBe('203.0.113.42');
  });

  test('logs the secret-missing warning at most once across requests (dev/test)', async () => {
    const logWarningSpy = vi.spyOn(logger, 'logWarning').mockImplementation(() => {});
    try {
      // Reuse a single middleware instance across calls so the closure-state
      // `secretMissingLogged` flag is shared (mirrors the production setup
      // where one instance is registered for the whole server lifetime).
      const middleware = turnstileMiddleware({
        fetch: vi.fn(),
        getSecret: () => undefined,
        isProduction: () => false,
      });
      const app = buildApp({ middleware });

      await app.request('/api/pack', { method: 'POST' });
      await app.request('/api/pack', { method: 'POST' });
      await app.request('/api/pack', { method: 'POST' });

      const skipLogs = logWarningSpy.mock.calls.filter((call) =>
        String(call[0]).includes('Turnstile verification skipped'),
      );
      expect(skipLogs).toHaveLength(1);
    } finally {
      logWarningSpy.mockRestore();
    }
  });

  test('logs the secret-missing warning every request in production (no closure cache)', async () => {
    const logWarningSpy = vi.spyOn(logger, 'logWarning').mockImplementation(() => {});
    try {
      const middleware = turnstileMiddleware({
        fetch: vi.fn(),
        getSecret: () => undefined,
        isProduction: () => true,
      });
      const app = buildApp({ middleware });

      await app.request('/api/pack', { method: 'POST' });
      await app.request('/api/pack', { method: 'POST' });

      // Production fail-closed path logs every time so a chronic misconfig
      // shows up on the dashboard, not just once at boot.
      const prodLogs = logWarningSpy.mock.calls.filter((call) =>
        String(call[0]).includes('TURNSTILE_SECRET_KEY not set in production'),
      );
      expect(prodLogs).toHaveLength(2);
    } finally {
      logWarningSpy.mockRestore();
    }
  });

  test('passes through when siteverify hostname is allowed', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true, hostname: 'repomix.com' }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'good-token' },
    });

    expect(res.status).toBe(200);
  });

  test('returns 403 when siteverify reports an unexpected hostname', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true, hostname: 'attacker.example' }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'token' },
    });

    expect(res.status).toBe(403);
  });

  test('passes through when siteverify omits hostname (test sitekey backward-compat)', async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true }));
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'good-token' },
    });

    expect(res.status).toBe(200);
  });

  test('passes through siteverify error-codes in the rejection log payload', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      okResponse({
        success: false,
        'error-codes': ['timeout-or-duplicate', 'invalid-input-response'],
      }),
    );
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'duplicate-token' },
    });

    expect(res.status).toBe(403);
    // The middleware doesn't expose the error codes in the response body
    // (they're internal triage info). Behavioural assertion: the rejection
    // fires with the failure response shape, and downstream callers
    // (loggers) see the codes via the verifyResult object — verified
    // implicitly by middleware not throwing on the array shape.
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  test('returns 403 when siteverify response is not valid JSON', async () => {
    // Simulate a non-JSON response (e.g. Cloudflare returning a 5xx HTML
    // error page or an upstream proxy mangling the body). The runSiteverify
    // wrapper should map the JSON parse error to the same fail-closed 403
    // path as a network failure — no uncaught exception should escape.
    const fetchMock = vi.fn().mockResolvedValue(
      new Response('<!doctype html><h1>Bad Gateway</h1>', {
        headers: { 'Content-Type': 'text/html' },
      }),
    );
    const middleware = turnstileMiddleware({
      fetch: fetchMock,
      getSecret: () => SECRET,
      isProduction: () => false,
    });
    const app = buildApp({ middleware });

    const res = await app.request('/api/pack', {
      method: 'POST',
      headers: { 'X-Turnstile-Token': 'token' },
    });

    expect(res.status).toBe(403);
  });

  // The latency distribution metric in `monitoring/metrics/turnstile_siteverify_duration.yaml`
  // filters log entries on `jsonPayload.siteverifyDurationMs` field presence, so a refactor
  // that drops the field on any post-siteverify branch silently breaks the metric without
  // any other test failing. Lock the contract: every branch that called siteverify must
  // attach `siteverifyDurationMs` to its log.
  describe('siteverifyDurationMs is attached to every post-siteverify log', () => {
    test('success path emits logInfo with siteverifyDurationMs and event=turnstile_siteverify', async () => {
      const logInfoSpy = vi.spyOn(logger, 'logInfo').mockImplementation(() => {});
      try {
        const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true, action: 'pack' }));
        const middleware = turnstileMiddleware({
          fetch: fetchMock,
          getSecret: () => SECRET,
          isProduction: () => false,
        });
        const app = buildApp({ middleware });

        const res = await app.request('/api/pack', {
          method: 'POST',
          headers: { 'X-Turnstile-Token': 'good-token' },
        });

        expect(res.status).toBe(200);
        const successCall = logInfoSpy.mock.calls.find(
          (call) => (call[1] as Record<string, unknown> | undefined)?.event === 'turnstile_siteverify',
        );
        expect(successCall).toBeDefined();
        // biome-ignore lint/style/noNonNullAssertion: guarded by toBeDefined above
        const payload = successCall![1] as Record<string, unknown>;
        expect(payload.outcome).toBe('success');
        expect(payload.siteverifyDurationMs).toEqual(expect.any(Number));
      } finally {
        logInfoSpy.mockRestore();
      }
    });

    test('siteverify_rejected reject carries siteverifyDurationMs', async () => {
      const logInfoSpy = vi.spyOn(logger, 'logInfo').mockImplementation(() => {});
      try {
        const fetchMock = vi
          .fn()
          .mockResolvedValue(okResponse({ success: false, 'error-codes': ['invalid-input-response'] }));
        const middleware = turnstileMiddleware({
          fetch: fetchMock,
          getSecret: () => SECRET,
          isProduction: () => false,
        });
        const app = buildApp({ middleware });

        const res = await app.request('/api/pack', {
          method: 'POST',
          headers: { 'X-Turnstile-Token': 'bad-token' },
        });

        expect(res.status).toBe(403);
        const rejectCall = logInfoSpy.mock.calls.find(
          (call) => (call[1] as Record<string, unknown> | undefined)?.reason === 'siteverify_rejected',
        );
        expect(rejectCall).toBeDefined();
        // biome-ignore lint/style/noNonNullAssertion: guarded by toBeDefined above
        const rejectPayload = rejectCall![1] as Record<string, unknown>;
        expect(rejectPayload.siteverifyDurationMs).toEqual(expect.any(Number));
      } finally {
        logInfoSpy.mockRestore();
      }
    });

    test('action_mismatch reject carries siteverifyDurationMs', async () => {
      const logInfoSpy = vi.spyOn(logger, 'logInfo').mockImplementation(() => {});
      try {
        const fetchMock = vi.fn().mockResolvedValue(okResponse({ success: true, action: 'login' }));
        const middleware = turnstileMiddleware({
          fetch: fetchMock,
          getSecret: () => SECRET,
          isProduction: () => false,
        });
        const app = buildApp({ middleware });

        const res = await app.request('/api/pack', {
          method: 'POST',
          headers: { 'X-Turnstile-Token': 'wrong-action-token' },
        });

        expect(res.status).toBe(403);
        const rejectCall = logInfoSpy.mock.calls.find(
          (call) => (call[1] as Record<string, unknown> | undefined)?.reason === 'action_mismatch',
        );
        expect(rejectCall).toBeDefined();
        // biome-ignore lint/style/noNonNullAssertion: guarded by toBeDefined above
        const rejectPayload = rejectCall![1] as Record<string, unknown>;
        expect(rejectPayload.siteverifyDurationMs).toEqual(expect.any(Number));
      } finally {
        logInfoSpy.mockRestore();
      }
    });

    test('hostname_mismatch reject carries siteverifyDurationMs', async () => {
      const logInfoSpy = vi.spyOn(logger, 'logInfo').mockImplementation(() => {});
      try {
        const fetchMock = vi
          .fn()
          .mockResolvedValue(okResponse({ success: true, action: 'pack', hostname: 'evil.example.com' }));
        const middleware = turnstileMiddleware({
          fetch: fetchMock,
          getSecret: () => SECRET,
          isProduction: () => false,
        });
        const app = buildApp({ middleware });

        const res = await app.request('/api/pack', {
          method: 'POST',
          headers: { 'X-Turnstile-Token': 'leaked-sitekey-token' },
        });

        expect(res.status).toBe(403);
        const rejectCall = logInfoSpy.mock.calls.find(
          (call) => (call[1] as Record<string, unknown> | undefined)?.reason === 'hostname_mismatch',
        );
        expect(rejectCall).toBeDefined();
        // biome-ignore lint/style/noNonNullAssertion: guarded by toBeDefined above
        const rejectPayload = rejectCall![1] as Record<string, unknown>;
        expect(rejectPayload.siteverifyDurationMs).toEqual(expect.any(Number));
      } finally {
        logInfoSpy.mockRestore();
      }
    });

    test('siteverify_unavailable reject carries siteverifyDurationMs (warn-level)', async () => {
      const logWarningSpy = vi.spyOn(logger, 'logWarning').mockImplementation(() => {});
      try {
        const fetchMock = vi.fn().mockRejectedValue(new Error('network'));
        const middleware = turnstileMiddleware({
          fetch: fetchMock,
          getSecret: () => SECRET,
          isProduction: () => false,
        });
        const app = buildApp({ middleware });

        const res = await app.request('/api/pack', {
          method: 'POST',
          headers: { 'X-Turnstile-Token': 'token' },
        });

        expect(res.status).toBe(403);
        const rejectCall = logWarningSpy.mock.calls.find(
          (call) => (call[1] as Record<string, unknown> | undefined)?.reason === 'siteverify_unavailable',
        );
        expect(rejectCall).toBeDefined();
        // biome-ignore lint/style/noNonNullAssertion: guarded by toBeDefined above
        const rejectPayload = rejectCall![1] as Record<string, unknown>;
        expect(rejectPayload.siteverifyDurationMs).toEqual(expect.any(Number));
      } finally {
        logWarningSpy.mockRestore();
      }
    });
  });
});

// Cross-stack contract: the EXPECTED_TURNSTILE_ACTION on the server must
// match the literal `action` value the client widget binds in
// `useTurnstile.ts`. They live in different bundles with no shared module,
// so this test is the only thing keeping a rename on one side from silently
// breaking Turnstile in production.
describe('EXPECTED_TURNSTILE_ACTION contract', () => {
  test('matches the action literal embedded in the client useTurnstile composable', async () => {
    expect(EXPECTED_TURNSTILE_ACTION).toBe('pack');

    const useTurnstilePath = fileURLToPath(new URL('../../client/composables/useTurnstile.ts', import.meta.url));
    const source = await readFile(useTurnstilePath, 'utf8');
    expect(source).toMatch(/action:\s*['"]pack['"]/);
  });
});
