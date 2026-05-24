import fs from "node:fs/promises";
import path from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { endpointDefs } from "../src/generated/endpoints.js";
import { operationIds } from "../src/generated/manifest.js";
import { operationIndex } from "../src/generated/operation-index.js";
import { WkteamClient } from "../src/sdk/client.js";

function findRepoRootFrom(startDir: string): string {
  const anchor = path.join(
    "docs",
    "specs",
    "engineering-spec",
    "02_Technical_Design",
    "schemas",
    "api_catalog.json",
  );
  let cur = startDir;
  // eslint-disable-next-line no-constant-condition
  while (true) {
    if (existsSync(path.join(cur, anchor))) return cur;
    const parent = path.dirname(cur);
    if (parent === cur) throw new Error(`无法定位 repo root：未找到 ${anchor}`);
    cur = parent;
  }
}

function buildMinimalParams(def: (typeof endpointDefs)[number]): Record<string, unknown> {
  const obj: Record<string, unknown> = {};
  for (const p of def.params) {
    if (!p.required) continue;
    const type = String(p.type ?? "").toLowerCase();
    if (type.includes("string")) obj[p.name] = "x";
    else if (type.includes("bool")) obj[p.name] = true;
    else if (
      type.includes("int") ||
      type.includes("long") ||
      type.includes("double") ||
      type.includes("float")
    )
      obj[p.name] = 1;
    else if (type.includes("array") || type.includes("list")) obj[p.name] = [];
    else if (type.includes("object") || type.includes("map")) obj[p.name] = {};
    else obj[p.name] = "x";
  }
  return obj;
}

describe("API coverage (offline docs -> generated SDK)", () => {
  it("operationIds matches api_catalog endpoint entries", async () => {
    const packageRoot = path.dirname(fileURLToPath(import.meta.url));
    const repoRoot = findRepoRootFrom(packageRoot);
    const catalogPath = path.join(
      repoRoot,
      "docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json",
    );
    const raw = JSON.parse(await fs.readFile(catalogPath, "utf8"));
    const endpoints = (raw.catalog as Array<any>).filter((e) => e.kind === "endpoint");
    const idsFromCatalog = endpoints.map((e) => String(e.operationId)).sort();
    const idsFromSdk = [...operationIds].map(String).sort();
    expect(idsFromSdk).toEqual(idsFromCatalog);
  });

  it("every operationId has a callable wrapper under client.api", async () => {
    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      transport: async () => ({
        status: 200,
        headers: { "content-type": "application/json" },
        bodyText: JSON.stringify({ code: 1000, message: "ok", data: null }),
      }),
    });

    for (const opId of operationIds) {
      const idx = (operationIndex as any)[opId];
      expect(idx).toBeDefined();
      const fn = (client.api as any)[idx.moduleKey]?.[idx.methodName];
      expect(typeof fn).toBe("function");
    }
  });

  it("all wrappers issue requests with correct method/path (contract smoke)", async () => {
    const defsByOp = new Map(endpointDefs.map((d) => [d.operationId, d]));
    let expected: null | { method: string; path: string } = null;

    const client = new WkteamClient({
      baseUrl: "https://example.invalid",
      authorization: "token",
      logLevel: "silent",
      retry: { enabled: false, maxAttempts: 1 },
      transport: async (req) => {
        expect(expected).not.toBeNull();
        expect(req.method.toUpperCase()).toBe(expected!.method.toUpperCase());
        expect(req.url).toContain(expected!.path);
        return {
          status: 200,
          headers: { "content-type": "application/json" },
          bodyText: JSON.stringify({ code: 1000, message: "ok", data: null }),
        };
      },
    });

    for (const opId of operationIds) {
      const def = defsByOp.get(String(opId));
      expect(def).toBeDefined();
      expected = { method: def!.method, path: def!.path };

      const idx = (operationIndex as any)[opId];
      const fn = (client.api as any)[idx.moduleKey][idx.methodName] as (
        params: any,
      ) => Promise<unknown>;
      await fn(buildMinimalParams(def!));
    }
  }, 30_000);
});
