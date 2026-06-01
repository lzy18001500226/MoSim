import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

/**
 * Antigravity CLI (agy) keeps its state under `~/.gemini/antigravity-cli/`.
 * The credentials themselves live in the OS keyring (so they aren't visible
 * to us), but the post-login `cache/onboarding.json` flips
 * `onboardingComplete: true` once sign-in finishes. We use that as the
 * file-state heuristic, with an `ANTIGRAVITY_API_KEY` env var as the
 * headless escape hatch.
 */
export function isAntigravityAuthenticated(
  env: NodeJS.ProcessEnv = process.env,
): boolean {
  if (env.ANTIGRAVITY_API_KEY?.trim()) return true;

  const onboardingPath = join(
    homedir(),
    ".gemini",
    "antigravity-cli",
    "cache",
    "onboarding.json",
  );
  if (!existsSync(onboardingPath)) return false;
  try {
    const parsed = JSON.parse(readFileSync(onboardingPath, "utf-8")) as {
      onboardingComplete?: unknown;
      consumerOnboardingComplete?: unknown;
      enterpriseOnboardingComplete?: unknown;
    };
    return (
      parsed.onboardingComplete === true ||
      parsed.consumerOnboardingComplete === true ||
      parsed.enterpriseOnboardingComplete === true
    );
  } catch {
    return false;
  }
}
