import { test, expect } from "../../fixtures/index";
import { getApiBaseUrl } from "../../helpers/env";

/**
 * Webhook endpoint tests.
 * Verifies webhook endpoints exist and respond (may be 503 if providers not configured).
 */
test.describe("Billing Webhooks", () => {
  const baseUrl = getApiBaseUrl();

  test("stripe webhook endpoint responds", async () => {
    const res = await fetch(`${baseUrl}/api/v1/webhooks/stripe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: "test" }),
    });
    // 400 (bad signature), 401, or 503 (not configured) — endpoint exists
    expect([400, 401, 503]).toContain(res.status);
  });

  test("alipay webhook endpoint responds", async () => {
    const res = await fetch(`${baseUrl}/api/v1/webhooks/alipay`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    expect([400, 401, 503]).toContain(res.status);
  });

  test("wechat webhook endpoint responds", async () => {
    const res = await fetch(`${baseUrl}/api/v1/webhooks/wechat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    expect([400, 401, 503]).toContain(res.status);
  });
});
