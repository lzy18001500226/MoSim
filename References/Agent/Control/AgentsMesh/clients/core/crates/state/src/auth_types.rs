// Client-side auth view types. Each maps loosely to a proto record but
// carries extra fields the renderer needs in one place (sessions bundle
// tokens + user; organizations include role + subscription).

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: i64,
    pub email: String,
    pub username: String,
    pub name: Option<String>,
    pub avatar_url: Option<String>,
    #[serde(default)]
    pub is_email_verified: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserIdentity {
    pub id: i64,
    pub provider: String,
    pub provider_user_id: Option<String>,
    pub provider_username: Option<String>,
    pub created_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Organization {
    pub id: i64,
    pub name: String,
    pub slug: String,
    pub role: Option<String>,
    pub logo_url: Option<String>,
    pub subscription_plan: Option<String>,
    pub subscription_status: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthSession {
    pub token: String,
    pub refresh_token: String,
    pub user: User,
    pub expires_in: Option<i64>,
    /// Backend register/login may emit a banner message (e.g. "Please verify
    /// your email"). Keep so the UI can surface it; absent on most sessions.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthTokens {
    pub token: String,
    pub refresh_token: String,
    pub expires_in: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RegisterRequest {
    pub name: String,
    pub email: String,
    pub username: String,
    pub password: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SSOConfig {
    pub domain: String,
    pub protocol: String,
    pub name: Option<String>,
    pub enforce_sso: Option<bool>,
}
