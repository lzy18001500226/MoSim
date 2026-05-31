import { invoke } from "./invoke";
import type { IBillingService } from "@agentsmesh/service-interface";

export class ElectronBillingService implements IBillingService {
  async get_overview(): Promise<string> {
    return invoke<string>("billingGetOverview");
  }

  async get_subscription(): Promise<string> {
    return invoke<string>("billingGetSubscription");
  }

  async create_subscription(json: string): Promise<string> {
    return invoke<string>("billingCreateSubscription", json);
  }

  async update_subscription(json: string): Promise<string> {
    return invoke<string>("billingUpdateSubscription", json);
  }

  async cancel_subscription(): Promise<string> {
    return invoke<string>("billingCancelSubscription");
  }

  async reactivate(): Promise<string> {
    return invoke<string>("billingReactivate");
  }

  async request_cancel(json: string): Promise<string> {
    return invoke<string>("billingRequestCancel", json);
  }

  async upgrade(json: string): Promise<string> {
    return invoke<string>("billingUpgrade", json);
  }

  async change_cycle(json: string): Promise<string> {
    return invoke<string>("billingChangeCycle", json);
  }

  async check_quota(resource: string, amount?: number | null): Promise<string> {
    return invoke<string>("billingCheckQuota", resource, amount);
  }

  async create_checkout(json: string): Promise<string> {
    return invoke<string>("billingCreateCheckout", json);
  }

  async get_checkout_status(orderNo: string): Promise<string> {
    return invoke<string>("billingGetCheckoutStatus", orderNo);
  }

  async get_customer_portal(json: string): Promise<string> {
    return invoke<string>("billingGetCustomerPortal", json);
  }

  async get_deployment_info(): Promise<string> {
    return invoke<string>("billingGetDeploymentInfo");
  }

  async get_public_deployment_info(): Promise<string> {
    return invoke<string>("billingGetPublicDeploymentInfo");
  }

  async get_public_pricing(): Promise<string> {
    return invoke<string>("billingGetPublicPricing");
  }

  async get_seat_usage(): Promise<string> {
    return invoke<string>("billingGetSeatUsage");
  }

  async get_usage(usageType?: string | null): Promise<string> {
    return invoke<string>("billingGetUsage", usageType);
  }

  async list_invoices(limit?: number | null, offset?: number | null): Promise<string> {
    return invoke<string>("billingListInvoices", limit, offset);
  }

  async list_plans(): Promise<string> {
    return invoke<string>("billingListPlans");
  }

  async purchase_seats(json: string): Promise<string> {
    return invoke<string>("billingPurchaseSeats", json);
  }

  async update_auto_renew(json: string): Promise<string> {
    return invoke<string>("billingUpdateAutoRenew", json);
  }
}
