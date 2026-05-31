use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn env_bundle_list_env_bundles_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.env_bundle.lock().await;
        svc.list_env_bundles_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn env_bundle_get_env_bundle_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.env_bundle.lock().await;
        svc.get_env_bundle_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn env_bundle_create_env_bundle_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.env_bundle.lock().await;
        svc.create_env_bundle_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn env_bundle_update_env_bundle_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.env_bundle.lock().await;
        svc.update_env_bundle_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn env_bundle_delete_env_bundle_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.env_bundle.lock().await;
        svc.delete_env_bundle_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn env_bundle_set_primary_env_bundle_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.env_bundle.lock().await;
        svc.set_primary_env_bundle_connect(&request).await.map_err(err)
    }
}
