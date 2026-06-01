/**
 * Unit tests: vault.ts
 *
 * Covers the pure validation + index helpers. Native keyring round-trip
 * is exercised by the end-to-end CLI invocation, not here, because
 * @napi-rs/keyring touches the host OS credential store and must not
 * leave artifacts in CI runs.
 */

import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Force HOME to an isolated temp dir so vault-index.json writes there.
let tmpHome: string;

beforeEach(() => {
  tmpHome = mkdtempSync(path.join(tmpdir(), "oma-vault-test-"));
  vi.stubEnv("HOME", tmpHome);
});

afterEach(() => {
  vi.unstubAllEnvs();
  rmSync(tmpHome, { recursive: true, force: true });
});

describe("isValidKeyName", () => {
  it("accepts plausible API key names", async () => {
    const { isValidKeyName } = await import("./vault.js");
    for (const name of [
      "anthropic",
      "openai-prod",
      "github_pat",
      "sentry.dsn",
      "a",
      "A1.B2-C3_D4",
    ]) {
      expect(isValidKeyName(name)).toBe(true);
    }
  });

  it("rejects unsafe / oversized names", async () => {
    const { isValidKeyName } = await import("./vault.js");
    for (const bad of [
      "",
      "has space",
      "has/slash",
      "has;semi",
      "../escape",
      "x".repeat(65),
    ]) {
      expect(isValidKeyName(bad)).toBe(false);
    }
  });
});

describe("vault index roundtrip (without keyring backend)", () => {
  it("listSecrets returns [] when no index exists", async () => {
    const { listSecrets } = await import("./vault.js");
    expect(listSecrets()).toEqual([]);
  });
});
