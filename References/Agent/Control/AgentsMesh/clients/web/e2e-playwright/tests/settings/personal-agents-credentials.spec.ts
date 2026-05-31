import { test, expect } from "../../fixtures/index";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import { TEST_ORG_SLUG, TEST_USER } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

// Regression coverage for the credential dialog after the EnvBundle refactor:
//
//   - "Credential" is now one kind of EnvBundle (kind='credential'); requests
//     reach EnvBundleService over Connect-RPC with a unified {kind, data} payload.
//   - Backend stays a pure KV store; the per-agent form spec lives on the
//     frontend (declared ENVs + custom ENV section).
//
// Three flows are covered:
//   * Claude Code — Base URL on top, RadioGroup XOR for API Key vs Auth
//     Token (only one input visible at a time).
//   * Loopal — three distinct provider labels + a custom-ENV section
//     that round-trips (e.g. XAI_API_KEY).
//   * Codex CLI — single declared field + custom-ENV section so users can
//     add OPENAI_BASE_URL etc. for proxy setups.

const NAME_PREFIX = "E2E Bundle";

function unique(label: string): string {
  return `${NAME_PREFIX} ${label} ${Date.now()}`;
}

test.describe("Personal Agent Credentials — Claude Code (XOR auth)", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  test("dialog shows Base URL first + RadioGroup that toggles inputs", async ({ page }) => {
    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("personal", `agents/claude-code`);

    await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
      .first().click();

    await expect(page.locator("#cred-name")).toBeVisible();
    await expect(page.locator("#cred-desc")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_BASE_URL")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_BASE_URL")).toHaveAttribute("type", "text");

    // RadioGroup defaults to API Key — Auth Token input must not exist yet.
    await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toHaveAttribute("type", "password");
    await expect(page.locator("#cred-ANTHROPIC_AUTH_TOKEN")).toHaveCount(0);

    // Switching the radio swaps the active input.
    await page.getByTestId("oneof-option-anthropic_auth-ANTHROPIC_AUTH_TOKEN").click();
    await expect(page.locator("#cred-ANTHROPIC_AUTH_TOKEN")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_AUTH_TOKEN")).toHaveAttribute("type", "password");
    await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toHaveCount(0);
  });

  test("seeded credential bundle renders in the list", async ({ page, api, db }) => {
    const bundleName = unique("seeded");
    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`);

    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();
    await cc.envBundle.createEnvBundle({
      agentSlug: "claude-code",
      name: bundleName,
      description: "seeded by e2e",
      kind: "credential",
      data: { ANTHROPIC_API_KEY: "sk-ant-e2e-seeded" },
    });

    try {
      const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
      await nav.goto("personal", `agents/claude-code`);
      await expect(page.getByText(bundleName, { exact: true })).toBeVisible({ timeout: 15_000 });
    } finally {
      db.cleanup(`DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`);
    }
  });

  test("UI create flow: new credential appears in the list after submit", async ({ page, db }) => {
    const bundleName = unique("ui-create");
    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`);

    try {
      const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
      await nav.goto("personal", `agents/claude-code`);

      await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
        .first().click();
      await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toBeVisible();

      await page.locator("#cred-name").fill(bundleName);
      await page.locator("#cred-desc").fill("created via UI");
      await page.locator("#cred-ANTHROPIC_BASE_URL").fill("https://proxy.anthropic.example");
      await page.locator("#cred-ANTHROPIC_API_KEY").fill("sk-ant-e2e-ui-created");

      await page.getByRole("button", { name: /^(Create|创建)$/ }).click();

      await expect(page.getByText(bundleName, { exact: true })).toBeVisible({ timeout: 15_000 });
    } finally {
      db.cleanup(`DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`);
    }
  });
});

test.describe("Personal Agent Credentials — Loopal (custom env)", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  test("dialog renders three distinct provider keys + custom env section", async ({ page }) => {
    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("personal", `agents/loopal`);

    await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
      .first().click();

    await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toBeVisible();
    await expect(page.locator("#cred-OPENAI_API_KEY")).toBeVisible();
    await expect(page.locator("#cred-GOOGLE_API_KEY")).toBeVisible();
    await expect(page.getByRole("button", { name: /Add Variable|添加环境变量/ })).toBeVisible();
  });

  test("custom env round-trips through the backend", async ({ page, db }) => {
    const bundleName = unique("loopal-custom");
    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`);

    try {
      const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
      await nav.goto("personal", `agents/loopal`);

      await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
        .first().click();
      await page.locator("#cred-name").fill(bundleName);
      await page.locator("#cred-OPENAI_API_KEY").fill("sk-openai-loopal");
      await page.getByRole("button", { name: /Add Variable|添加环境变量/ }).click();

      const keyInputs = page.getByLabel(/ENV_NAME|环境变量名/);
      await keyInputs.last().fill("XAI_API_KEY");
      const valueInputs = page.getByLabel(/^Value$|^值$/);
      await valueInputs.last().fill("xai-secret-value");

      await page.getByRole("button", { name: /^(Create|创建)$/ }).click();
      await expect(page.getByText(bundleName, { exact: true })).toBeVisible({ timeout: 15_000 });

      // The bundle should have landed in env_bundles with kind=credential and
      // agent_slug=loopal. We only verify presence; the encrypted blob lives
      // in `data` JSONB which we don't probe from e2e.
      const count = db.queryValue(
        `SELECT count(*) FROM env_bundles
         WHERE name = '${bundleName}' AND agent_slug = 'loopal' AND kind = 'credential'`
      );
      expect(count).toBe("1");
    } finally {
      db.cleanup(`DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`);
    }
  });
});

test.describe("Personal Agent Credentials — Codex (custom env)", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
  });

  test("declared OPENAI_API_KEY + custom env button", async ({ page }) => {
    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("personal", `agents/codex-cli`);

    await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
      .first().click();
    await expect(page.locator("#cred-OPENAI_API_KEY")).toBeVisible();
    await expect(page.getByRole("button", { name: /Add Variable|添加环境变量/ })).toBeVisible();
  });
});
