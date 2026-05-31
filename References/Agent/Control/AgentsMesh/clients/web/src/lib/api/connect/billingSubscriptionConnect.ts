// Subscription lifecycle mutations for proto.billing.v1.BillingService.
// Split from billingConnect.ts for SRP.

import {
  CancelSubscriptionRequestSchema,
  CancelSubscriptionResponseSchema,
  ChangeBillingCycleRequestSchema,
  ChangeBillingCycleResponseSchema,
  CreateSubscriptionRequestSchema,
  GetSeatUsageRequestSchema,
  PurchaseSeatsRequestSchema,
  PurchaseSeatsResponseSchema,
  ReactivateSubscriptionRequestSchema,
  RequestCancelSubscriptionRequestSchema,
  RequestCancelSubscriptionResponseSchema,
  SeatUsageSchema,
  SubscriptionSchema,
  UpdateAutoRenewRequestSchema,
  UpdateSubscriptionRequestSchema,
  UpgradeSubscriptionRequestSchema,
} from "@proto/billing/v1/billing_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getBillingService } from "@/lib/wasm-core";
import { fromProtoSeatUsage, fromProtoSubscription } from "./billingConnect";
import type { BillingCycle, SeatUsage, Subscription } from "@/lib/viewModels/billing";

export async function createSubscriptionConnect(
  orgSlug: string,
  planName: string,
  billingCycle?: BillingCycle,
): Promise<Subscription> {
  const req = create(CreateSubscriptionRequestSchema, { orgSlug, planName, billingCycle });
  const bytes = toBinary(CreateSubscriptionRequestSchema, req);
  const respBytes = await getBillingService().create_subscription_connect(bytes);
  return fromProtoSubscription(fromBinary(SubscriptionSchema, new Uint8Array(respBytes)));
}

export async function updateSubscriptionConnect(
  orgSlug: string,
  planName: string,
): Promise<Subscription> {
  const req = create(UpdateSubscriptionRequestSchema, { orgSlug, planName });
  const bytes = toBinary(UpdateSubscriptionRequestSchema, req);
  const respBytes = await getBillingService().update_subscription_connect(bytes);
  return fromProtoSubscription(fromBinary(SubscriptionSchema, new Uint8Array(respBytes)));
}

export async function cancelSubscriptionConnect(orgSlug: string): Promise<void> {
  const req = create(CancelSubscriptionRequestSchema, { orgSlug });
  const bytes = toBinary(CancelSubscriptionRequestSchema, req);
  const respBytes = await getBillingService().cancel_subscription_connect(bytes);
  fromBinary(CancelSubscriptionResponseSchema, new Uint8Array(respBytes));
}

export async function requestCancelSubscriptionConnect(
  orgSlug: string,
  immediate: boolean,
): Promise<{ immediate: boolean; current_period_end?: string }> {
  const req = create(RequestCancelSubscriptionRequestSchema, { orgSlug, immediate });
  const bytes = toBinary(RequestCancelSubscriptionRequestSchema, req);
  const respBytes = await getBillingService().request_cancel_connect(bytes);
  const resp = fromBinary(RequestCancelSubscriptionResponseSchema, new Uint8Array(respBytes));
  return { immediate: resp.immediate, current_period_end: resp.currentPeriodEnd };
}

export async function reactivateSubscriptionConnect(orgSlug: string): Promise<Subscription> {
  const req = create(ReactivateSubscriptionRequestSchema, { orgSlug });
  const bytes = toBinary(ReactivateSubscriptionRequestSchema, req);
  const respBytes = await getBillingService().reactivate_connect(bytes);
  return fromProtoSubscription(fromBinary(SubscriptionSchema, new Uint8Array(respBytes)));
}

export async function upgradeSubscriptionConnect(
  orgSlug: string,
  planName: string,
): Promise<Subscription> {
  const req = create(UpgradeSubscriptionRequestSchema, { orgSlug, planName });
  const bytes = toBinary(UpgradeSubscriptionRequestSchema, req);
  const respBytes = await getBillingService().upgrade_connect(bytes);
  return fromProtoSubscription(fromBinary(SubscriptionSchema, new Uint8Array(respBytes)));
}

export async function changeBillingCycleConnect(
  orgSlug: string,
  billingCycle: BillingCycle,
): Promise<{ current_cycle: string; next_cycle: string; effective_date: string }> {
  const req = create(ChangeBillingCycleRequestSchema, { orgSlug, billingCycle });
  const bytes = toBinary(ChangeBillingCycleRequestSchema, req);
  const respBytes = await getBillingService().change_cycle_connect(bytes);
  const resp = fromBinary(ChangeBillingCycleResponseSchema, new Uint8Array(respBytes));
  return {
    current_cycle: resp.currentCycle,
    next_cycle: resp.nextCycle,
    effective_date: resp.effectiveDate,
  };
}

export async function updateAutoRenewConnect(
  orgSlug: string,
  autoRenew: boolean,
): Promise<Subscription> {
  const req = create(UpdateAutoRenewRequestSchema, { orgSlug, autoRenew });
  const bytes = toBinary(UpdateAutoRenewRequestSchema, req);
  const respBytes = await getBillingService().update_auto_renew_connect(bytes);
  return fromProtoSubscription(fromBinary(SubscriptionSchema, new Uint8Array(respBytes)));
}

export async function getSeatUsageConnect(orgSlug: string): Promise<SeatUsage> {
  const req = create(GetSeatUsageRequestSchema, { orgSlug });
  const bytes = toBinary(GetSeatUsageRequestSchema, req);
  const respBytes = await getBillingService().get_seat_usage_connect(bytes);
  return fromProtoSeatUsage(fromBinary(SeatUsageSchema, new Uint8Array(respBytes)));
}

export async function purchaseSeatsConnect(
  orgSlug: string,
  seats: number,
): Promise<SeatUsage | undefined> {
  const req = create(PurchaseSeatsRequestSchema, { orgSlug, seats });
  const bytes = toBinary(PurchaseSeatsRequestSchema, req);
  const respBytes = await getBillingService().purchase_seats_connect(bytes);
  const resp = fromBinary(PurchaseSeatsResponseSchema, new Uint8Array(respBytes));
  return resp.seats ? fromProtoSeatUsage(resp.seats) : undefined;
}
