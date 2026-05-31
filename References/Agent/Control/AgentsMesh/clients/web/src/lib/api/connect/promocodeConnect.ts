// Connect-RPC adapter for proto.promocode.v1.PromoCodeService.
//
// Wire layer is proto-SSOT: returns and consumes `@proto/promocode/v1` types
// directly. No adapter DTO layer.

import {
  GetRedemptionHistoryRequestSchema,
  GetRedemptionHistoryResponseSchema,
  RedeemPromoCodeRequestSchema,
  RedeemPromoCodeResponseSchema,
  ValidatePromoCodeRequestSchema,
  ValidatePromoCodeResponseSchema,
  type Redemption,
  type RedeemPromoCodeResponse,
  type ValidatePromoCodeResponse,
} from "@proto/promocode/v1/promocode_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getPromoCodeService } from "@/lib/wasm-core";

export type {
  Redemption as PromoCodeRedemption,
  RedeemPromoCodeResponse,
  ValidatePromoCodeResponse,
} from "@proto/promocode/v1/promocode_pb";

export type PromoCodeType = "media" | "partner" | "campaign" | "internal" | "referral";

export async function validatePromoCode(
  orgSlug: string,
  code: string,
): Promise<ValidatePromoCodeResponse> {
  const req = create(ValidatePromoCodeRequestSchema, { orgSlug, code });
  const bytes = toBinary(ValidatePromoCodeRequestSchema, req);
  const respBytes = await getPromoCodeService().validatePromoCodeConnect(bytes);
  return fromBinary(ValidatePromoCodeResponseSchema, new Uint8Array(respBytes));
}

export async function redeemPromoCode(
  orgSlug: string,
  code: string,
): Promise<RedeemPromoCodeResponse> {
  const req = create(RedeemPromoCodeRequestSchema, { orgSlug, code });
  const bytes = toBinary(RedeemPromoCodeRequestSchema, req);
  const respBytes = await getPromoCodeService().redeemPromoCodeConnect(bytes);
  return fromBinary(RedeemPromoCodeResponseSchema, new Uint8Array(respBytes));
}

export async function getRedemptionHistory(
  orgSlug: string,
  opts: { offset?: number; limit?: number } = {},
): Promise<{
  items: Redemption[];
  total: number;
  limit: number;
  offset: number;
}> {
  const req = create(GetRedemptionHistoryRequestSchema, {
    orgSlug,
    offset: opts.offset,
    limit: opts.limit,
  });
  const bytes = toBinary(GetRedemptionHistoryRequestSchema, req);
  const respBytes = await getPromoCodeService().getRedemptionHistoryConnect(bytes);
  const resp = fromBinary(GetRedemptionHistoryResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items,
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}
