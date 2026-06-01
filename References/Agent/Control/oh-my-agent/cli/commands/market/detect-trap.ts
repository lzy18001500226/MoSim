/**
 * `oma market detect-trap` — topic preflight guard.
 *
 * Design ref: docs/plans/designs/011-oma-market-research.md §4.1 + §7.
 *
 * Detects two classes of low-signal topics before the pipeline starts:
 *   Class 1 — Demographic shopping queries (broad gift/present searches)
 *   Class 2 — Single-token common-noun topics that are too broad to research
 *
 * Pure CPU, no I/O, no network.
 */

// ---------------------------------------------------------------------------
// Regex constants — compiled once at module load
// ---------------------------------------------------------------------------

/** Strips ASCII control characters (0x00-0x1F, DEL 0x7F). */
// biome-ignore lint/suspicious/noControlCharactersInRegex: control-char strip is intentional input sanitization
const RE_CONTROL_CHARS = /[\x00-\x1F\x7F]/g;

// Class 1 — Demographic shopping patterns (case-insensitive, checked after strip)
const RE_GIFT_AGE =
  /^(birthday\s+)?(gift|gifts|present|presents)\s+(for|ideas\s+for)\s+(a\s+|my\s+)?\d+[\s-]?year[\s-]?old\b/i;
const RE_BEST_FOR_DEMO =
  /^(best|top)\s+[\w\s-]+?\s+for\s+(men|women|kids|guys|girls|teens|dads|moms|husbands|wives|brothers|sisters|friends)\b/i;
const RE_WHAT_TO_BUY =
  /^what\s+to\s+(buy|get|gift)\s+(for\s+)?(a\s+|my\s+)?(\d+[\s-]?year[\s-]?old|husband|wife|dad|mom|brother|sister|friend|boss|coworker)\b/i;
const RE_PRESENT_FOR =
  /^(present|presents|gift|gifts)\s+for\s+(a\s+|my\s+)?(husband|wife|dad|mom|brother|sister|friend|boss|coworker)\b/i;

const CLASS1_PATTERNS = [
  RE_GIFT_AGE,
  RE_BEST_FOR_DEMO,
  RE_WHAT_TO_BUY,
  RE_PRESENT_FOR,
] as const;

// Qualifier escape — if any of these match, Class 1 refusal is skipped
const RE_BUDGET_DOLLAR = /\$\d+|budget/i;
const RE_WHO_LOVES = /who\s+(loves|likes|is\s+into|enjoys)/i;
const RE_HOBBIES = /hobbies?/i;
const RE_HOBBY_WORD_ENTHUSIAST =
  /\b(cooking|running|reading|gaming|golf|woodworking|coding|hiking|cycling|fishing|music)\s+(obsessed|enthusiast|fan|lover)\b/i;

/** Relational or generic-person nouns that disqualify the "activity-noun
 *  after age" escape — these still produce listicle noise, not market signal. */
const RELATIONAL_NOUNS = new Set([
  "husband",
  "wife",
  "dad",
  "mom",
  "father",
  "mother",
  "brother",
  "sister",
  "friend",
  "boss",
  "coworker",
  "son",
  "daughter",
  "grandma",
  "grandpa",
  "aunt",
  "uncle",
  "nephew",
  "niece",
  "partner",
  "boyfriend",
  "girlfriend",
  "man",
  "woman",
  "guy",
  "gal",
  "men",
  "women",
  "kid",
  "kids",
  "teen",
  "teens",
]);

/**
 * Matches "<n> year old <noun>" where noun is NOT a relational noun.
 * Capture group 1 = the noun token(s) after "year old".
 */
const RE_AGE_ACTIVITY_NOUN = /\d+[\s-]?year[\s-]?old\s+(\w+)/i;

// Class 2 — Single common-noun stop list (exact, case-insensitive)
const COMMON_NOUN_STOP_LIST = new Set([
  "sneakers",
  "shoes",
  "food",
  "music",
  "books",
  "games",
  "phones",
  "laptops",
  "ai",
  "crypto",
  "nft",
  "sports",
  "fashion",
]);

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface DetectTrapOptions {
  topic: string;
  force?: boolean;
}

