// Usage / quota / invoices / checkout / customer portal for
// proto.billing.v1.BillingService. Split from billingConnect.ts for SRP.

import {
  CheckoutStatusSchema,
  CheckQuotaRequestSchema,
  CheckQuotaResponseSchema,
  CreateCheckoutRequestSchema,
  CreateCheckoutResponseSchema,
  CreateCustomerPortalRequestSchema,
  CreateCustomerPortalResponseSchema,
  GetCheckoutStatusRequestSchema,
  GetUsageHistoryRequestSchema,
  GetUsageHistoryResponseSchema,
  GetUsageRequestSchema,
  GetUsageResponseSchema,
  ListInvoicesRequestSchema,
  ListInvoicesResponseSchema,
  SetCustomQuotaRequestSchema,
  SetCustomQuotaResponseSchema,
} from "@proto/billing/v1/billing_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getBillingService } from "@/lib/wasm-core";
import { fromProtoCheckoutStatus, fromProtoInvoice } from "./billingConnect";
import type {
  BillingCycle,
  CheckoutResponse,
  CheckoutStatus,
  CustomerPortalResponse,
  Invoice,
  OrderType,
  PaymentProvider,
  UsageQueryResponse,
  UsageRecord,
} from "@/lib/viewModels/billing";

// ============== Invoices ==============

export async function listInvoicesConnect(
  orgSlug: string,
  opts: { limit?: number; offset?: number } = {},
): Promise<{ items: Invoice[]; total: number; limit: number; offset: number }> {
  const req = create(ListInvoicesRequestSchema, {
    orgSlug,
    limit: opts.limit,
    offset: opts.offset,
  });
  const bytes = toBinary(ListInvoicesRequestSchema, req);
  const respBytes = await getBillingService().list_invoices_connect(bytes);
  const resp = fromBinary(ListInvoicesResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProtoInvoice),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

// ============== Checkout ==============

export interface CreateCheckoutInput {
  order_type: OrderType;
  plan_name?: string;
  billing_cycle?: BillingCycle;
  seats?: number;
  provider?: PaymentProvider;
  success_url: string;
  cancel_url: string;
}

export async function createCheckoutConnect(
  orgSlug: string,
  input: CreateCheckoutInput,
): Promise<CheckoutResponse> {
  const req = create(CreateCheckoutRequestSchema, {
    orgSlug,
    orderType: input.order_type,
    planName: input.plan_name,
    billingCycle: input.billing_cycle,
    seats: input.seats,
    provider: input.provider,
    successUrl: input.success_url,
    cancelUrl: input.cancel_url,
  });
  const bytes = toBinary(CreateCheckoutRequestSchema, req);
  const respBytes = await getBillingService().create_checkout_connect(bytes);
  const resp = fromBinary(CreateCheckoutResponseSchema, new Uint8Array(respBytes));
  return {
    order_no: resp.orderNo,
    session_id: resp.sessionId,
    session_url: resp.sessionUrl,
    qr_code_url: resp.qrCodeUrl,
    expires_at: resp.expiresAt,
    provider: (resp.provider || undefined) as PaymentProvider | undefined,
  };
}

export async function getCheckoutStatusConnect(
  orgSlug: string,
  orderNo: string,
): Promise<CheckoutStatus> {
  const req = create(GetCheckoutStatusRequestSchema, { orgSlug, orderNo });
  const bytes = toBinary(GetCheckoutStatusRequestSchema, req);
  const respBytes = await getBillingService().get_checkout_status_connect(bytes);
  return fromProtoCheckoutStatus(fromBinary(CheckoutStatusSchema, new Uint8Array(respBytes)));
}

// ============== Usage / quota ==============

export async function getUsageConnect(
  orgSlug: string,
  usageType?: string,
): Promise<UsageQueryResponse> {
  const req = create(GetUsageRequestSchema, {
    orgSlug,
    usageType: usageType ?? undefined,
  });
  const bytes = toBinary(GetUsageRequestSchema, req);
  const respBytes = await getBillingService().get_usage_connect(bytes);
  const resp = fromBinary(GetUsageResponseSchema, new Uint8Array(respBytes));
  const out: UsageQueryResponse = {};
  if (resp.metricValue !== undefined) {
    out.metric_value = resp.metricValue;
  }
  if (resp.metricType !== undefined) {
    out.metric_type = resp.metricType;
  }
  if (resp.overview) {
    out.overview = {
      pod_minutes: resp.overview.podMinutes,
      included_pod_minutes: resp.overview.includedPodMinutes,
      users: resp.overview.users,
      max_users: resp.overview.maxUsers,
      runners: resp.overview.runners,
      max_runners: resp.overview.maxRunners,
      repositories: resp.overview.repositories,
      max_repositories: resp.overview.maxRepositories,
    };
  }
  return out;
}

export async function getUsageHistoryConnect(
  orgSlug: string,
  opts: { usageType?: string; months?: number } = {},
): Promise<{ records: UsageRecord[] }> {
  const req = create(GetUsageHistoryRequestSchema, {
    orgSlug,
    usageType: opts.usageType ?? undefined,
    months: opts.months ?? 3,
  });
  const bytes = toBinary(GetUsageHistoryRequestSchema, req);
  const respBytes = await getBillingService().get_usage_history_connect(bytes);
  const resp = fromBinary(GetUsageHistoryResponseSchema, new Uint8Array(respBytes));
  return {
    records: resp.records.map((r) => ({
      id: Number(r.id),
      organization_id: Number(r.organizationId),
      usage_type: r.usageType,
      quantity: r.quantity,
      period_start: r.periodStart,
      period_end: r.periodEnd,
      created_at: r.createdAt,
    })),
  };
}

export async function checkQuotaConnect(
  orgSlug: string,
  resource: string,
  amount = 1,
): Promise<{ available: boolean }> {
  const req = create(CheckQuotaRequestSchema, { orgSlug, resource, amount });
  const bytes = toBinary(CheckQuotaRequestSchema, req);
  const respBytes = await getBillingService().check_quota_connect(bytes);
  const resp = fromBinary(CheckQuotaResponseSchema, new Uint8Array(respBytes));
  return { available: resp.available };
}

export async function setCustomQuotaConnect(
  orgSlug: string,
  resource: string,
  limit: number,
): Promise<{ message: string }> {
  const req = create(SetCustomQuotaRequestSchema, { orgSlug, resource, limit });
  const bytes = toBinary(SetCustomQuotaRequestSchema, req);
  const respBytes = await getBillingService().set_custom_quota_connect(bytes);
  const resp = fromBinary(SetCustomQuotaResponseSchema, new Uint8Array(respBytes));
  return { message: resp.message };
}

// ============== Customer portal ==============

export async function createCustomerPortalConnect(
  orgSlug: string,
  returnUrl: string,
): Promise<CustomerPortalResponse> {
  const req = create(CreateCustomerPortalRequestSchema, { orgSlug, returnUrl });
  const bytes = toBinary(CreateCustomerPortalRequestSchema, req);
  const respBytes = await getBillingService().create_customer_portal_connect(bytes);
  const resp = fromBinary(CreateCustomerPortalResponseSchema, new Uint8Array(respBytes));
  return { url: resp.url };
}
