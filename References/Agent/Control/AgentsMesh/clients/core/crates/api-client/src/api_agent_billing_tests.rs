#[cfg(test)]
mod api_agent_billing_tests {
    use std::sync::Mutex;

    use serde_json::json;
    use wiremock::matchers::{method, path, query_param};
    use wiremock::{Mock, MockServer, ResponseTemplate};

    use crate::{ApiClient, AuthTokenStore};

    struct MockTokenStore {
        org_slug: Mutex<Option<String>>,
    }
    impl MockTokenStore {
        fn with_org(slug: &str) -> std::sync::Arc<Self> {
            std::sync::Arc::new(Self { org_slug: Mutex::new(Some(slug.into())) })
        }
        fn no_org() -> std::sync::Arc<Self> {
            std::sync::Arc::new(Self { org_slug: Mutex::new(None) })
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

    // ── agentpod ────────────────────────────────────────────────────────
    // REST surface dropped; covered by agentpod.rs Connect block.

    // ── autopilot ───────────────────────────────────────────────────────
    // REST surface dropped; covered by autopilot_connect.rs.

    // ── billing ─────────────────────────────────────────────────────────
    // REST surface dropped entirely; covered by billing.rs Connect block.
    // Subscription / plans / invoices / seats / overview / usage / quota all
    // route through proto.billing.v1.BillingService now.
}
