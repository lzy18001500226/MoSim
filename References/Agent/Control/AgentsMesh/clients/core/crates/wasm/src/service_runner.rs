use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::RunnerService;
use agentsmesh_state::runner_state::RunnerState;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmRunnerService(pub(crate) RunnerService);

#[wasm_bindgen]
impl WasmRunnerService {
    pub(crate) fn new(client: Arc<ApiClient>, state: RunnerState) -> Self {
        Self(RunnerService::new(client, state))
    }

    pub fn runners_json(&self) -> String { self.0.runners_json() }
    pub fn available_runners_json(&self) -> String { self.0.available_runners_json() }

    pub fn current_runner_json(&self) -> JsValue {
        match self.0.current_runner_json() {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn get_runner_json(&self, id: i64) -> JsValue {
        match self.0.get_runner_json(id) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn set_runners(&self, json: &str) { self.0.set_runners(json); }
    pub fn set_available_runners(&self, json: &str) { self.0.set_available_runners(json); }
    pub fn set_current_runner(&self, json: &str) { self.0.set_current_runner(json); }

    pub fn update_runner_local(&self, id: f64, json: &str) {
        self.0.update_runner_local(id, json);
    }

    pub fn update_runner_status(&self, id: i64, status: &str) {
        self.0.update_runner_status(id, status);
    }

    pub fn remove_runner_local(&self, id: i64) { self.0.remove_runner_local(id); }

    pub async fn update_runner(&self, id: i64, request_json: &str) -> Result<String, String> {
        self.0.update_runner(id, request_json).await
    }

    pub async fn list_runner_pods(
        &self, id: i64, status: Option<String>, limit: Option<u32>, offset: Option<u32>,
    ) -> Result<String, String> {
        self.0.list_runner_pods(id, status, limit, offset).await
    }

    pub async fn get_auth_status(&self, auth_key: &str) -> Result<String, String> {
        self.0.get_auth_status(auth_key).await
    }

    pub async fn authorize_runner(&self, request_json: &str) -> Result<String, String> {
        self.0.authorize_runner(request_json).await
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
    // Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
    // No JSON intermediate; conventions §2.5 forbids it on the client.
    //
    // js_name is camelCase to match the existing JS-side conventions; the
    // `_connect` suffix marks the migration lane so the legacy JSON methods
    // can coexist until all 26 services flip.

    #[wasm_bindgen(js_name = listRunnersConnect)]
    pub async fn list_runners_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_runners_connect(request).await
    }

    #[wasm_bindgen(js_name = listAvailableRunnersConnect)]
    pub async fn list_available_runners_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_available_runners_connect(request).await
    }

    #[wasm_bindgen(js_name = getRunnerConnect)]
    pub async fn get_runner_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_runner_connect(request).await
    }

    #[wasm_bindgen(js_name = updateRunnerConnect)]
    pub async fn update_runner_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_runner_connect(request).await
    }

    #[wasm_bindgen(js_name = deleteRunnerConnect)]
    pub async fn delete_runner_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_runner_connect(request).await
    }

    #[wasm_bindgen(js_name = upgradeRunnerConnect)]
    pub async fn upgrade_runner_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.upgrade_runner_connect(request).await
    }

    #[wasm_bindgen(js_name = requestLogUploadConnect)]
    pub async fn request_log_upload_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.request_log_upload_connect(request).await
    }

    #[wasm_bindgen(js_name = listRunnerLogsConnect)]
    pub async fn list_runner_logs_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_runner_logs_connect(request).await
    }

    #[wasm_bindgen(js_name = querySandboxesConnect)]
    pub async fn query_sandboxes_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.query_sandboxes_connect(request).await
    }

    #[wasm_bindgen(js_name = createRunnerTokenConnect)]
    pub async fn create_runner_token_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_runner_token_connect(request).await
    }

    #[wasm_bindgen(js_name = listRunnerTokensConnect)]
    pub async fn list_runner_tokens_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_runner_tokens_connect(request).await
    }

    #[wasm_bindgen(js_name = deleteRunnerTokenConnect)]
    pub async fn delete_runner_token_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_runner_token_connect(request).await
    }
}
