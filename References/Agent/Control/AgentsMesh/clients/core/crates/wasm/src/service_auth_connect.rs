use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::AuthConnectService;
use wasm_bindgen::prelude::*;

// WasmAuthConnectService — wasm-bindgen front for AuthConnectService.
// Binary in / binary out (conventions §2.5): TS encodes via @bufbuild/
// protobuf .toBinary(), passes the Uint8Array in, decodes the Uint8Array
// response via .fromBinary(). No JSON intermediate on the client wire.
//
// js_name is camelCase to match existing JS conventions; the `_connect`
// suffix marks the migration lane so the legacy JSON-over-REST
// `WasmAuthApiService` can coexist until call sites finish flipping over.
#[wasm_bindgen]
pub struct WasmAuthConnectService(pub(crate) AuthConnectService);

#[wasm_bindgen]
impl WasmAuthConnectService {
    pub(crate) fn new(client: Arc<ApiClient>) -> Self {
        Self(AuthConnectService::new(client))
    }

    #[wasm_bindgen(js_name = loginConnect)]
    pub async fn login_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.login_connect(request).await
    }

    #[wasm_bindgen(js_name = registerConnect)]
    pub async fn register_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.register_connect(request).await
    }

    #[wasm_bindgen(js_name = refreshTokenConnect)]
    pub async fn refresh_token_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.refresh_token_connect(request).await
    }

    #[wasm_bindgen(js_name = verifyEmailConnect)]
    pub async fn verify_email_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.verify_email_connect(request).await
    }

    #[wasm_bindgen(js_name = resendVerificationConnect)]
    pub async fn resend_verification_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.resend_verification_connect(request).await
    }

    #[wasm_bindgen(js_name = forgotPasswordConnect)]
    pub async fn forgot_password_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.forgot_password_connect(request).await
    }

    #[wasm_bindgen(js_name = resetPasswordConnect)]
    pub async fn reset_password_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.reset_password_connect(request).await
    }

    #[wasm_bindgen(js_name = oauthRedirectConnect)]
    pub async fn oauth_redirect_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.oauth_redirect_connect(request).await
    }

    #[wasm_bindgen(js_name = oauthCallbackConnect)]
    pub async fn oauth_callback_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.oauth_callback_connect(request).await
    }

    #[wasm_bindgen(js_name = logoutConnect)]
    pub async fn logout_connect(&self, request: &[u8]) -> Result<Vec<u8>, String> {
        self.0.logout_connect(request).await
    }
}
