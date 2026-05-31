import type { Page } from "@playwright/test";

/** Navigate the Electron renderer via hash router (react-router-dom createHashRouter). */
export async function gotoHash(page: Page, path: string): Promise<void> {
  const normalized = path.startsWith("#") ? path : `#${path.startsWith("/") ? path : `/${path}`}`;
  const substring = normalized.slice(1);

  // Set the hash and wait for the router to settle there. If the app rebounces
  // back to a different route (rare on cold routes like mesh with async
  // guards), retry once with an explicit dispatch.
  const setOnce = async () => {
    await page.evaluate((h) => {
      const prevHash = window.location.hash;
      window.location.hash = h;
      if (prevHash === h) {
        window.dispatchEvent(new HashChangeEvent("hashchange", { oldURL: prevHash, newURL: h }));
      }
    }, normalized);
  };

  await setOnce();
  try {
    await page.waitForFunction(
      (sub) => window.location.hash.includes(sub),
      substring,
      { timeout: 10_000 },
    );
  } catch {
    // Retry loop: dashboard routes can bounce back to /workspace on cold
    // boot when the Connect-RPC adapters race with the route guard. Hammer
    // the hash a few times — once the cache populator settles, the next
    // setHash sticks. Empirically 3 attempts at 500 ms covers it.
    for (let i = 0; i < 4; i++) {
      await page.waitForTimeout(800);
      await setOnce();
      try {
        await page.waitForFunction(
          (sub) => window.location.hash.includes(sub),
          substring,
          { timeout: 5_000 },
        );
        return;
      } catch { /* try again */ }
    }
    // Final attempt — let it throw with the diagnostic message.
    await page.waitForFunction(
      (sub) => window.location.hash.includes(sub),
      substring,
      { timeout: 5_000 },
    );
  }
}

/** Wait until window.location.hash includes the substring. */
export async function waitForHash(
  page: Page,
  substring: string,
  timeout = 20_000
): Promise<void> {
  await page.waitForFunction(
    (sub) => window.location.hash.includes(sub),
    substring,
    { timeout }
  );
}

/** Return current hash path without the leading '#'. */
export async function currentRoute(page: Page): Promise<string> {
  return page.evaluate(() => window.location.hash.replace(/^#/, ""));
}

/** Wait for the hash to match the regex; returns the matched hash. */
export async function expectHashMatches(
  page: Page,
  re: RegExp,
  timeout = 20_000
): Promise<string> {
  await page.waitForFunction(
    ({ src, flags }) => new RegExp(src, flags).test(window.location.hash),
    { src: re.source, flags: re.flags },
    { timeout }
  );
  return currentRoute(page);
}
