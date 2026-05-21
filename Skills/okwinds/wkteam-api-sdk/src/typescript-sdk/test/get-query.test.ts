import { describe, expect, it } from "vitest";
import { WkteamClient } from "../src/sdk/client.js";

describe("WkteamClient GET query encoding", () => {
  it("encodes params into query string for GET", async () => {
    let seenUrl = "";
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      transport: async (req) => {
        seenUrl = req.url;
        return {
          status: 200,
          headers: { "content-type": "application/json" },
          bodyText: JSON.stringify({ code: 1000, message: "ok", data: null }),
        };
      },
    });

    await client.call({
      operationId: "get_query",
      method: "GET",
      path: "/getSomething",
      params: { a: "1", b: "2" },
      requiresAuth: true,
    });

    expect(seenUrl).toContain("/getSomething");
    expect(seenUrl).toContain("a=1");
    expect(seenUrl).toContain("b=2");
  });
});
