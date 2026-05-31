use serde::{Deserialize, Serialize};

// REST-only request payloads not covered by proto.runner_api.v1. The wasm
// bridge accepts a JSON string from JS/NAPI, deserializes into these, then
// re-encodes onto the matching proto type before calling Connect-RPC. Once
// these REST surfaces grow proto coverage these can move into the proto-
// driven path and disappear from this file.

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UpdateRunnerRequest {
    pub description: Option<String>,
    pub max_concurrent_pods: Option<i32>,
    pub is_enabled: Option<bool>,
    pub visibility: Option<String>,
}

// Interactive registration (Tailscale-style device authorization). The
// browser polls /runners/grpc/auth-status while the runner waits for
// authorization. No proto coverage — backend keeps these on REST.

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthorizeRunnerRequest {
    pub auth_key: String,
    pub node_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RunnerAuthStatus {
    pub status: String,
    pub runner_id: Option<i64>,
    pub organization_slug: Option<String>,
}
