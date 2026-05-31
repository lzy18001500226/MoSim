use std::sync::Arc;

use futures::lock::Mutex;
use reqwest::Client;

use crate::error::ApiError;
use crate::token_store::AuthTokenStore;

/// Connect-RPC client. Owns the shared `reqwest::Client` + auth token store.
///
/// After R7 the surface is intentionally tiny: every business RPC goes through
/// `connect_call()` (binary application/proto). Two protocol-外 escape hatches:
///   - `put_raw_bytes` — S3 / MinIO presigned PUT (file + skill upload).
///   - `current_org_slug` — exposes the cached slug to services that build
///     proto request bodies (`org_slug` is always proto field 1).
///
/// Token refresh is also Connect-only — see `refresh.rs` (calls
/// `/proto.auth.v1.AuthService/RefreshToken`).
pub struct ApiClient {
    pub(crate) http: Client,
    pub(crate) base_url: String,
    pub(crate) auth_store: Arc<dyn AuthTokenStore>,
    pub(crate) refresh_lock: Mutex<()>,
}

impl ApiClient {
    pub fn new(base_url: String, auth_store: Arc<dyn AuthTokenStore>) -> Self {
        Self {
            http: Client::new(),
            base_url,
            auth_store,
            refresh_lock: Mutex::new(()),
        }
    }

    /// Current org slug for Connect-RPC request bodies. Services use this to
    /// populate `org_slug` (proto field 1) before invoking `*_connect`.
    pub fn current_org_slug(&self) -> String {
        self.auth_store.get_current_org_slug().unwrap_or_default()
    }

    /// Direct PUT of raw bytes — protocol-外 path used for S3 presigned
    /// uploads (file attachments + skill packages). Connect doesn't carry
    /// blob bodies, so renderer code calls this after first asking the
    /// backend for a presigned URL via a Connect RPC.
    pub async fn put_raw_bytes(
        &self, url: &str, content_type: &str, body: Vec<u8>,
    ) -> Result<(), ApiError> {
        let resp = self.http
            .put(url)
            .header("Content-Type", content_type)
            .body(body)
            .send()
            .await?;
        if !resp.status().is_success() {
            return Err(ApiError::Http {
                status: resp.status().as_u16(),
                status_text: resp.status().canonical_reason().unwrap_or("Unknown").to_string(),
                code: None, server_message: None, data: None,
                url: Some(url.to_string()),
            });
        }
        Ok(())
    }
}
