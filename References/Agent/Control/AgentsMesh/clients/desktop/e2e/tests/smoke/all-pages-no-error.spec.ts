import { test, expect } from "../../fixtures";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { gotoHash } from "../../helpers/nav";

// Page-level smoke: each dashboard route must mount without throwing a JS
// exception. Catches SSOT-sync regressions where desktop Electron adapters
// lag behind Rust SSOT (e.g. a shim missing `blocks_json()` crashes the
// Blocks sidebar, but the old route-opens smoke didn't notice because React
// ErrorBoundary swallows the error).
//
// Uncaught exceptions bubble through `page.on("pageerror")`; we snapshot
// them per route and assert zero.

const ROUTES = [
  "workspace",
  "blocks",
  "channels",
  "mesh",
  "loops",
  "tickets",
  "infra",
] as const;

test.describe("all pages · no uncaught error", () => {
  for (const route of ROUTES) {
    test(`${route} page mounts without pageerror`, async ({ page }) => {
      const errors: string[] = [];
      const consoleMsgs: string[] = [];
      page.on("pageerror", (err) => errors.push(err.message));
      page.on("console", (msg) => {
        if (msg.type() === "error" || msg.type() === "warning") {
          consoleMsgs.push(`[${msg.type()}] ${msg.text().slice(0, 200)}`);
        }
      });

      try {
        await gotoHash(page, `/${TEST_ORG_SLUG}/${route}`);
      } catch (e) {
        const hash = await page.evaluate(() => window.location.hash);
        // eslint-disable-next-line no-console
        console.log(`[gotoHash timeout on /${route}] current hash=${hash} errors=${errors.join("|")} console=${consoleMsgs.slice(0, 3).join("|")}`);
        throw e;
      }

      // Give React a moment to mount + effects to settle.
      await page.waitForTimeout(1500);

      expect(errors, `pageerror on /${route}: ${errors.join(" | ")}`).toEqual([]);
    });
  }
});
