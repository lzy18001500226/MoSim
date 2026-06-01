import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fetchOpenRouterModels } from "./openrouter.js";

describe("fetchOpenRouterModels", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns models on successful response", async () => {
    const mockData = {
      data: [
        {
          id: "anthropic/claude-sonnet-4-6",
          context_length: 200000,
          pricing: { prompt: "0.000003", completion: "0.000015" },
        },
        {
          id: "openai/gpt-5.5",
          context_length: 128000,
          pricing: { prompt: "0.000005", completion: "0.000015" },
        },
      ],
    };

    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => mockData,
    } as Response);

    const result = await fetchOpenRouterModels();
    expect(result.ok).toBe(true);
    if (!result.ok) throw new Error("expected ok");

    expect(result.models).toHaveLength(2);
    expect(result.models[0]).toEqual({
      slug: "anthropic/claude-sonnet-4-6",
      contextLength: 200000,
      pricingPrompt: "0.000003",
      pricingCompletion: "0.000015",
    });
    expect(result.models[1]).toEqual({
      slug: "openai/gpt-5.5",
      contextLength: 128000,
      pricingPrompt: "0.000005",
      pricingCompletion: "0.000015",
    });
  });

  it("returns ok:false on 4xx response", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: false,
      status: 401,
      statusText: "Unauthorized",
      json: async () => ({}),
    } as Response);

    const result = await fetchOpenRouterModels();
    expect(result.ok).toBe(false);
    if (result.ok) throw new Error("expected not ok");
    expect(result.error).toContain("401");
  });

  it("returns ok:false on AbortError (timeout)", async () => {
    const abortError = new DOMException("signal timed out", "TimeoutError");
    vi.mocked(fetch).mockRejectedValueOnce(abortError);

    const result = await fetchOpenRouterModels(100);
    expect(result.ok).toBe(false);
    if (result.ok) throw new Error("expected not ok");
    expect(result.error).toMatch(/timed out|timeout|abort/i);
  });

  it("returns ok:false on JSON parse failure", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => {
        throw new SyntaxError("Unexpected token");
      },
    } as unknown as Response);

    const result = await fetchOpenRouterModels();
    expect(result.ok).toBe(false);
    if (result.ok) throw new Error("expected not ok");
    expect(result.error).toContain("JSON");
  });

  it("returns ok:true with empty models array on empty data", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({ data: [] }),
    } as Response);

    const result = await fetchOpenRouterModels();
    expect(result.ok).toBe(true);
    if (!result.ok) throw new Error("expected ok");
    expect(result.models).toEqual([]);
  });

  it("handles missing pricing and context_length gracefully", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({
        data: [{ id: "some/model" }],
      }),
    } as Response);

    const result = await fetchOpenRouterModels();
    expect(result.ok).toBe(true);
    if (!result.ok) throw new Error("expected ok");
    expect(result.models[0]).toEqual({
      slug: "some/model",
      contextLength: 0,
      pricingPrompt: "0",
      pricingCompletion: "0",
    });
  });

  it("returns ok:false on unexpected response shape (missing data array)", async () => {
    vi.mocked(fetch).mockResolvedValueOnce({
      ok: true,
      status: 200,
      statusText: "OK",
      json: async () => ({ models: [] }),
    } as Response);

    const result = await fetchOpenRouterModels();
    expect(result.ok).toBe(false);
    if (result.ok) throw new Error("expected not ok");
    expect(result.error).toContain("data array");
  });
});
