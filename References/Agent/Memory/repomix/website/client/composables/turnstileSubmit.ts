// Helpers for translating Turnstile token-acquisition outcomes into the
// shape usePackRequest's `submitRequest` consumes. Splitting these out keeps
// usePackRequest under the 250-line file-size guideline and centralises the
// user-facing error copy.

import type { useTurnstile } from './useTurnstile';

export type TurnstileTokenResult =
  // Token acquired (or dev/preview fallthrough where the server skips
  // verification when TURNSTILE_SECRET_KEY is unset).
  | { kind: 'token'; token: string | undefined }
  // The pack-request controller was aborted while the Turnstile challenge
  // was in flight. `reason` mirrors AbortSignal.reason so the caller can
  // distinguish user cancel from the 30s timeout.
  | { kind: 'aborted'; reason: AbortSignal['reason'] }
  // Production verification failure — surface a user-visible error instead
  // of calling /api/pack since the server-side middleware would 403 anyway.
  | { kind: 'error'; message: string };

// Acquire a Turnstile token for the click path. The signal aborts an
// in-flight challenge when the surrounding pack request is cancelled.
export async function acquireTurnstileToken(
  turnstile: ReturnType<typeof useTurnstile>,
  signal: AbortSignal,
): Promise<TurnstileTokenResult> {
  try {
    return { kind: 'token', token: await turnstile.takeToken(signal) };
  } catch (err) {
    // Abort is a normal flow (user cancel, 30s timeout). Don't log it as
    // a failure — only log genuine challenge / script-load errors.
    if (signal.aborted) {
      return { kind: 'aborted', reason: signal.reason };
    }
    console.warn('Turnstile token acquisition failed:', err);
    if (import.meta.env.PROD) {
      return { kind: 'error', message: turnstileFailureMessage(err) };
    }
    // Dev/preview: continue without a token. The server skips verification
    // when TURNSTILE_SECRET_KEY is unset, so contributors without a
    // Cloudflare account can still exercise the pack flow.
    return { kind: 'token', token: undefined };
  }
}

// Distinguish "Turnstile script blocked" (likely an extension) from generic
// verification failure so the user has a path to recovery instead of just
// being told "try again".
function turnstileFailureMessage(err: unknown): string {
  const msg = err instanceof Error ? err.message : '';
  const isScriptIssue = /script|load|missing/i.test(msg);
  return isScriptIssue
    ? 'Bot protection failed to load. Please disable ad blockers or privacy extensions blocking challenges.cloudflare.com and reload, or use the CLI: npx repomix --remote owner/repo.'
    : 'Verification failed. Please reload the page and try again.';
}

// Mirror handlePackRequest's onAbort messaging. Used when the Turnstile
// challenge is aborted before /api/pack is reached, so we short-circuit
// rather than calling handlePackRequest at all.
export function abortMessage(reason: AbortSignal['reason']): string {
  return reason === 'timeout'
    ? 'Request timed out.\nPlease consider using Include Patterns or Ignore Patterns to reduce the scope.'
    : 'Request was cancelled.';
}
