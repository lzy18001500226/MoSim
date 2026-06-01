import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

/**
 * Regression contract for the shipped deck-stage.js asset.
 *
 * Bug (fixed): when a slide author loads `deck-stage.js` in <head> (no defer),
 * customElements.define() runs during parsing and connectedCallback fires at
 * the <deck-stage> start tag — BEFORE .deck-stage / .slide children are parsed.
 * querySelector(".deck-stage") returns null, init bails, slide 0 never gets
 * .active, and the deck renders BLANK (export PNG and editor screenshots blank).
 *
 * The fix defers init to DOMContentLoaded when the subtree is not yet parsed.
 * These assertions lock that guard in so it cannot be silently reverted. They
 * run as a source-contract check because the asset is plain copied-verbatim JS
 * (not importable TS) and CI has no browser to exercise custom-element upgrade.
 */
describe("deck-stage.js asset — early-upgrade guard", () => {
  const assetPath = join(
    dirname(fileURLToPath(import.meta.url)),
    "..",
    "..",
    "..",
    ".agents",
    "skills",
    "oma-slide",
    "resources",
    "assets",
    "deck-stage.js",
  );
  const source = readFileSync(assetPath, "utf8");

  it("guards connectedCallback against being upgraded before children parse", () => {
    // Must detect the not-yet-parsed case via readyState and defer init.
    expect(source).toMatch(/document\.readyState\s*===\s*["']loading["']/);
    expect(source).toMatch(
      /addEventListener\(\s*["']DOMContentLoaded["']\s*,\s*this\.#init/,
    );
  });

  it("routes initialization through a reusable #init handler", () => {
    // Init logic must live in #init (callable both directly and as a
    // DOMContentLoaded listener), not inline in connectedCallback.
    expect(source).toMatch(/#init\s*=\s*\(\)\s*=>/);
    expect(source).toMatch(/this\.#goTo\(0/);
  });

  it("removes the deferred DOMContentLoaded listener on disconnect", () => {
    expect(source).toMatch(
      /removeEventListener\(\s*["']DOMContentLoaded["']\s*,\s*this\.#init/,
    );
  });
});
