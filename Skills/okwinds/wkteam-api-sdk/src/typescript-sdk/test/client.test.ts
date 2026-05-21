import { describe, expect, it } from "vitest";
import { WkteamClient } from "../src/sdk/client.js";

describe("WkteamClient", () => {
  it("throws when baseUrl is missing", () => {
    expect(
      () =>
        new WkteamClient({
          // @ts-expect-error test invalid
          baseUrl: "",
          authorization: "x",
        }),
    ).toThrow();
  });

  it("throws when authorization is missing", () => {
    expect(
      () =>
        new WkteamClient({
          baseUrl: "https://example.invalid",
          // @ts-expect-error test invalid
          authorization: "",
        }),
    ).toThrow();
  });
});
