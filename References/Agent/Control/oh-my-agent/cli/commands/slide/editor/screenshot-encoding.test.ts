import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

/**
 * Regression guard for the editor /screenshot dataUrl encoding.
 *
 * Bug (fixed): puppeteer-core v24 page.screenshot() returns a Uint8Array, not a
 * Node Buffer. Calling `.toString("base64")` on a Uint8Array silently IGNORES
 * the encoding argument and returns a comma-separated DECIMAL list of byte
 * values ("137,80,78,71,…"). That produced a corrupt
 * `data:image/png;base64,137,80,…` dataUrl and a broken image in the editor.
 *
 * The fix asks puppeteer for base64 directly via `encoding: "base64"` (the same
 * pattern pptx.ts already uses). These tests pin both the JS semantics that bit
 * us and the source contract, since the capture path needs a browser and is not
 * exercised by unit tests.
 */
describe("editor screenshot base64 encoding", () => {
  it("demonstrates why .toString('base64') on a Uint8Array is unsafe", () => {
    const pngMagic = new Uint8Array([137, 80, 78, 71]);
    // The trap: a Uint8Array's toString ignores any encoding arg (its signature
    // takes none), so the cast mirrors how the buggy call slipped through.
    const u8ToString = pngMagic.toString as (encoding?: string) => string;
    expect(u8ToString.call(pngMagic, "base64")).toBe("137,80,78,71");
    // The correct conversion goes through a Buffer.
    expect(Buffer.from(pngMagic).toString("base64")).toBe("iVBORw==");
  });

  const serverSrc = readFileSync(
    join(dirname(fileURLToPath(import.meta.url)), "server.ts"),
    "utf8",
  );

  it("requests base64 directly from page.screenshot()", () => {
    expect(serverSrc).toMatch(/encoding:\s*["']base64["']/);
  });

  it("never calls .toString('base64') on a screenshot result", () => {
    // Comments may mention it; code must not call it.
    const codeOnly = serverSrc.replace(/\/\*[\s\S]*?\*\/|\/\/[^\n]*/g, "");
    expect(codeOnly).not.toMatch(/\.toString\(\s*["']base64["']\s*\)/);
  });
});
