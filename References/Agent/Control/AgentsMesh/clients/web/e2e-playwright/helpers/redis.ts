import { execSync } from "node:child_process";
import { getComposeProject } from "../helpers/env";

/**
 * Redis helper for E2E tests.
 * Clears rate limit keys to prevent 429 errors during test runs.
 */
export function clearAuthRateLimit(): void {
  const container = `${getComposeProject()}-redis-1`;
  try {
    execSync(
      `docker exec ${container} redis-cli --scan --pattern 'ratelimit:auth:*' | xargs -r docker exec -i ${container} redis-cli DEL`,
      { encoding: "utf-8", timeout: 5_000 }
    );
  } catch {
    // Fallback: try KEYS + DEL directly
    try {
      execSync(
        `docker exec ${container} redis-cli EVAL "local keys = redis.call('KEYS', 'ratelimit:auth:*') for i,k in ipairs(keys) do redis.call('DEL', k) end return #keys" 0`,
        { encoding: "utf-8", timeout: 5_000 }
      );
    } catch {
      // Silently ignore — fail-open
    }
  }
}
