/**
 * Discover competitor / peer entity CANDIDATES for a topic via DuckDuckGo.
 *
 * Architecture: LLM-first, same as the SWOT/5F/PESTEL refactor. The CLI
 * never tries to decide "is X a brand?" — domain/language hardcoded
 * keyword lists do not generalize (see Decision Log 2026-05-15). Instead
 * the CLI emits a frequency-ranked list of capitalized brand-shaped
 * candidates extracted from DDG SERP titles + snippets, and the host LLM
 * picks the actual competitors from the candidate pool.
 *
 * Pipeline:
 *   1. Fan out 2-3 phrasings of the "vs / alternatives / competitor" query.
 *   2. Apply CAPITALIZED_PHRASE / KR_BRAND regex to each title + snippet
 *      (processed separately so phrases never bridge field boundaries).
 *   3. Universal-only normalization: strip trailing KR particles
 *      (그래마틱 normalization, not semantic), drop pure-digit / 1-char
 *      tokens, drop candidates that fully overlap the topic.
 *   4. Frequency-rank. Apply subsumption (drop "Copilot" when its count is
 *      explained by "GitHub Copilot") — pure deduplication, no semantics.
 *   5. Return top-N candidates. The host LLM filters listicle words,
 *      generic nouns, news-cycle vocabulary, etc.
 *
 * Why no hardcoded stopwords: every domain (KR ecommerce vs EN dev tools
 * vs JP gaming) needs different "what's not a brand" lists. Maintaining
 * them is the brittle-classifier failure mode this skill exists to avoid.
 */

import { apiKeywordSearch } from "../../search/strategies/api/index.js";
import type { FetchContext } from "../../search/types.js";

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface DiscoverOpts {
  topic: string;
  locale: "en" | "ko";
  limit?: number; // default 20 — generous because LLM filters
  timeoutMs?: number; // default 20_000
}

export interface DiscoverResult {
  topic: string;
  locale: "en" | "ko";
  queries_used: string[];
  items_scanned: number;
  candidates: Array<{ entity: string; mentions: number }>;
  reason?: string;
}

// ---------------------------------------------------------------------------
// Universal grammar / regex constants (no semantic content)
// ---------------------------------------------------------------------------

// Brand-shaped EN token: starts uppercase OR camelCase (xAI, iPhone).
const BRAND_TOKEN =
  "(?:[A-Z][A-Za-z0-9&.\\-]*|[a-z][A-Za-z0-9&.\\-]*[A-Z][A-Za-z0-9&.\\-]*)";
// 1-4 brand tokens separated by whitespace.
const CAPITALIZED_PHRASE = new RegExp(
  `\\b${BRAND_TOKEN}(?:\\s+${BRAND_TOKEN}){0,3}\\b`,
  "g",
);

// KR brand-shaped candidate (≥2 chars): pure Hangul, or Hangul+digit, or
// short-ASCII+Hangul (G마켓, T맵).
const KR_BRAND = /(?:[가-힣]{2,}|\d+[가-힣]{1,}|[A-Za-z]{1,3}[가-힣]{1,})/g;

// Unambiguous trailing KR particles — pure grammar normalization. Skip
// 가/이 (too commonly inside real brand names: 11번가, 위메프이).
const KR_TRAILING_PARTICLES =
  /(?:은|는|을|를|의|도|에|에서|으로|로|와|과|만|까지|부터|이고|이며|입니다|이에요|예요|입니다요|입니다만)$/u;

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

const DEFAULT_LIMIT = 20;
const DEFAULT_TIMEOUT_MS = 20_000;

export async function discoverCompetitors(
  opts: DiscoverOpts,
): Promise<DiscoverResult> {
  const limit = opts.limit ?? DEFAULT_LIMIT;
  const timeoutMs = opts.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const queries = buildQueries(opts.topic, opts.locale);

  const ctx: FetchContext = {
    timeoutMs,
    locale: opts.locale === "ko" ? "ko-KR,ko;q=0.9" : "en-US,en;q=0.9",
  };

  const items: Array<{ title: string; snippet: string }> = [];
  for (const q of queries) {
    try {
      const results = await apiKeywordSearch(q, ctx, ["duckduckgo"]);
      const r = results[0];
      if (!r || r.status !== "ok") continue;
      let parsed: unknown;
      try {
        parsed = JSON.parse(r.content);
      } catch {
        continue;
      }
      const envelope = parsed as {
        items?: Array<{ title?: string; snippet?: string | null }>;
      };
      for (const it of envelope.items ?? []) {
        items.push({
          title: String(it.title ?? ""),
          snippet: String(it.snippet ?? ""),
        });
      }
    } catch {
      /* skip the failing query, continue with the others */
    }
  }

  if (items.length === 0) {
    return {
      topic: opts.topic,
      locale: opts.locale,
      queries_used: queries,
      items_scanned: 0,
      candidates: [],
      reason: "no SERP results — uvx / ddgs may be unavailable",
    };
  }

  const candidates = rankCandidates(items, opts.topic, opts.locale, limit);
  return {
    topic: opts.topic,
    locale: opts.locale,
    queries_used: queries,
    items_scanned: items.length,
    candidates,
  };
}

