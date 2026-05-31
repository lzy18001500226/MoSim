use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_types::proto_extension_v1 as ext_proto;
use prost::Message;

pub struct ExtensionService {
    client: Arc<ApiClient>,
}

impl ExtensionService {
    pub fn new(client: Arc<ApiClient>) -> Self {
        Self { client }
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // Each method accepts a prost-encoded request body (`Vec<u8>`) and returns
    // a prost-encoded response body — matching the wasm bridge's
    // `Result<Vec<u8>, String>` surface (conventions §2.5).
    //
    // org_slug is sourced from the caller-supplied request, not from
    // AuthManager — keeps these methods unit-testable without an org context
    // in the token store. The wasm bridge populates org_slug before encoding.

    pub async fn list_skill_registries_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::ListSkillRegistriesRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_skill_registries request: {e}"))?;
        let resp = self.client.list_skill_registries_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn create_skill_registry_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::CreateSkillRegistryRequest::decode(request_bytes)
            .map_err(|e| format!("decode create_skill_registry request: {e}"))?;
        let resp = self.client.create_skill_registry_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn sync_skill_registry_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::SyncSkillRegistryRequest::decode(request_bytes)
            .map_err(|e| format!("decode sync_skill_registry request: {e}"))?;
        let resp = self.client.sync_skill_registry_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn delete_skill_registry_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::DeleteSkillRegistryRequest::decode(request_bytes)
            .map_err(|e| format!("decode delete_skill_registry request: {e}"))?;
        let resp = self.client.delete_skill_registry_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn toggle_platform_registry_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::TogglePlatformRegistryRequest::decode(request_bytes)
            .map_err(|e| format!("decode toggle_platform_registry request: {e}"))?;
        let resp = self.client.toggle_platform_registry_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_skill_registry_overrides_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::ListSkillRegistryOverridesRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_skill_registry_overrides request: {e}"))?;
        let resp = self.client.list_skill_registry_overrides_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    // ---- MarketService ----

    pub async fn list_market_skills_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::ListMarketSkillsRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_market_skills request: {e}"))?;
        let resp = self.client.list_market_skills_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_market_mcp_servers_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::ListMarketMcpServersRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_market_mcp_servers request: {e}"))?;
        let resp = self.client.list_market_mcp_servers_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    // ---- RepoSkillService ----

    pub async fn list_repo_skills_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::ListRepoSkillsRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_repo_skills request: {e}"))?;
        let resp = self.client.list_repo_skills_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn install_skill_from_market_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::InstallSkillFromMarketRequest::decode(request_bytes)
            .map_err(|e| format!("decode install_skill_from_market request: {e}"))?;
        let resp = self.client.install_skill_from_market_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn install_skill_from_github_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::InstallSkillFromGitHubRequest::decode(request_bytes)
            .map_err(|e| format!("decode install_skill_from_github request: {e}"))?;
        let resp = self.client.install_skill_from_github_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn presign_skill_upload_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::PresignSkillUploadRequest::decode(request_bytes)
            .map_err(|e| format!("decode presign_skill_upload request: {e}"))?;
        let resp = self.client.presign_skill_upload_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn install_skill_from_uploaded_file_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::InstallSkillFromUploadedFileRequest::decode(request_bytes)
            .map_err(|e| format!("decode install_skill_from_uploaded_file request: {e}"))?;
        let resp = self.client.install_skill_from_uploaded_file_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_skill_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::UpdateSkillRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_skill request: {e}"))?;
        let resp = self.client.update_skill_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn uninstall_skill_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::UninstallSkillRequest::decode(request_bytes)
            .map_err(|e| format!("decode uninstall_skill request: {e}"))?;
        let resp = self.client.uninstall_skill_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    // ---- RepoMcpService ----

    pub async fn list_repo_mcp_servers_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::ListRepoMcpServersRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_repo_mcp_servers request: {e}"))?;
        let resp = self.client.list_repo_mcp_servers_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn install_mcp_from_market_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::InstallMcpFromMarketRequest::decode(request_bytes)
            .map_err(|e| format!("decode install_mcp_from_market request: {e}"))?;
        let resp = self.client.install_mcp_from_market_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn install_custom_mcp_server_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::InstallCustomMcpServerRequest::decode(request_bytes)
            .map_err(|e| format!("decode install_custom_mcp_server request: {e}"))?;
        let resp = self.client.install_custom_mcp_server_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_mcp_server_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::UpdateMcpServerRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_mcp_server request: {e}"))?;
        let resp = self.client.update_mcp_server_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn uninstall_mcp_server_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = ext_proto::UninstallMcpServerRequest::decode(request_bytes)
            .map_err(|e| format!("decode uninstall_mcp_server request: {e}"))?;
        let resp = self.client.uninstall_mcp_server_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }
}
