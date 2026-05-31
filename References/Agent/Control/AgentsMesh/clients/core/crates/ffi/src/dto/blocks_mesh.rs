use agentsmesh_types::proto_mesh_v1 as mesh_proto;
use agentsmesh_types::proto_notification_v1 as notification_proto;
use agentsmesh_state::blockstore_types::{
    ActorType, ApplyOpsRequest, ApplyOpsResult, Block, BlockOp, BlockRef, ChildrenResult,
    OpEnvelope, OpKind, SearchHit, SemanticSearchRequest, Workspace,
};

use super::{PodStatusDto, RunnerStatusDto};

// R2: PodStatus wire is `string` in proto.mesh.v1.MeshNode. Parse into
// PodStatusDto here so Swift consumers keep the strongly-typed enum.
fn parse_pod_status_from_str(s: &str) -> PodStatusDto {
    match s {
        "pending" => PodStatusDto::Pending,
        "creating" => PodStatusDto::Creating,
        "initializing" => PodStatusDto::Initializing,
        "running" => PodStatusDto::Running,
        "paused" => PodStatusDto::Paused,
        "stopping" => PodStatusDto::Stopping,
        "disconnected" => PodStatusDto::Disconnected,
        "orphaned" => PodStatusDto::Orphaned,
        "completed" => PodStatusDto::Completed,
        "terminated" => PodStatusDto::Terminated,
        "error" => PodStatusDto::Error,
        "failed" => PodStatusDto::Failed,
        _ => PodStatusDto::Unknown,
    }
}

// ── Blockstore ────────────────────────────────────────────

#[derive(Clone, Copy, Debug, uniffi::Enum)]
pub enum ActorTypeDto {
    User,
    Agent,
    System,
}

impl From<ActorType> for ActorTypeDto {
    fn from(a: ActorType) -> Self {
        match a {
            ActorType::User => Self::User,
            ActorType::Agent => Self::Agent,
            ActorType::System => Self::System,
        }
    }
}

impl From<ActorTypeDto> for ActorType {
    fn from(a: ActorTypeDto) -> Self {
        match a {
            ActorTypeDto::User => Self::User,
            ActorTypeDto::Agent => Self::Agent,
            ActorTypeDto::System => Self::System,
        }
    }
}

#[derive(Clone, Copy, Debug, uniffi::Enum)]
pub enum OpKindDto {
    CreateBlock,
    UpdateBlock,
    DeleteBlock,
    AddRef,
    RemoveRef,
    UpdateRef,
}

impl From<OpKind> for OpKindDto {
    fn from(o: OpKind) -> Self {
        match o {
            OpKind::CreateBlock => Self::CreateBlock,
            OpKind::UpdateBlock => Self::UpdateBlock,
            OpKind::DeleteBlock => Self::DeleteBlock,
            OpKind::AddRef => Self::AddRef,
            OpKind::RemoveRef => Self::RemoveRef,
            OpKind::UpdateRef => Self::UpdateRef,
        }
    }
}

impl From<OpKindDto> for OpKind {
    fn from(o: OpKindDto) -> Self {
        match o {
            OpKindDto::CreateBlock => Self::CreateBlock,
            OpKindDto::UpdateBlock => Self::UpdateBlock,
            OpKindDto::DeleteBlock => Self::DeleteBlock,
            OpKindDto::AddRef => Self::AddRef,
            OpKindDto::RemoveRef => Self::RemoveRef,
            OpKindDto::UpdateRef => Self::UpdateRef,
        }
    }
}

fn value_to_string(v: serde_json::Value) -> String {
    serde_json::to_string(&v).unwrap_or_else(|_| "{}".into())
}

