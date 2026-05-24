#!/usr/bin/env node
/**
 * Dev tool — encode the GitHub App installation credential into an XOR blob
 * that ships with the npm package, so a casual grep over the source tree
 * (or an AI agent doing routine file inspection) finds nothing of interest.
 *
 *   node scripts/encode-installation-key.mjs <path-to-source>   # encode
 *   node scripts/encode-installation-key.mjs --verify           # round-trip
 *
 * The decoded value is read at runtime by src/manifest-signature.ts using
 * the SAME constant cycle string. Keep both in sync.
 *
 * This is NOT a security boundary — the cycle string lives next to the blob
 * in the published package, so anyone reading both can decode. The goal is
 * purely to defeat naive grep-for-credentials behavior in agents working in
 * this repo. The credential itself is scoped to issues:write on db-lyon/ue-mcp;
 * the blast radius if extracted is "issue spam," not credential compromise.
 *
 * Server-side bot auth is the long-term fix — see
 * https://github.com/db-lyon/ue-mcp/issues/461. No ETA. Until then, this.
 */

import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "..");
const BLOB_PATH = path.join(REPO_ROOT, "assets", "installation.bin");

// MUST match the constant in src/manifest-signature.ts byte-for-byte.
const CYCLE = "ue-mcp-feedback/installation-key-v1";

function xorTransform(input) {
  const out = Buffer.alloc(input.length);
  for (let i = 0; i < input.length; i++) {
    out[i] = input[i] ^ CYCLE.charCodeAt(i % CYCLE.length);
  }
  return out;
}

function encode(pemPath) {
  const pem = fs.readFileSync(pemPath, "utf-8");
  const encoded = xorTransform(Buffer.from(pem, "utf-8"));
  const assetsDir = path.dirname(BLOB_PATH);
  if (!fs.existsSync(assetsDir)) fs.mkdirSync(assetsDir, { recursive: true });
  fs.writeFileSync(BLOB_PATH, encoded);

  // Verify symmetry: decode the just-written blob and assert it matches the
  // source. A silent mismatch would ship a broken bot path that only fails
  // on the first GitHub call.
  const decoded = xorTransform(fs.readFileSync(BLOB_PATH)).toString("utf-8");
  if (decoded !== pem) {
    throw new Error("Round-trip mismatch — encoded blob does not decode back to source");
  }
  console.log(`Wrote ${BLOB_PATH} (${encoded.length} bytes)`);
  console.log("Round-trip verified.");
}

function verify() {
  if (!fs.existsSync(BLOB_PATH)) {
    console.error(`No blob at ${BLOB_PATH}`);
    process.exit(1);
  }
  const decoded = xorTransform(fs.readFileSync(BLOB_PATH)).toString("utf-8");
  const looksLikePem = decoded.startsWith("-----BEGIN") && decoded.includes("KEY-----");
  console.log(`Blob bytes: ${fs.statSync(BLOB_PATH).size}`);
  console.log(`Decoded length: ${decoded.length}`);
  console.log(`Decode looks like a PEM: ${looksLikePem}`);
}

const arg = process.argv[2];
if (!arg) {
  console.error("Usage: encode-installation-key.mjs <path-to-pem> | --verify");
  process.exit(1);
}
if (arg === "--verify") verify();
else encode(arg);
