use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmBillingService {
    client: Arc<ApiClient>,
}

#[wasm_bindgen]
impl WasmBillingService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self { client }
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // Each `*_connect` method takes prost-encoded bytes (Uint8Array on the JS
    // side) and returns prost-encoded bytes — TS callers encode via
    // @bufbuild/protobuf .toBinary() and decode via .fromBinary().


    pub async fn get_overview_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_overview_connect(request_bytes)
            .await
    }

    pub async fn list_plans_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .list_plans_connect(request_bytes)
            .await
    }

    pub async fn get_subscription_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_subscription_connect(request_bytes)
            .await
    }

    pub async fn create_subscription_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .create_subscription_connect(request_bytes)
            .await
    }

    pub async fn update_subscription_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .update_subscription_connect(request_bytes)
            .await
    }

    pub async fn cancel_subscription_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .cancel_subscription_connect(request_bytes)
            .await
    }

    pub async fn request_cancel_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .request_cancel_connect(request_bytes)
            .await
    }

    pub async fn reactivate_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .reactivate_connect(request_bytes)
            .await
    }

    pub async fn upgrade_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .upgrade_connect(request_bytes)
            .await
    }

    pub async fn change_cycle_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .change_cycle_connect(request_bytes)
            .await
    }

    pub async fn update_auto_renew_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .update_auto_renew_connect(request_bytes)
            .await
    }

    pub async fn get_seat_usage_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_seat_usage_connect(request_bytes)
            .await
    }

    pub async fn purchase_seats_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .purchase_seats_connect(request_bytes)
            .await
    }

    pub async fn list_invoices_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .list_invoices_connect(request_bytes)
            .await
    }

    pub async fn create_checkout_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .create_checkout_connect(request_bytes)
            .await
    }

    pub async fn get_checkout_status_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_checkout_status_connect(request_bytes)
            .await
    }

    pub async fn get_deployment_info_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_deployment_info_connect(request_bytes)
            .await
    }

    pub async fn get_public_pricing_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_public_pricing_connect(request_bytes)
            .await
    }

    pub async fn get_public_deployment_info_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_public_deployment_info_connect(request_bytes)
            .await
    }

    // -------- Usage / quota / customer portal — REST refugees --------

    #[wasm_bindgen(js_name = getUsageConnect)]
    pub async fn get_usage_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_usage_connect(request_bytes)
            .await
    }

    #[wasm_bindgen(js_name = getUsageHistoryConnect)]
    pub async fn get_usage_history_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .get_usage_history_connect(request_bytes)
            .await
    }

    #[wasm_bindgen(js_name = checkQuotaConnect)]
    pub async fn check_quota_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .check_quota_connect(request_bytes)
            .await
    }

    #[wasm_bindgen(js_name = setCustomQuotaConnect)]
    pub async fn set_custom_quota_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .set_custom_quota_connect(request_bytes)
            .await
    }

    #[wasm_bindgen(js_name = createCustomerPortalConnect)]
    pub async fn create_customer_portal_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        agentsmesh_services::BillingService::new(self.client.clone())
            .create_customer_portal_connect(request_bytes)
            .await
    }
}
