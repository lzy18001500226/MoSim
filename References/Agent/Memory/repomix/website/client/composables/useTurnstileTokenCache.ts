// Token cache for Cloudflare Turnstile. Decoupled from widget lifecycle so
// useTurnstile.ts stays focused on script loading / widget rendering / abort
// propagation.
//
// Responsibilities:
// - Stash a freshly minted token between preMintToken() and the next
//   takeToken() so the click path skips the challenge round-trip.
// - Single-flight the mint: a debounced pre-mint that fires while a click
//   is already in flight must NOT call mint() twice on the same widget
//   (the supersede logic in mintToken would otherwise reject the older
//   call and surface "Verification failed" on a perfectly valid challenge).
// - Make takeToken's cache claim atomic so two concurrent callers awaiting
//   the same shared mint promise can't both walk away with the same
//   one-shot token (siteverify would reject the second as
//   `timeout-or-duplicate`).

// Cached tokens are treated as expired before Cloudflare's hard 300s ceiling,
// to leave a safety margin for clock skew and network round-trips. A user
// who starts a pack just inside the window won't get a `timeout-or-duplicate`
// from siteverify because they were 1 second from the cliff.
const TOKEN_TTL_MS = 240_000;

interface CachedToken {
  token: string;
  mintedAt: number;
}

export interface TurnstileTokenCache {
  preMintToken(): Promise<string>;
  takeToken(signal?: AbortSignal): Promise<string>;
  reset(): void;
}

export function createTurnstileTokenCache(mint: () => Promise<string>): TurnstileTokenCache {
  let cachedToken: CachedToken | null = null;
  let mintPromise: Promise<string> | null = null;

  function isExpired(entry: CachedToken): boolean {
    return Date.now() - entry.mintedAt > TOKEN_TTL_MS;
  }

  // Single in-flight mint. The signal is intentionally NOT threaded through
  // — pre-mint is unaware of any submit lifecycle. takeToken() races the
  // shared promise against the caller's signal so a click-then-cancel
  // unblocks the awaiter without aborting the underlying mint, leaving
  // the resolved token in the cache for the next submit.
  function startMint(): Promise<string> {
    if (mintPromise) return mintPromise;
    mintPromise = mint()
      .then((token) => {
        cachedToken = { token, mintedAt: Date.now() };
        return token;
      })
      .catch((err) => {
        // Don't cache failures — let the next takeToken/preMintToken retry.
        cachedToken = null;
        throw err;
      })
      .finally(() => {
        mintPromise = null;
      });
    // Swallow rejections at the boundary so an unawaited preMintToken() (the
    // common case) doesn't trigger an unhandled rejection in the console;
    // errors surface on the actual submit path via takeToken.
    mintPromise.catch(() => {});
    return mintPromise;
  }

  function preMintToken(): Promise<string> {
    if (cachedToken && !isExpired(cachedToken)) {
      return Promise.resolve(cachedToken.token);
    }
    return startMint();
  }

  // Tokens are 1-shot, so claim the cache atomically (synchronous read +
  // null-out before any await). The shared mint's resolution value is
  // intentionally ignored — two concurrent callers awaiting the same
  // promise would otherwise both receive the same token. If a concurrent
  // caller already drained the cache, loop and start a fresh mint instead
  // of returning a duplicate that siteverify would reject with
  // `timeout-or-duplicate`.
  async function takeToken(signal?: AbortSignal): Promise<string> {
    while (true) {
      if (cachedToken && !isExpired(cachedToken)) {
        const token = cachedToken.token;
        cachedToken = null;
        return token;
      }
      const sharedMint = startMint();
      await waitWithAbort(sharedMint, signal);
      // Loop back: the mint resolved into the cache via startMint's `.then`,
      // but a concurrent takeToken may have claimed it first. The cache
      // check at the top of the loop is the single source of truth for
      // whether we got the token or need to mint another one.
    }
  }

  // Drop any cached token. Called from useTurnstile on widget
  // `expired-callback` (so the next take re-mints) and on unmount.
  // mintPromise stays — if a mint is currently running, its resolution
  // will populate the new cache; we just lost the previous unused token.
  function reset(): void {
    cachedToken = null;
  }

  return { preMintToken, takeToken, reset };
}

// Race a promise against an AbortSignal. Used by takeToken so a user-
// initiated cancel unblocks the await without cancelling the shared
// mint behind it (which may still cache its token for the next submit).
function waitWithAbort<T>(promise: Promise<T>, signal: AbortSignal | undefined): Promise<T> {
  if (!signal) return promise;
  if (signal.aborted) {
    return Promise.reject(new Error('Turnstile challenge aborted'));
  }
  return new Promise<T>((resolve, reject) => {
    const onAbort = () => reject(new Error('Turnstile challenge aborted'));
    signal.addEventListener('abort', onAbort, { once: true });
    promise.then(
      (value) => {
        signal.removeEventListener('abort', onAbort);
        resolve(value);
      },
      (err) => {
        signal.removeEventListener('abort', onAbort);
        reject(err);
      },
    );
  });
}
