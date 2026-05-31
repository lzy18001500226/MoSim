use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::GrantService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmGrantService(pub(crate) GrantService);

#[wasm_bindgen]
impl WasmGrantService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(GrantService::new(client))
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
    // Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
    // No JSON intermediate; conventions §2.5 forbids it on the client.

    #[wasm_bindgen(js_name = listGrantsConnect)]
    pub async fn list_grants_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_grants_connect(request).await
    }

    #[wasm_bindgen(js_name = createGrantConnect)]
    pub async fn create_grant_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_grant_connect(request).await
    }

    #[wasm_bindgen(js_name = deleteGrantConnect)]
    pub async fn delete_grant_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_grant_connect(request).await
    }
}
