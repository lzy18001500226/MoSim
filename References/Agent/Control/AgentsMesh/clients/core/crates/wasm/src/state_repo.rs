use agentsmesh_state::repo_state::RepoState;
use agentsmesh_types::proto_repository_v1::{Branch, Repository};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmRepoState {
    inner: RepoState,
}

#[wasm_bindgen]
impl WasmRepoState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        Self { inner: RepoState::with_storage(crate::new_memory_backend()) }
    }

    pub fn repositories_json(&self) -> String {
        serde_json::to_string(self.inner.repositories()).unwrap_or_default()
    }

    pub fn current_repo_json(&self) -> JsValue {
        match self.inner.current_repo() {
            Some(r) => JsValue::from_str(&serde_json::to_string(r).unwrap_or_default()),
            None => JsValue::NULL,
        }
    }

    pub fn branches_json(&self) -> String {
        serde_json::to_string(self.inner.branches()).unwrap_or_default()
    }

    pub fn set_repositories(&mut self, json: &str) {
        if let Ok(repos) = serde_json::from_str::<Vec<Repository>>(json) {
            self.inner.set_repositories(repos);
        }
    }

    pub fn set_current_repo(&mut self, json: &str) {
        let repo = if json.is_empty() { None } else { serde_json::from_str::<Repository>(json).ok() };
        self.inner.set_current_repo(repo);
    }

    pub fn set_branches(&mut self, json: &str) {
        if let Ok(branches) = serde_json::from_str::<Vec<Branch>>(json) {
            self.inner.set_branches(branches);
        }
    }

    pub fn add_repository(&mut self, json: &str) {
        if let Ok(repo) = serde_json::from_str::<Repository>(json) {
            self.inner.add_repository(repo);
        }
    }

    pub fn update_repository(&mut self, id: &str, json: &str) {
        if let Ok(repo) = serde_json::from_str::<Repository>(json) {
            self.inner.update_repository(id, repo);
        }
    }

    pub fn remove_repository(&mut self, id: &str) {
        self.inner.remove_repository(id);
    }
}
