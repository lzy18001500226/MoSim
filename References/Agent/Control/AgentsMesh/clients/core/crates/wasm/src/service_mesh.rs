use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::MeshService;
use agentsmesh_state::mesh_state::MeshState;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmMeshService(pub(crate) MeshService);

#[wasm_bindgen]
impl WasmMeshService {
    pub(crate) fn new(client: Arc<ApiClient>, state: MeshState) -> Self {
        Self(MeshService::new(client, state))
    }

    pub fn topology_json(&self) -> JsValue {
        match self.0.topology_json() {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn selected_node(&self) -> JsValue {
        match self.0.selected_node() {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn get_node_json(&self, pod_key: &str) -> JsValue {
        match self.0.get_node_json(pod_key) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn get_edges_for_node_json(&self, pod_key: &str) -> String {
        self.0.get_edges_for_node_json(pod_key)
    }

    pub fn get_channels_for_node_json(&self, pod_key: &str) -> String {
        self.0.get_channels_for_node_json(pod_key)
    }

    pub fn get_active_nodes_json(&self) -> String { self.0.get_active_nodes_json() }

    pub fn get_nodes_by_runner_json(&self, runner_id: i64) -> String {
        self.0.get_nodes_by_runner_json(runner_id)
    }

    pub fn get_runner_info_json(&self, runner_id: i64) -> JsValue {
        match self.0.get_runner_info_json(runner_id) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn clear_topology(&self) { self.0.clear_topology(); }

    pub fn select_node(&self, pod_key: Option<String>) {
        self.0.select_node(pod_key);
    }

    pub async fn fetch_topology(&self) -> Result<String, String> {
        self.0.fetch_topology().await
    }
}
