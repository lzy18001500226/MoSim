/**
 * Operator pack loader for `oma market` pipeline.
 *
 * Operator packs are markdown files that live at:
 *   ${repoRoot}/.agents/skills/oma-market/resources/operator-packs/${pack}.md
 *
 * They are the single source of truth for OR clause keywords injected into
 * harvest queries. This module reads, parses, and caches them so repeated
 * calls within a process pay no I/O cost.
 */

import { readFile } from "node:fs/promises";
import { join } from "node:path";
import type { Intent } from "./schema.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type OperatorPack =
  | "pain"
  | "positive"
  | "competitor"
  | "discovery"
  | "none";

export interface OperatorPackContent {
  pack: OperatorPack;
  /** OR clause for English keywords, e.g. "(broken OR bug OR crash OR ...)" */
  en: string;
  /** OR clause for Korean keywords */
  ko: string;
  /** Noise-reduction suffix, e.g. "-is:retweet -is:reply", may be "" */
  noiseReduction: string;
  /** One-line summary from the pack file's rationale section, or "" */
  rationale: string;
}

// ---------------------------------------------------------------------------
// Module-scope regex (compiled once)
// ---------------------------------------------------------------------------

/**
 * Matches a code-fenced line that is an OR clause of ASCII-only keywords.
 * The line must start with `(`, contain ` OR `, and must NOT contain any
 * CJK / Hangul characters (so it stays English-only).
 *
 * We allow quoted phrases like "migrating from" inside the clause.
 */
const RE_EN_OR_CLAUSE = /^\((?:[^()ᄀ-ᇿ가-힯]+)\)$/m;

/**
 * Matches a code-fenced line that is an OR clause containing Korean Hangul.
 * Unicode block AC00–D7AF covers the full syllable block; 1100–11FF covers
 * jamo; 3130–318F covers compatibility jamo.
 */
const RE_KO_OR_CLAUSE = /^\((?:[^\n]*[가-힯ᄀ-ᇿ㄰-㆏][^\n]*)\)$/m;

/**
 * Matches the full `-is:retweet -is:reply` noise-reduction pattern.
 * We capture exactly this canonical form; a looser variant (`-is:retweet` only)
 * is also accepted for packs that mention only one filter.
 */
const RE_NOISE_REDUCTION = /-is:retweet(?:\s+-is:reply)?/;

/**
 * Matches an ATX heading line (# ... or ## ...).
 */
const RE_HEADING = /^#{1,6}\s/;

/**
 * Matches a code-fence opening/closing line.
 */
const RE_CODE_FENCE = /^```/;

// ---------------------------------------------------------------------------
// Module-scope cache
// ---------------------------------------------------------------------------

const _cache = new Map<OperatorPack, OperatorPackContent>();

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function _extractEnOrClause(text: string): string {
  const match = RE_EN_OR_CLAUSE.exec(text);
  return match ? match[0].trim() : "";
}

function _extractKoOrClause(text: string): string {
  const match = RE_KO_OR_CLAUSE.exec(text);
  return match ? match[0].trim() : "";
}

function _extractNoiseReduction(text: string): string {
  const match = RE_NOISE_REDUCTION.exec(text);
  return match ? match[0].trim() : "";
}

/**
 * Returns the first non-heading, non-code-fence, non-empty prose line that is
 * shorter than 200 characters.
 */
function _extractRationale(text: string): string {
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (line.length === 0) continue;
    if (RE_HEADING.test(line)) continue;
    if (RE_CODE_FENCE.test(line)) continue;
    if (line.length < 200) return line;
  }
  return "";
}

function _syntheticNone(): OperatorPackContent {
  return {
    pack: "none",
    en: "",
    ko: "",
    noiseReduction: "",
    rationale: "No operator pack — bare query is used as-is.",
  };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Loads and parses an operator pack from its markdown file.
 *
 * Results are cached in the module-scope Map so repeated calls within a
 * process incur no additional I/O.
 *
 * @param pack     - The operator pack identifier.
 * @param repoRoot - Absolute path to the repository root (used to resolve
 *                   the `.agents/` directory).
 */
export async function loadOperatorPack(
  pack: OperatorPack,
  repoRoot: string,
): Promise<OperatorPackContent> {
  const cached = _cache.get(pack);
  if (cached !== undefined) return cached;

  if (pack === "none") {
    const content = _syntheticNone();
    _cache.set("none", content);
    return content;
  }

  const filePath = join(
    repoRoot,
    ".agents",
    "skills",
    "oma-market",
    "resources",
    "operator-packs",
    `${pack}.md`,
  );

  let text: string;
  try {
    text = await readFile(filePath, "utf-8");
  } catch {
    throw new Error(`[operators] pack file not found: ${pack}.md`);
  }

  const content: OperatorPackContent = {
    pack,
    en: _extractEnOrClause(text),
    ko: _extractKoOrClause(text),
    noiseReduction: _extractNoiseReduction(text),
    rationale: _extractRationale(text),
  };

  _cache.set(pack, content);
  return content;
}

/**
 * Maps a pipeline `Intent` value to the corresponding `OperatorPack`.
 *
 * - `"pain"`       → `"pain"`
 * - `"trend"`      → `"none"` (trend uses a bare query without keyword operators)
 * - `"competitor"` → `"competitor"`
 * - `"discovery"`  → `"discovery"`
 */
export function intentToOperatorPack(
  intent: "pain" | "trend" | "competitor" | "discovery",
): OperatorPack {
  const mapping: Record<Intent, OperatorPack> = {
    pain: "pain",
    trend: "none",
    competitor: "competitor",
    discovery: "discovery",
  };
  return mapping[intent];
}

/**
 * Appends the locale-appropriate OR clause and noise-reduction suffix to a
 * base query string.
 *
 * When the pack has empty strings (e.g. `"none"` pack or no KO clause for a
 * given pack) only the non-empty parts are included, preventing double-spaces.
 *
 * @param baseQuery - The raw topic / entity string entered by the user.
 * @param content   - The loaded `OperatorPackContent`.
 * @param locale    - `"en"` (default) or `"ko"`.
 * @returns The fully composed query string, trimmed.
 */
export function buildQueryWithOperators(
  baseQuery: string,
  content: OperatorPackContent,
  locale: "en" | "ko" = "en",
): string {
  const orClause = locale === "ko" ? content.ko : content.en;
  return [baseQuery, orClause, content.noiseReduction]
    .map((s) => s.trim())
    .filter(Boolean)
    .join(" ");
}
