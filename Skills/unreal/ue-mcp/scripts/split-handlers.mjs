#!/usr/bin/env node
// Generic god-file splitter: moves a set of FClassName methods from a source
// .cpp into a sibling .cpp, keeping the same class. Can be driven by any of
// the recipes under `scripts/split-recipes/`.
//
// Usage:
//   node scripts/split-handlers.mjs <recipe.json>
//
// Recipe shape:
// {
//   "class": "FAnimationHandlers",
//   "src":   "plugin/.../AnimationHandlers.cpp",
//   "dst":   "plugin/.../AnimationHandlers_StateMachine.cpp",
//   "move":  ["CreateStateMachine", "AddState", ...],
//   "moveStatics": ["LoadAnimBP", "FindGraphByName", ...],   // optional
//   "includes": ["#include \"...h\"", ...]                   // optional extras
// }

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const ROOT = join(here, "..");

const recipePath = process.argv[2];
if (!recipePath) { console.error("usage: split-handlers.mjs <recipe.json>"); process.exit(2); }
const recipe = JSON.parse(readFileSync(resolve(recipePath), "utf8"));

const SRC = resolve(ROOT, recipe.src);
const DST = resolve(ROOT, recipe.dst);
const CLASS = recipe.class;
const TO_MOVE = new Set(recipe.move ?? []);
const STATICS_TO_MOVE = new Set(recipe.moveStatics ?? []);
const EXTRA_INCLUDES = recipe.includes ?? [];

if (existsSync(DST)) {
  console.error(`DST already exists: ${DST}. Delete it first if you really want to re-run.`);
  process.exit(1);
}

const src = readFileSync(SRC, "utf8");
const lines = src.split(/\r?\n/);

// --- find handler method definitions ----------------------------------------
const methodRe = new RegExp(`^TSharedPtr<FJsonValue> ${CLASS}::(\\w+)\\(`);
const handlers = [];
for (let i = 0; i < lines.length; i++) {
  const m = lines[i].match(methodRe);
  if (m) handlers.push({ kind: "method", name: m[1], start: i });
}

// --- find file-local static helper definitions ------------------------------
// Matches a top-level (col-0) definition of a static function. We look for
// the opening brace on the same line OR within the next ~4 lines.
const staticHeadRe = /^static\s+[\w<>,:\*\s&]+\s+(\w+)\s*\(/;
for (let i = 0; i < lines.length; i++) {
  const m = lines[i].match(staticHeadRe);
  if (m) handlers.push({ kind: "static", name: m[1], start: i });
}

handlers.sort((a, b) => a.start - b.start);

// End line: just before the next top-level definition, or EOF.
for (let j = 0; j < handlers.length; j++) {
  const next = handlers[j + 1];
  handlers[j].end = next ? next.start - 1 : lines.length - 1;
}

// Walk preceding comments/blank-lines back so documentation moves with the fn.
for (const h of handlers) {
  let s = h.start - 1;
  while (s > 0) {
    const t = lines[s].trimEnd();
    if (t === "" || t.startsWith("//")) { s--; continue; }
    break;
  }
  h.start = s + 1;
}

const toMove = handlers.filter((h) =>
  (h.kind === "method" && TO_MOVE.has(h.name)) ||
  (h.kind === "static" && STATICS_TO_MOVE.has(h.name)),
);

const foundMethods = new Set(handlers.filter((h) => h.kind === "method").map((h) => h.name));
const foundStatics = new Set(handlers.filter((h) => h.kind === "static").map((h) => h.name));
const missingMethods = [...TO_MOVE].filter((n) => !foundMethods.has(n));
const missingStatics = [...STATICS_TO_MOVE].filter((n) => !foundStatics.has(n));
if (missingMethods.length || missingStatics.length) {
  console.error(`Missing in source: methods=${missingMethods.join(",")} statics=${missingStatics.join(",")}`);
  process.exit(1);
}

// Capture ranges to remove from source.
const drop = new Set();
for (const h of toMove) for (let i = h.start; i <= h.end; i++) drop.add(i);

const kept = lines.filter((_, i) => !drop.has(i));
const moved = toMove
  .map((h) => lines.slice(h.start, h.end + 1).join("\n").replace(/\n+$/, ""))
  .join("\n\n");

// --- emit the new file ------------------------------------------------------
const srcBasename = SRC.split(/[\\/]/).pop();
const header = [
  `// Split from ${srcBasename} to keep that file under 3k lines.`,
  `// All functions below are still members of ${CLASS} - this file is a`,
  `// translation-unit partition, not a new class. Handler registration`,
  `// stays in ${srcBasename}::RegisterHandlers.`,
  ``,
  ...EXTRA_INCLUDES,
  ``,
  ``,
].join("\n");

writeFileSync(DST, header + moved + "\n");

const keptText = kept.join("\n").replace(/\n{4,}/g, "\n\n\n");
writeFileSync(SRC, keptText);

console.log(`Moved ${toMove.length} definitions (${toMove.filter(h => h.kind === "method").length} methods, ${toMove.filter(h => h.kind === "static").length} statics).`);
console.log(`  ${SRC}: ${kept.length} lines (was ${lines.length})`);
console.log(`  ${DST}: ${(header + moved + "\n").split(/\r?\n/).length} lines`);
for (const h of toMove) console.log(`  - ${h.kind}: ${h.name}`);
