use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn sso_discover_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.sso.lock().await;
        svc.discover_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn sso_ldap_auth_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.sso.lock().await;
        svc.ldap_auth_connect(&request).await.map_err(err)
    }
}
