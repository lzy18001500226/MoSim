// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Promo Codes", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-PROMO-002: Validate promo code
   */
  test("validate promo code endpoint exists", async ({ api }) => {
    const cc = await api.connect();
    // 200 if valid, 400/404 if invalid code — Connect throws on non-2xx; success is unlikely.
    await cc.promocode.validate({
      orgSlug: TEST_ORG_SLUG,
      code: "TESTCODE",
    }).catch((err: { status?: number }) => {
      expect([400, 404]).toContain(err.status);
    });
  });

  /**
   * TC-PROMO-003: Invalid promo code
   */
  test("invalid promo code returns valid=false", async ({ api }) => {
    const cc = await api.connect();
    const resp = await cc.promocode.validate({
      orgSlug: TEST_ORG_SLUG,
      code: "INVALID_CODE_XYZ_999",
    }) as { valid: boolean };
    expect(resp.valid).toBe(false);
  });

  /**
   * TC-PROMO-004: Redemption history
   */
  test("get promo code redemption history", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.promocode.getRedemptionHistory({
      orgSlug: TEST_ORG_SLUG,
    }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  /**
   * Connect-RPC binary lane (proto-migration feature branch). The PromoCodeInput
   * component now calls `validatePromoCode(orgSlug, code)` from
   * lib/api/promocodeConnect.ts — which goes through the wasm bridge →
   * ApiClient.validate_promo_code_connect → Connect handler at
   * /proto.promocode.v1.PromoCodeService/Validate.
   *
   * Asserting the UI surfaces a "not found" i18n message after submitting an
   * invalid code proves the binary protobuf path preserves `message_code`
   * end-to-end. Same pattern as skill-registry-wasm-roundtrip.spec.ts but
   * scoped to the error surface — seeding a real "valid" code would need
   * platform-admin DB fixtures that promo redemption (owner-only) won't
   * tolerate idempotently.
   */
  test("UI surfaces validation message_code via Connect path", async ({ page }) => {
    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("organization", "billing");

    // The PromoCodeInput is only visible once billing data has loaded; wait
    // for the input to render. Placeholder text varies by locale — match
    // the input by its uppercase-only class instead.
    const input = page.locator("input.uppercase").first();
    await expect(input).toBeVisible();
    await input.fill("INVALID_CONNECT_XYZ_999");

    const validateButton = page.getByRole("button", { name: /^Validate$|^Validating/i });
    await validateButton.click();

    // The Connect handler returns valid=false with message_code
    // "promo_code_not_found"; the renderer maps that i18n key to a
    // user-facing message. We assert the i18n-resolved text appears,
    // which only happens if the Connect response was decoded correctly
    // (a drift in the message_code field would render "Invalid promo
    // code" as the fallback instead).
    await expect(page.getByText(/Promo code not found|优惠码不存在/i)).toBeVisible();
  });
});
