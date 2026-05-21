import { describe, expect, it } from "vitest";
import { WkteamClient } from "../src/sdk/client.js";

describe("WkteamClient authorization header", () => {
  it("injects Authorization header with optional prefix", async () => {
    let seen: { headers: Record<string, string> } | undefined;
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token_raw",
      logLevel: "silent",
      authorizationPrefix: "Bearer ",
      transport: async (req) => {
        seen = { headers: req.headers };
        return {
          status: 200,
          headers: { "content-type": "application/json" },
          bodyText: JSON.stringify({ code: 1000, message: "ok", data: null }),
        };
      },
    });

    await client.call({
      operationId: "test_auth",
      method: "POST",
      path: "/x",
      params: { a: 1 },
      requiresAuth: true,
    });

    expect(seen).toBeDefined();
    expect(seen?.headers.Authorization).toBe("Bearer token_raw");
  });
});
