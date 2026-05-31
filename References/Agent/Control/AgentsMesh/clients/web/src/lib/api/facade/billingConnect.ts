// Facade re-export of the billing Connect-RPC adapter. Business code imports
// from here (or from the `@/lib/api` barrel) so the wire-shape layer stays
// internal to the facade boundary. Tests mock this path.
//
// The wire layer was split into 3 SRP-aligned files (core reads + public /
// subscription mutations / usage+checkout+portal) — this facade unifies them.

export {
  getOverviewConnect,
  listPlansConnect,
  getSubscriptionConnect,
  getDeploymentInfoConnect,
  getPublicPricingConnect,
  getPublicDeploymentInfoConnect,
} from "../connect/billingConnect";

export {
  createSubscriptionConnect,
  updateSubscriptionConnect,
  cancelSubscriptionConnect,
  requestCancelSubscriptionConnect,
  reactivateSubscriptionConnect,
  upgradeSubscriptionConnect,
  changeBillingCycleConnect,
  updateAutoRenewConnect,
  getSeatUsageConnect,
  purchaseSeatsConnect,
} from "../connect/billingSubscriptionConnect";

export {
  listInvoicesConnect,
  createCheckoutConnect,
  getCheckoutStatusConnect,
  getUsageConnect,
  getUsageHistoryConnect,
  checkQuotaConnect,
  setCustomQuotaConnect,
  createCustomerPortalConnect,
  type CreateCheckoutInput,
} from "../connect/billingUsageConnect";
