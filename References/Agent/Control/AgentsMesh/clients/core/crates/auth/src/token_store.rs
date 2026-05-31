use agentsmesh_api_client::AuthTokenStore;
use agentsmesh_state::auth_types::AuthTokens;

use crate::manager::{now_unix_secs, AuthManager};

/// Used when the server response omits `expires_in`. 1h matches the
/// backend's default JWT TTL — see `backend/internal/config/jwt.go`.
/// If the server actually configures a different TTL, the client will
/// 401 → refresh once before realigning. Acceptable but suboptimal.
const REFRESH_FALLBACK_TTL_SECS: i64 = 3600;

impl AuthTokenStore for AuthManager {
    fn get_token(&self) -> Option<String> {
        self.read_state().token().map(String::from)
    }

    fn get_refresh_token(&self) -> Option<String> {
        self.read_state().refresh_token().map(String::from)
    }

    fn set_tokens(&self, token: String, refresh_token: String, expires_in_secs: Option<i64>) {
        let ttl = expires_in_secs.unwrap_or_else(|| {
            tracing::warn!(
                "auth refresh: server did not return expires_in; falling back to {}s",
                REFRESH_FALLBACK_TTL_SECS
            );
            REFRESH_FALLBACK_TTL_SECS
        });
        let tokens = AuthTokens {
            token,
            refresh_token,
            expires_in: Some(ttl),
        };
        self.write_state()
            .apply_tokens(&tokens, &self.base_url, now_unix_secs());
        self.persist();
    }

    fn clear_tokens(&self) {
        self.reset_local();
    }

    fn get_current_org_slug(&self) -> Option<String> {
        self.read_state()
            .current_org
            .as_ref()
            .map(|o| o.slug.clone())
    }
}
