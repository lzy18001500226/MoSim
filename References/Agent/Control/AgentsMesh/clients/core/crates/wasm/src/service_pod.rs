use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::PodService;
use agentsmesh_state::pod_state::PodState;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmPodService(pub(crate) PodService);

#[wasm_bindgen]
impl WasmPodService {
    pub(crate) fn new(client: Arc<ApiClient>, state: PodState) -> Self {
        Self(PodService::new(client, state))
    }

    pub fn pods_json(&self) -> String { self.0.pods_json() }

    pub fn current_pod_json(&self) -> JsValue {
        match self.0.current_pod_json() {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn get_pod_json(&self, pod_key: &str) -> JsValue {
        match self.0.get_pod_json(pod_key) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn update_pod_status(
        &self, pod_key: &str, status: &str,
        agent_status: Option<String>, error_code: Option<String>,
        error_message: Option<String>, timestamp: Option<i64>,
    ) {
        self.0.update_pod_status(pod_key, status, agent_status, error_code, error_message, timestamp);
    }

    pub fn update_pod_title(&self, pod_key: &str, title: &str, timestamp: Option<i64>) {
        self.0.update_pod_title(pod_key, title, timestamp);
    }

    pub fn update_pod_alias(&self, pod_key: &str, alias: &str) {
        self.0.update_pod_alias(pod_key, alias);
    }

    pub fn update_agent_status(&self, pod_key: &str, agent_status: &str) {
        self.0.update_agent_status(pod_key, agent_status);
    }

    pub fn remove_pod(&self, pod_key: &str) { self.0.remove_pod(pod_key); }

    // -------- Connect-RPC (binary wire) --------
    //
    // Each `*_connect` method takes prost-encoded bytes (Uint8Array on the JS
    // side) and returns prost-encoded bytes — TS callers encode via
    // @bufbuild/protobuf .toBinary() and decode via .fromBinary().

    pub async fn list_pods_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_pods_connect(request_bytes).await
    }

    pub async fn get_pod_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_pod_connect(request_bytes).await
    }

    pub async fn create_pod_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_pod_connect(request_bytes).await
    }

    pub async fn terminate_pod_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.terminate_pod_connect(request_bytes).await
    }

    pub async fn update_pod_alias_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_pod_alias_connect(request_bytes).await
    }

    pub async fn update_pod_perpetual_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_pod_perpetual_connect(request_bytes).await
    }

    pub async fn get_pod_connection_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.get_pod_connection_connect(request_bytes).await
    }

    pub async fn send_pod_prompt_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.send_pod_prompt_connect(request_bytes).await
    }

    pub async fn list_pods_by_ticket_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_pods_by_ticket_connect(request_bytes).await
    }
}
