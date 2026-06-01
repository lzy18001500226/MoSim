import { describe, expect, it } from "vitest";
import { buildQueries, rankCandidates } from "./competitors.js";

describe("buildQueries", () => {
  it("emits 3 EN phrasings", () => {
    expect(buildQueries("Cursor", "en")).toEqual([
      "Cursor vs",
      "alternatives to Cursor",
      "Cursor competitors",
    ]);
  });

  it("emits 3 KR phrasings", () => {
    expect(buildQueries("쿠팡", "ko")).toEqual([
      "쿠팡 경쟁사",
      "쿠팡 대안",
      "쿠팡 vs",
    ]);
  });

  it("trims surrounding whitespace from topic", () => {
    expect(buildQueries("  Cursor  ", "en")[0]).toBe("Cursor vs");
  });
});

// ---------------------------------------------------------------------------
// rankCandidates exercises only the UNIVERSAL filters:
//   - topic-overlap exclusion
//   - pure-digit / 1-char rejection
//   - KR particle stripping
//   - subsumption (deduplication)
//   - frequency ranking + deterministic tie-break
//
// No assertions about "is this a stopword?" — that's the host LLM's job.
// ---------------------------------------------------------------------------

describe("rankCandidates — frequency + topic exclusion", () => {
  it("ranks brand candidates by mention count, descending", () => {
    const items = [
      {
        title: "Cursor vs Windsurf - Which AI Editor is Better?",
        snippet: "We compare Cursor and Windsurf. Codeium also shows up.",
      },
      {
        title: "Top 5 Cursor Alternatives: Windsurf, Codeium, Cline",
        snippet: "Windsurf leads, with Codeium and Cline close behind.",
      },
      {
        title: "Cursor competitors: GitHub Copilot vs Windsurf",
        snippet: "Codeium and Cline are also worth a look.",
      },
    ];
    const ranked = rankCandidates(items, "Cursor", "en", 10);
    const entities = ranked.map((c) => c.entity);
    expect(entities).not.toContain("Cursor"); // topic excluded
    expect(entities[0]).toBe("Windsurf"); // most mentions
    expect(entities).toEqual(
      expect.arrayContaining([
        "Windsurf",
        "Codeium",
        "Cline",
        "GitHub Copilot",
      ]),
    );
  });

  it("attaches mention count to each candidate", () => {
    const items = [
      { title: "Brand1 is great", snippet: "Brand1 leads. Brand2 follows." },
    ];
    const ranked = rankCandidates(items, "Topic", "en", 10);
    const brand1 = ranked.find((c) => c.entity === "Brand1");
    const brand2 = ranked.find((c) => c.entity === "Brand2");
    expect(brand1?.mentions).toBe(2);
    expect(brand2?.mentions).toBe(1);
  });

  it("preserves casing of first occurrence (xAI, iPhone, GitHub Copilot)", () => {
    const items = [
      { title: "xAI vs OpenAI", snippet: "xAI competing with OpenAI" },
      { title: "OpenAI updates", snippet: "OpenAI announces new model" },
    ];
    const ranked = rankCandidates(items, "Grok", "en", 10);
    const entities = ranked.map((c) => c.entity);
    expect(entities).toContain("OpenAI");
    expect(entities).toContain("xAI");
  });

  it("returns empty array when no brand-shaped tokens exist", () => {
    const items = [{ title: "the of and", snippet: "in for to with" }];
    expect(rankCandidates(items, "Cursor", "en", 5)).toEqual([]);
  });

  it("rejects pure-digit candidates (years, numbers)", () => {
    const items = [
      { title: "2026 best apps include Brand1", snippet: "2026 is the year." },
    ];
    const ranked = rankCandidates(items, "Topic", "en", 5);
    expect(ranked.map((c) => c.entity)).not.toContain("2026");
  });

  it("respects the limit cap", () => {
    const items = [
      {
        title: "Brand1, Brand2, Brand3, Brand4, Brand5, Brand6, Brand7",
        snippet: "Brand1, Brand2, Brand3, Brand4, Brand5, Brand6, Brand7",
      },
    ];
    expect(rankCandidates(items, "Topic", "en", 3)).toHaveLength(3);
  });

  it("breaks ties by first-seen order (deterministic)", () => {
    const items = [
      { title: "Alpha is great", snippet: "" },
      { title: "Beta is also great", snippet: "" },
    ];
    const ranked = rankCandidates(items, "Topic", "en", 5);
    expect(ranked[0]?.entity).toBe("Alpha");
    expect(ranked[1]?.entity).toBe("Beta");
  });

  it("does not bridge title + snippet (no spurious cross-field phrases)", () => {
    // Title ends with "OpenAI" and snippet starts with "xAI". Without the
    // per-field split, the regex would match "OpenAI xAI" as one phrase.
    const items = [{ title: "vs OpenAI", snippet: "xAI competing" }];
    const ranked = rankCandidates(items, "Grok", "en", 5);
    const entities = ranked.map((c) => c.entity);
    expect(entities).not.toContain("OpenAI xAI");
    expect(entities).toContain("OpenAI");
    expect(entities).toContain("xAI");
  });
});

