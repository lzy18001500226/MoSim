import { test, expect } from "../../fixtures";
import { TEST_ORG_SLUG, TEST_USER } from "../../helpers/env";
import { gotoHash } from "../../helpers/nav";

// Desktop counterpart of
// clients/web/e2e-playwright/tests/settings/personal-agents-credentials.spec.ts.
//
// The renderer reuses AgentConfigPage + AgentCredentialsSettings from the
// web tree; Desktop drives the same Rust Core via node-bridge. After the
// credential-form rework the dialog spec lives entirely in the renderer —
// these tests verify the new XOR / custom-env UX still wires through the
// native dylib path.

const NAME_PREFIX = "Desktop E2E Credential";

function unique(label: string): string {
  return `${NAME_PREFIX} ${label} ${Date.now()}`;
}

async function gotoAgentSettings(
  page: import("@playwright/test").Page,
  slug: string
): Promise<void> {
  await gotoHash(
    page,
    `/${TEST_ORG_SLUG}/settings?scope=personal&tab=agents/${slug}`
  );
}

test.describe("Desktop · Claude Code (XOR auth)", () => {
  test("dialog shows Base URL first + RadioGroup toggles inputs", async ({ page }) => {
    await gotoAgentSettings(page, "claude-code");

    await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
      .first().click();

    await expect(page.locator("#cred-name")).toBeVisible();
    await expect(page.locator("#cred-desc")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_BASE_URL")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_AUTH_TOKEN")).toHaveCount(0);

    await page.getByTestId("oneof-option-anthropic_auth-ANTHROPIC_AUTH_TOKEN").click();
    await expect(page.locator("#cred-ANTHROPIC_AUTH_TOKEN")).toBeVisible();
    await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toHaveCount(0);
  });

  test("seeded credential bundle renders in the list", async ({ page, api, db }) => {
    const bundleName = unique("seeded");
    db.cleanup(
      `DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`
    );

    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();
    await cc.envBundle.createEnvBundle({
      agentSlug: "claude-code",
      name: bundleName,
      description: "seeded by desktop e2e",
      kind: "credential",
      data: { ANTHROPIC_API_KEY: "sk-ant-desktop-seeded" },
    });

    try {
      await gotoAgentSettings(page, "claude-code");
      await expect(page.getByText(bundleName, { exact: true })).toBeVisible({ timeout: 15_000 });
    } finally {
      db.cleanup(
        `DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`
      );
    }
  });

  test("UI create flow: new credential appears in the list after submit", async ({ page, db }) => {
    const bundleName = unique("ui-create");
    db.cleanup(
      `DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`
    );

    try {
      await gotoAgentSettings(page, "claude-code");

      await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
        .first().click();
      await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toBeVisible();

      await page.locator("#cred-name").fill(bundleName);
      await page.locator("#cred-desc").fill("created via desktop UI");
      await page.locator("#cred-ANTHROPIC_BASE_URL").fill("https://proxy.anthropic.example");
      await page.locator("#cred-ANTHROPIC_API_KEY").fill("sk-ant-desktop-ui-created");

      await page.getByRole("button", { name: /^(Create|创建)$/ }).click();
      await expect(page.getByText(bundleName, { exact: true })).toBeVisible({ timeout: 15_000 });
    } finally {
      db.cleanup(
        `DELETE FROM env_bundles WHERE name LIKE '${NAME_PREFIX}%'`
      );
    }
  });
});

test.describe("Desktop · Loopal (custom env)", () => {
  test("dialog renders three distinct provider keys + add-variable button", async ({ page }) => {
    await gotoAgentSettings(page, "loopal");

    await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
      .first().click();

    await expect(page.locator("#cred-ANTHROPIC_API_KEY")).toBeVisible();
    await expect(page.locator("#cred-OPENAI_API_KEY")).toBeVisible();
    await expect(page.locator("#cred-GOOGLE_API_KEY")).toBeVisible();
    await expect(page.getByRole("button", { name: /Add Variable|添加环境变量/ })).toBeVisible();
  });
});

test.describe("Desktop · Codex (custom env)", () => {
  test("declared OPENAI_API_KEY + add-variable button", async ({ page }) => {
    await gotoAgentSettings(page, "codex-cli");

    await page.getByRole("button", { name: /Add Custom Credentials|添加自定义凭据/i })
      .first().click();
    await expect(page.locator("#cred-OPENAI_API_KEY")).toBeVisible();
    await expect(page.getByRole("button", { name: /Add Variable|添加环境变量/ })).toBeVisible();
  });
});
