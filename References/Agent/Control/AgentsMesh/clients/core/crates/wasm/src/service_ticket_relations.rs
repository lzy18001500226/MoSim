use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::TicketRelationsService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmTicketRelationsService(pub(crate) TicketRelationsService);

// Connect-RPC binary wire. Each `*_connect` method takes prost-encoded bytes
// (Uint8Array on the JS side) and returns prost-encoded bytes — TS callers
// encode via @bufbuild/protobuf `.toBinary()` and decode via `.fromBinary()`.
#[wasm_bindgen]
impl WasmTicketRelationsService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(TicketRelationsService::new(client))
    }

    pub async fn list_relations_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_relations_connect(request_bytes).await
    }

    pub async fn create_relation_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_relation_connect(request_bytes).await
    }

    pub async fn delete_relation_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_relation_connect(request_bytes).await
    }

    pub async fn list_merge_requests_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_merge_requests_connect(request_bytes).await
    }

    pub async fn list_commits_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_commits_connect(request_bytes).await
    }

    pub async fn link_commit_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.link_commit_connect(request_bytes).await
    }

    pub async fn unlink_commit_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.unlink_commit_connect(request_bytes).await
    }

    pub async fn list_comments_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_comments_connect(request_bytes).await
    }

    pub async fn create_comment_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_comment_connect(request_bytes).await
    }

    pub async fn update_comment_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_comment_connect(request_bytes).await
    }

    pub async fn delete_comment_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_comment_connect(request_bytes).await
    }
}
