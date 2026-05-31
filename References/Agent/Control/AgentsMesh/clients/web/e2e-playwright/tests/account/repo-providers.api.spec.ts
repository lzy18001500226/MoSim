// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Repository Providers API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-REPOPROV-001: List repository providers
   */
  test("list repository providers", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.userRepositoryProvider.listRepositoryProviders({}) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list repository providers without auth returns unauthenticated", async ({ api }) => {
    const cc = api.connectWithToken("bad");
    await expect(
      cc.userRepositoryProvider.listRepositoryProviders({})
    ).rejects.toMatchObject({ status: 401 });
  });

  /**
   * TC-REPOPROV-002: Create GitHub provider
   */
  test("create GitHub provider", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E GitHub Provider " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_test_bot_token_e2e",
    }) as { id: number };
    expect(created.id).toBeTruthy();

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: created.id });
  });

  /**
   * TC-REPOPROV-003: Update provider name
   */
  test("update provider name", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E Update Provider " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_update_test",
    }) as { id: number };
    expect(created.id, "create must return a provider id").toBeTruthy();

    const updated = await cc.userRepositoryProvider.updateRepositoryProvider({
      id: created.id,
      name: "E2E Updated Provider",
    }) as { name: string };
    expect(updated.name).toBe("E2E Updated Provider");

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: created.id });
  });

  /**
   * TC-REPOPROV-004: Delete provider
   */
  test("delete provider", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E Delete Provider " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_delete_test",
    }) as { id: number };
    expect(created.id, "create must return a provider id").toBeTruthy();

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: created.id });

    // Verify gone
    await expect(
      cc.userRepositoryProvider.getRepositoryProvider({ id: created.id })
    ).rejects.toMatchObject({ status: 404 });
  });

  /**
   * TC-REPOPROV-006: Test connection (with invalid token)
   */
  test("test connection with invalid token fails", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E Connection Test " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_invalid_token",
    }) as { id: number };
    expect(created.id, "create must return a provider id").toBeTruthy();

    // Tolerates success or failure due to invalid token — backend dependency.
    await cc.userRepositoryProvider
      .testRepositoryProviderConnection({ id: created.id })
      .catch((e) => e);

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: created.id });
  });

  /**
   * TC-REPOPROV-007: Created provider defaults to is_active=true and exposes has_* flags
   *
   * Regression for the user-reported bug where every provider showed as
   * "已禁用" (disabled). The wasm-core RepositoryProvider struct used to drop
   * is_active / has_identity / has_bot_token / has_client_id during the
   * deserialize-then-reserialize relay, so the frontend always read undefined.
   */
  test("created provider exposes is_active=true and has_* flags by default", async ({ api }) => {
    const cc = await api.connect();
    const provider = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E IsActive Default " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_default_active",
    }) as {
      id: number;
      isActive: boolean;
      hasBotToken: boolean;
      hasClientId: boolean;
      hasIdentity: boolean;
    };

    expect(provider.isActive).toBe(true);
    expect(provider.hasBotToken).toBe(true);
    expect(provider.hasClientId).toBe(false);
    expect(provider.hasIdentity).toBe(false);

    const list = await cc.userRepositoryProvider.listRepositoryProviders({}) as {
      items: Array<{ id: number; isActive: boolean; hasBotToken: boolean }>;
    };
    const inList = list.items.find((p) => p.id === provider.id);
    expect(inList?.isActive).toBe(true);
    expect(inList?.hasBotToken).toBe(true);

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: provider.id });
  });

  /**
   * TC-REPOPROV-008: Toggling is_active persists across reloads.
   *
   * This is the exact flow that broke under the wasm-core bug: the
   * UpdateRepositoryProviderRequest struct lacked is_active, so sending
   * {is_active: true} from EditProviderDialog produced an empty PUT body
   * and the change silently no-op'd.
   */
  test("Update is_active=false then is_active=true persists each toggle", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E IsActive Toggle " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_toggle_test",
    }) as { id: number };

    const off = await cc.userRepositoryProvider.updateRepositoryProvider({
      id: created.id,
      isActive: false,
    }) as { isActive: boolean };
    expect(off.isActive).toBe(false);

    const reloadAfterOff = await cc.userRepositoryProvider.getRepositoryProvider({
      id: created.id,
    }) as { isActive: boolean };
    expect(reloadAfterOff.isActive).toBe(false);

    const on = await cc.userRepositoryProvider.updateRepositoryProvider({
      id: created.id,
      isActive: true,
    }) as { isActive: boolean };
    expect(on.isActive).toBe(true);

    const reloadAfterOn = await cc.userRepositoryProvider.getRepositoryProvider({
      id: created.id,
    }) as { isActive: boolean };
    expect(reloadAfterOn.isActive).toBe(true);

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: created.id });
  });

  /**
   * TC-REPOPROV-009: Partial update (name only) preserves is_active.
   */
  test("partial update preserves is_active across renames", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: "E2E Partial Original " + Date.now(),
      baseUrl: "https://api.github.com",
      botToken: "ghp_partial",
    }) as { id: number };

    await cc.userRepositoryProvider.updateRepositoryProvider({
      id: created.id,
      isActive: false,
    });

    const renamed = await cc.userRepositoryProvider.updateRepositoryProvider({
      id: created.id,
      name: "E2E Partial Renamed",
    }) as { name: string; isActive: boolean };
    expect(renamed.name).toBe("E2E Partial Renamed");
    expect(renamed.isActive).toBe(false);

    await cc.userRepositoryProvider.deleteRepositoryProvider({ id: created.id });
  });
});
