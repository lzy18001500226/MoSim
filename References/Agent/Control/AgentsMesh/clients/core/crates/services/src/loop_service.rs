use std::sync::Arc;
use std::sync::RwLock;

use agentsmesh_api_client::ApiClient;
use agentsmesh_state::loop_state::{LoopData, LoopRunData, LoopState};

pub struct LoopService {
    client: Arc<ApiClient>,
    state: RwLock<LoopState>,
}

impl LoopService {
    pub fn new(client: Arc<ApiClient>, state: LoopState) -> Self {
        Self { client, state: RwLock::new(state) }
    }

    pub fn loops_json(&self) -> String {
        serde_json::to_string(self.state.read().unwrap().get_loops()).unwrap_or_default()
    }

    pub fn current_loop_json(&self) -> Option<String> {
        self.state.read().unwrap().get_current_loop()
            .map(|l| serde_json::to_string(l).unwrap_or_default())
    }

    pub fn runs_json(&self) -> String {
        serde_json::to_string(self.state.read().unwrap().get_runs()).unwrap_or_default()
    }

    pub fn get_loop_by_slug_json(&self, slug: &str) -> Option<String> {
        self.state.read().unwrap().get_loop_by_slug(slug)
            .map(|l| serde_json::to_string(l).unwrap_or_default())
    }

    pub fn set_loops(&self, json: &str) {
        if let Ok(v) = serde_json::from_str::<Vec<LoopData>>(json) {
            self.state.write().unwrap().set_loops(v);
        }
    }

    pub fn set_current_loop(&self, json: &str) {
        let l = if json.is_empty() { None } else { serde_json::from_str::<LoopData>(json).ok() };
        self.state.write().unwrap().set_current_loop(l);
    }

    pub fn update_loop_local(&self, slug: &str, json: &str) {
        if let Ok(l) = serde_json::from_str::<LoopData>(json) {
            self.state.write().unwrap().update_loop(slug, l);
        }
    }

    pub fn add_run(&self, json: &str) {
        if let Ok(r) = serde_json::from_str::<LoopRunData>(json) {
            self.state.write().unwrap().add_run(r);
        }
    }

    pub fn set_runs(&self, json: &str) {
        if let Ok(v) = serde_json::from_str::<Vec<LoopRunData>>(json) {
            self.state.write().unwrap().set_runs(v);
        }
    }

    pub fn append_runs(&self, json: &str) {
        if let Ok(v) = serde_json::from_str::<Vec<LoopRunData>>(json) {
            self.state.write().unwrap().append_runs(v);
        }
    }

    pub fn update_run_status(&self, run_id: i64, status: &str) {
        self.state.write().unwrap().update_run_status(run_id, status);
    }

    pub fn clear_runs(&self) {
        self.state.write().unwrap().clear_runs();
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // 10 Connect lanes — request bytes in, response bytes out. State is
    // bypassed (caller is the TS adapter); the existing REST methods
    // above keep updating the LoopState during the dual-track migration
    // so realtime event handlers stay correct.

    pub async fn list_loops_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::ListLoopsRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_loops request: {e}"))?;
        let resp = self.client.list_loops_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_loop_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::GetLoopRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_loop request: {e}"))?;
        let resp = self.client.get_loop_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn create_loop_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::CreateLoopRequest::decode(request_bytes)
            .map_err(|e| format!("decode create_loop request: {e}"))?;
        let resp = self.client.create_loop_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_loop_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::UpdateLoopRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_loop request: {e}"))?;
        let resp = self.client.update_loop_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn delete_loop_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::DeleteLoopRequest::decode(request_bytes)
            .map_err(|e| format!("decode delete_loop request: {e}"))?;
        let resp = self.client.delete_loop_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn loop_action_connect(
        &self, action: &str, request_bytes: &[u8],
    ) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::LoopActionRequest::decode(request_bytes)
            .map_err(|e| format!("decode loop_action request: {e}"))?;
        let resp = match action {
            "enable" => self.client.enable_loop_connect(&req).await,
            "disable" => self.client.disable_loop_connect(&req).await,
            other => return Err(format!("unknown loop action: {other}")),
        }.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn trigger_loop_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::TriggerLoopRequest::decode(request_bytes)
            .map_err(|e| format!("decode trigger_loop request: {e}"))?;
        let resp = self.client.trigger_loop_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_runs_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::ListRunsRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_runs request: {e}"))?;
        let resp = self.client.list_loop_runs_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn cancel_run_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        use agentsmesh_types::proto_loop_v1 as lp;
        use prost::Message;
        let req = lp::CancelRunRequest::decode(request_bytes)
            .map_err(|e| format!("decode cancel_run request: {e}"))?;
        let resp = self.client.cancel_loop_run_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }
}