fn string_to_value(s: String) -> serde_json::Value {
    serde_json::from_str(&s).unwrap_or(serde_json::Value::Null)
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct BlockDto {
    pub id: String,
    pub workspace_id: String,
    pub block_type: String,
    pub data_json: String,
    pub text: Option<String>,
    pub meta_json: String,
    pub created_by: i64,
    pub created_at: String,
    pub updated_at: String,
    pub deleted_at: Option<String>,
}

impl From<Block> for BlockDto {
    fn from(b: Block) -> Self {
        Self {
            id: b.id,
            workspace_id: b.workspace_id,
            block_type: b.block_type,
            data_json: value_to_string(b.data),
            text: b.text,
            meta_json: value_to_string(b.meta),
            created_by: b.created_by,
            created_at: b.created_at,
            updated_at: b.updated_at,
            deleted_at: b.deleted_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct BlockRefDto {
    pub id: i64,
    pub workspace_id: String,
    pub from_id: String,
    pub to_id: String,
    pub rel: String,
    pub order_key: Option<String>,
    pub anchor: Option<String>,
    pub meta_json: String,
    pub created_by: i64,
    pub created_at: String,
    pub updated_at: String,
}

impl From<BlockRef> for BlockRefDto {
    fn from(r: BlockRef) -> Self {
        Self {
            id: r.id,
            workspace_id: r.workspace_id,
            from_id: r.from_id,
            to_id: r.to_id,
            rel: r.rel,
            order_key: r.order_key,
            anchor: r.anchor,
            meta_json: value_to_string(r.meta),
            created_by: r.created_by,
            created_at: r.created_at,
            updated_at: r.updated_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct BlockOpDto {
    pub id: i64,
    pub workspace_id: String,
    pub idempotency_key: Option<String>,
    pub actor_type: ActorTypeDto,
    pub actor_id: i64,
    pub op: OpKindDto,
    pub target_block: Option<String>,
    pub target_ref: Option<i64>,
    pub payload_json: String,
    pub forward_json: String,
    pub inverse_json: String,
    pub parent_op_id: Option<i64>,
    pub applied_at: String,
}

impl From<BlockOp> for BlockOpDto {
    fn from(o: BlockOp) -> Self {
        Self {
            id: o.id,
            workspace_id: o.workspace_id,
            idempotency_key: o.idempotency_key,
            actor_type: o.actor_type.into(),
            actor_id: o.actor_id,
            op: o.op.into(),
            target_block: o.target_block,
            target_ref: o.target_ref,
            payload_json: value_to_string(o.payload),
            forward_json: value_to_string(o.forward),
            inverse_json: value_to_string(o.inverse),
            parent_op_id: o.parent_op_id,
            applied_at: o.applied_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct WorkspaceDto {
    pub id: String,
    pub organization_id: i64,
    pub slug: String,
    pub name: String,
    pub root_block_id: Option<String>,
    pub created_at: String,
}

impl From<Workspace> for WorkspaceDto {
    fn from(w: Workspace) -> Self {
        Self {
            id: w.id,
            organization_id: w.organization_id,
            slug: w.slug,
            name: w.name,
            root_block_id: w.root_block_id,
            created_at: w.created_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct OpEnvelopeDto {
    pub op: OpKindDto,
    pub payload_json: String,
}

impl From<OpEnvelopeDto> for OpEnvelope {
    fn from(d: OpEnvelopeDto) -> Self {
        Self {
            op: d.op.into(),
            payload: string_to_value(d.payload_json),
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ApplyOpsRequestDto {
    pub workspace_id: String,
    pub ops: Vec<OpEnvelopeDto>,
    pub idempotency_key: Option<String>,
    pub parent_op_id: Option<i64>,
}

impl From<ApplyOpsRequestDto> for ApplyOpsRequest {
    fn from(d: ApplyOpsRequestDto) -> Self {
        Self {
            workspace_id: d.workspace_id,
            ops: d.ops.into_iter().map(Into::into).collect(),
            idempotency_key: d.idempotency_key,
            parent_op_id: d.parent_op_id,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ApplyOpsResultDto {
    pub op_ids: Vec<i64>,
    pub was_replay: bool,
    pub parent_op_id: Option<i64>,
}

impl From<ApplyOpsResult> for ApplyOpsResultDto {
    fn from(r: ApplyOpsResult) -> Self {
        Self {
            op_ids: r.op_ids,
            was_replay: r.was_replay,
            parent_op_id: r.parent_op_id,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChildrenResultDto {
    pub blocks: Vec<BlockDto>,
    pub refs: Vec<BlockRefDto>,
}

impl From<ChildrenResult> for ChildrenResultDto {
    fn from(r: ChildrenResult) -> Self {
        Self {
            blocks: r.blocks.into_iter().map(BlockDto::from).collect(),
            refs: r.refs.into_iter().map(BlockRefDto::from).collect(),
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct SearchHitDto {
    pub block_id: String,
    pub block_type: String,
    pub snippet: String,
    pub score: f64,
}

impl From<SearchHit> for SearchHitDto {
    fn from(h: SearchHit) -> Self {
        Self {
            block_id: h.block_id,
            block_type: h.block_type,
            snippet: h.snippet,
            score: h.score,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct SemanticSearchRequestDto {
    pub query: String,
    pub top_k: Option<u32>,
    pub min_score: Option<f64>,
    pub block_type: Option<String>,
}

impl From<SemanticSearchRequestDto> for SemanticSearchRequest {
    fn from(d: SemanticSearchRequestDto) -> Self {
        Self {
            query: d.query,
            top_k: d.top_k,
            min_score: d.min_score,
            block_type: d.block_type,
        }
    }
}

// ── Mesh ──────────────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct MeshNodeDto {
    pub pod_key: String,
    pub alias: Option<String>,
    pub status: PodStatusDto,
    pub agent_status: Option<String>,
    pub agent_slug: String,
    pub runner_id: Option<i64>,
    pub model: Option<String>,
    pub title: Option<String>,
    pub ticket_id: Option<i64>,
    pub ticket_slug: Option<String>,
    pub ticket_title: Option<String>,
    pub repository_id: Option<i64>,
    pub created_by_id: Option<i64>,
    pub runner_node_id: Option<String>,
    pub runner_status: Option<String>,
    pub started_at: Option<String>,
}

impl From<mesh_proto::MeshNode> for MeshNodeDto {
    fn from(n: mesh_proto::MeshNode) -> Self {
        Self {
            pod_key: n.pod_key,
            alias: n.alias,
            status: parse_pod_status_from_str(&n.status),
            agent_status: if n.agent_status.is_empty() { None } else { Some(n.agent_status) },
            agent_slug: n.agent_slug,
            runner_id: if n.runner_id == 0 { None } else { Some(n.runner_id) },
            model: n.model,
            title: n.title,
            ticket_id: n.ticket_id,
            ticket_slug: n.ticket_slug,
            ticket_title: n.ticket_title,
            repository_id: n.repository_id,
            created_by_id: if n.created_by_id == 0 { None } else { Some(n.created_by_id) },
            runner_node_id: if n.runner_node_id.is_empty() { None } else { Some(n.runner_node_id) },
            runner_status: if n.runner_status.is_empty() { None } else { Some(n.runner_status) },
            started_at: n.started_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct MeshEdgeDto {
    pub id: Option<i64>,
    pub source: String,
    pub target: String,
    pub binding_status: Option<String>,
    pub status: Option<String>,
    pub granted_scopes: Option<Vec<String>>,
    pub pending_scopes: Option<Vec<String>>,
}

impl From<mesh_proto::MeshEdge> for MeshEdgeDto {
    fn from(e: mesh_proto::MeshEdge) -> Self {
        Self {
            id: if e.id == 0 { None } else { Some(e.id) },
            source: e.source,
            target: e.target,
            binding_status: if e.status.is_empty() { None } else { Some(e.status.clone()) },
            status: if e.status.is_empty() { None } else { Some(e.status) },
            granted_scopes: if e.granted_scopes.is_empty() { None } else { Some(e.granted_scopes) },
            pending_scopes: if e.pending_scopes.is_empty() { None } else { Some(e.pending_scopes) },
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct MeshChannelInfoDto {
    pub id: i64,
    pub name: String,
    pub description: Option<String>,
    pub pod_keys: Vec<String>,
    pub message_count: Option<i64>,
    pub is_archived: Option<bool>,
}

impl From<mesh_proto::ChannelInfo> for MeshChannelInfoDto {
    fn from(c: mesh_proto::ChannelInfo) -> Self {
        Self {
            id: c.id,
            name: c.name,
            description: c.description,
            pod_keys: c.pod_keys,
            message_count: Some(c.message_count as i64),
            is_archived: Some(c.is_archived),
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct MeshRunnerInfoDto {
    pub id: i64,
    pub name: String,
    pub status: RunnerStatusDto,
    pub node_id: Option<String>,
    pub max_concurrent_pods: Option<i32>,
    pub current_pods: Option<i32>,
    pub pod_keys: Vec<String>,
}

// R2: parse proto wire string into the typed UniFFI enum.
fn parse_runner_status_from_str(s: &str) -> RunnerStatusDto {
    match s {
        "online" => RunnerStatusDto::Online,
        "offline" => RunnerStatusDto::Offline,
        "maintenance" => RunnerStatusDto::Maintenance,
        _ => RunnerStatusDto::Unknown,
    }
}

impl From<mesh_proto::RunnerInfo> for MeshRunnerInfoDto {
    fn from(r: mesh_proto::RunnerInfo) -> Self {
        Self {
            id: r.id,
            name: r.node_id.clone(),
            status: parse_runner_status_from_str(&r.status),
            node_id: if r.node_id.is_empty() { None } else { Some(r.node_id) },
            max_concurrent_pods: Some(r.max_concurrent_pods),
            current_pods: Some(r.current_pods),
            pod_keys: Vec::new(),
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct MeshTopologyDto {
    pub nodes: Vec<MeshNodeDto>,
    pub edges: Vec<MeshEdgeDto>,
    pub channels: Vec<MeshChannelInfoDto>,
    pub runners: Vec<MeshRunnerInfoDto>,
}

impl From<mesh_proto::MeshTopology> for MeshTopologyDto {
    fn from(t: mesh_proto::MeshTopology) -> Self {
        Self {
            nodes: t.nodes.into_iter().map(MeshNodeDto::from).collect(),
            edges: t.edges.into_iter().map(MeshEdgeDto::from).collect(),
            channels: t
                .channels
                .into_iter()
                .map(MeshChannelInfoDto::from)
                .collect(),
            runners: t.runners.into_iter().map(MeshRunnerInfoDto::from).collect(),
        }
    }
}

// ── Notification ──────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct NotificationPreferenceDto {
    pub source: Option<String>,
    pub entity_id: Option<String>,
    pub is_muted: Option<bool>,
    pub channels: Option<Vec<String>>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct NotificationPreferenceListResponseDto {
    pub preferences: Vec<NotificationPreferenceDto>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct SetNotificationPreferenceRequestDto {
    pub source: String,
    pub entity_id: Option<String>,
    pub is_muted: Option<bool>,
    pub channels: Option<Vec<String>>,
}

// Proto NotificationPreference carries channels as HashMap<String, bool>;
// the Swift DTO surfaces them as Vec<String> of enabled keys. False entries
// are dropped — matches the REST projection that web/iOS originally consumed.
impl From<notification_proto::NotificationPreference> for NotificationPreferenceDto {
    fn from(p: notification_proto::NotificationPreference) -> Self {
        let channels: Vec<String> = p
            .channels
            .into_iter()
            .filter(|(_, enabled)| *enabled)
            .map(|(k, _)| k)
            .collect();
        Self {
            source: if p.source.is_empty() { None } else { Some(p.source) },
            entity_id: p.entity_id,
            is_muted: Some(p.is_muted),
            channels: Some(channels),
        }
    }
}

pub(crate) fn notification_list_from_proto(
    resp: notification_proto::ListPreferencesResponse,
) -> NotificationPreferenceListResponseDto {
    NotificationPreferenceListResponseDto {
        preferences: resp
            .items
            .into_iter()
            .map(NotificationPreferenceDto::from)
            .collect(),
    }
}

// proto.mesh.v1 MeshTopology → MeshTopologyDto is handled by the standard
// `impl From<mesh_proto::MeshTopology>` above (defined inline alongside the
// per-message converters).
