use agentsmesh_types::proto_runner_api_v1 as runner_proto;
use agentsmesh_types::{AuthorizeRunnerRequest, RunnerAuthStatus};

#[derive(Clone, Copy, Debug, uniffi::Enum)]
pub enum RunnerStatusDto {
    Online,
    Offline,
    Maintenance,
    Unknown,
}

fn parse_proto_runner_status(s: &str) -> RunnerStatusDto {
    match s {
        "online" => RunnerStatusDto::Online,
        "offline" => RunnerStatusDto::Offline,
        "maintenance" => RunnerStatusDto::Maintenance,
        _ => RunnerStatusDto::Unknown,
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct RunnerDto {
    pub id: i64,
    pub name: String,
    pub node_id: Option<String>,
    pub description: Option<String>,
    pub status: RunnerStatusDto,
    pub version: Option<String>,
    pub max_concurrent_pods: i32,
    pub active_pod_count: i32,
    pub is_enabled: bool,
    /// Raw `serde_json::Value` serialized to JSON — Swift side decodes if it
    /// needs specific fields. Keeps DTO schema stable across runner versions.
    pub host_info_json: Option<String>,
    pub last_heartbeat: Option<String>,
    pub available_agents: Option<Vec<String>>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

impl From<runner_proto::Runner> for RunnerDto {
    fn from(r: runner_proto::Runner) -> Self {
        let host_info_json = if r.host_info_json.is_empty() {
            None
        } else {
            Some(r.host_info_json)
        };
        Self {
            id: r.id,
            // Legacy DTO `name` mirrored node_id at the REST layer — preserve.
            name: r.node_id.clone(),
            node_id: Some(r.node_id),
            description: if r.description.is_empty() { None } else { Some(r.description) },
            status: parse_proto_runner_status(&r.status),
            version: r.runner_version,
            max_concurrent_pods: r.max_concurrent_pods,
            // proto carries current_pods on the entity; the legacy DTO called
            // this active_pod_count.
            active_pod_count: r.current_pods,
            is_enabled: r.is_enabled,
            host_info_json,
            last_heartbeat: r.last_heartbeat,
            available_agents: Some(r.available_agents),
            created_at: if r.created_at.is_empty() { None } else { Some(r.created_at) },
            updated_at: if r.updated_at.is_empty() { None } else { Some(r.updated_at) },
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct RunnerListResponseDto {
    pub runners: Vec<RunnerDto>,
    pub latest_runner_version: Option<String>,
}

pub(crate) fn runner_list_from_proto(
    resp: runner_proto::ListRunnersResponse,
) -> RunnerListResponseDto {
    RunnerListResponseDto {
        runners: resp.items.into_iter().map(RunnerDto::from).collect(),
        latest_runner_version: resp.latest_runner_version,
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct GrpcRegistrationTokenDto {
    pub id: i64,
    pub name: Option<String>,
    pub token: Option<String>,
    pub max_uses: Option<i32>,
    pub used_count: Option<i32>,
    pub expires_at: Option<String>,
    pub created_at: Option<String>,
}

impl From<runner_proto::RunnerToken> for GrpcRegistrationTokenDto {
    fn from(t: runner_proto::RunnerToken) -> Self {
        Self {
            id: t.id,
            name: t.name,
            token: t.token,
            max_uses: t.max_uses,
            used_count: t.used_count,
            expires_at: t.expires_at,
            created_at: t.created_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct RunnerTokenListResponseDto {
    pub tokens: Vec<GrpcRegistrationTokenDto>,
}

pub(crate) fn runner_token_list_from_proto(
    resp: runner_proto::ListRunnerTokensResponse,
) -> RunnerTokenListResponseDto {
    RunnerTokenListResponseDto {
        tokens: resp.items.into_iter().map(GrpcRegistrationTokenDto::from).collect(),
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct RunnerAuthStatusDto {
    pub status: String,
    pub runner_id: Option<i64>,
    pub organization_slug: Option<String>,
}

impl From<RunnerAuthStatus> for RunnerAuthStatusDto {
    fn from(s: RunnerAuthStatus) -> Self {
        Self {
            status: s.status,
            runner_id: s.runner_id,
            organization_slug: s.organization_slug,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct UpdateRunnerRequestDto {
    pub description: Option<String>,
    pub max_concurrent_pods: Option<i32>,
    pub is_enabled: Option<bool>,
    pub visibility: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct CreateRunnerTokenRequestDto {
    pub name: Option<String>,
    pub labels: Option<Vec<String>>,
    pub max_uses: Option<i32>,
    pub expires_in_days: Option<i64>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct UpgradeRunnerRequestDto {
    pub target_version: Option<String>,
    pub force: Option<bool>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct AuthorizeRunnerRequestDto {
    pub auth_key: String,
    pub node_id: Option<String>,
}

impl From<AuthorizeRunnerRequestDto> for AuthorizeRunnerRequest {
    fn from(d: AuthorizeRunnerRequestDto) -> Self {
        Self {
            auth_key: d.auth_key,
            node_id: d.node_id,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct RunnerLogDto {
    pub id: i64,
    pub runner_id: i64,
    pub filename: Option<String>,
    pub url: Option<String>,
    pub created_at: Option<String>,
}

impl From<runner_proto::RunnerLog> for RunnerLogDto {
    fn from(l: runner_proto::RunnerLog) -> Self {
        Self {
            id: l.id,
            runner_id: l.runner_id,
            // proto: storage_key (S3 key) is the closest analog to legacy filename.
            filename: l.storage_key,
            url: l.download_url,
            created_at: l.created_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct RunnerLogListResponseDto {
    pub logs: Vec<RunnerLogDto>,
}

pub(crate) fn runner_log_list_from_proto(
    resp: runner_proto::ListRunnerLogsResponse,
) -> RunnerLogListResponseDto {
    RunnerLogListResponseDto {
        logs: resp.items.into_iter().map(RunnerLogDto::from).collect(),
    }
}