export interface DetectTrapResult {
  ok: boolean;
  exitCode: 0 | 2 | 4;
  reason?:
    | "empty"
    | "too-long"
    | "demographic-shopping"
    | "single-noun-too-broad";
  message?: string;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Returns true when the topic qualifies for the Class 1 escape hatch, meaning
 * the query is sufficiently specific despite matching a demographic pattern.
 */
function hasQualifierEscape(topic: string): boolean {
  if (RE_BUDGET_DOLLAR.test(topic)) return true;
  if (RE_WHO_LOVES.test(topic)) return true;
  if (RE_HOBBIES.test(topic)) return true;
  if (RE_HOBBY_WORD_ENTHUSIAST.test(topic)) return true;

  // "<n> year old <noun>" where noun is NOT a relational noun → escape
  const ageMatch = RE_AGE_ACTIVITY_NOUN.exec(topic);
  if (ageMatch !== null) {
    const noun = ageMatch[1]?.toLowerCase() ?? "";
    if (!RELATIONAL_NOUNS.has(noun)) return true;
  }

  return false;
}

// ---------------------------------------------------------------------------
// Core logic
// ---------------------------------------------------------------------------

/**
 * Sanitises and validates `opts.topic`, returning a structured result.
 * Never throws; all error states are encoded in `DetectTrapResult`.
 */
export function detectTrap(opts: DetectTrapOptions): DetectTrapResult {
  const { force = false } = opts;
  let { topic } = opts;

  // --- Sanitization (always runs) ---

  // 1. Reject empty / whitespace-only before stripping
  if (topic.trim().length === 0) {
    return {
      ok: false,
      exitCode: 4,
      reason: "empty",
      message: "[INVALID] topic is required",
    };
  }

  // 2. Strip ASCII control characters
  topic = topic.replace(RE_CONTROL_CHARS, "");

  // 3. Reject length > 200
  if (topic.length > 200) {
    return {
      ok: false,
      exitCode: 4,
      reason: "too-long",
      message: "[INVALID] topic too long (>200 chars)",
    };
  }

  // --- Trap detection (skipped when --force) ---

  if (!force) {
    // Class 1 — Demographic shopping
    const matchesClass1 = CLASS1_PATTERNS.some((re) => re.test(topic));
    if (matchesClass1 && !hasQualifierEscape(topic)) {
      return {
        ok: false,
        exitCode: 2,
        reason: "demographic-shopping",
        message:
          "[REFUSE] This topic matches a demographic shopping pattern (e.g., broad gift/present queries for a person type).\n" +
          "These queries return listicle noise rather than market signals.\n" +
          'Suggested reframe: "home automation gifts for adults who enjoy woodworking" or "top ergonomic desk accessories under $50 for remote workers".\n' +
          "Hint: use --force to bypass this check.",
      };
    }

    // Class 2 — Single-noun too broad
    const tokens = topic.trim().split(/\s+/);
    if (
      tokens.length === 1 &&
      tokens[0] !== undefined &&
      COMMON_NOUN_STOP_LIST.has(tokens[0].toLowerCase())
    ) {
      return {
        ok: false,
        exitCode: 2,
        reason: "single-noun-too-broad",
        message:
          `[REFUSE] "${topic}" is a single common-noun topic that is too broad for meaningful market research.\n` +
          "A one-word topic produces high-volume, low-signal results across unrelated niches.\n" +
          `Suggested reframe: combine the noun with an audience, use-case, or pain point — e.g., "${topic} for remote workers" or "best ${topic} under $100 for beginners".\n` +
          "Hint: use --force to bypass this check.",
      };
    }
  }

  return { ok: true, exitCode: 0 };
}

// ---------------------------------------------------------------------------
// CLI entry
// ---------------------------------------------------------------------------

/**
 * Parses raw argv, calls `detectTrap`, writes to stderr when needed, and
 * returns the exit code. The caller is responsible for `process.exit`.
 *
 * Supported argv shapes:
 *   ["<topic>"]
 *   ["<topic>", "--force"]
 *   ["--force", "<topic>"]
 */
export async function runDetectTrap(argv: string[]): Promise<number> {
  let force = false;
  const positionals: string[] = [];

  for (const arg of argv) {
    if (arg === "--force") {
      force = true;
    } else if (!arg.startsWith("--")) {
      positionals.push(arg);
    }
    // Unknown flags are silently ignored
  }

  const topic = positionals.join(" ");

  const result = detectTrap({ topic, force });

  if (!result.ok && result.message !== undefined) {
    process.stderr.write(`${result.message}\n`);
  }

  return result.exitCode;
}
