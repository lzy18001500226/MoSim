use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn extension_list_skill_registries_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.list_skill_registries_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_create_skill_registry_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.create_skill_registry_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_sync_skill_registry_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.sync_skill_registry_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_toggle_platform_registry_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.toggle_platform_registry_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_delete_skill_registry_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.delete_skill_registry_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_list_skill_registry_overrides_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.list_skill_registry_overrides_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_list_market_skills_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.list_market_skills_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_list_market_mcp_servers_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.list_market_mcp_servers_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_list_repo_skills_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.list_repo_skills_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_install_skill_from_market_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.install_skill_from_market_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_install_skill_from_github_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.install_skill_from_github_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_presign_skill_upload_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.presign_skill_upload_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_install_skill_from_uploaded_file_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.install_skill_from_uploaded_file_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_update_skill_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.update_skill_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_uninstall_skill_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.uninstall_skill_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_list_repo_mcp_servers_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.list_repo_mcp_servers_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_install_mcp_from_market_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.install_mcp_from_market_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_install_custom_mcp_server_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.install_custom_mcp_server_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_update_mcp_server_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.update_mcp_server_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn extension_uninstall_mcp_server_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.extension.lock().await;
        svc.uninstall_mcp_server_connect(&request).await.map_err(err)
    }
}
