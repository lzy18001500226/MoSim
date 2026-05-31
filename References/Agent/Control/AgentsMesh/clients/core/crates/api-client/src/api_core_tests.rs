#[cfg(test)]
mod api_core_tests {
    use std::sync::{Arc, Mutex};

    use serde_json::json;
    use wiremock::matchers::{method, path, query_param};
    use wiremock::{Mock, MockServer, ResponseTemplate};

    use crate::{ApiClient, AuthTokenStore};

    struct MockTokenStore {
        org_slug: Mutex<Option<String>>,
    }
    impl MockTokenStore {
        fn with_org(slug: &str) -> Arc<Self> {
            Arc::new(Self { org_slug: Mutex::new(Some(slug.into())) })
        }
        fn no_org() -> Arc<Self> {
            Arc::new(Self { org_slug: Mutex::new(None) })
        }
    }
    impl AuthTokenStore for MockTokenStore {
        fn get_token(&self) -> Option<String> { Some("tok".into()) }
        fn get_refresh_token(&self) -> Option<String> { None }
        fn set_tokens(&self, _t: String, _r: String, _e: Option<i64>) {}
        fn clear_tokens(&self) {}
        fn get_current_org_slug(&self) -> Option<String> {
            self.org_slug.lock().unwrap().clone()
        }
    }

    fn ok(body: serde_json::Value) -> ResponseTemplate {
        ResponseTemplate::new(200).set_body_json(body)
    }

    // ── pod ─────────────────────────────────────────────────────────────
    // Pod tests removed: REST surface eliminated; Connect handler tests in
    // backend/internal/api/connect/pod cover the same surface.

    // ── ticket ──────────────────────────────────────────────────────────
    // ticket REST mocks removed: REST surface eliminated; Connect handler
    // tests in backend/internal/api/connect/ticket cover the same surface.

    // ── runner ──────────────────────────────────────────────────────────
    // list_runners + sibling REST mocks removed: REST surface eliminated;
    // Connect handler tests in backend/internal/api/connect/runner cover
    // the same surface.

    // ── billing ─────────────────────────────────────────────────────────
    // get_billing_overview removed — Connect handler tests cover it
    // (backend/internal/api/connect/billing).

    // ── mesh ────────────────────────────────────────────────────────────
    // get_mesh_topology REST mock removed: REST surface eliminated;
    // Connect handler tests in backend/internal/api/connect/mesh cover
    // the same surface.

    // ── loop ────────────────────────────────────────────────────────────
    // REST surface dropped; covered by loop_connect.rs.

    // ── agentpod ────────────────────────────────────────────────────────
    // REST surface dropped; covered by agentpod.rs Connect block.

    // ── autopilot ───────────────────────────────────────────────────────
    // REST surface dropped; covered by autopilot_connect.rs.

    // ── billing_public ──────────────────────────────────────────────────
    // REST surface dropped; covered by billing.rs Connect block
    // (`get_public_pricing_connect` + `get_public_deployment_info_connect`).

    // ── file ────────────────────────────────────────────────────────────
    // REST `files/presign` removed; covered by file_connect.rs.


    // ── invitation ──────────────────────────────────────────────────────
    // REST surface dropped; covered by invitation_connect.rs.

    // ── message ─────────────────────────────────────────────────────────
    // REST surface dropped; mesh messaging has no Connect counterpart yet.

    // ── notification ────────────────────────────────────────────────────
    // REST surface dropped; covered by notification_connect.rs.

    // ── organization ────────────────────────────────────────────────────
    // REST surface dropped; covered by organization.rs Connect block.

    // ── promocode ───────────────────────────────────────────────────────
    // REST surface dropped; validate / redeem / history all live on
    // proto.promocode.v1.PromoCodeService — covered by
    // promocode_connect.rs and the wasm service tests.

    // ── repository ──────────────────────────────────────────────────────
    // REST surface dropped; covered by repository.rs Connect block.

    // ── ticket_relations ────────────────────────────────────────────────
    // REST mocks removed: REST surface eliminated; Connect handler tests in
    // backend/internal/api/connect/ticket_relations cover the same surface.

    // ── token_usage ─────────────────────────────────────────────────────
    // REST surface dropped; covered by token_usage_connect.rs.

    // ── user_agent_credential ───────────────────────────────────────────
    // REST surface dropped; covered by user_agent_credential_connect.rs.

    // ── user_git_credential ─────────────────────────────────────────────
    // REST surface dropped; covered by user_git_credential_connect.rs.

    // ── user_repository_provider ────────────────────────────────────────
    // REST surface dropped; covered by user_repository_provider_connect.rs.
}
