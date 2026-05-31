// Migrated R5+: Connect-RPC only (no REST middle layer).
//
// Pre-R5 these were `api.get('/api/v1/orgs/.../bindings')` calls that the REST
// handler authed via the X-Pod-Key header — without one the response was a
// 200-empty / 401. The Connect surface bakes the calling pod into every
// request as `initiator_pod`, so we exercise the same code path with a
// synthetic key. The handler validates the pod against the org membership,
// so an unknown key yields a normal error (caught below) rather than the
// REST-era status-code-ladder.
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Binding API Operations", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list bindings tolerates missing pod context", async ({ api }) => {
    const cc = await api.connect();
    // Connect throws on unknown pod; the surface contract is "no 5xx" — we
    // accept either a successful empty result or a 4xx ConnectError.
    try {
      const res = await cc.binding.listBindings({
        orgSlug: TEST_ORG_SLUG,
        initiatorPod: "e2e-nonexistent-pod",
      }) as { items: unknown[] };
      expect(Array.isArray(res.items)).toBe(true);
    } catch (err: unknown) {
      expect((err as { status: number }).status).toBeGreaterThanOrEqual(400);
      expect((err as { status: number }).status).toBeLessThan(500);
    }
  });

  test("get pending bindings", async ({ api }) => {
    const cc = await api.connect();
    try {
      const res = await cc.binding.getPendingBindings({
        orgSlug: TEST_ORG_SLUG,
        initiatorPod: "e2e-nonexistent-pod",
      }) as { items: unknown[] };
      expect(Array.isArray(res.items)).toBe(true);
    } catch (err: unknown) {
      expect((err as { status: number }).status).toBeGreaterThanOrEqual(400);
      expect((err as { status: number }).status).toBeLessThan(500);
    }
  });

  test("get bound pods", async ({ api }) => {
    const cc = await api.connect();
    try {
      const res = await cc.binding.getBoundPods({
        orgSlug: TEST_ORG_SLUG,
        initiatorPod: "e2e-nonexistent-pod",
      }) as { pods: string[] };
      expect(Array.isArray(res.pods)).toBe(true);
    } catch (err: unknown) {
      expect((err as { status: number }).status).toBeGreaterThanOrEqual(400);
      expect((err as { status: number }).status).toBeLessThan(500);
    }
  });
});
