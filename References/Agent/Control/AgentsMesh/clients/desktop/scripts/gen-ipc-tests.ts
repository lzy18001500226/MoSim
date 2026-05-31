#!/usr/bin/env tsx
/**
 * IPC contract test generator.
 *
 * Source of truth: the compiled napi-rs `.node` binary at
 *   bazel-bin/clients/core/crates/node-bridge/agentsmesh-node-bridge.darwin-arm64.node
 * The binary embeds method names as null-terminated strings clustered after
 * each `clients/core/crates/node-bridge/src/commands/<group>.rs` marker,
 * so we can extract the exact set of handlers napi exposed in the latest
 * build (which is what Desktop's reflective IPC binding then registers).
 *
 * Using the binary as SSOT avoids drift between:
 *   - the .rs sources (intent)
 *   - index.d.ts (sometimes stale, hand-maintained)
 *   - what napi actually emits (truth)
 *
 * Each emitted spec validates a handler via `invokeIpcContract`, which goes
 * beyond a smoke `toBeDefined` check:
 *   - the bridge must reply (no silent undefined)
 *   - on error, the message must NOT be a JS runtime/wire fault
 *     ("is not a function" / "TypeError" / "No such IPC handler" / …) —
 *     typed service errors pass, wire faults fail
 *   - on success, the return value must match the declared TypeScript
 *     return shape (string → string, void → null, boolean → boolean,
 *     Array<number> → Array/Uint8Array, number → number|string|bigint)
 *
 * Regenerate:
 *   bazel build //clients/core/crates/node-bridge:node_bridge
 *   pnpm --filter desktop e2e:gen
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync, readdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const REPO_ROOT = resolve(__dirname, "..", "..", "..");
const NAPI_BINARY = resolve(
  REPO_ROOT,
  "bazel-bin/clients/core/crates/node-bridge/agentsmesh-node-bridge.darwin-arm64.node",
);
const INDEX_DTS = resolve(REPO_ROOT, "clients/core/crates/node-bridge/index.d.ts");
const OUT_DIR = resolve(REPO_ROOT, "clients/desktop/e2e/tests/ipc/_generated");
const SCHEMA_FILE = resolve(REPO_ROOT, "clients/desktop/e2e/tests/ipc/schema.ts");

interface IpcMethod {
  name: string;
  group: string;
  params: Array<{ name: string; type: string }>;
  returnType: string;
}

// Returns a Map from method name → its declared TS signature from index.d.ts.
// We use index.d.ts only for return-type / param annotation; the binary
// dictates which methods ACTUALLY exist.
function loadIndexDtsSignatures(): Map<string, { params: IpcMethod["params"]; returnType: string }> {
  const out = new Map<string, { params: IpcMethod["params"]; returnType: string }>();
  if (!existsSync(INDEX_DTS)) return out;
  const src = readFileSync(INDEX_DTS, "utf-8");
  const lineRe = /^\s{2}(\w+)\(([\s\S]*?)\):\s*(.+?)$/gm;
  let m: RegExpExecArray | null;
  while ((m = lineRe.exec(src)) !== null) {
    const name = m[1];
    if (name === "constructor") continue;
    let returnType = m[3].trim();
    const promiseMatch = returnType.match(/^Promise<([\s\S]+)>$/);
    if (promiseMatch) returnType = promiseMatch[1].trim();
    returnType = returnType.replace(/[,;]$/, "");
    const params = parseParams(m[2].trim());
    out.set(name, { params, returnType });
  }
  return out;
}

function parseParams(raw: string): IpcMethod["params"] {
  if (!raw) return [];
  const parts: string[] = [];
  let depth = 0;
  let start = 0;
  for (let i = 0; i < raw.length; i++) {
    const c = raw[i];
    if (c === "<" || c === "(" || c === "{" || c === "[") depth++;
    else if (c === ">" || c === ")" || c === "}" || c === "]") depth--;
    else if (c === "," && depth === 0) {
      parts.push(raw.slice(start, i).trim());
      start = i + 1;
    }
  }
  parts.push(raw.slice(start).trim());
  const out: IpcMethod["params"] = [];
  for (const p of parts) {
    if (!p) continue;
    const colon = p.indexOf(":");
    if (colon < 0) continue;
    const pname = p.slice(0, colon).replace(/\?$/, "").trim();
    const ptype = p.slice(colon + 1).trim();
    if (pname && ptype) out.push({ name: pname, type: ptype });
  }
  return out;
}

// Parse the `strings(1)` output of the napi binary. Every `#[napi]` async
// fn emits its name into the binary's literal pool as a null-terminated
// camelCase identifier. We keep tokens whose prefix matches a known service
// group (so we don't pick up arbitrary Rust strings like field names).
// index.d.ts may declare methods that don't exist in the binary
// (stale) or omit methods that the binary actually exports, so the binary
// alone is the source of truth.
function extractMethodsFromBinary(): IpcMethod[] {
  if (!existsSync(NAPI_BINARY)) {
    throw new Error(
      `[gen-ipc-tests] napi binary not found at ${NAPI_BINARY}. Run: bazel build //clients/core/crates/node-bridge:node_bridge`,
    );
  }
  const signatures = loadIndexDtsSignatures();

  // Dynamic introspection: load the napi addon, instantiate AppState, and
  // enumerate `Object.getOwnPropertyNames(Object.getPrototypeOf(...))`. This
  // is exactly what `desktop/src/main/index.ts` does at boot to register
  // IPC handlers, so the resulting list is authoritative and cannot drift.
  // Static analysis of `strings(1)` output was tried first; the binary's
  // const pool concatenates method names without separators so naive scans
  // produce spurious tokens (`apikeyUpdateConnectclients/core/...`).
  const helper = `
    const { AppState } = require(${JSON.stringify(NAPI_BINARY)});
    let proto;
    try {
      // Construct with placeholder baseUrl + storageDir; we don't make any
      // calls, just enumerate the prototype.
      const inst = new AppState("http://introspection.local", "/tmp");
      proto = Object.getPrototypeOf(inst);
    } catch (e) {
      // If construction fails (e.g. validates env), fall back to the class
      // prototype directly — napi-rs attaches methods there.
      proto = AppState.prototype;
    }
    const names = Object.getOwnPropertyNames(proto).filter((k) => {
      if (k === "constructor") return false;
      return typeof proto[k] === "function";
    });
    process.stdout.write(JSON.stringify(names));
  `;
  const raw = execFileSync(process.execPath, ["-e", helper], { encoding: "utf-8" });
  const names = JSON.parse(raw) as string[];

  const methods: IpcMethod[] = [];
  for (const name of names) {
    const group = groupOf(name);
    const sig = signatures.get(name) ?? { params: [], returnType: "any" };
    methods.push({ name, group, params: sig.params, returnType: sig.returnType });
  }
  methods.sort((a, b) => a.group.localeCompare(b.group) || a.name.localeCompare(b.name));
  return methods;
}

function buildGroupAnchorRegex(): RegExp {
  const sorted = [...SERVICE_GROUPS].sort((a, b) => b.length - a.length);
  return new RegExp(`(${sorted.join("|")})`, "g");
}

function isLowerStart(ch: string): boolean {
  return ch >= "a" && ch <= "z";
}

function startsWithKnownPrefix(src: string, idx: number): boolean {
  for (const g of SERVICE_GROUPS) {
    if (src.startsWith(g, idx)) {
      const after = src[idx + g.length];
      if (after && /[A-Z]/.test(after)) return true;
    }
  }
  return false;
}

function hasCamelSuffix(name: string, group: string): boolean {
  for (const g of SERVICE_GROUPS) {
    if (
      name.startsWith(g) &&
      (name.length === g.length || /[A-Z]/.test(name[g.length])) &&
      camelToSnake(g) === group
    ) {
      const rest = name.slice(g.length);
      if (rest.length > 0 && /[A-Z]/.test(rest)) return true;
    }
  }
  return false;
}

// Splits camelCase / PascalCase method names into the group prefix and the
// remaining verb. `apikeyListConnect` → group "apikey", verb "ListConnect".
// We group by the longest known prefix from a fixed allowlist of service
// groups — picking the first lowercase-run as the group works for the
// codebase's `<group><Verb…>` naming convention.
const SERVICE_GROUPS = [
  "agent",
  "apikey",
  "authConnect",
  "auth",
  "autopilot",
  "billing",
  "binding",
  "blockstore",
  "channelApi",
  "channelState",
  "channel",
  "envBundle",
  "extension",
  "file",
  "grant",
  "invitation",
  "localRunner",
  "loopService",
  "loopSvc",
  "mesh",
  "message",
  "notification",
  "org",
  "pod",
  "promocode",
  "repository",
  "runnerApi",
  "runner",
  "sso",
  "supportTicket",
  "ticketApi",
  "ticketRelations",
  "ticket",
  "token",
  "userEnvBundle",
  "userCredential",
  "user",
  "api",
] as const;

function groupOf(name: string): string {
  for (const g of SERVICE_GROUPS) {
    if (name.startsWith(g) && (name.length === g.length || /[A-Z]/.test(name[g.length]))) {
      return camelToSnake(g);
    }
  }
  return "uncategorized";
}

function camelToSnake(s: string): string {
  return s.replace(/[A-Z]/g, (c, i) => (i === 0 ? c.toLowerCase() : `_${c.toLowerCase()}`));
}

function defaultValue(type: string): string {
  // Strip `| undefined | null` etc.
  const t = type.replace(/\s*\|\s*(undefined|null)/g, "").trim();
  if (/^string$/i.test(t)) return '""';
  if (/^number$/i.test(t)) return "0";
  if (/^boolean$/i.test(t)) return "false";
  if (/^Array</.test(t) || /^Uint8Array$/.test(t) || /^Buffer$/.test(t)) return "[]";
  if (/^Record<|^\{/.test(t)) return "{}";
  return "null";
}

function sanitizeTestName(n: string): string {
  return n.replace(/[^a-zA-Z0-9_·\s]/g, "_");
}

function emitSchemaFile(methods: IpcMethod[]): string {
  const header = `// AUTO-GENERATED — regenerate: pnpm --filter desktop e2e:gen
//
// Source of truth: clients/core/crates/node-bridge/index.d.ts (the
// napi-rs-emitted TypeScript declaration of AppState). Desktop main
// reflects over the prototype to register one ipcMain handler per method,
// so this mirror is what the renderer can actually invoke at runtime.
export interface IpcMethodSchema {
  name: string;
  group: string;
  params: Array<{ name: string; type: string }>;
  returnType: string;
}

export const ipcSchema: IpcMethodSchema[] = `;
  return header + JSON.stringify(methods, null, 2) + ";\n";
}

function emitGroupSpec(group: string, methods: IpcMethod[]): string {
  // IPC contract specs share a worker-scoped Electron app (see
  // fixtures/electron-shared.fixture.ts). Launching Electron once per IPC
  // method saturated fd/memory after ~250 tests and produced flaky
  // worker-teardown timeouts. The shared fixture keeps per-test reporting,
  // retries, and timeouts intact — only the Electron process is reused.
  //
  // Each test calls `invokeIpcContract` which goes beyond a smoke
  // `toBeDefined()` check: it asserts (a) the bridge replied (not undefined),
  // (b) any error message is a *typed service error*, not a JS wire fault
  // ("is not a function" / "TypeError" / "No such IPC handler" / …), and
  // (c) on success the return value matches the Rust handler's declared
  // type (String → string, () → null, bool → boolean, Buffer/Vec<u8> →
  // Uint8Array, numerics → number|string|bigint). Wire faults turn the
  // bridge silently green under the old smoke test — this layer catches them.
  const header = `// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · ${group}", () => {
`;

  const body = methods
    .map((m) => {
      const args = m.params.map((p) => defaultValue(p.type)).join(", ");
      const argsTrailing = args ? ", " + args : "";
      return `  test("${sanitizeTestName(m.name)}", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "${m.name}", returnType: ${JSON.stringify(m.returnType)} }${argsTrailing});
  });
`;
    })
    .join("\n");

  return header + body + "});\n";
}

function main(): void {
  const methods = extractMethodsFromBinary();
  console.log(`[gen-ipc-tests] Extracted ${methods.length} handlers from ${NAPI_BINARY}`);

  const byGroup: Record<string, IpcMethod[]> = {};
  for (const m of methods) {
    if (!byGroup[m.group]) byGroup[m.group] = [];
    byGroup[m.group].push(m);
  }

  // Wipe old generated dir (preserve only dotfiles if any)
  if (existsSync(OUT_DIR)) {
    for (const f of readdirSync(OUT_DIR)) {
      if (f.endsWith(".spec.ts")) rmSync(resolve(OUT_DIR, f), { force: true });
    }
  } else {
    mkdirSync(OUT_DIR, { recursive: true });
  }

  for (const [group, items] of Object.entries(byGroup)) {
    const file = resolve(OUT_DIR, `${group}.api.spec.ts`);
    writeFileSync(file, emitGroupSpec(group, items), "utf-8");
    console.log(`[gen-ipc-tests] ${group}: ${items.length} handlers → ${file}`);
  }

  mkdirSync(dirname(SCHEMA_FILE), { recursive: true });
  writeFileSync(SCHEMA_FILE, emitSchemaFile(methods), "utf-8");
  console.log(`[gen-ipc-tests] schema → ${SCHEMA_FILE}`);
}

main();
