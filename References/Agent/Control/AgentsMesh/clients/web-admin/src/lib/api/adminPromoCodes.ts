// Connect-RPC adapter for the 8 procedures on
// proto.promocode.v1.PromoCodeAdminService. Migrated from REST
// `/api/v1/admin/promo-codes/*`.
//
// Public surface preserved (PromoCode, PromoCodeListParams,
// CreatePromoCodeRequest, UpdatePromoCodeRequest, PromoCodeRedemption,
// PaginatedResponse<PromoCode>) so consumer pages don't need touching.
// Proto carries bigint ids on the wire; the legacy REST shape uses number,
// so we downcast on the boundary (admin ids fit in JS number).
//
// expires_at semantics on Update: REST treated "" as "clear" and omitted
// field as "no change". The proto exposes that explicitly via
// `clear_expires_at` — see promocode_admin.proto for the rationale.
import {
  ActivatePromoCodeRequestSchema,
  ActivatePromoCodeResponseSchema,
  CreatePromoCodeRequestSchema,
  DeactivatePromoCodeRequestSchema,
  DeactivatePromoCodeResponseSchema,
  DeletePromoCodeRequestSchema,
  DeletePromoCodeResponseSchema,
  GetPromoCodeRequestSchema,
  ListPromoCodeRedemptionsRequestSchema,
  ListPromoCodeRedemptionsResponseSchema,
  ListPromoCodesRequestSchema,
  ListPromoCodesResponseSchema,
  PromoCodeSchema,
  UpdatePromoCodeRequestSchema,
} from "@proto/promocode/v1/promocode_admin_pb";

import { callConnect } from "@/lib/connect/transport";
import type { PaginatedResponse } from "./base";
import type {
  CreatePromoCodeRequest,
  PromoCode,
  PromoCodeListParams,
  PromoCodeRedemption,
  UpdatePromoCodeRequest,
} from "./adminTypes";
import { promoCodeFromProto, redemptionFromProto } from "./adminPromoCodesConvert";

const SERVICE = "proto.promocode.v1.PromoCodeAdminService";

export async function listPromoCodes(
  params?: PromoCodeListParams,
): Promise<PaginatedResponse<PromoCode>> {
  const resp = await callConnect(
    SERVICE,
    "ListPromoCodes",
    ListPromoCodesRequestSchema,
    ListPromoCodesResponseSchema,
    {
      type: params?.type,
      planName: params?.plan_name,
      isActive: params?.is_active,
      search: params?.search,
      page: params?.page,
      pageSize: params?.page_size,
    },
  );
  return {
    data: resp.data.map(promoCodeFromProto),
    total: Number(resp.total),
    page: resp.page,
    page_size: resp.pageSize,
    total_pages: resp.totalPages,
  };
}

export async function getPromoCode(id: number): Promise<PromoCode> {
  const resp = await callConnect(
    SERVICE,
    "GetPromoCode",
    GetPromoCodeRequestSchema,
    PromoCodeSchema,
    { id: BigInt(id) },
  );
  return promoCodeFromProto(resp);
}

export async function createPromoCode(data: CreatePromoCodeRequest): Promise<PromoCode> {
  const resp = await callConnect(
    SERVICE,
    "CreatePromoCode",
    CreatePromoCodeRequestSchema,
    PromoCodeSchema,
    {
      code: data.code,
      name: data.name,
      description: data.description ?? "",
      type: data.type,
      planName: data.plan_name,
      durationMonths: data.duration_months,
      maxUses: data.max_uses,
      maxUsesPerOrg: data.max_uses_per_org ?? 0,
      startsAt: data.starts_at,
      expiresAt: data.expires_at,
    },
  );
  return promoCodeFromProto(resp);
}

export async function updatePromoCode(
  id: number,
  data: UpdatePromoCodeRequest,
): Promise<PromoCode> {
  // REST treated `expires_at === ""` as the "clear" signal; the proto makes
  // that explicit so the wire can distinguish unset vs cleared without
  // relying on empty-string semantics.
  const clearExpiresAt = data.expires_at === "";
  const resp = await callConnect(
    SERVICE,
    "UpdatePromoCode",
    UpdatePromoCodeRequestSchema,
    PromoCodeSchema,
    {
      id: BigInt(id),
      name: data.name,
      description: data.description,
      maxUses: data.max_uses,
      maxUsesPerOrg: data.max_uses_per_org,
      expiresAt: clearExpiresAt ? undefined : data.expires_at,
      clearExpiresAt,
    },
  );
  return promoCodeFromProto(resp);
}

export async function activatePromoCode(id: number): Promise<{ message: string }> {
  const resp = await callConnect(
    SERVICE,
    "ActivatePromoCode",
    ActivatePromoCodeRequestSchema,
    ActivatePromoCodeResponseSchema,
    { id: BigInt(id) },
  );
  return { message: resp.message };
}

export async function deactivatePromoCode(id: number): Promise<{ message: string }> {
  const resp = await callConnect(
    SERVICE,
    "DeactivatePromoCode",
    DeactivatePromoCodeRequestSchema,
    DeactivatePromoCodeResponseSchema,
    { id: BigInt(id) },
  );
  return { message: resp.message };
}

export async function deletePromoCode(id: number): Promise<{ message: string }> {
  const resp = await callConnect(
    SERVICE,
    "DeletePromoCode",
    DeletePromoCodeRequestSchema,
    DeletePromoCodeResponseSchema,
    { id: BigInt(id) },
  );
  return { message: resp.message };
}

export async function listPromoCodeRedemptions(
  id: number,
  params?: { page?: number; page_size?: number },
): Promise<PaginatedResponse<PromoCodeRedemption>> {
  const resp = await callConnect(
    SERVICE,
    "ListPromoCodeRedemptions",
    ListPromoCodeRedemptionsRequestSchema,
    ListPromoCodeRedemptionsResponseSchema,
    {
      id: BigInt(id),
      page: params?.page,
      pageSize: params?.page_size,
    },
  );
  return {
    data: resp.data.map(redemptionFromProto),
    total: Number(resp.total),
    page: resp.page,
    page_size: resp.pageSize,
    total_pages: resp.totalPages,
  };
}
