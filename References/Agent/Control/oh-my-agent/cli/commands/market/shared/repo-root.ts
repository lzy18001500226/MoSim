/**
 * Resolve the oh-my-agent repository root by walking up from a starting
 * directory until a marker file is found. Works for:
 *   - `bunx tsx cli/cli.ts` (source path under cli/commands/market/)
 *   - `node cli/bin/cli.js` (bundled binary)
 *   - any cwd inside the repo
 *
 * The marker is `.agents/skills/oma-market/SKILL.md`, which is
 * specific enough that no upstream directory will accidentally match.
 */

import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const MARKER = ".agents/skills/oma-market/SKILL.md";

let cachedRoot: string | undefined;

export function findRepoRoot(startUrl: string = import.meta.url): string {
  if (cachedRoot !== undefined) return cachedRoot;

  const seeds = new Set<string>();
  try {
    seeds.add(dirname(fileURLToPath(startUrl)));
  } catch {
    // ignore unparseable URL
  }
  seeds.add(process.cwd());

  for (const seed of seeds) {
    let dir = seed;
    while (true) {
      if (existsSync(resolve(dir, MARKER))) {
        cachedRoot = dir;
        return dir;
      }
      const parent = dirname(dir);
      if (parent === dir) break;
      dir = parent;
    }
  }

  throw new Error(
    `[market] could not locate repo root (looking for ${MARKER}). ` +
      `Run from inside the oh-my-agent repository.`,
  );
}
