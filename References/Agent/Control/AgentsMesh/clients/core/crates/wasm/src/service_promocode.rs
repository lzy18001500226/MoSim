use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::PromoCodeService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmPromoCodeService {
    inner: PromoCodeService,
}

#[wasm_bindgen]
impl WasmPromoCodeService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self { inner: PromoCodeService::new(client) }
    }

    // -------- Connect-RPC (binary wire) --------

    #[wasm_bindgen(js_name = validatePromoCodeConnect)]
    pub async fn validate_promo_code_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.validate_promo_code_connect(request).await
    }

    #[wasm_bindgen(js_name = redeemPromoCodeConnect)]
    pub async fn redeem_promo_code_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.redeem_promo_code_connect(request).await
    }

    #[wasm_bindgen(js_name = getRedemptionHistoryConnect)]
    pub async fn get_redemption_history_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.get_redemption_history_connect(request).await
    }
}
