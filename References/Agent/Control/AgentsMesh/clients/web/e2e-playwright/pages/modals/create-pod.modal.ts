import type { Page } from "@playwright/test";

/**
 * Page Object Model for the Create Pod Modal.
 * Based on: web/src/components/ide/CreatePodModal.tsx
 *           web/src/components/pod/CreatePodForm/index.tsx
 */
export class CreatePodModal {
  constructor(private page: Page) {}

  /** Wait for the modal dialog to appear. */
  async waitForOpen(): Promise<void> {
    await this.page
      .locator('[role="dialog"]')
      .first()
      .waitFor({ state: "visible" });
  }

  /** Wait for the modal to disappear after a successful submit. */
  async waitForClosed(timeoutMs = 15_000): Promise<void> {
    await this.page
      .locator('[role="dialog"]')
      .first()
      .waitFor({ state: "hidden", timeout: timeoutMs });
  }

  /**
   * Select an agent. The form renders a native `<select id="agent-select">`
   * (web/src/components/pod/CreatePodForm/AgentSelect.tsx) — `<option>` text
   * is not in the visible DOM until the dropdown is opened, so the previous
   * `getByText(...).click()` was a silent no-op and left the Create Pod
   * button disabled.
   */
  async selectAgent(agentSlug: string): Promise<void> {
    const select = this.page
      .locator('[role="dialog"] select#agent-select')
      .first();
    // The dialog opens before usePodCreationData finishes loading agents,
    // so AgentSelect renders "no agents" until runners + agents arrive.
    // Wait up to 15s for the actual <select> to mount.
    await select.waitFor({ state: "visible", timeout: 15_000 });
    await select.selectOption(agentSlug);
  }

  /** Fill the prompt text area. */
  async fillPrompt(prompt: string): Promise<void> {
    const textarea = this.page.locator("textarea").first();
    await textarea.fill(prompt);
  }

  /**
   * Expand the AdvancedOptions disclosure that wraps runner / env-bundle /
   * repository / branch / config inputs. No-op when already open.
   * AdvancedOptions defaults closed, so spec code that needs any field
   * inside it must call this before locating the input.
   */
  async expandAdvancedOptions(): Promise<void> {
    const trigger = this.page
      .locator('[role="dialog"]')
      .getByRole("button", { name: /advanced options|高级选项/i });
    if (!(await trigger.isVisible().catch(() => false))) return;
    const state = await trigger.getAttribute("data-state");
    if (state !== "open") {
      await trigger.click();
    }
  }

  /**
   * Select an API credential bundle by name. The credential picker is a
   * single-select `<select id="credential-bundle-select">`; pass "" to pick
   * the "Use Agent default auth" option (i.e. inject no credential).
   * Lives inside AdvancedOptions — call `expandAdvancedOptions()` first.
   */
  async selectCredential(bundleName: string): Promise<void> {
    const select = this.page
      .locator('[role="dialog"] select#credential-bundle-select')
      .first();
    await select.selectOption(bundleName);
  }

  /**
   * Toggle a runtime-kind EnvBundle row by name (multi-select). Calling
   * once with a name not yet checked adds it to the ordered selection;
   * calling again un-checks it. Multiple calls in succession build an
   * ordered list — the order matches selection order and drives
   * USE_ENV_BUNDLE emission order (later bundles override earlier ones on
   * conflicting env keys). The checkboxes live inside AdvancedOptions —
   * call `expandAdvancedOptions()` first.
   */
  async toggleRuntimeBundle(bundleName: string): Promise<void> {
    const row = this.page
      .locator('[role="dialog"]')
      .locator('label', { hasText: bundleName })
      .first();
    const checkbox = row.locator('input[type="checkbox"]').first();
    await checkbox.click();
  }

  /**
   * Convenience: clear the runtime selection then toggle each name in
   * order so the post-call selection equals exactly `bundleNames`.
   */
  async selectRuntimeBundles(bundleNames: string[]): Promise<void> {
    const all = this.page
      .locator('[role="dialog"] input[type="checkbox"]');
    const count = await all.count();
    for (let i = 0; i < count; i += 1) {
      const box = all.nth(i);
      if (await box.isChecked()) await box.click();
    }
    for (const name of bundleNames) {
      await this.toggleRuntimeBundle(name);
    }
  }

  /** Click the submit/create button. */
  async submit(): Promise<void> {
    const btn = this.page
      .locator('[role="dialog"]')
      .getByRole("button", { name: /create|创建/i });
    await btn.click();
  }

  /** Close the modal. */
  async cancel(): Promise<void> {
    const btn = this.page
      .locator('[role="dialog"]')
      .getByRole("button", { name: /cancel|取消/i });
    if (await btn.isVisible()) await btn.click();
  }
}
