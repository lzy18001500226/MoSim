// proto ↔ legacy-REST shape conversions for adminPromoCodes adapter.
// Kept in a sibling file so adminPromoCodes.ts stays under the 200-line
// hard cap. See adminPromoCodes.ts for the wire-format rationale.
import type {
  PromoCode as ProtoPromoCode,
  RedemptionDetail as ProtoRedemptionDetail,
} from "@proto/promocode/v1/promocode_admin_pb";

import type { PromoCode, PromoCodeRedemption, PromoCodeType } from "./adminTypes";

export function promoCodeFromProto(p: ProtoPromoCode): PromoCode {
  return {
    id: Number(p.id),
    code: p.code,
    name: p.name,
    description: p.description,
    type: p.type as PromoCodeType,
    plan_name: p.planName,
    duration_months: p.durationMonths,
    max_uses: p.maxUses ?? null,
    used_count: p.usedCount,
    max_uses_per_org: p.maxUsesPerOrg,
    starts_at: p.startsAt,
    expires_at: p.expiresAt ?? null,
    is_active: p.isActive,
    created_by_id: p.createdById !== undefined ? Number(p.createdById) : null,
    created_at: p.createdAt,
    updated_at: p.updatedAt,
  };
}

export function redemptionFromProto(r: ProtoRedemptionDetail): PromoCodeRedemption {
  const userId = Number(r.userId);
  const orgId = Number(r.organizationId);
  const out: PromoCodeRedemption = {
    id: Number(r.id),
    promo_code_id: Number(r.promoCodeId),
    organization_id: orgId,
    user_id: userId,
    plan_name: r.planName,
    duration_months: r.durationMonths,
    new_period_end: r.newPeriodEnd,
    ip_address: r.ipAddress ?? null,
    created_at: r.createdAt,
  };
  // REST shape embedded the full User/Organization rows from GORM; the
  // admin UI only reads {email,username,avatar_url,name,id} on user and
  // {name,id} on org. Proto carries just the display fields — fill the
  // rest with safe defaults so the typed shape stays compatible.
  if (r.userEmail !== undefined || r.userUsername !== undefined) {
    out.user = {
      id: userId,
      email: r.userEmail ?? "",
      username: r.userUsername ?? "",
      name: null,
      avatar_url: null,
      is_active: true,
      is_system_admin: false,
      is_email_verified: false,
      last_login_at: null,
      created_at: "",
      updated_at: "",
    };
  }
  if (r.organizationName !== undefined || r.organizationSlug !== undefined) {
    out.organization = {
      id: orgId,
      name: r.organizationName ?? "",
      slug: r.organizationSlug ?? "",
      description: null,
      logo_url: null,
      created_at: "",
      updated_at: "",
    };
  }
  return out;
}
