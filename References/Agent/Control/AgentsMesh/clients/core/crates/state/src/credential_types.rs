// Client-side credential view types — projections of proto.user_credential.v1
// and proto.repository.v1 messages with optional fields populated.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RepositoryProvider {
    pub id: i64,
    pub provider_type: String,
    pub name: String,
    pub base_url: Option<String>,
    #[serde(default)]
    pub has_client_id: Option<bool>,
    #[serde(default)]
    pub has_bot_token: Option<bool>,
    #[serde(default)]
    pub has_identity: Option<bool>,
    pub is_default: Option<bool>,
    #[serde(default)]
    pub is_active: Option<bool>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProviderRepository {
    pub id: Option<String>,
    pub name: String,
    pub slug: Option<String>,
    pub description: Option<String>,
    pub default_branch: Option<String>,
    pub visibility: Option<String>,
    pub http_clone_url: Option<String>,
    pub ssh_clone_url: Option<String>,
    pub web_url: Option<String>,
}
