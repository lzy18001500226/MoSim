import { describe, it, expect } from "vitest";
import { ApiError } from "../api-types";
import {
  getApiErrorCode,
  getErrorSuggestion,
  isApiErrorCode,
  isApiStatus,
  getLocalizedErrorMessage,
} from "../errors";

const apiErr = (data: unknown, status = 400) =>
  new ApiError(status, "Bad Request", data);

describe("getApiErrorCode", () => {
  it("returns code from ApiError", () => {
    expect(getApiErrorCode(apiErr({ code: "VALIDATION_FAILED" }))).toBe(
      "VALIDATION_FAILED",
    );
  });
  it("returns undefined for non-ApiError", () => {
    expect(getApiErrorCode(new Error("plain"))).toBeUndefined();
    expect(getApiErrorCode("string error")).toBeUndefined();
    expect(getApiErrorCode(undefined)).toBeUndefined();
  });
  it("returns undefined when ApiError data has no code", () => {
    expect(getApiErrorCode(apiErr({}))).toBeUndefined();
  });
});

describe("getErrorSuggestion", () => {
  it("extracts suggestion from ApiError data", () => {
    expect(
      getErrorSuggestion(apiErr({ code: "VALIDATION_FAILED", suggestion: "john-doe" })),
    ).toBe("john-doe");
  });
  it("returns undefined when suggestion missing", () => {
    expect(getErrorSuggestion(apiErr({ code: "VALIDATION_FAILED" }))).toBeUndefined();
  });
  it("returns undefined when suggestion is empty string", () => {
    expect(getErrorSuggestion(apiErr({ suggestion: "" }))).toBeUndefined();
  });
  it("returns undefined when suggestion is non-string", () => {
    expect(getErrorSuggestion(apiErr({ suggestion: 42 }))).toBeUndefined();
    expect(getErrorSuggestion(apiErr({ suggestion: null }))).toBeUndefined();
  });
  it("returns undefined for non-ApiError", () => {
    expect(getErrorSuggestion(new Error("plain"))).toBeUndefined();
  });
});

describe("isApiErrorCode", () => {
  it("matches exact code", () => {
    expect(isApiErrorCode(apiErr({ code: "ALREADY_EXISTS" }), "ALREADY_EXISTS")).toBe(true);
  });
  it("returns false for different code", () => {
    expect(isApiErrorCode(apiErr({ code: "ALREADY_EXISTS" }), "VALIDATION_FAILED")).toBe(false);
  });
  it("returns false for non-ApiError", () => {
    expect(isApiErrorCode(new Error("plain"), "ANY")).toBe(false);
  });
});

describe("isApiStatus", () => {
  it("matches status code", () => {
    expect(isApiStatus(apiErr({}, 409), 409)).toBe(true);
  });
  it("returns false for different status", () => {
    expect(isApiStatus(apiErr({}, 400), 409)).toBe(false);
  });
  it("returns false for non-ApiError", () => {
    expect(isApiStatus(new Error("plain"), 500)).toBe(false);
  });
});

describe("getLocalizedErrorMessage", () => {
  const fallback = "default-fallback";
  const tIdentity = (k: string) => k; // simulate next-intl missing-key behaviour
  const tWithTranslation = (k: string) =>
    k === "apiErrors.VALIDATION_FAILED" ? "翻译后的错误" : k;

  it("returns translated message when i18n key resolves", () => {
    const err = apiErr({ code: "VALIDATION_FAILED", error: "server msg" });
    expect(getLocalizedErrorMessage(err, tWithTranslation, fallback)).toBe("翻译后的错误");
  });

  it("falls back to server message when i18n key missing", () => {
    const err = apiErr({ code: "UNKNOWN_CODE", error: "server msg" });
    expect(getLocalizedErrorMessage(err, tIdentity, fallback)).toBe("server msg");
  });

  it("falls back to ApiError default message when no code, no server message", () => {
    // ApiError extends Error with `super(\`API Error: ${status} ${statusText}\`)`,
    // so `error instanceof Error` always wins before the explicit `fallback`.
    // Caller-supplied fallback only kicks in for non-Error values (next case).
    const err = apiErr({});
    expect(getLocalizedErrorMessage(err, tIdentity, fallback)).toBe(
      "API Error: 400 Bad Request",
    );
  });

  it("returns Error.message for plain Error instances", () => {
    expect(getLocalizedErrorMessage(new Error("plain"), tIdentity, fallback)).toBe("plain");
  });

  it("returns fallback for non-Error values", () => {
    expect(getLocalizedErrorMessage("a string", tIdentity, fallback)).toBe(fallback);
    expect(getLocalizedErrorMessage(undefined, tIdentity, fallback)).toBe(fallback);
  });

  it("handles t() throwing — should still fall through to server message", () => {
    const tThrows = () => {
      throw new Error("missing translation");
    };
    const err = apiErr({ code: "ANY", error: "server msg" });
    expect(getLocalizedErrorMessage(err, tThrows, fallback)).toBe("server msg");
  });
});
