// cli/commands/model/check.ts
// Diff engine and formatters for model:check command.

import pc from "picocolors";
import type { ModelSpec } from "../../platform/model-registry.js";
import type { CursorModel } from "./sources/cursor.js";
import type { OpenRouterModel } from "./sources/openrouter.js";

export type SourceModel = OpenRouterModel | CursorModel;

export type DriftedEntry = {
  slug: string;
  current: Partial<ModelSpec>;
  source: Partial<SourceModel>;
};

export type RemovedEntry = {
  slug: string;
  spec: ModelSpec;
};

export type DiffResult = {
  new: SourceModel[];
  removed: RemovedEntry[];
  drifted: DriftedEntry[];
};

/**
 * Compute the diff between the registered models and the live source models.
 *
 * - new: models present in source but not in registry
 * - removed: models present in registry but not in source
 * - drifted: models present in both but with differing attributes
 *   (currently a no-op placeholder — drift detection is minimal for now,
 *    reserved for future contextLength comparison once registry carries it)
 */
export function computeDiff(
  registered: Map<string, ModelSpec>,
  sourceModels: SourceModel[],
): DiffResult {
  const sourceBySlug = new Map<string, SourceModel>(
    sourceModels.map((m) => [m.slug, m]),
  );

  const newModels: SourceModel[] = [];
  const removedModels: RemovedEntry[] = [];
  const driftedModels: DriftedEntry[] = [];

  // Find new models (in source, not in registry)
  for (const [slug, sourceModel] of sourceBySlug) {
    if (!registered.has(slug)) {
      newModels.push(sourceModel);
    }
  }

  // Find removed models (in registry, not in source)
  for (const [slug, spec] of registered) {
    if (!sourceBySlug.has(slug)) {
      removedModels.push({ slug, spec });
    }
  }

  // Drift detection placeholder — drifted array is intentionally empty for now.
  // Future: compare contextLength, pricing when registry captures these fields.

  return {
    new: newModels,
    removed: removedModels,
    drifted: driftedModels,
  };
}

/**
 * Format a DiffResult as a human-readable string with color-coded prefixes.
 */
export function formatHumanReadable(diff: DiffResult): string {
  const lines: string[] = [];

  if (
    diff.new.length === 0 &&
    diff.removed.length === 0 &&
    diff.drifted.length === 0
  ) {
    lines.push(pc.dim("  (no changes)"));
    return lines.join("\n");
  }

  for (const model of diff.new) {
    lines.push(pc.green(`  + ${model.slug}`));
  }

  for (const { slug } of diff.removed) {
    lines.push(pc.red(`  - ${slug}`));
  }

  for (const entry of diff.drifted) {
    lines.push(pc.yellow(`  ~ ${entry.slug}`));
  }

  return lines.join("\n");
}

/**
 * Format a DiffResult as a JSON string.
 */
export function formatJson(diff: DiffResult): string {
  return JSON.stringify(diff, null, 2);
}
