import { describe, it, expect } from "vitest";
import {
  parseServiceError,
  isResourceNotFound,
  isAuthExpired,
  getErrorStatus,
  getErrorCode,
  getErrorMessage,
} from "../serviceError";

describe("parseServiceError", () => {
  it("parses JSON wire format from Rust", () => {
    const wire = '{"kind":"resource_not_found","resource":"Pod","id":"pk_1"}';
    const err = new Error(wire);
    const svc = parseServiceError(err);
    expect(svc).toEqual({
      kind: "resource_not_found",
      resource: "Pod",
      id: "pk_1",
    });
  });

  it("parses auth_expired", () => {
    const err = new Error('{"kind":"auth_expired"}');
    expect(parseServiceError(err)).toEqual({ kind: "auth_expired" });
  });

  it("parses http with code and status", () => {
    const err = new Error(
      '{"kind":"http","status":500,"code":"DB_DOWN","message":"db unreachable"}',
    );
    const svc = parseServiceError(err);
    expect(svc).toEqual({
      kind: "http",
      status: 500,
      code: "DB_DOWN",
      message: "db unreachable",
    });
  });

  it("falls back to resource_not_found for legacy HTTP 404 strings", () => {
    const svc = parseServiceError(new Error("HTTP 404: Pod not found"));
    expect(svc.kind).toBe("resource_not_found");
  });

  it("falls back to http variant for other legacy HTTP strings", () => {
    const svc = parseServiceError(new Error("HTTP 500: internal"));
    expect(svc).toEqual({ kind: "http", status: 500, message: "internal" });
  });

  it("returns unknown for free-form messages", () => {
    const svc = parseServiceError(new Error("boom"));
    expect(svc).toEqual({ kind: "unknown", message: "boom" });
  });

  it("handles string errors", () => {
    const svc = parseServiceError("raw string error");
    expect(svc.kind).toBe("unknown");
  });

  it("handles null/undefined", () => {
    expect(parseServiceError(null).kind).toBe("unknown");
    expect(parseServiceError(undefined).kind).toBe("unknown");
  });

  it("rejects malformed JSON with unknown kind", () => {
    const svc = parseServiceError(new Error('{"kind":"made_up","x":1}'));
    expect(svc.kind).toBe("unknown");
  });
});

describe("typed helpers", () => {
  it("isResourceNotFound matches without resource filter", () => {
    const err = new Error(
      '{"kind":"resource_not_found","resource":"Pod"}',
    );
    expect(isResourceNotFound(err)).toBe(true);
  });

  it("isResourceNotFound filters by resource name (case-insensitive)", () => {
    const err = new Error(
      '{"kind":"resource_not_found","resource":"Pod"}',
    );
    expect(isResourceNotFound(err, "pod")).toBe(true);
    expect(isResourceNotFound(err, "Runner")).toBe(false);
  });

  it("isAuthExpired", () => {
    expect(isAuthExpired(new Error('{"kind":"auth_expired"}'))).toBe(true);
    expect(isAuthExpired(new Error("boom"))).toBe(false);
  });

  it("getErrorStatus extracts from http and resource_not_found", () => {
    expect(
      getErrorStatus(new Error('{"kind":"http","status":418,"message":"tea"}')),
    ).toBe(418);
    expect(
      getErrorStatus(new Error('{"kind":"resource_not_found","resource":"x"}')),
    ).toBe(404);
    expect(getErrorStatus(new Error('{"kind":"auth_expired"}'))).toBe(401);
  });

  it("getErrorCode extracts http code", () => {
    expect(
      getErrorCode(
        new Error('{"kind":"http","status":500,"code":"DB","message":"x"}'),
      ),
    ).toBe("DB");
    expect(getErrorCode(new Error("plain"))).toBeUndefined();
  });

  it("getErrorMessage returns human text per variant", () => {
    expect(
      getErrorMessage(
        new Error('{"kind":"resource_not_found","resource":"Pod"}'),
      ),
    ).toBe("Pod not found");
    expect(getErrorMessage(new Error('{"kind":"auth_expired"}'))).toBe(
      "auth expired",
    );
    expect(getErrorMessage(new Error("random"))).toBe("random");
  });
});
