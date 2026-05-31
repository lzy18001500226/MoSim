use std::sync::Arc;
use std::sync::RwLock;

use agentsmesh_api_client::ApiClient;
use agentsmesh_state::runner_state::RunnerState;
use agentsmesh_types::proto_runner_api_v1 as runner_proto;
use agentsmesh_types::proto_runner_api_v1::Runner;
use agentsmesh_types::UpdateRunnerRequest;
use prost::Message;

pub struct RunnerService {
    client: Arc<ApiClient>,
    state: RwLock<RunnerState>,
}

impl RunnerService {
    pub fn new(client: Arc<ApiClient>, state: RunnerState) -> Self {
        Self { client, state: RwLock::new(state) }
    }

    pub fn runners_json(&self) -> String {
        serde_json::to_string(self.state.read().unwrap().runners()).unwrap_or_default()
    }

    pub fn available_runners_json(&self) -> String {
        serde_json::to_string(self.state.read().unwrap().available_runners()).unwrap_or_default()
    }

    pub fn current_runner_json(&self) -> Option<String> {
        self.state.read().unwrap().current_runner()
            .map(|r| serde_json::to_string(r).unwrap_or_default())
    }

    pub fn get_runner_json(&self, id: i64) -> Option<String> {
        self.state.read().unwrap().get_runner(id)
            .map(|r| serde_json::to_string(r).unwrap_or_default())
    }

    pub fn set_runners(&self, json: &str) {
        if let Ok(v) = serde_json::from_str::<Vec<Runner>>(json) {
            self.state.write().unwrap().set_runners(v);
        }
    }

    pub fn set_available_runners(&self, json: &str) {
        if let Ok(v) = serde_json::from_str::<Vec<Runner>>(json) {
            self.state.write().unwrap().set_available_runners(v);
        }
    }

    pub fn set_current_runner(&self, json: &str) {
        let r = if json.is_empty() { None } else { serde_json::from_str::<Runner>(json).ok() };
        self.state.write().unwrap().set_current_runner(r);
    }

    pub fn update_runner_local(&self, id: f64, json: &str) {
        if let Ok(r) = serde_json::from_str::<Runner>(json) {
            self.state.write().unwrap().update_runner(id as i64, r);
        }
    }

    pub fn update_runner_status(&self, id: i64, status: &str) {
        self.state.write().unwrap().update_runner_status(id, status);
    }

    pub fn remove_runner_local(&self, id: i64) {
        self.state.write().unwrap().remove_runner(id);
    }

    pub async fn update_runner(&self, id: i64, request_json: &str) -> Result<String, String> {
        let req_legacy: UpdateRunnerRequest = serde_json::from_str(request_json)
            .map_err(crate::wire)?;
        let req = runner_proto::UpdateRunnerRequest {
            org_slug: self.client.current_org_slug(),
            id,
            description: req_legacy.description,
            max_concurrent_pods: req_legacy.max_concurrent_pods,
            is_enabled: req_legacy.is_enabled,
            visibility: req_legacy.visibility,
            tags: None,
        };
        let runner = self.client.update_runner_connect(&req).await.map_err(crate::wire)?;
        self.state.write().unwrap().update_runner(id, runner.clone());
        serde_json::to_string(&runner).map_err(crate::wire)
    }

    pub async fn list_runner_pods(
        &self, id: i64, status: Option<String>, limit: Option<u32>, offset: Option<u32>,
    ) -> Result<String, String> {
        // proto.runner_api.v1 doesn't expose runner-scoped pod listing — the
        // proto SSOT routes per-runner pod lookup through QuerySandboxes
        // for sandbox state. Keep the legacy REST path here so existing
        // callers (web's runner detail view) keep working until proto.pod.v1
        // adds a runner_id filter. Touches:
        //   - clients/web/src/lib/api/runner.ts (legacy fetch path)
        let resp = self.client
            .list_runner_pods(id, status.as_deref(), limit, offset)
            .await.map_err(crate::wire)?;
        serde_json::to_string(&resp).map_err(crate::wire)
    }

    pub async fn get_auth_status(&self, auth_key: &str) -> Result<String, String> {
        // No proto coverage for /runners/auth/<key> — registration flow is
        // a backend-side bootstrap kept on REST until the runner-mgmt RPCs
        // land (see runbook §"Service-specific deviations").
        let resp = self.client
            .get_runner_auth_status(auth_key)
            .await.map_err(crate::wire)?;
        serde_json::to_string(&resp).map_err(crate::wire)
    }

    pub async fn authorize_runner(&self, request_json: &str) -> Result<String, String> {
        // Same reason as get_auth_status — registration bootstrap.
        let req: agentsmesh_types::AuthorizeRunnerRequest = serde_json::from_str(request_json)
            .map_err(crate::wire)?;
        let resp = self.client
            .authorize_runner(&req)
            .await.map_err(crate::wire)?;
        serde_json::to_string(&resp).map_err(crate::wire)
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // Each `*_connect` method takes prost-encoded bytes and returns prost-encoded
    // bytes — matching the wasm bridge's `Result<Vec<u8>, String>` surface
    // (conventions §2.5). Caller (TS) encodes via @bufbuild/protobuf .toBinary()
    // and decodes via .fromBinary().

    pub async fn list_runners_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::ListRunnersRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_runners request: {e}"))?;
        let resp = self.client.list_runners_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_available_runners_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::ListAvailableRunnersRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_available_runners request: {e}"))?;
        let resp = self.client.list_available_runners_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_runner_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::GetRunnerRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_runner request: {e}"))?;
        let resp = self.client.get_runner_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_runner_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::UpdateRunnerRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_runner request: {e}"))?;
        let resp = self.client.update_runner_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn delete_runner_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::DeleteRunnerRequest::decode(request_bytes)
            .map_err(|e| format!("decode delete_runner request: {e}"))?;
        let resp = self.client.delete_runner_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn upgrade_runner_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::UpgradeRunnerRequest::decode(request_bytes)
            .map_err(|e| format!("decode upgrade_runner request: {e}"))?;
        let resp = self.client.upgrade_runner_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn request_log_upload_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::RequestLogUploadRequest::decode(request_bytes)
            .map_err(|e| format!("decode request_log_upload request: {e}"))?;
        let resp = self.client.request_log_upload_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_runner_logs_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::ListRunnerLogsRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_runner_logs request: {e}"))?;
        let resp = self.client.list_runner_logs_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn query_sandboxes_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::QuerySandboxesRequest::decode(request_bytes)
            .map_err(|e| format!("decode query_sandboxes request: {e}"))?;
        let resp = self.client.query_sandboxes_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn create_runner_token_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::CreateRunnerTokenRequest::decode(request_bytes)
            .map_err(|e| format!("decode create_runner_token request: {e}"))?;
        let resp = self.client.create_runner_token_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_runner_tokens_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::ListRunnerTokensRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_runner_tokens request: {e}"))?;
        let resp = self.client.list_runner_tokens_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn delete_runner_token_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = runner_proto::DeleteRunnerTokenRequest::decode(request_bytes)
            .map_err(|e| format!("decode delete_runner_token request: {e}"))?;
        let resp = self.client.delete_runner_token_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }
}
