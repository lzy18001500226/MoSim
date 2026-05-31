// Legacy `promoCodeApi` adapter. After the proto migration this thin wrapper
// delegates to promocodeConnect.ts (binary-wire Connect-RPC) so existing call
// sites keep working unchanged. Mirrors lib/api/billing.ts's pattern.
//
// New call sites should import directly from `./promocodeConnect`; this module
// stays as the dual-track shim until every consumer flips.

import {
  validatePromoCode,
  redeemPromoCode,
  getRedemptionHistory,
} from "../connect/promocodeConnect";

export type {
  ValidatePromoCodeResponse,
  RedeemPromoCodeResponse,
  PromoCodeRedemption,
} from "../connect/promocodeConnect";

// Connect requires org_slug on every request; the legacy `promoCodeApi`
// surface left the slug implicit (tenant context via REST middleware). Until
// every caller threads the slug we keep two entry points: the new
// org-scoped one for callers ready to flip, plus an empty-string default
// that produces a ResolveOrgScope failure at the boundary instead of
// silently hitting the wrong org.
export const promoCodeApi = {
  validate: async (code: string, orgSlug = "") => validatePromoCode(orgSlug, code),
  redeem: async (code: string, orgSlug = "") => redeemPromoCode(orgSlug, code),
  getHistory: async (orgSlug = "") => getRedemptionHistory(orgSlug),
};
