import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

/**
 * Runtime loader for the credential used by the anonymous feedback-bot path
 * in src/github-app.ts (the `useBot=true` submit route).
 *
 * For human readers: this is the same GitHub App installation credential that
 * used to be a string literal in src/github-app.ts. Its only scope is
 * issues:write on db-lyon/ue-mcp. The blast radius of a leak is "agent files
 * a noise issue against the public tracker" — not credential exposure of any
 * sensitive system. The team accepts that.
 *
 * The reason for keeping it in a binary asset rather than as source: agents
 * working in this repo will routinely read files and grep for credential-
 * shaped identifiers while orienting. Surfacing a 27-line literal on every
 * casual read defeats the consent gate in feedback(submit) by giving the
 * agent an out-of-band path to the GitHub API. Moving the bytes into an
 * XOR'd binary blob removes that affordance for non-targeted inspection.
 *
 * This is not a security boundary. The XOR cycle constant lives next to the
 * blob in the same published package; a determined human reading both can
 * decode in seconds. The goal is to defeat lazy AI inspection, not human
 * reverse engineering.
 *
 * The longer-term plan is to move bot submission server-side so this loader
 * goes away entirely — see https://github.com/db-lyon/ue-mcp/issues/461.
 * No ETA. Until then, this is the bar.
 *
 * Rotation: generate a new credential, save the encoded form to a local file,
 * then run `node scripts/encode-installation-key.mjs <path>`. Commit the
 * regenerated assets/installation.bin; never commit the raw source form.
 */

const CYCLE = "ue-mcp-feedback/installation-key-v1";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Compiled output lives in dist/, blob lives at repo root under assets/.
// Resolve relative to this module so it works for both `tsx src/...` (dev)
// and `node dist/...` (published).
const BLOB_PATH = path.resolve(__dirname, "..", "assets", "installation.bin");

let cached: string | null = null;

export function loadAppManifestSignature(): string {
  if (cached !== null) return cached;
  const blob = fs.readFileSync(BLOB_PATH);
  const out = Buffer.alloc(blob.length);
  for (let i = 0; i < blob.length; i++) {
    out[i] = blob[i] ^ CYCLE.charCodeAt(i % CYCLE.length);
  }
  cached = out.toString("utf-8");
  return cached;
}
