use agentsmesh_state::runner_state::RunnerState;
use agentsmesh_types::proto_runner_api_v1::Runner;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmRunnerState {
    inner: RunnerState,
}

#[wasm_bindgen]
impl WasmRunnerState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { inner: RunnerState::with_storage(crate::new_memory_backend()) }
    }

    pub fn runners_json(&self) -> String {
        serde_json::to_string(self.inner.runners()).unwrap_or_default()
    }

    pub fn available_runners_json(&self) -> String {
        serde_json::to_string(self.inner.available_runners())
            .unwrap_or_default()
    }

    pub fn current_runner_json(&self) -> JsValue {
        match self.inner.current_runner() {
            Some(r) => JsValue::from_str(
                &serde_json::to_string(r).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn get_runner_json(&self, id: i64) -> JsValue {
        match self.inner.get_runner(id) {
            Some(r) => JsValue::from_str(
                &serde_json::to_string(r).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn set_runners(&mut self, json: &str) {
        if let Ok(runners) = serde_json::from_str::<Vec<Runner>>(json) {
            self.inner.set_runners(runners);
        }
    }

    pub fn set_available_runners(&mut self, json: &str) {
        if let Ok(runners) = serde_json::from_str::<Vec<Runner>>(json) {
            self.inner.set_available_runners(runners);
        }
    }

    pub fn set_current_runner(&mut self, json: &str) {
        let runner = if json.is_empty() {
            None
        } else {
            serde_json::from_str::<Runner>(json).ok()
        };
        self.inner.set_current_runner(runner);
    }

    pub fn update_runner(&mut self, id: f64, json: &str) {
        if let Ok(runner) = serde_json::from_str::<Runner>(json) {
            self.inner.update_runner(id as i64, runner);
        }
    }

    pub fn update_runner_status(&mut self, id: i64, status: &str) {
        self.inner.update_runner_status(id, status);
    }

    pub fn remove_runner(&mut self, id: i64) {
        self.inner.remove_runner(id);
    }

    pub fn can_accept_pods(runner_json: &str) -> bool {
        match serde_json::from_str::<Runner>(runner_json) {
            Ok(runner) => RunnerState::can_accept_pods(&runner),
            Err(_) => false,
        }
    }
}