describe("rankCandidates — subsumption (deduplication, not semantics)", () => {
  it("drops 'Copilot' when 'GitHub Copilot' has ≥2 mentions accounting for it", () => {
    const items = [
      { title: "GitHub Copilot is great", snippet: "GitHub Copilot leads." },
      {
        title: "Cursor vs GitHub Copilot",
        snippet: "GitHub Copilot vs Cursor.",
      },
    ];
    const ranked = rankCandidates(items, "Cursor", "en", 10);
    const entities = ranked.map((c) => c.entity);
    expect(entities).toContain("GitHub Copilot");
    expect(entities).not.toContain("Copilot");
  });

  it("keeps single-word form when it has independent mentions", () => {
    const items = [
      { title: "Copilot alone here", snippet: "Just Copilot." },
      { title: "Copilot leads", snippet: "" },
      { title: "GitHub Copilot is one variant", snippet: "" },
    ];
    // Counts: Copilot=3, GitHub Copilot=1. Subsumption requires longerCount≥2
    // → does NOT subsume. Both kept.
    const ranked = rankCandidates(items, "Cursor", "en", 10);
    const entities = ranked.map((c) => c.entity);
    expect(entities).toContain("Copilot");
    expect(entities).toContain("GitHub Copilot");
  });
});

describe("rankCandidates — KR grammar normalization", () => {
  it("extracts both Hangul and ASCII brand names from KR SERPs", () => {
    const items = [
      {
        title: "쿠팡 vs 11번가",
        snippet: "G마켓도 비교. 옥션 위메프 티몬도 고려.",
      },
      {
        title: "쿠팡 경쟁사: 11번가, G마켓, 위메프",
        snippet: "옥션과 티몬도 빠질 수 없죠.",
      },
    ];
    const entities = rankCandidates(items, "쿠팡", "ko", 10).map(
      (c) => c.entity,
    );
    expect(entities).not.toContain("쿠팡");
    expect(entities).toContain("11번가");
    expect(entities).toContain("G마켓");
    expect(entities).toContain("위메프");
  });

  it("strips trailing KR particles 도/은/는/을/를/의 so 'G마켓도' counts as 'G마켓'", () => {
    const items = [
      {
        title: "쿠팡 vs G마켓도",
        snippet: "G마켓은 종합몰. G마켓의 강점.",
      },
    ];
    const ranked = rankCandidates(items, "쿠팡", "ko", 10);
    const gmarket = ranked.find((c) => c.entity === "G마켓");
    expect(gmarket?.mentions).toBe(3); // three forms collapse to one
  });

  it("keeps brand-internal 가/이 (does NOT strip from 11번가)", () => {
    const items = [{ title: "11번가는 종합몰 1위", snippet: "11번가가 강력." }];
    const entities = rankCandidates(items, "쿠팡", "ko", 10).map(
      (c) => c.entity,
    );
    expect(entities).toContain("11번가");
  });
});
