use std::sync::Arc;
use std::sync::RwLock;

use agentsmesh_api_client::ApiClient;
use agentsmesh_state::pod_state::PodState;
use agentsmesh_types::proto_pod_v1 as pod_proto;
use prost::Message;

pub struct PodService {
    client: Arc<ApiClient>,
    state: RwLock<PodState>,
}

impl PodService {
    pub fn new(client: Arc<ApiClient>, state: PodState) -> Self {
        Self { client, state: RwLock::new(state) }
    }

    pub fn pods_json(&self) -> String {
        serde_json::to_string(self.state.read().unwrap().pods()).unwrap_or_default()
    }

    pub fn current_pod_json(&self) -> Option<String> {
        self.state.read().unwrap().current_pod()
            .map(|pod| serde_json::to_string(pod).unwrap_or_default())
    }

    pub fn get_pod_json(&self, pod_key: &str) -> Option<String> {
        self.state.read().unwrap().get_pod(pod_key)
            .map(|pod| serde_json::to_string(pod).unwrap_or_default())
    }

    pub fn update_pod_status(
        &self, pod_key: &str, status: &str,
        agent_status: Option<String>, error_code: Option<String>,
        error_message: Option<String>, timestamp: Option<i64>,
    ) {
        self.state.write().unwrap().update_pod_status(
            pod_key, status, agent_status.as_deref(),
            error_code.as_deref(), error_message.as_deref(), timestamp,
        );
    }

    pub fn update_pod_title(&self, pod_key: &str, title: &str, timestamp: Option<i64>) {
        self.state.write().unwrap().update_pod_title(pod_key, title, timestamp);
    }

    pub fn update_pod_alias(&self, pod_key: &str, alias: &str) {
        self.state.write().unwrap().update_pod_alias(pod_key, alias);
    }

    pub fn update_agent_status(&self, pod_key: &str, agent_status: &str) {
        self.state.write().unwrap().update_agent_status(pod_key, agent_status);
    }

    pub fn remove_pod(&self, pod_key: &str) {
        self.state.write().unwrap().remove_pod(pod_key);
    }

    // -------- Connect-RPC (binary wire) --------

    pub async fn list_pods_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::ListPodsRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_pods request: {e}"))?;
        let resp = self.client.list_pods_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_pod_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::GetPodRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_pod request: {e}"))?;
        let resp = self.client.get_pod_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn create_pod_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::CreatePodRequest::decode(request_bytes)
            .map_err(|e| format!("decode create_pod request: {e}"))?;
        let resp = self.client.create_pod_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn terminate_pod_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::TerminatePodRequest::decode(request_bytes)
            .map_err(|e| format!("decode terminate_pod request: {e}"))?;
        let resp = self.client.terminate_pod_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_pod_alias_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::UpdatePodAliasRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_pod_alias request: {e}"))?;
        let resp = self.client.update_pod_alias_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_pod_perpetual_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::UpdatePodPerpetualRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_pod_perpetual request: {e}"))?;
        let resp = self.client.update_pod_perpetual_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_pod_connection_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::GetPodConnectionRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_pod_connection request: {e}"))?;
        let resp = self.client.get_pod_connection_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn send_pod_prompt_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::SendPodPromptRequest::decode(request_bytes)
            .map_err(|e| format!("decode send_pod_prompt request: {e}"))?;
        let resp = self.client.send_pod_prompt_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_pods_by_ticket_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = pod_proto::ListPodsByTicketRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_pods_by_ticket request: {e}"))?;
        let resp = self.client.list_pods_by_ticket_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }
}