// ---------------------------------------------------------------------------
// Internals — exported for tests
// ---------------------------------------------------------------------------

export function buildQueries(topic: string, locale: "en" | "ko"): string[] {
  const t = topic.trim();
  if (locale === "ko") {
    return [`${t} 경쟁사`, `${t} 대안`, `${t} vs`];
  }
  return [`${t} vs`, `alternatives to ${t}`, `${t} competitors`];
}

export function rankCandidates(
  items: Array<{ title: string; snippet: string }>,
  topic: string,
  locale: "en" | "ko",
  limit: number,
): Array<{ entity: string; mentions: number }> {
  const topicTokens = tokenize(topic);
  // canonical lowercase key → first-seen display form
  const display = new Map<string, string>();
  const counts = new Map<string, number>();
  const firstSeen = new Map<string, number>();
  let order = 0;

  // Process title and snippet SEPARATELY so the phrase regex never bridges
  // across fields (would otherwise yield "OpenAI xAI" from "vs OpenAI" +
  // "xAI vs ...").
  const fields: string[] = [];
  for (const item of items) {
    if (item.title) fields.push(item.title);
    if (item.snippet) fields.push(item.snippet);
  }
  for (const text of fields) {
    for (const raw of extractCandidates(text, locale)) {
      const candidate = normalizeCandidate(raw);
      if (!isUniversallyValid(candidate, topicTokens)) continue;
      const key = candidate.toLowerCase();
      if (!display.has(key)) {
        display.set(key, candidate);
        firstSeen.set(key, order++);
      }
      counts.set(key, (counts.get(key) ?? 0) + 1);
    }
  }

  // Subsumption: when a multi-word candidate (e.g. "GitHub Copilot") fully
  // accounts for a single-word candidate's count (e.g. "Copilot"), drop the
  // shorter form. Pure deduplication — no semantic content.
  const dropped = new Set<string>();
  for (const longerKey of counts.keys()) {
    if (!longerKey.includes(" ")) continue;
    const longerCount = counts.get(longerKey) ?? 0;
    if (longerCount < 2) continue; // need ≥2 hits before subsuming
    const tail = longerKey.split(/\s+/).slice(-1)[0]?.toLowerCase();
    if (!tail) continue;
    const shorter = counts.get(tail);
    if (shorter !== undefined && shorter <= longerCount) {
      dropped.add(tail);
    }
  }

  return [...counts.entries()]
    .filter(([k]) => !dropped.has(k))
    .sort(([ka, ca], [kb, cb]) => {
      if (cb !== ca) return cb - ca;
      return (firstSeen.get(ka) ?? 0) - (firstSeen.get(kb) ?? 0);
    })
    .slice(0, limit)
    .map(([k, c]) => ({
      entity: display.get(k) ?? k,
      mentions: c,
    }));
}

function extractCandidates(text: string, locale: "en" | "ko"): string[] {
  const out: string[] = [];
  // EN regex runs in both modes — KR tech blogs mention English brand
  // names verbatim.
  for (const m of text.matchAll(CAPITALIZED_PHRASE)) {
    out.push(m[0]);
  }
  if (locale === "ko") {
    for (const m of text.matchAll(KR_BRAND)) {
      out.push(m[0]);
    }
  }
  return out;
}

function normalizeCandidate(raw: string): string {
  let s = raw.replace(/\s+/g, " ").trim();
  // strip trailing punctuation / closing bracket
  s = s.replace(/[.,;:\-)]+$/u, "").trim();
  // strip unambiguous trailing KR particles when candidate contains Hangul
  if (/[가-힣]/.test(s)) {
    s = s.replace(KR_TRAILING_PARTICLES, "").trim();
  }
  return s;
}

function isUniversallyValid(
  candidate: string,
  topicTokens: Set<string>,
): boolean {
  if (candidate.length < 2) return false;
  // Pure digit / year tokens are never brand names.
  if (/^\d+$/.test(candidate)) return false;
  // Reject candidates that fully overlap the topic in either direction
  // (case-insensitive, token-set).
  const candTokens = tokenize(candidate);
  if (candTokens.size === 0) return false;
  if (isSubset(candTokens, topicTokens)) return false;
  if (isSubset(topicTokens, candTokens)) return false;
  return true;
}

function tokenize(s: string): Set<string> {
  return new Set(
    s
      .toLowerCase()
      .split(/[\s.,;:()/]+/)
      .map((t) => t.replace(/[^a-z0-9가-힣]/g, ""))
      .filter((t) => t.length > 0),
  );
}

function isSubset(a: Set<string>, b: Set<string>): boolean {
  if (a.size === 0) return false;
  for (const t of a) if (!b.has(t)) return false;
  return true;
}
