
use agentsmesh_state::loop_state::{LoopData, LoopRunData, LoopState};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmLoopState {
    inner: LoopState,
}

#[wasm_bindgen]
impl WasmLoopState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { inner: LoopState::with_storage(crate::new_memory_backend()) }
    }

    pub fn loops_json(&self) -> String {
        serde_json::to_string(self.inner.get_loops()).unwrap_or_default()
    }

    pub fn current_loop_json(&self) -> JsValue {
        match self.inner.get_current_loop() {
            Some(l) => JsValue::from_str(
                &serde_json::to_string(l).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn runs_json(&self) -> String {
        serde_json::to_string(self.inner.get_runs()).unwrap_or_default()
    }

    pub fn get_loop_by_slug_json(&self, slug: &str) -> JsValue {
        match self.inner.get_loop_by_slug(slug) {
            Some(l) => JsValue::from_str(
                &serde_json::to_string(l).unwrap_or_default(),
            ),
            None => JsValue::NULL,
        }
    }

    pub fn set_loops(&mut self, json: &str) {
        if let Ok(loops) = serde_json::from_str::<Vec<LoopData>>(json) {
            self.inner.set_loops(loops);
        }
    }

    pub fn set_current_loop(&mut self, json: &str) {
        let loop_data = if json.is_empty() {
            None
        } else {
            serde_json::from_str::<LoopData>(json).ok()
        };
        self.inner.set_current_loop(loop_data);
    }

    pub fn update_loop(&mut self, slug: &str, json: &str) {
        if let Ok(loop_data) = serde_json::from_str::<LoopData>(json) {
            self.inner.update_loop(slug, loop_data);
        }
    }

    pub fn add_run(&mut self, run_json: &str) {
        if let Ok(run) = serde_json::from_str::<LoopRunData>(run_json) {
            self.inner.add_run(run);
        }
    }

    pub fn set_runs(&mut self, json: &str) {
        if let Ok(runs) = serde_json::from_str::<Vec<LoopRunData>>(json) {
            self.inner.set_runs(runs);
        }
    }

    pub fn append_runs(&mut self, json: &str) {
        if let Ok(runs) = serde_json::from_str::<Vec<LoopRunData>>(json) {
            self.inner.append_runs(runs);
        }
    }

    pub fn update_run_status(&mut self, run_id: i64, status: &str) {
        self.inner.update_run_status(run_id, status);
    }

    pub fn clear_runs(&mut self) {
        self.inner.clear_runs();
    }
}
