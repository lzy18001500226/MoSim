use agentsmesh_state::mesh_state::MeshState;
use agentsmesh_types::proto_mesh_v1::MeshTopology;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmMeshState {
    inner: MeshState,
}

#[wasm_bindgen]
impl WasmMeshState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { inner: MeshState::new() }
    }

    pub fn topology_json(&self) -> JsValue {
        match self.inner.topology() {
            Some(t) => JsValue::from_str(
                &serde_json::to_string(t).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn selected_node(&self) -> JsValue {
        match self.inner.selected_node() {
            Some(key) => JsValue::from_str(key),
            None => JsValue::NULL,
        }
    }

    pub fn set_topology(&mut self, json: &str) {
        if let Ok(topology) = serde_json::from_str::<MeshTopology>(json) {
            self.inner.set_topology(topology);
        }
    }

    pub fn clear_topology(&mut self) {
        self.inner.clear_topology();
    }

    pub fn select_node(&mut self, pod_key: Option<String>) {
        self.inner.select_node(pod_key);
    }

    pub fn get_node_json(&self, pod_key: &str) -> JsValue {
        match self.inner.get_node_by_key(pod_key) {
            Some(n) => JsValue::from_str(
                &serde_json::to_string(n).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn get_edges_for_node_json(&self, pod_key: &str) -> String {
        let edges = self.inner.get_edges_for_node(pod_key);
        serde_json::to_string(&edges).unwrap_or_default()
    }

    pub fn get_channels_for_node_json(&self, pod_key: &str) -> String {
        let channels = self.inner.get_channels_for_node(pod_key);
        serde_json::to_string(&channels).unwrap_or_default()
    }

    pub fn get_nodes_by_runner_json(&self, runner_id: i64) -> String {
        let nodes = self.inner.get_nodes_by_runner(runner_id);
        serde_json::to_string(&nodes).unwrap_or_default()
    }

    pub fn get_active_nodes_json(&self) -> String {
        let nodes = self.inner.get_active_nodes();
        serde_json::to_string(&nodes).unwrap_or_default()
    }

    pub fn get_runner_info_json(&self, runner_id: i64) -> JsValue {
        match self.inner.get_runner_info(runner_id) {
            Some(r) => JsValue::from_str(
                &serde_json::to_string(r).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }
}
