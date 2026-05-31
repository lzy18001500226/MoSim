// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Notification API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("get notification preferences", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.notification.listPreferences({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("update notification preferences", async ({ api }) => {
    const cc = await api.connect();
    // SetPreference is the upsert primitive (proto.notification.v1) — exercise
    // a benign no-op source/channel pair so we don't poison the dev user's prefs.
    const pref = await cc.notification.setPreference({
      orgSlug: TEST_ORG_SLUG,
      source: "channel:message",
      isMuted: false,
      channels: { toast: true, browser: true },
    }) as { source: string };
    expect(pref.source).toBe("channel:message");
  });
});
