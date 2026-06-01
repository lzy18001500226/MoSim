// cli/commands/model/sources/openrouter.ts
// Fetches model list from OpenRouter API.

export type OpenRouterModel = {
  slug: string;
  contextLength: number;
  pricingPrompt: string;
  pricingCompletion: string;
};

export type OpenRouterResult =
  | { ok: true; models: OpenRouterModel[] }
  | { ok: false; error: string };

type OpenRouterResponseItem = {
  id: string;
  context_length?: number;
  pricing?: {
    prompt?: string;
    completion?: string;
  };
};

type OpenRouterResponse = {
  data: OpenRouterResponseItem[];
};

const OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models";

export async function fetchOpenRouterModels(
  timeoutMs?: number,
): Promise<OpenRouterResult> {
  try {
    const signal = AbortSignal.timeout(timeoutMs ?? 10_000);
    const response = await fetch(OPENROUTER_MODELS_URL, { signal });

    if (!response.ok) {
      return {
        ok: false,
        error: `HTTP ${response.status}: ${response.statusText}`,
      };
    }

    let json: unknown;
    try {
      json = await response.json();
    } catch {
      return {
        ok: false,
        error: "Failed to parse JSON response from OpenRouter",
      };
    }

    const body = json as OpenRouterResponse;
    if (!body || !Array.isArray(body.data)) {
      return {
        ok: false,
        error: "Unexpected response shape: missing data array",
      };
    }

    const models: OpenRouterModel[] = body.data.map((item) => ({
      slug: item.id,
      contextLength: item.context_length ?? 0,
      pricingPrompt: item.pricing?.prompt ?? "0",
      pricingCompletion: item.pricing?.completion ?? "0",
    }));

    return { ok: true, models };
  } catch (err) {
    if (err instanceof DOMException && err.name === "TimeoutError") {
      return { ok: false, error: "Request timed out" };
    }
    if (err instanceof Error && err.name === "AbortError") {
      return { ok: false, error: "Request aborted (timeout)" };
    }
    return {
      ok: false,
      error: err instanceof Error ? err.message : String(err),
    };
  }
}
