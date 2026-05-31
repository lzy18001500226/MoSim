import type { Locator, Page } from "@playwright/test";

/**
 * Activity bar navigation sections. Mirrors ACTIVITIES in web/src/stores/ide.ts.
 * After the IA-Infra refactor, Runner + Repository live under /infra?tab=...
 * rather than as top-level activities. Legacy /repositories and /runners URLs
 * still redirect, but the activity bar no longer exposes them.
 */
export type NavSection =
  | "workspace"
  | "tickets"
  | "channels"
  | "mesh"
  | "loops"
  | "blocks"
  | "infra"
  | "settings";

export class SidebarPage {
  constructor(
    private page: Page,
    private orgSlug: string
  ) {}

  /**
   * ActivityBar nav link. The bar renders inside `<aside class="w-[136px] …">`
   * with one `<Link>` per `ACTIVITIES` entry; scoping by aside avoids the old
   * Tailwind-class brittleness (specs used to pin `a.w-10.h-10` from the
   * icon-square era — the bar is now a 136-wide label list).
   *
   * Use prefix match (`href^=`) because `/infra` rewrites to
   * `/infra?tab=runners` in `getActivityRoute`. Other sections have no
   * overlapping prefixes among NavSection so this stays unambiguous.
   */
  getNavLink(section: NavSection): Locator {
    return this.page.locator(
      `aside a[href^="/${this.orgSlug}/${section}"]`
    );
  }

  /** Dev overlay intercepts pointer events — strip it in dev mode. */
  async dismissDevOverlay(): Promise<void> {
    await this.page.evaluate(() => {
      document.querySelectorAll("nextjs-portal").forEach((el) => el.remove());
    });
  }

  async navigateTo(section: NavSection): Promise<void> {
    await this.dismissDevOverlay();
    const link = this.getNavLink(section);
    await link.waitFor({ state: "visible", timeout: 10_000 });
    // Radix Tooltip wraps the <Link> via TooltipTrigger asChild, which can
    // eat pointer events from native click. Dispatch a synthetic MouseEvent
    // to invoke Next's Link click handler directly and trigger navigation.
    await link.click({ timeout: 5000 }).catch(async () => {
      await link.dispatchEvent("click");
    });
    // The URL may settle to the bare section route or one of its auto-redirect
    // forms (e.g., /infra → /infra?tab=repositories&id=<n>). Poll current URL
    // instead of awaiting a navigation event — if the URL is already matching
    // at waitForURL entry, the predicate isn't re-checked. If the first click
    // didn't register (tooltip ate it + dispatchEvent no-op), try a force
    // click before giving up.
    try {
      await this.page.waitForFunction(
        ({ orgSlug, section }) => window.location.pathname.includes(`/${orgSlug}/${section}`),
        { orgSlug: this.orgSlug, section },
        { timeout: 8_000 },
      );
    } catch {
      await link.click({ force: true, timeout: 5000 });
      await this.page.waitForFunction(
        ({ orgSlug, section }) => window.location.pathname.includes(`/${orgSlug}/${section}`),
        { orgSlug: this.orgSlug, section },
        { timeout: 10_000 },
      );
    }
  }

  async isOnSection(section: NavSection): Promise<boolean> {
    return this.page.url().includes(`/${this.orgSlug}/${section}`);
  }
}
