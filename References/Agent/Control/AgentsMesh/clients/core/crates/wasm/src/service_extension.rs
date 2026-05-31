use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::ExtensionService;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmExtensionService(pub(crate) ExtensionService);

#[wasm_bindgen]
impl WasmExtensionService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(ExtensionService::new(client))
    }

    // -------- Connect-RPC (binary wire) --------
    //
    // TS encodes the request via @bufbuild/protobuf .toBinary(), passes the
    // Uint8Array in, receives a Uint8Array back, decodes via .fromBinary().
    // No JSON intermediate; conventions §2.5 forbids it on the client.
    //
    // js_name is camelCase to match the existing JS-side conventions; the
    // `_connect` suffix marks the migration lane so the legacy JSON methods
    // can coexist until all 26 services flip.

    #[wasm_bindgen(js_name = listSkillRegistriesConnect)]
    pub async fn list_skill_registries_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_skill_registries_connect(request).await
    }

    #[wasm_bindgen(js_name = createSkillRegistryConnect)]
    pub async fn create_skill_registry_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.create_skill_registry_connect(request).await
    }

    #[wasm_bindgen(js_name = syncSkillRegistryConnect)]
    pub async fn sync_skill_registry_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.sync_skill_registry_connect(request).await
    }

    #[wasm_bindgen(js_name = deleteSkillRegistryConnect)]
    pub async fn delete_skill_registry_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.delete_skill_registry_connect(request).await
    }

    #[wasm_bindgen(js_name = togglePlatformRegistryConnect)]
    pub async fn toggle_platform_registry_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.toggle_platform_registry_connect(request).await
    }

    #[wasm_bindgen(js_name = listSkillRegistryOverridesConnect)]
    pub async fn list_skill_registry_overrides_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_skill_registry_overrides_connect(request).await
    }

    // -- MarketService --

    #[wasm_bindgen(js_name = listMarketSkillsConnect)]
    pub async fn list_market_skills_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_market_skills_connect(request).await
    }

    #[wasm_bindgen(js_name = listMarketMcpServersConnect)]
    pub async fn list_market_mcp_servers_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_market_mcp_servers_connect(request).await
    }

    // -- RepoSkillService --

    #[wasm_bindgen(js_name = listRepoSkillsConnect)]
    pub async fn list_repo_skills_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_repo_skills_connect(request).await
    }

    #[wasm_bindgen(js_name = installSkillFromMarketConnect)]
    pub async fn install_skill_from_market_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.install_skill_from_market_connect(request).await
    }

    #[wasm_bindgen(js_name = installSkillFromGithubConnect)]
    pub async fn install_skill_from_github_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.install_skill_from_github_connect(request).await
    }

    #[wasm_bindgen(js_name = presignSkillUploadConnect)]
    pub async fn presign_skill_upload_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.presign_skill_upload_connect(request).await
    }

    #[wasm_bindgen(js_name = installSkillFromUploadedFileConnect)]
    pub async fn install_skill_from_uploaded_file_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.install_skill_from_uploaded_file_connect(request).await
    }

    #[wasm_bindgen(js_name = updateSkillConnect)]
    pub async fn update_skill_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_skill_connect(request).await
    }

    #[wasm_bindgen(js_name = uninstallSkillConnect)]
    pub async fn uninstall_skill_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.uninstall_skill_connect(request).await
    }

    // -- RepoMcpService --

    #[wasm_bindgen(js_name = listRepoMcpServersConnect)]
    pub async fn list_repo_mcp_servers_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.list_repo_mcp_servers_connect(request).await
    }

    #[wasm_bindgen(js_name = installMcpFromMarketConnect)]
    pub async fn install_mcp_from_market_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.install_mcp_from_market_connect(request).await
    }

    #[wasm_bindgen(js_name = installCustomMcpServerConnect)]
    pub async fn install_custom_mcp_server_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.install_custom_mcp_server_connect(request).await
    }

    #[wasm_bindgen(js_name = updateMcpServerConnect)]
    pub async fn update_mcp_server_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.update_mcp_server_connect(request).await
    }

    #[wasm_bindgen(js_name = uninstallMcpServerConnect)]
    pub async fn uninstall_mcp_server_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.uninstall_mcp_server_connect(request).await
    }
}
