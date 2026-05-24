#!/usr/bin/env node
/**
 * Minimal local CLI wrapper for html2pptx.js.
 *
 * Usage:
 *   node agent/skills/pptx-offline/scripts/html2pptx-local.cjs slide.html output.pptx
 *
 * Notes:
 * - This expects Node deps installed under agent/skills/pptx-offline/ (see SKILL.md).
 * - If you need multiple slides, invoke this script repeatedly or write a tiny driver
 *   that calls html2pptx() multiple times on the same pptx instance.
 */

const path = require("path");

const PptxGenJS = require("pptxgenjs");
const html2pptx = require("./html2pptx");

async function main() {
  const [htmlFile, outputFile] = process.argv.slice(2);
  if (!htmlFile || !outputFile) {
    process.stderr.write(
      "Usage: html2pptx-local.cjs <slide.html> <output.pptx>\n"
    );
    process.exit(2);
  }

  const pptx = new PptxGenJS();
  // Default: 16:9. Ensure your HTML body dimensions match.
  // You can override by setting PptxGenJS `layout` yourself in a custom driver.
  pptx.layout = "LAYOUT_16x9";

  await html2pptx(htmlFile, pptx);

  const outPath = path.isAbsolute(outputFile)
    ? outputFile
    : path.join(process.cwd(), outputFile);
  await pptx.writeFile({ fileName: outPath });
}

main().catch((err) => {
  process.stderr.write(String(err?.stack || err) + "\n");
  process.exit(1);
});
