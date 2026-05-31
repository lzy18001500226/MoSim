#!/usr/bin/env node
// Vitest entry shim. Resolves vitest from CWD (= js_test chdir = caller
// package dir) by locating its package.json, then spawning the bin file.
// We can't `require.resolve('vitest/vitest.mjs')` because that subpath
// isn't in the package's `exports` map.
//
// `--experimental-require-module` is set via NODE_OPTIONS so vitest's
// forked test workers inherit it. vite@7+ is ESM-only and vitest's CJS
// shim (+ transitively jsdom → html-encoding-sniffer → @exodus/bytes)
// each need CJS-to-ESM require interop at startup. Without the flag
// Node throws ERR_REQUIRE_ESM before any test runs.
const { createRequire } = require("node:module");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const req = createRequire(path.join(process.cwd(), "noop.cjs"));
const pkgJsonPath = req.resolve("vitest/package.json");
const binPath = path.join(path.dirname(pkgJsonPath), "vitest.mjs");

const nodeOptions = [
  process.env.NODE_OPTIONS || "",
  "--experimental-require-module",
].filter(Boolean).join(" ");

const result = spawnSync(process.execPath, [binPath, ...process.argv.slice(2)], {
  stdio: "inherit",
  cwd: process.cwd(),
  env: { ...process.env, NODE_OPTIONS: nodeOptions },
});
process.exit(result.status ?? 1);
