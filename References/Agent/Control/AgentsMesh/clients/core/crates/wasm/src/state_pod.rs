use agentsmesh_state::pod_state::PodState;
use agentsmesh_types::proto_pod_v1::Pod;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmPodState {
    inner: PodState,
}

#[wasm_bindgen]
impl WasmPodState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { inner: PodState::with_storage(crate::new_memory_backend()) }
    }

    pub fn pods_json(&self) -> String {
        serde_json::to_string(self.inner.pods()).unwrap_or_default()
    }

    pub fn current_pod_json(&self) -> JsValue {
        match self.inner.current_pod() {
            Some(pod) => JsValue::from_str(
                &serde_json::to_string(pod).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn get_pod_json(&self, pod_key: &str) -> JsValue {
        match self.inner.get_pod(pod_key) {
            Some(pod) => JsValue::from_str(
                &serde_json::to_string(pod).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn upsert_pod(&mut self, pod_json: &str, timestamp: Option<i64>) {
        if let Ok(pod) = serde_json::from_str::<Pod>(pod_json) {
            self.inner.upsert_pod(pod, timestamp);
        }
    }

    /// Replace the entire pod list with a fresh batch from a ListPods call.
    /// Mirrors WasmRunnerState::set_runners. Stores/pod.ts::fetchPods +
    /// fetchSidebarPods call this after each Connect ListPods round-trip
    /// so the sidebar / workspace pod list reflects the latest server state.
    /// Without this method, the JS call throws TypeError silently inside
    /// the store's try/catch and the UI keeps showing "暂无 Pod" even
    /// though the network round-trip succeeded.
    pub fn set_pods(&mut self, json: &str) {
        if let Ok(pods) = serde_json::from_str::<Vec<Pod>>(json) {
            self.inner.set_pods(pods);
        }
    }

    pub fn update_pod_status(
        &mut self,
        pod_key: &str,
        status: &str,
        agent_status: Option<String>,
        error_code: Option<String>,
        error_message: Option<String>,
        timestamp: Option<i64>,
    ) {
        self.inner.update_pod_status(
            pod_key,
            status,
            agent_status.as_deref(),
            error_code.as_deref(),
            error_message.as_deref(),
            timestamp,
        );
    }

    pub fn update_pod_title(
        &mut self,
        pod_key: &str,
        title: &str,
        timestamp: Option<i64>,
    ) {
        self.inner.update_pod_title(pod_key, title, timestamp);
    }

    pub fn update_pod_alias(&mut self, pod_key: &str, alias: &str) {
        self.inner.update_pod_alias(pod_key, alias);
    }

    pub fn update_agent_status(&mut self, pod_key: &str, agent_status: &str) {
        self.inner.update_agent_status(pod_key, agent_status);
    }

    pub fn remove_pod(&mut self, pod_key: &str) {
        self.inner.remove_pod(pod_key);
    }
}
