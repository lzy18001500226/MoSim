// Connect-RPC adapter for proto.billing.v1.BillingService — core read +
// public pricing + shared wire converters.
//
// Subscription mutations live in `billingSubscriptionConnect.ts`; usage,
// invoices, checkout, and customer portal in `billingUsageConnect.ts`.
// The wire layer is hidden behind `facade/billingConnect.ts`.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out per conventions §2.5), decodes
// responses via .fromBinary(). No JSON intermediate.

import {
  BillingOverviewSchema,
  DeploymentInfoSchema,
  GetDeploymentInfoRequestSchema,
  GetOverviewRequestSchema,
  GetPublicDeploymentInfoRequestSchema,
  GetPublicPricingRequestSchema,
  GetSubscriptionRequestSchema,
  ListPlansRequestSchema,
  ListPlansResponseSchema,
  PublicPricingResponseSchema,
  SubscriptionSchema,
  type BillingOverview as ProtoBillingOverview,
  type CheckoutStatus as ProtoCheckoutStatus,
  type DeploymentInfo as ProtoDeploymentInfo,
  type Invoice as ProtoInvoice,
  type PublicPlanPricing as ProtoPublicPlanPricing,
  type PublicPricingResponse as ProtoPublicPricingResponse,
  type SeatUsage as ProtoSeatUsage,
  type Subscription as ProtoSubscription,
  type SubscriptionPlan as ProtoSubscriptionPlan,
} from "@proto/billing/v1/billing_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getBillingService } from "@/lib/wasm-core";
import type {
  BillingOverview,
  CheckoutStatus,
  Currency,
  DeploymentInfo,
  Invoice,
  PublicPlanPricing,
  PublicPricingResponse,
  SeatUsage,
  Subscription,
  SubscriptionPlan,
} from "@/lib/viewModels/billing";

// ============== Wire conversion (proto -> snake_case web shape) ==============
// Exported for cross-file use by billingSubscription/Usage Connect adapters.

export function fromProtoPlan(p: ProtoSubscriptionPlan): SubscriptionPlan {
  return {
    id: Number(p.id),
    name: p.name,
    display_name: p.displayName,
    price_per_seat_monthly: p.pricePerSeatMonthly,
    price_per_seat_yearly: p.pricePerSeatYearly,
    included_pod_minutes: p.includedPodMinutes,
    price_per_extra_minute: p.pricePerExtraMinute,
    max_users: p.maxUsers,
    max_runners: p.maxRunners,
    max_repositories: p.maxRepositories,
    max_concurrent_pods: p.maxConcurrentPods,
    features: {},
    is_active: p.isActive,
  };
}

export function fromProtoSubscription(s: ProtoSubscription): Subscription {
  return {
    id: Number(s.id),
    organization_id: Number(s.organizationId),
    plan_id: Number(s.planId),
    status: s.status,
    billing_cycle: s.billingCycle,
    current_period_start: s.currentPeriodStart,
    current_period_end: s.currentPeriodEnd,
    plan: s.plan ? fromProtoPlan(s.plan) : undefined,
    payment_provider: s.paymentProvider,
    payment_method: s.paymentMethod,
    auto_renew: s.autoRenew,
    cancel_at_period_end: s.cancelAtPeriodEnd,
    seat_count: s.seatCount,
    stripe_customer_id: s.stripeCustomerId,
    stripe_subscription_id: s.stripeSubscriptionId,
    lemonsqueezy_customer_id: s.lemonsqueezyCustomerId,
    lemonsqueezy_subscription_id: s.lemonsqueezySubscriptionId,
    frozen_at: s.frozenAt,
    downgrade_to_plan: s.downgradeToPlan,
    next_billing_cycle: s.nextBillingCycle,
  };
}

function fromProtoOverview(o: ProtoBillingOverview): BillingOverview {
  return {
    plan: o.plan ? fromProtoPlan(o.plan) : ({} as SubscriptionPlan),
    status: o.status,
    billing_cycle: o.billingCycle,
    current_period_start: o.currentPeriodStart,
    current_period_end: o.currentPeriodEnd,
    cancel_at_period_end: o.cancelAtPeriodEnd,
    usage: o.usage
      ? {
          pod_minutes: o.usage.podMinutes,
          included_pod_minutes: o.usage.includedPodMinutes,
          users: o.usage.users,
          max_users: o.usage.maxUsers,
          runners: o.usage.runners,
          max_runners: o.usage.maxRunners,
          repositories: o.usage.repositories,
          max_repositories: o.usage.maxRepositories,
        }
      : ({} as BillingOverview["usage"]),
  };
}

