import { describe, expect, it } from "vitest";
import { WkteamClient } from "../src/sdk/client.js";

describe("WkteamClient concurrency limit", () => {
  it("limits concurrent in-flight transport calls", async () => {
    let active = 0;
    let maxActive = 0;

    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      concurrency: 1,
      retry: { enabled: false, maxAttempts: 1 },
      transport: async () => {
        active += 1;
        maxActive = Math.max(maxActive, active);
        await new Promise((r) => setTimeout(r, 20));
        active -= 1;
        return {
          status: 200,
          headers: { "content-type": "application/json" },
          bodyText: JSON.stringify({ code: 1000, message: "ok", data: null }),
        };
      },
    });

    await Promise.all([
      client.call({
        operationId: "c1",
        method: "POST",
        path: "/x",
        params: {},
        requiresAuth: true,
      }),
      client.call({
        operationId: "c2",
        method: "POST",
        path: "/x",
        params: {},
        requiresAuth: true,
      }),
    ]);

    expect(maxActive).toBe(1);
  });
});
