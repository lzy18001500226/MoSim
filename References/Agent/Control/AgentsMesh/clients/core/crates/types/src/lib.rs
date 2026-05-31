// Client-side wire-format types. Three categories:
//   - `enums::PodStatus` — strongly-typed client mapping for the proto
//     string-status field; used by realtime event dispatch and pod cache.
//   - `runner::*` — REST-only request/response shapes for the runner
//     registration flow (Tailscale-style device authorization), which has
//     no proto coverage on the backend.
//   - `service_error::ServiceError` — tagged-enum error type that bridges
//     Rust errors across the wasm/UniFFI/NAPI boundary.
//
// All business-domain wire types come from the `proto_<svc>_v1` modules
// below — auto-generated prost crates re-exported here for the rest of the
// workspace to consume.

mod enums;
mod runner;
mod service_error;

pub use enums::*;
pub use runner::*;
pub use service_error::*;

// =============================================================================
// Connect-RPC binary-wire DTOs (prost). Single source of truth: the .proto
// schema. Each `proto_<svc>_v1` module re-exports an auto-generated crate
// produced by `rust_prost_library` (see proto/<svc>/v1/BUILD.bazel).
// =============================================================================

pub mod proto_agent_v1 {
    pub use ::agent_proto::proto::agent::v1::*;
}

pub mod proto_apikey_v1 {
    pub use ::apikey_proto::proto::apikey::v1::*;
}

pub mod proto_auth_v1 {
    pub use ::auth_proto::proto::auth::v1::*;
}

pub mod proto_autopilot_v1 {
    pub use ::autopilot_proto::proto::autopilot::v1::*;
}

pub mod proto_billing_v1 {
    pub use ::billing_proto::proto::billing::v1::*;
}

pub mod proto_binding_v1 {
    pub use ::binding_proto::proto::binding::v1::*;
}

pub mod proto_blockstore_v1 {
    pub use ::blockstore_proto::proto::blockstore::v1::*;
}

pub mod proto_channel_v1 {
    pub use ::channel_proto::proto::channel::v1::*;
}

pub mod proto_channel_state_v1 {
    pub use ::channel_state_proto::proto::channel_state::v1::*;
}

pub mod proto_extension_v1 {
    pub use ::extension_proto::proto::extension::v1::*;
}

pub mod proto_env_bundle_v1 {
    pub use ::env_bundle_proto::proto::env_bundle::v1::*;
}

pub mod proto_events_v1 {
    pub use ::events_proto::proto::events::v1::*;
}

pub mod proto_file_v1 {
    pub use ::file_proto::proto::file::v1::*;
}

pub mod proto_grant_v1 {
    pub use ::grant_proto::proto::grant::v1::*;
}

pub mod proto_invitation_v1 {
    pub use ::invitation_proto::proto::invitation::v1::*;
}

pub mod proto_license_v1 {
    pub use ::license_proto::proto::license::v1::*;
}

// `loop` is a Rust keyword; the prost-generated module uses the `r#loop`
// raw identifier and we forward that through the re-export.
pub mod proto_loop_v1 {
    pub use ::loop_proto::proto::r#loop::v1::*;
}

pub mod proto_mesh_v1 {
    pub use ::mesh_proto::proto::mesh::v1::*;
}

pub mod proto_notification_v1 {
    pub use ::notification_proto::proto::notification::v1::*;
}

pub mod proto_org_v1 {
    pub use ::org_proto::proto::org::v1::*;
}

pub mod proto_pod_v1 {
    pub use ::pod_proto::proto::pod::v1::*;
}

pub mod proto_promocode_v1 {
    pub use ::promocode_proto::proto::promocode::v1::*;
}

pub mod proto_repository_v1 {
    pub use ::repository_proto::proto::repository::v1::*;
}

pub mod proto_runner_api_v1 {
    pub use ::runner_api_proto::proto::runner_api::v1::*;
}

pub mod proto_sso_v1 {
    pub use ::sso_proto::proto::sso::v1::*;
}

pub mod proto_support_ticket_v1 {
    pub use ::support_ticket_proto::proto::support_ticket::v1::*;
}

pub mod proto_ticket_v1 {
    pub use ::ticket_proto::proto::ticket::v1::*;
}

pub mod proto_ticket_relations_v1 {
    pub use ::ticket_relations_proto::proto::ticket_relations::v1::*;
}

pub mod proto_token_usage_v1 {
    pub use ::token_usage_proto::proto::token_usage::v1::*;
}

pub mod proto_user_v1 {
    pub use ::user_proto::proto::user::v1::*;
}

pub mod proto_user_credential_v1 {
    pub use ::user_credential_proto::proto::user_credential::v1::*;
}

#[cfg(test)]
mod proto_serde_poc {
    //! R2 PoC: proto types double as wire DTO (prost::Message) and
    //! JSON-friendly cache/state type (serde derive). This test verifies that
    //! the `rust_prost_transform` injection in proto/<svc>/v1/BUILD.bazel
    //! actually produced the expected derives.
    use crate::proto_pod_v1::Pod;
    use prost::Message;

    #[test]
    fn pod_serde_roundtrip() {
        let pod = Pod {
            pod_key: "test-key".into(),
            alias: Some("my-pod".into()),
            ..Default::default()
        };
        let json = serde_json::to_string(&pod).unwrap();
        let decoded: Pod = serde_json::from_str(&json).unwrap();
        assert_eq!(decoded.pod_key, "test-key");
        assert_eq!(decoded.alias.as_deref(), Some("my-pod"));
    }

    #[test]
    fn pod_prost_still_works() {
        let pod = Pod {
            pod_key: "test-key".into(),
            ..Default::default()
        };
        let bytes = pod.encode_to_vec();
        let decoded = Pod::decode(&*bytes).unwrap();
        assert_eq!(decoded.pod_key, "test-key");
    }
}
