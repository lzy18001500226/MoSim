import { describe, expect, it } from "vitest";
import { WkteamClient } from "../src/sdk/client.js";
import { WkteamNetworkError } from "../src/sdk/errors.js";

describe("WkteamClient retry behavior", () => {
  it("retries network error for safe endpoints", async () => {
    let calls = 0;
    const retryEvents: Array<{ attempt: number; reason: string }> = [];
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      retry: { enabled: true, maxAttempts: 2, backoffMs: 0, retryOn: ["network"] },
      hooks: {
        onRetry: (e) => retryEvents.push({ attempt: e.attempt, reason: e.reason }),
      },
      transport: async () => {
        calls += 1;
        if (calls === 1) throw new Error("net down");
        return {
          status: 200,
          headers: { "content-type": "application/json" },
          bodyText: JSON.stringify({ code: 1000, message: "ok", data: { ok: true } }),
        };
      },
    });

    const data = await client.call({
      operationId: "retry_safe",
      method: "GET",
      path: "/getSomething",
      params: {},
      requiresAuth: true,
    });

    expect(data).toEqual({ ok: true });
    expect(calls).toBe(2);
    expect(retryEvents.length).toBe(1);
    expect(retryEvents[0]).toEqual({ attempt: 2, reason: "network" });
  });

  it("does not retry by default for side-effect endpoints", async () => {
    let calls = 0;
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      retry: { enabled: true, maxAttempts: 2, backoffMs: 0, retryOn: ["network"] },
      transport: async () => {
        calls += 1;
        throw new Error("net down");
      },
    });

    await expect(
      client.call({
        operationId: "retry_side_effect",
        method: "POST",
        path: "/sendText",
        params: { wId: "x" },
        requiresAuth: true,
      }),
    ).rejects.toBeInstanceOf(WkteamNetworkError);

    expect(calls).toBe(1);
  });
});
