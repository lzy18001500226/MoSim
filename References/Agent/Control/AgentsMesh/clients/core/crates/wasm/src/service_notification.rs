use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::NotificationService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmNotificationService {
    svc: NotificationService,
}

#[wasm_bindgen]
impl WasmNotificationService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self { svc: NotificationService::new(client) }
    }

    // -------- Connect-RPC (binary wire) --------

    #[wasm_bindgen(js_name = listPreferencesConnect)]
    pub async fn list_preferences_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.svc.list_preferences_connect(request).await
    }

    #[wasm_bindgen(js_name = setPreferenceConnect)]
    pub async fn set_preference_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.svc.set_preference_connect(request).await
    }
}
