use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::EnvBundleService;
use wasm_bindgen::prelude::*;

/// Wasm wrapper around EnvBundleService. Connect-RPC binary wire — the TS
/// caller encodes via `@bufbuild/protobuf .toBinary()`, passes the
/// Uint8Array in, receives a Uint8Array back, decodes via `.fromBinary()`.
#[wasm_bindgen]
pub struct WasmEnvBundleService {
    inner: EnvBundleService,
}

#[wasm_bindgen]
impl WasmEnvBundleService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self { inner: EnvBundleService::new(client) }
    }

    #[wasm_bindgen(js_name = listEnvBundlesConnect)]
    pub async fn list_env_bundles_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.list_env_bundles_connect(request).await
    }

    #[wasm_bindgen(js_name = getEnvBundleConnect)]
    pub async fn get_env_bundle_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.get_env_bundle_connect(request).await
    }

    #[wasm_bindgen(js_name = createEnvBundleConnect)]
    pub async fn create_env_bundle_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.create_env_bundle_connect(request).await
    }

    #[wasm_bindgen(js_name = updateEnvBundleConnect)]
    pub async fn update_env_bundle_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.update_env_bundle_connect(request).await
    }

    #[wasm_bindgen(js_name = deleteEnvBundleConnect)]
    pub async fn delete_env_bundle_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.delete_env_bundle_connect(request).await
    }

    #[wasm_bindgen(js_name = setPrimaryEnvBundleConnect)]
    pub async fn set_primary_env_bundle_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.inner.set_primary_env_bundle_connect(request).await
    }
}
