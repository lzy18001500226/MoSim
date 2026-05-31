import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { terminateAllPods } from "../../helpers/pod-cleanup";
import { uniqueSuffix } from "../../helpers/test-data";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import {
  createPodAndWaitRunning,
  readEnvDumpFromRunner,
  clearRunnerDumps,
} from "../../helpers/env-bundle-e2e";

// EnvBundle kinds on the wire. Backend / Rust core uses these literal
// strings; e2e is a black-box observer so referencing the frontend's
// EnvBundleKind constant would create a cross-package coupling.
const KIND_CREDENTIAL = "credential";
const KIND_RUNTIME = "runtime";

/**
 * EnvBundle end-to-end causal chain:
 *
 *   Settings UI → bundle row → Pod create dialog → backend agentfile eval →
 *   runner gRPC CreatePodCommand → bash spawn with env → e2e-echo writes
 *   env dump to /tmp/e2e-echo-env-dump-<pid>
 *
 * We verify the dump file via `docker exec cat` inside the runner
 * container. This proves the full Settings-UI → child-process env path
 * without depending on PTY streaming (which is async / unreliable for
 * daemon-managed pods).
 *
 * Uses the e2e-echo builtin agent, modified by migration 000150 to write
 * whitelisted env vars to a sandbox file on startup.
 */
const AGENT_SLUG = "e2e-echo";
const BUNDLE_PREFIX = "e2e-bundle-chain";

const unique = (label: string) => `${BUNDLE_PREFIX}-${label}-${uniqueSuffix()}`;

/**
 * Drive Settings UI to create an EnvBundle. The credential and runtime
 * dialogs share name + KV mechanics but differ in entry button + dialog
 * id namespace — encoded in the `selectors` discriminator below.
 */
async function createBundleViaSettingsUI(args: {
  page: import("@playwright/test").Page;
  kind: typeof KIND_CREDENTIAL | typeof KIND_RUNTIME;
  name: string;
  envKey: string;
  envValue: string;
}): Promise<void> {
  const { page, kind, name, envKey, envValue } = args;
  const selectors =
    kind === KIND_CREDENTIAL
      ? {
          openDialog: async () =>
            page
              .getByRole("button", { name: /添加自定义凭据|Add Custom Credentials/i })
              .click(),
          nameInput: "#cred-name",
          fillEnv: async () => page.locator(`#cred-${envKey}`).fill(envValue),
        }
      : {
          openDialog: async () => {
            const heading = page
              .getByRole("heading", { name: /Runtime Env Variables|运行时环境变量/i })
              .first();
            await heading.waitFor({ state: "visible", timeout: 10_000 });
            await heading.scrollIntoViewIfNeeded();
            await heading
              .locator(
                'xpath=following::button[normalize-space(.)="Add" or normalize-space(.)="添加"][1]',
              )
              .click();
          },
          nameInput: "#runtime-name",
          fillEnv: async () => {
            await page
              .locator('input[placeholder="ENV_NAME"], input[placeholder="环境变量名"]')
              .first()
              .fill(envKey);
            await page
              .locator('input[placeholder="Value"], input[placeholder="值"]')
              .first()
              .fill(envValue);
          },
        };

  const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
  await nav.goto("personal", `agents/${AGENT_SLUG}`);
  await selectors.openDialog();
  await page.locator(selectors.nameInput).waitFor({ state: "visible", timeout: 5000 });
  await page.locator(selectors.nameInput).fill(name);
  await selectors.fillEnv();
  await page.getByRole("button", { name: /^(创建|Create)$/ }).click();
  await page.locator(selectors.nameInput).waitFor({ state: "hidden", timeout: 5000 });
  await page.getByText(name, { exact: false }).first().waitFor({ timeout: 5000 });
}

/** Strip kind_primary off every credential bundle for e2e-echo so the
 *  Pod-create dialog's credential picker lands on "Use Agent default
 *  auth" rather than auto-selecting a leftover primary. */
function clearCredentialPrimary(db: { cleanup: (sql: string) => void }): void {
  db.cleanup(
    `UPDATE env_bundles SET kind_primary = FALSE WHERE agent_slug = '${AGENT_SLUG}' AND kind = '${KIND_CREDENTIAL}'`,
  );
}

