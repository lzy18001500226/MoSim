use napi_derive::napi;
use crate::{AppState, err};

#[napi]
impl AppState {
    #[napi]
    pub async fn promocode_validate_promo_code_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.promocode.lock().await;
        svc.validate_promo_code_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn promocode_redeem_promo_code_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.promocode.lock().await;
        svc.redeem_promo_code_connect(&request).await.map_err(err)
    }

    #[napi]
    pub async fn promocode_get_redemption_history_connect(&self, request: Vec<u8>) -> napi::Result<Vec<u8>> {
        let svc = self.promocode.lock().await;
        svc.get_redemption_history_connect(&request).await.map_err(err)
    }
}
