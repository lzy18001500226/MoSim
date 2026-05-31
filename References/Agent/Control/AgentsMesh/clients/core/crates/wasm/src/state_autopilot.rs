use agentsmesh_state::autopilot_state::{AutopilotController, AutopilotIteration, AutopilotState};
use serde_json::Value;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmAutopilotState {
    inner: AutopilotState,
}

#[wasm_bindgen]
impl WasmAutopilotState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { inner: AutopilotState::new() }
    }

    pub fn controllers_json(&self) -> String {
        serde_json::to_string(self.inner.controllers()).unwrap_or_default()
    }

    pub fn current_controller_json(&self) -> JsValue {
        match self.inner.current_controller() {
            Some(c) => JsValue::from_str(&serde_json::to_string(c).unwrap_or_default()),
            None => JsValue::NULL,
        }
    }

    pub fn set_controllers(&mut self, json: &str) {
        if let Ok(controllers) = serde_json::from_str::<Vec<AutopilotController>>(json) {
            self.inner.set_controllers(controllers);
        }
    }

    pub fn set_current_controller(&mut self, json: &str) {
        let ctrl = if json.is_empty() { None } else { serde_json::from_str::<AutopilotController>(json).ok() };
        self.inner.set_current_controller(ctrl);
    }

    pub fn add_controller(&mut self, json: &str) {
        if let Ok(controller) = serde_json::from_str::<AutopilotController>(json) {
            self.inner.add_controller(controller);
        }
    }

    pub fn update_controller(&mut self, key: &str, json: &str) {
        if let Ok(controller) = serde_json::from_str::<AutopilotController>(json) {
            self.inner.update_controller(key, controller);
        }
    }

    pub fn remove_controller(&mut self, key: &str) {
        self.inner.remove_controller(key);
    }

    pub fn get_iterations_json(&self, key: &str) -> JsValue {
        match self.inner.get_iterations(key) {
            Some(iters) => JsValue::from_str(&serde_json::to_string(iters).unwrap_or_default()),
            None => JsValue::NULL,
        }
    }

    pub fn set_iterations(&mut self, key: &str, json: &str) {
        if let Ok(iters) = serde_json::from_str::<Vec<AutopilotIteration>>(json) {
            self.inner.set_iterations(key.to_string(), iters);
        }
    }

    pub fn add_iteration(&mut self, key: &str, json: &str) {
        if let Ok(iter) = serde_json::from_str::<AutopilotIteration>(json) {
            self.inner.add_iteration(key.to_string(), iter);
        }
    }

    pub fn get_thinking_json(&self, key: &str) -> JsValue {
        match self.inner.get_thinking(key) {
            Some(t) => JsValue::from_str(&serde_json::to_string(t).unwrap_or_default()),
            None => JsValue::NULL,
        }
    }

    pub fn get_thinking_history_json(&self, key: &str) -> JsValue {
        match self.inner.get_thinking_history(key) {
            Some(h) => JsValue::from_str(&serde_json::to_string(h).unwrap_or_default()),
            None => JsValue::from_str("[]"),
        }
    }

    pub fn update_thinking(&mut self, key: &str, json: &str) {
        if let Ok(thinking) = serde_json::from_str::<Value>(json) {
            self.inner.update_thinking(key.to_string(), thinking);
        }
    }

    pub fn get_controller_by_pod_key_json(&self, pod_key: &str) -> JsValue {
        match self.inner.get_controller_by_pod_key(pod_key) {
            Some(c) => JsValue::from_str(&serde_json::to_string(c).unwrap_or_default()),
            None => JsValue::NULL,
        }
    }
}
