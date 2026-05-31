use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::ApiKeyService;
use wasm_bindgen::prelude::*;

// TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
// Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
// Conventions §2.5 forbids JSON on the client wire.

#[wasm_bindgen]
pub struct WasmApiKeyService(pub(crate) ApiKeyService);

#[wasm_bindgen]
impl WasmApiKeyService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(ApiKeyService::new(client))
    }

    #[wasm_bindgen(js_name = listApiKeysConnect)]
    pub async fn list_api_keys_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_api_keys_connect(request).await
    }

    #[wasm_bindgen(js_name = getApiKeyConnect)]
    pub async fn get_api_key_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_api_key_connect(request).await
    }

    #[wasm_bindgen(js_name = createApiKeyConnect)]
    pub async fn create_api_key_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_api_key_connect(request).await
    }

    #[wasm_bindgen(js_name = updateApiKeyConnect)]
    pub async fn update_api_key_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_api_key_connect(request).await
    }

    #[wasm_bindgen(js_name = revokeApiKeyConnect)]
    pub async fn revoke_api_key_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.revoke_api_key_connect(request).await
    }

    #[wasm_bindgen(js_name = deleteApiKeyConnect)]
    pub async fn delete_api_key_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_api_key_connect(request).await
    }
}
