/**
 * Poll an async condition until it resolves to true.
 * Used for waiting on async state transitions (pod status, runner online, etc.)
 */
export async function pollUntil(
  fn: () => Promise<boolean>,
  opts: { maxAttempts?: number; intervalMs?: number; label?: string } = {}
): Promise<void> {
  const { maxAttempts = 10, intervalMs = 1000, label = "condition" } = opts;

  for (let i = 0; i < maxAttempts; i++) {
    if (await fn()) return;
    if (i < maxAttempts - 1) {
      await new Promise((r) => setTimeout(r, intervalMs));
    }
  }
  throw new Error(
    `pollUntil(${label}) failed after ${maxAttempts} attempts`
  );
}
