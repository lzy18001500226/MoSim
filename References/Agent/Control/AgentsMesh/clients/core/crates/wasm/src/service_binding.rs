use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmBindingService {
    client: Arc<ApiClient>,
}

impl WasmBindingService {
    /// Crate-local accessor used by service_binding_connect.rs to forward to
    /// the underlying api-client `*_connect` methods.
    pub(crate) fn client_ref(&self) -> &ApiClient {
        &self.client
    }
}

#[wasm_bindgen]
impl WasmBindingService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self { client }
    }
}
