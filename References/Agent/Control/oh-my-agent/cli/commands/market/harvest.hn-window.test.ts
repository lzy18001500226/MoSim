/**
 * Regression: HN harvest must pass `numericFilters=created_at_i>${unixTs}`
 * via the directFetch path. Earlier the source routed through
 * apiKeywordSearch (which hits Algolia without that filter), so the
 * harvest `--window` was silently ignored.
 *
 * This test spies on `globalThis.fetch`, runs harvest with sources=['hn']
 * and window=7d, and asserts the captured URL contains the encoded
 * numericFilters with a unix timestamp ≈ now - 7d.
 */

import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { harvest } from "./harvest.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "../../..");

const HN_FIXTURE = {
  hits: [
    {
      objectID: "regression-1",
      title: "regression item",
      url: "https://example.com/regression-1",
      author: "tester",
      created_at_i: Math.floor(Date.now() / 1000) - 60,
      points: 1,
      num_comments: 0,
    },
  ],
};

describe("hn harvest window filter (regression)", () => {
  const original: Record<string, string | undefined> = {};
  const envKeys = [
    "OMA_MARKET_MOCK",
    "X_BEARER_TOKEN",
    "SCRAPECREATORS_API_KEY",
    "PERPLEXITY_API_KEY",
    "YOUTUBE_SC_AVAILABLE",
    "XDG_CACHE_HOME",
  ];

  let fetchSpy: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    for (const k of envKeys) original[k] = process.env[k];
    // Live path, not the mock-fixture replay.
    delete process.env.OMA_MARKET_MOCK;
    delete process.env.X_BEARER_TOKEN;
    delete process.env.SCRAPECREATORS_API_KEY;
    delete process.env.PERPLEXITY_API_KEY;
    delete process.env.YOUTUBE_SC_AVAILABLE;

    fetchSpy = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => HN_FIXTURE,
    }));
    vi.stubGlobal("fetch", fetchSpy);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    for (const k of envKeys) {
      if (original[k] === undefined) delete process.env[k];
      else process.env[k] = original[k];
    }
  });

  it("passes numericFilters=created_at_i><unixTs> for 7d window", async () => {
    const before = Math.floor(Date.now() / 1000);
    await harvest(
      {
        query: `hn-window-regression-${Date.now()}`,
        sources: ["hn"],
        window: "7d",
        perSourceLimit: 5,
        noCache: true,
      },
      repoRoot,
    );
    const after = Math.floor(Date.now() / 1000);

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const url = String((fetchSpy.mock.calls[0] as unknown[])[0]);
    expect(url).toContain("hn.algolia.com/api/v1/search");
    expect(url).toContain("hitsPerPage=5");

    // numericFilters=created_at_i>{ts} with `>` URL-encoded as %3E
    const m = /numericFilters=created_at_i%3E(\d+)/.exec(url);
    expect(m).not.toBeNull();
    const tsInUrl = Number(m?.[1]);

    // ts should be ≈ now - 7d (allow a small skew for clock drift / encoding)
    const sevenDays = 7 * 24 * 60 * 60;
    const expectedLo = before - sevenDays - 2;
    const expectedHi = after - sevenDays + 2;
    expect(tsInUrl).toBeGreaterThanOrEqual(expectedLo);
    expect(tsInUrl).toBeLessThanOrEqual(expectedHi);
  });

  it("uses a different unixTs for 30d (4x larger lookback)", async () => {
    await harvest(
      {
        query: `hn-window-regression-30d-${Date.now()}`,
        sources: ["hn"],
        window: "30d",
        perSourceLimit: 3,
        noCache: true,
      },
      repoRoot,
    );

    const url = String((fetchSpy.mock.calls[0] as unknown[])[0]);
    const m = /numericFilters=created_at_i%3E(\d+)/.exec(url);
    expect(m).not.toBeNull();
    const tsInUrl = Number(m?.[1]);
    const now = Math.floor(Date.now() / 1000);
    const thirtyDays = 30 * 24 * 60 * 60;
    expect(now - tsInUrl).toBeGreaterThanOrEqual(thirtyDays - 2);
    expect(now - tsInUrl).toBeLessThanOrEqual(thirtyDays + 2);
  });
});
