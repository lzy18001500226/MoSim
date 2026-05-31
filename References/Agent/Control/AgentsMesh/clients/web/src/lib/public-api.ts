// Public (no-auth) API for marketing pages. Goes through Connect-RPC
// over plain fetch (NOT wasm) — see public-connect.ts for rationale.
//
// Underlying RPCs:
//   - proto.billing.v1.BillingPublicService.GetPublicPricing
//   - proto.billing.v1.BillingPublicService.GetPublicDeploymentInfo

import {
  GetPublicDeploymentInfoRequestSchema,
  GetPublicPricingRequestSchema,
  PublicPricingResponseSchema,
  DeploymentInfoSchema,
} from "@proto/billing/v1/billing_pb";

import type { PublicPricingResponse, DeploymentInfo, Currency } from "@/lib/viewModels/billing";
import { callPublicConnect } from "./public-connect";

const SERVICE = "proto.billing.v1.BillingPublicService";

export async function fetchPublicPricing(currency?: string): Promise<PublicPricingResponse> {
  const resp = await callPublicConnect(
    SERVICE,
    "GetPublicPricing",
    GetPublicPricingRequestSchema,
    PublicPricingResponseSchema,
    { currency },
  );
  return {
    deployment_type: resp.deploymentType,
    currency: resp.currency as Currency,
    plans: resp.plans.map((p) => ({
      name: p.name,
      display_name: p.displayName,
      price_monthly: p.priceMonthly,
      price_yearly: p.priceYearly,
      max_users: p.maxUsers,
      max_runners: p.maxRunners,
      max_repositories: p.maxRepositories,
      max_concurrent_pods: p.maxConcurrentPods,
    })),
  };
}

export async function fetchPublicDeploymentInfo(): Promise<DeploymentInfo> {
  const resp = await callPublicConnect(
    SERVICE,
    "GetPublicDeploymentInfo",
    GetPublicDeploymentInfoRequestSchema,
    DeploymentInfoSchema,
    {},
  );
  return {
    deployment_type: resp.deploymentType as DeploymentInfo["deployment_type"],
    available_providers: resp.availableProviders,
  };
}
