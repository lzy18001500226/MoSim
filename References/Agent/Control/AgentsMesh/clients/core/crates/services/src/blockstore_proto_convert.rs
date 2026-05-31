// Proto ↔ internal type conversions for the blockstore service. Wire types
// carry `data` / `meta` / `payload` / `forward` / `inverse` as opaque JSON
// strings; the internal `Block`/`BlockOp` types hold `serde_json::Value`.
// Conversions parse the JSON once at the boundary, matching what the legacy
// REST path delivered.

use agentsmesh_state::blockstore_types::{
    ActorType, Block, BlockOp, BlockRef, OpEnvelope, OpKind, SearchHit, Workspace,
};
use agentsmesh_types::proto_blockstore_v1 as blockstore_proto;
use serde_json::Value;


// Synthesize a BlockOp from an envelope when the server returned op_ids but
// no full ops (happy path on apply_ops). Keeps the local mutation logic in one
// place (apply_remote_op) so replay and realtime paths converge.
pub(super) fn synthesize_op(workspace_id: &str, id: i64, env: &OpEnvelope, applied_at: &str) -> BlockOp {
    let mut forward = env.payload.clone();
    // Server assigns ids/timestamps on create. For local apply we tolerate
    // missing fields — the forward is a best-effort projection used only to
    // keep the client cache warm until `catchup_ops` delivers the canonical op.
    if matches!(env.op, OpKind::AddRef) {
        if let Value::Object(ref mut m) = forward {
            m.entry("id").or_insert(Value::from(id));
        }
    }
    BlockOp {
        id,
        workspace_id: workspace_id.to_string(),
        idempotency_key: None,
        actor_type: ActorType::User,
        actor_id: 0,
        op: env.op.clone(),
        target_block: None,
        target_ref: None,
        payload: env.payload.clone(),
        forward,
        inverse: Value::Null,
        parent_op_id: None,
        applied_at: applied_at.to_string(),
    }
}

pub(super) fn chrono_like_now() -> String {
    // Services crate is WASM-compatible: avoid chrono. The server replaces this
    // with its authoritative timestamp via catchup_ops.
    "".into()
}

// ── proto.blockstore.v1 → internal type conversions ──
//
// Proto carries `data`/`meta`/`payload`/`forward`/`inverse` as opaque JSON
// strings; the internal `Block`/`BlockOp` types hold `serde_json::Value`.
// Conversions parse the JSON once at the boundary, matching what the legacy
// REST path delivered.

pub(super) fn json_string_to_value(s: &str) -> Result<Value, String> {
    if s.is_empty() { return Ok(Value::Null); }
    serde_json::from_str(s).map_err(|e| format!("invalid JSON string: {e}"))
}

pub(super) fn workspace_from_proto(w: blockstore_proto::Workspace) -> Workspace {
    Workspace {
        id: w.id,
        organization_id: w.organization_id,
        slug: w.slug,
        name: w.name,
        root_block_id: w.root_block_id,
        created_at: w.created_at,
    }
}

pub(super) fn block_from_proto(b: blockstore_proto::Block) -> Result<Block, String> {
    Ok(Block {
        id: b.id,
        workspace_id: b.workspace_id,
        block_type: b.r#type,
        data: json_string_to_value(&b.data_json)?,
        text: b.text,
        meta: json_string_to_value(&b.meta_json)?,
        created_by: b.created_by,
        created_at: b.created_at,
        updated_at: b.updated_at,
        deleted_at: b.deleted_at,
    })
}

pub(super) fn block_ref_from_proto(r: blockstore_proto::BlockRef) -> Result<BlockRef, String> {
    Ok(BlockRef {
        id: r.id,
        workspace_id: r.workspace_id,
        from_id: r.from_id,
        to_id: r.to_id,
        rel: r.rel,
        order_key: r.order_key,
        anchor: r.anchor,
        meta: json_string_to_value(&r.meta_json)?,
        created_by: r.created_by,
        created_at: r.created_at,
        updated_at: r.updated_at,
    })
}

pub(super) fn block_op_from_proto(o: blockstore_proto::BlockOp) -> Result<BlockOp, String> {
    Ok(BlockOp {
        id: o.id,
        workspace_id: o.workspace_id,
        idempotency_key: o.idempotency_key,
        actor_type: parse_actor_type(&o.actor_type),
        actor_id: o.actor_id,
        op: parse_op_kind(&o.op)?,
        target_block: o.target_block,
        target_ref: o.target_ref,
        payload: json_string_to_value(&o.payload_json)?,
        forward: json_string_to_value(&o.forward_json)?,
        inverse: json_string_to_value(&o.inverse_json)?,
        parent_op_id: o.parent_op_id,
        applied_at: o.applied_at,
    })
}

pub(super) fn parse_actor_type(s: &str) -> ActorType {
    match s {
        "user" => ActorType::User,
        "agent" => ActorType::Agent,
        _ => ActorType::System,
    }
}

pub(super) fn parse_op_kind(s: &str) -> Result<OpKind, String> {
    // Proto carries OpKind as a serde-camelCase string (matching the JSON wire
    // shape) so callers can decode without a parallel enum vocabulary.
    match s {
        "createBlock" => Ok(OpKind::CreateBlock),
        "updateBlock" => Ok(OpKind::UpdateBlock),
        "deleteBlock" => Ok(OpKind::DeleteBlock),
        "addRef" => Ok(OpKind::AddRef),
        "removeRef" => Ok(OpKind::RemoveRef),
        "updateRef" => Ok(OpKind::UpdateRef),
        other => Err(format!("unknown op kind: {other}")),
    }
}

pub(super) fn search_hit_from_proto(h: blockstore_proto::SearchHit) -> SearchHit {
    SearchHit {
        block_id: h.block_id,
        block_type: h.r#type,
        snippet: h.snippet,
        score: h.score as f64,
    }
}

pub(super) fn op_kind_to_proto_string(k: &OpKind) -> &'static str {
    match k {
        OpKind::CreateBlock => "createBlock",
        OpKind::UpdateBlock => "updateBlock",
        OpKind::DeleteBlock => "deleteBlock",
        OpKind::AddRef => "addRef",
        OpKind::RemoveRef => "removeRef",
        OpKind::UpdateRef => "updateRef",
    }
}

pub(super) fn op_envelope_to_proto(env: &OpEnvelope) -> blockstore_proto::OpEnvelope {
    blockstore_proto::OpEnvelope {
        op: op_kind_to_proto_string(&env.op).to_string(),
        payload_json: serde_json::to_string(&env.payload).unwrap_or_else(|_| "null".into()),
    }
}