export function fromProtoSeatUsage(u: ProtoSeatUsage): SeatUsage {
  return {
    total_seats: u.totalSeats,
    used_seats: u.usedSeats,
    available_seats: u.availableSeats,
    max_seats: u.maxSeats,
    can_add_seats: u.canAddSeats,
  };
}

export function fromProtoDeployment(d: ProtoDeploymentInfo): DeploymentInfo {
  return {
    deployment_type: (d.deploymentType || "global") as DeploymentInfo["deployment_type"],
    available_providers: d.availableProviders,
  };
}

export function fromProtoInvoice(i: ProtoInvoice): Invoice {
  return {
    id: Number(i.id),
    organization_id: Number(i.organizationId),
    invoice_no: i.invoiceNo,
    order_no: undefined,
    amount: i.subtotal,
    tax_amount: i.taxAmount,
    total_amount: i.total,
    currency: i.currency,
    status: i.status,
    billing_period_start: i.periodStart,
    billing_period_end: i.periodEnd,
    paid_at: i.paidAt,
    created_at: i.createdAt,
  };
}

export function fromProtoCheckoutStatus(c: ProtoCheckoutStatus): CheckoutStatus {
  return {
    order_no: c.orderNo,
    status: c.status,
    order_type: c.orderType,
    amount: c.amount,
    currency: c.currency,
    created_at: c.createdAt,
    paid_at: c.paidAt,
  };
}

function fromProtoPublicPlan(p: ProtoPublicPlanPricing): PublicPlanPricing {
  return {
    name: p.name,
    display_name: p.displayName,
    price_monthly: p.priceMonthly,
    price_yearly: p.priceYearly,
    max_users: p.maxUsers,
    max_runners: p.maxRunners,
    max_repositories: p.maxRepositories,
    max_concurrent_pods: p.maxConcurrentPods,
  };
}

function fromProtoPublicPricing(r: ProtoPublicPricingResponse): PublicPricingResponse {
  return {
    deployment_type: r.deploymentType,
    currency: (r.currency || "USD") as Currency,
    plans: r.plans.map(fromProtoPublicPlan),
  };
}

// ============== Core reads ==============

export async function getOverviewConnect(orgSlug: string): Promise<BillingOverview> {
  const req = create(GetOverviewRequestSchema, { orgSlug });
  const bytes = toBinary(GetOverviewRequestSchema, req);
  const respBytes = await getBillingService().get_overview_connect(bytes);
  return fromProtoOverview(fromBinary(BillingOverviewSchema, new Uint8Array(respBytes)));
}

export async function listPlansConnect(orgSlug: string): Promise<SubscriptionPlan[]> {
  const req = create(ListPlansRequestSchema, { orgSlug });
  const bytes = toBinary(ListPlansRequestSchema, req);
  const respBytes = await getBillingService().list_plans_connect(bytes);
  const resp = fromBinary(ListPlansResponseSchema, new Uint8Array(respBytes));
  return resp.items.map(fromProtoPlan);
}

export async function getSubscriptionConnect(orgSlug: string): Promise<Subscription> {
  const req = create(GetSubscriptionRequestSchema, { orgSlug });
  const bytes = toBinary(GetSubscriptionRequestSchema, req);
  const respBytes = await getBillingService().get_subscription_connect(bytes);
  return fromProtoSubscription(fromBinary(SubscriptionSchema, new Uint8Array(respBytes)));
}

export async function getDeploymentInfoConnect(orgSlug: string): Promise<DeploymentInfo> {
  const req = create(GetDeploymentInfoRequestSchema, { orgSlug });
  const bytes = toBinary(GetDeploymentInfoRequestSchema, req);
  const respBytes = await getBillingService().get_deployment_info_connect(bytes);
  return fromProtoDeployment(fromBinary(DeploymentInfoSchema, new Uint8Array(respBytes)));
}

// ============== BillingPublicService — no org_slug, no auth ==============

export async function getPublicPricingConnect(currency?: string): Promise<PublicPricingResponse> {
  const req = create(GetPublicPricingRequestSchema, { currency });
  const bytes = toBinary(GetPublicPricingRequestSchema, req);
  const respBytes = await getBillingService().get_public_pricing_connect(bytes);
  return fromProtoPublicPricing(fromBinary(PublicPricingResponseSchema, new Uint8Array(respBytes)));
}

export async function getPublicDeploymentInfoConnect(): Promise<DeploymentInfo> {
  const req = create(GetPublicDeploymentInfoRequestSchema, {});
  const bytes = toBinary(GetPublicDeploymentInfoRequestSchema, req);
  const respBytes = await getBillingService().get_public_deployment_info_connect(bytes);
  return fromProtoDeployment(fromBinary(DeploymentInfoSchema, new Uint8Array(respBytes)));
}
