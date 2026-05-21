import { describe, expect, it } from "vitest";
import { WkteamClient } from "../src/sdk/client.js";
import {
  WkteamApiBusinessError,
  WkteamHttpError,
  WkteamParseError,
  WkteamTimeoutError,
} from "../src/sdk/errors.js";

describe("WkteamClient.call error mapping", () => {
  it("throws WkteamHttpError for non-2xx responses", async () => {
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      transport: async () => ({ status: 500, headers: {}, bodyText: "oops" }),
    });

    await expect(
      client.call({
        operationId: "test_http_error",
        method: "POST",
        path: "/x",
        params: {},
        requiresAuth: true,
      }),
    ).rejects.toBeInstanceOf(WkteamHttpError);
  });

  it("throws WkteamApiBusinessError for code!=1000", async () => {
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      transport: async () => ({
        status: 200,
        headers: { "content-type": "application/json" },
        bodyText: JSON.stringify({ code: 1001, message: "fail", data: { ok: false } }),
      }),
    });

    await expect(
      client.call({
        operationId: "test_business_error",
        method: "POST",
        path: "/x",
        params: {},
        requiresAuth: true,
      }),
    ).rejects.toBeInstanceOf(WkteamApiBusinessError);
  });

  it("throws WkteamParseError for non-json response body", async () => {
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      transport: async () => ({
        status: 200,
        headers: { "content-type": "text/plain" },
        bodyText: "not-json",
      }),
    });

    await expect(
      client.call({
        operationId: "test_parse_error",
        method: "POST",
        path: "/x",
        params: {},
        requiresAuth: true,
      }),
    ).rejects.toBeInstanceOf(WkteamParseError);
  });

  it("throws WkteamTimeoutError when transport aborts", async () => {
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      transport: async () => {
        const e = new Error("aborted");
        (e as any).name = "AbortError";
        throw e;
      },
    });

    await expect(
      client.call({
        operationId: "test_timeout_error",
        method: "POST",
        path: "/x",
        params: {},
        requiresAuth: true,
      }),
    ).rejects.toBeInstanceOf(WkteamTimeoutError);
  });
});
