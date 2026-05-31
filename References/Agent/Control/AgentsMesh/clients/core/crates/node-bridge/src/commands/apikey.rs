use napi_derive::napi;
use crate::{AppState, err};

// Binary-wire Connect bridge — TS encodes/decodes via @bufbuild/protobuf;
// node-bridge just forwards bytes.

#[napi]
impl AppState {
    #[napi]
    pub async fn apikey_list_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.apikey.lock().await;
        svc.list_api_keys_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn apikey_get_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.apikey.lock().await;
        svc.get_api_key_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn apikey_create_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.apikey.lock().await;
        svc.create_api_key_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn apikey_update_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.apikey.lock().await;
        svc.update_api_key_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn apikey_delete_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.apikey.lock().await;
        svc.delete_api_key_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn apikey_revoke_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.apikey.lock().await;
        svc.revoke_api_key_connect(&request).await.map_err(err)
    }
}
