use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_billing_v1 as billing_proto;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// These methods call the Connect handlers in backend/internal/api/connect/billing/.
// Procedure paths derive from `proto.billing.v1.BillingService.<Method>` (§12).
//
// Public service (BillingPublicService) methods live below the authenticated
// block — same procedure-path convention, but the handler bypasses
// ResolveOrgScope per conventions §3.5 (landing-page pricing card).

impl ApiClient {
    pub async fn get_billing_overview_connect(
        &self,
        req: &billing_proto::GetOverviewRequest,
    ) -> Result<billing_proto::BillingOverview, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/GetOverview", req).await
    }

    pub async fn list_billing_plans_connect(
        &self,
        req: &billing_proto::ListPlansRequest,
    ) -> Result<billing_proto::ListPlansResponse, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/ListPlans", req).await
    }

    pub async fn get_billing_subscription_connect(
        &self,
        req: &billing_proto::GetSubscriptionRequest,
    ) -> Result<billing_proto::Subscription, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/GetSubscription", req).await
    }

    pub async fn create_billing_subscription_connect(
        &self,
        req: &billing_proto::CreateSubscriptionRequest,
    ) -> Result<billing_proto::Subscription, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/CreateSubscription", req).await
    }

    pub async fn update_billing_subscription_connect(
        &self,
        req: &billing_proto::UpdateSubscriptionRequest,
    ) -> Result<billing_proto::Subscription, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/UpdateSubscription", req).await
    }

    pub async fn cancel_billing_subscription_connect(
        &self,
        req: &billing_proto::CancelSubscriptionRequest,
    ) -> Result<billing_proto::CancelSubscriptionResponse, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/CancelSubscription", req).await
    }

    pub async fn request_cancel_subscription_connect(
        &self,
        req: &billing_proto::RequestCancelSubscriptionRequest,
    ) -> Result<billing_proto::RequestCancelSubscriptionResponse, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/RequestCancelSubscription",
            req,
        )
        .await
    }

    pub async fn reactivate_subscription_connect(
        &self,
        req: &billing_proto::ReactivateSubscriptionRequest,
    ) -> Result<billing_proto::Subscription, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/ReactivateSubscription",
            req,
        )
        .await
    }

    pub async fn upgrade_subscription_connect(
        &self,
        req: &billing_proto::UpgradeSubscriptionRequest,
    ) -> Result<billing_proto::Subscription, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/UpgradeSubscription",
            req,
        )
        .await
    }

    pub async fn change_billing_cycle_connect(
        &self,
        req: &billing_proto::ChangeBillingCycleRequest,
    ) -> Result<billing_proto::ChangeBillingCycleResponse, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/ChangeBillingCycle",
            req,
        )
        .await
    }

    pub async fn update_auto_renew_connect(
        &self,
        req: &billing_proto::UpdateAutoRenewRequest,
    ) -> Result<billing_proto::Subscription, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/UpdateAutoRenew", req).await
    }

    pub async fn get_seat_usage_connect(
        &self,
        req: &billing_proto::GetSeatUsageRequest,
    ) -> Result<billing_proto::SeatUsage, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/GetSeatUsage", req).await
    }

    pub async fn purchase_seats_connect(
        &self,
        req: &billing_proto::PurchaseSeatsRequest,
    ) -> Result<billing_proto::PurchaseSeatsResponse, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/PurchaseSeats", req).await
    }

    pub async fn list_billing_invoices_connect(
        &self,
        req: &billing_proto::ListInvoicesRequest,
    ) -> Result<billing_proto::ListInvoicesResponse, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/ListInvoices", req).await
    }

    pub async fn create_billing_checkout_connect(
        &self,
        req: &billing_proto::CreateCheckoutRequest,
    ) -> Result<billing_proto::CreateCheckoutResponse, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/CreateCheckout", req).await
    }

    pub async fn get_billing_checkout_status_connect(
        &self,
        req: &billing_proto::GetCheckoutStatusRequest,
    ) -> Result<billing_proto::CheckoutStatus, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/GetCheckoutStatus",
            req,
        )
        .await
    }

    pub async fn get_billing_deployment_info_connect(
        &self,
        req: &billing_proto::GetDeploymentInfoRequest,
    ) -> Result<billing_proto::DeploymentInfo, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/GetDeploymentInfo",
            req,
        )
        .await
    }

    // BillingPublicService — no org_slug, no auth interceptor on the backend
    // (conventions §3.5 exception). Same wire format; just a different
    // service stem.

    pub async fn get_public_pricing_connect(
        &self,
        req: &billing_proto::GetPublicPricingRequest,
    ) -> Result<billing_proto::PublicPricingResponse, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingPublicService/GetPublicPricing",
            req,
        )
        .await
    }

    pub async fn get_public_deployment_info_connect(
        &self,
        req: &billing_proto::GetPublicDeploymentInfoRequest,
    ) -> Result<billing_proto::DeploymentInfo, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingPublicService/GetPublicDeploymentInfo",
            req,
        )
        .await
    }

    // -------- Usage / quota / customer portal — REST refugees --------

    pub async fn get_usage_connect(
        &self,
        req: &billing_proto::GetUsageRequest,
    ) -> Result<billing_proto::GetUsageResponse, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/GetUsage", req).await
    }

    pub async fn get_usage_history_connect(
        &self,
        req: &billing_proto::GetUsageHistoryRequest,
    ) -> Result<billing_proto::GetUsageHistoryResponse, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/GetUsageHistory",
            req,
        )
        .await
    }

    pub async fn check_quota_connect(
        &self,
        req: &billing_proto::CheckQuotaRequest,
    ) -> Result<billing_proto::CheckQuotaResponse, ApiError> {
        connect_call(self, "/proto.billing.v1.BillingService/CheckQuota", req).await
    }

    pub async fn set_custom_quota_connect(
        &self,
        req: &billing_proto::SetCustomQuotaRequest,
    ) -> Result<billing_proto::SetCustomQuotaResponse, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/SetCustomQuota",
            req,
        )
        .await
    }

    pub async fn create_customer_portal_connect(
        &self,
        req: &billing_proto::CreateCustomerPortalRequest,
    ) -> Result<billing_proto::CreateCustomerPortalResponse, ApiError> {
        connect_call(
            self,
            "/proto.billing.v1.BillingService/CreateCustomerPortal",
            req,
        )
        .await
    }
}
