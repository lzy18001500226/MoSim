use agentsmesh_state::app_state::AppState;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmAppState {
    inner: AppState,
}

#[wasm_bindgen]
impl WasmAppState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { inner: AppState::with_storage(crate::new_memory_backend()) }
    }

    pub fn dispatch_event(&mut self, event_json: &str) {
        if let Ok(event) = serde_json::from_str(event_json) {
            self.inner.dispatch(&event);
        }
    }

    pub fn pods_json(&self) -> String {
        serde_json::to_string(self.inner.pods.pods()).unwrap_or_default()
    }

    pub fn channels_json(&self) -> String {
        serde_json::to_string(self.inner.channels.get_channels()).unwrap_or_default()
    }

    pub fn runners_json(&self) -> String {
        serde_json::to_string(self.inner.runners.runners()).unwrap_or_default()
    }

    pub fn tickets_json(&self) -> String {
        serde_json::to_string(self.inner.tickets.get_tickets()).unwrap_or_default()
    }

    pub fn loops_json(&self) -> String {
        serde_json::to_string(self.inner.loops.get_loops()).unwrap_or_default()
    }

    pub fn mesh_json(&self) -> String {
        match self.inner.mesh.topology() {
            Some(t) => serde_json::to_string(t).unwrap_or_default(),
            None => "null".to_string(),
        }
    }
}
