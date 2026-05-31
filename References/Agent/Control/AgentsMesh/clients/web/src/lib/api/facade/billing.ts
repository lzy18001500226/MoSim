// Legacy `billingApi` adapter. After the proto migration this thin wrapper
// delegates to billingConnect.ts (binary-wire Connect-RPC) so existing call
// sites keep working unchanged while the wire is now prost-encoded — PR #334
// fix preserved end-to-end.
//
// New call sites should import directly from `./billingConnect`; this module
// stays as the dual-track shim until every consumer flips.

import {
  changeBillingCycleConnect,
  createCheckoutConnect,
  createSubscriptionConnect,
  getCheckoutStatusConnect,
  getDeploymentInfoConnect,
  getOverviewConnect,
  getPublicPricingConnect,
  getSeatUsageConnect,
  listInvoicesConnect,
  listPlansConnect,
  purchaseSeatsConnect,
  reactivateSubscriptionConnect,
  requestCancelSubscriptionConnect,
  updateSubscriptionConnect,
  upgradeSubscriptionConnect,
  type CreateCheckoutInput,
} from "./billingConnect";

export type {
  SubscriptionPlan, PlanPrice, PlanWithPrice, UsageOverview, BillingOverview,
  Subscription, CheckoutRequest, CheckoutResponse, CheckoutStatus,
  SeatUsage, Invoice, DeploymentInfo, PublicPlanPricing, PublicPricingResponse,
  Currency, BillingCycle, OrderType, PaymentProvider,
} from "@/lib/viewModels/billing";

// Most legacy callers don't pass orgSlug — they let the wasm session carry
// it. With Connect every RPC needs the slug on the request body. We let
// callers continue to invoke without slug; tenant-aware components must now
// pass it through (see useBillingData migration). The default empty string
// is a deliberate ResolveOrgScope-fail at the boundary so the call surfaces
// the missing context instead of silently hitting the wrong org.
export const billingApi = {
  getOverview: async (orgSlug = "") => getOverviewConnect(orgSlug),
  listPlans: async (orgSlug = "") => ({ plans: await listPlansConnect(orgSlug) }),
  getDeploymentInfo: async (orgSlug = "") => getDeploymentInfoConnect(orgSlug),
  createSubscription: async (orgSlug: string, planName: string) =>
    createSubscriptionConnect(orgSlug, planName),
  updateSubscription: async (orgSlug: string, planName: string) =>
    updateSubscriptionConnect(orgSlug, planName),
  upgradeSubscription: async (orgSlug: string, planName: string) =>
    upgradeSubscriptionConnect(orgSlug, planName),
  reactivateSubscription: async (orgSlug: string) => reactivateSubscriptionConnect(orgSlug),
  requestCancelSubscription: async (orgSlug: string, immediate: boolean) =>
    requestCancelSubscriptionConnect(orgSlug, immediate),
  listInvoices: async (orgSlug: string, limit?: number, offset?: number) =>
    listInvoicesConnect(orgSlug, { limit, offset }),
  createCheckout: async (orgSlug: string, input: CreateCheckoutInput) =>
    createCheckoutConnect(orgSlug, input),
  getCheckoutStatus: async (orgSlug: string, orderNo: string) =>
    getCheckoutStatusConnect(orgSlug, orderNo),
  changeBillingCycle: async (orgSlug: string, cycle: "monthly" | "yearly") =>
    changeBillingCycleConnect(orgSlug, cycle),
  getSeatUsage: async (orgSlug: string) => getSeatUsageConnect(orgSlug),
  purchaseSeats: async (orgSlug: string, count: number) => purchaseSeatsConnect(orgSlug, count),
  getPublicPricing: async (currency?: string) => getPublicPricingConnect(currency),
};