test.describe("EnvBundle end-to-end (Settings UI → Pod → child env)", () => {
  test.beforeEach(async () => {
    clearAuthRateLimit();
    await terminateAllPods();
  });

  test.afterEach(async ({ db }) => {
    // Only terminateAllPods is async; the other two cleanups are sync and
    // gain nothing from Promise.all wrapping. Order: pods first (drops
    // dump files via their own teardown), then SQL + dump rm.
    await terminateAllPods();
    db.cleanup(`DELETE FROM env_bundles WHERE name LIKE '${BUNDLE_PREFIX}%'`);
    clearRunnerDumps();
  });

  test("runtime bundle: Settings UI → Pod create → env injected to child process", async ({
    page,
    api,
  }) => {
    const bundleName = unique("rt");
    const envKey = "E2E_TEST_BUNDLE_RUNTIME";
    const envValue = `runtime-marker-${Date.now()}`;

    await createBundleViaSettingsUI({
      page,
      kind: KIND_RUNTIME,
      name: bundleName,
      envKey,
      envValue,
    });

    await createPodAndWaitRunning({
      page,
      api,
      agentSlug: AGENT_SLUG,
      selectRuntimeBundleNames: [bundleName],
    });

    const dump = await readEnvDumpFromRunner();
    expect(dump).toContain(`${envKey}=${envValue}`);
  });

  test("credential bundle: Settings UI → Pod create → env injected to child process", async ({
    page,
    api,
  }) => {
    const bundleName = unique("cred");
    const envKey = "E2E_TEST_CRED_KEY";
    const envValue = `cred-marker-${Date.now()}`;

    await createBundleViaSettingsUI({
      page,
      kind: KIND_CREDENTIAL,
      name: bundleName,
      envKey,
      envValue,
    });

    await createPodAndWaitRunning({
      page,
      api,
      agentSlug: AGENT_SLUG,
      selectCredentialName: bundleName,
    });

    const dump = await readEnvDumpFromRunner();
    expect(dump).toContain(`${envKey}=${envValue}`);
  });

  test("default-auth selection: no credential bundle → no cred key in child env", async ({
    page,
    api,
    db,
  }) => {
    const bundleName = unique("cred-not-picked");
    const envKey = "E2E_TEST_CRED_KEY";
    const envValue = `should-not-appear-${Date.now()}`;

    const cc = await api.connect();
    await cc.envBundle.createEnvBundle({
      agentSlug: AGENT_SLUG,
      name: bundleName,
      kind: KIND_CREDENTIAL,
      data: { [envKey]: envValue },
    });
    clearCredentialPrimary(db);

    // Empty string explicitly selects "Use Agent default auth", overriding
    // any primary that survived clearCredentialPrimary in a race.
    await createPodAndWaitRunning({
      page,
      api,
      agentSlug: AGENT_SLUG,
      selectCredentialName: "",
    });

    const dump = await readEnvDumpFromRunner();
    expect(dump).not.toContain(envValue);
  });

  test("credential switch: changing dropdown selection swaps which bundle is injected", async ({
    page,
    api,
    db,
  }) => {
    const bundleAName = unique("cred-A");
    const bundleBName = unique("cred-B");
    const envKey = "E2E_TEST_CRED_KEY";
    const valueA = `cred-A-value-${Date.now()}`;
    const valueB = `cred-B-value-${Date.now()}`;

    const cc = await api.connect();
    await Promise.all([
      cc.envBundle.createEnvBundle({
        agentSlug: AGENT_SLUG,
        name: bundleAName,
        kind: KIND_CREDENTIAL,
        data: { [envKey]: valueA },
      }),
      cc.envBundle.createEnvBundle({
        agentSlug: AGENT_SLUG,
        name: bundleBName,
        kind: KIND_CREDENTIAL,
        data: { [envKey]: valueB },
      }),
    ]);
    clearCredentialPrimary(db);

    // Pick A first, then B — exercises the switch path inside the dropdown
    // rather than just first-time selection. Final submitted value = B.
    await createPodAndWaitRunning({
      page,
      api,
      agentSlug: AGENT_SLUG,
      selectCredentialName: bundleAName,
      customizeModal: async (modal) => {
        await modal.selectCredential(bundleBName);
      },
    });

    const dump = await readEnvDumpFromRunner();
    expect(dump).toContain(`${envKey}=${valueB}`);
    expect(dump).not.toContain(valueA);
  });
});
