use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::SSOService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmSSOService(pub(crate) SSOService);

#[wasm_bindgen]
impl WasmSSOService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(SSOService::new(client))
    }

    // -------- Connect-RPC (binary wire) --------

    #[wasm_bindgen(js_name = discoverConnect)]
    pub async fn discover_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.discover_connect(request).await
    }

    #[wasm_bindgen(js_name = ldapAuthConnect)]
    pub async fn ldap_auth_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.ldap_auth_connect(request).await
    }
}
