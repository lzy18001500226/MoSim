use std::sync::{Arc, RwLock};

use agentsmesh_api_client::ApiClient;
use agentsmesh_state::blockstore_state::BlockstoreState;
use agentsmesh_state::blockstore_types::{
    ApplyOpsRequest, ApplyOpsResult, Block, BlockOp, BlockRef, OpKind,
    SearchHit, SemanticSearchRequest, Workspace,
};
use agentsmesh_types::proto_blockstore_v1 as blockstore_proto;
use prost::Message;

use crate::blockstore_proto_convert::{
    block_from_proto, block_op_from_proto, block_ref_from_proto, chrono_like_now,
    op_envelope_to_proto, search_hit_from_proto, synthesize_op, workspace_from_proto,
};

pub struct BlockstoreService {
    client: Arc<ApiClient>,
    state: RwLock<BlockstoreState>,
}

impl BlockstoreService {
    pub fn new(client: Arc<ApiClient>, state: BlockstoreState) -> Self {
        Self { client, state: RwLock::new(state) }
    }

    pub(crate) fn client(&self) -> &ApiClient { &self.client }

    fn org_slug(&self) -> String { self.client.current_org_slug() }

    // ── Mutations ──

    pub async fn apply_ops(&self, req_json: &str) -> Result<String, String> {
        let req: ApplyOpsRequest = serde_json::from_str(req_json)
            .map_err(|e| format!("invalid ApplyOpsRequest JSON: {e}"))?;
        let proto_req = blockstore_proto::ApplyOpsRequest {
            org_slug: self.org_slug(),
            workspace_id: req.workspace_id.clone(),
            ops: req.ops.iter().map(op_envelope_to_proto).collect(),
            idempotency_key: req.idempotency_key.clone(),
            parent_op_id: req.parent_op_id,
        };
        let resp = self.client.blockstore_apply_ops_connect(&proto_req).await
            .map_err(crate::wire)?;
        let res = ApplyOpsResult {
            op_ids: resp.op_ids,
            was_replay: resp.was_replay,
            parent_op_id: resp.parent_op_id,
        };
        self.apply_local_ops(&req, &res);
        serde_json::to_string(&res).map_err(crate::wire)
    }

    fn apply_local_ops(&self, req: &ApplyOpsRequest, res: &ApplyOpsResult) {
        if res.was_replay { return; }
        let mut state = self.state.write().unwrap();
        let ts = chrono_like_now();
        for (idx, env) in req.ops.iter().enumerate() {
            let Some(&op_id) = res.op_ids.get(idx) else { continue };
            // Ref-level ops (AddRef/RemoveRef/UpdateRef) carry a server-assigned
            // ref_id that the client cannot synthesize. Applying locally with
            // op_id as a stand-in creates a ghost ref; when the authoritative
            // op arrives via WS/catchup the real ref_id is different, so the
            // ghost isn't replaced — it accumulates and causes duplicate nest
            // children (same to_id under two distinct ref ids). Skip locally;
            // the UI reflects the mutation once the server broadcasts the real op.
            if matches!(env.op, OpKind::AddRef | OpKind::RemoveRef | OpKind::UpdateRef) {
                continue;
            }
            let synthetic = synthesize_op(&req.workspace_id, op_id, env, &ts);
            state.apply_remote_op(&synthetic);
        }
    }

    // ── Fetches (cache + return JSON) ──

    pub async fn list_workspaces(&self) -> Result<String, String> {
        let req = blockstore_proto::ListWorkspacesRequest { org_slug: self.org_slug() };
        let resp = self.client.blockstore_list_workspaces_connect(&req).await
            .map_err(crate::wire)?;
        let list: Vec<Workspace> = resp.items.into_iter().map(workspace_from_proto).collect();
        self.state.write().unwrap().replace_workspaces(list.clone());
        serde_json::to_string(&serde_json::json!({ "workspaces": list }))
            .map_err(crate::wire)
    }

    pub async fn ensure_default_workspace(&self) -> Result<String, String> {
        let req = blockstore_proto::EnsureDefaultWorkspaceRequest { org_slug: self.org_slug() };
        let resp = self.client.blockstore_ensure_default_workspace_connect(&req).await
            .map_err(crate::wire)?;
        let ws = workspace_from_proto(resp);
        self.state.write().unwrap().upsert_workspace(ws.clone());
        serde_json::to_string(&ws).map_err(crate::wire)
    }

    pub async fn load_subtree(&self, workspace_id: &str, root_id: &str) -> Result<(), String> {
        let req = blockstore_proto::GetSubtreeRequest {
            org_slug: self.org_slug(),
            workspace_id: workspace_id.to_string(),
            root_id: root_id.to_string(),
            max_depth: Some(64),
        };
        let resp = self.client.blockstore_get_subtree_connect(&req).await
            .map_err(crate::wire)?;
        let mut state = self.state.write().unwrap();
        for b in resp.blocks { state.upsert_block(block_from_proto(b)?); }
        for r in resp.refs { state.upsert_ref(block_ref_from_proto(r)?); }
        // Seed watermark so WS subscription recognises this workspace.
        if state.last_op_id.get(workspace_id).is_none() {
            state.set_last_op_id(workspace_id, 0);
        }
        Ok(())
    }

    pub async fn load_type_defs(&self, workspace_id: &str) -> Result<(), String> {
        let req = blockstore_proto::ListTypeDefsRequest {
            org_slug: self.org_slug(),
            workspace_id: workspace_id.to_string(),
        };
        let resp = self.client.blockstore_list_type_defs_connect(&req).await
            .map_err(crate::wire)?;
        let mut state = self.state.write().unwrap();
        for b in resp.items { state.upsert_block(block_from_proto(b)?); }
        Ok(())
    }

    pub async fn catchup(&self, workspace_id: &str) -> Result<(), String> {
        let after = self.state.read().unwrap().get_last_op_id(workspace_id);
        let req = blockstore_proto::StreamOpsRequest {
            org_slug: self.org_slug(),
            workspace_id: workspace_id.to_string(),
            after: Some(after),
            limit: Some(500),
        };
        let resp = self.client.blockstore_stream_ops_connect(&req).await
            .map_err(crate::wire)?;
        let mut state = self.state.write().unwrap();
        for op in resp.items {
            let op = block_op_from_proto(op)?;
            state.apply_remote_op(&op);
        }
        Ok(())
    }

    pub async fn semantic_search(&self, workspace_id: &str, req_json: &str) -> Result<String, String> {
        let req: SemanticSearchRequest = serde_json::from_str(req_json)
            .map_err(|e| format!("invalid search request: {e}"))?;
        let proto_req = blockstore_proto::SemanticSearchRequest {
            org_slug: self.org_slug(),
            workspace_id: workspace_id.to_string(),
            query: req.query,
            top_k: req.top_k.map(|v| v as i32),
            min_score: req.min_score.map(|v| v as f32),
            r#type: req.block_type,
        };
        let resp = self.client.blockstore_semantic_search_connect(&proto_req).await
            .map_err(crate::wire)?;
        let hits: Vec<SearchHit> = resp.hits.into_iter().map(search_hit_from_proto).collect();
        serde_json::to_string(&serde_json::json!({ "hits": hits })).map_err(crate::wire)
    }

    // ── Remote op stream (realtime) ──

    pub fn apply_remote_op(&self, op_json: &str) -> Result<(), String> {
        let op: BlockOp = serde_json::from_str(op_json)
            .map_err(|e| format!("invalid op JSON: {e}"))?;
        self.state.write().unwrap().apply_remote_op(&op);
        Ok(())
    }

    // ── Getters (sync, return JSON) ──

    pub fn workspaces_json(&self) -> String {
        self.state.read().unwrap().workspaces_json()
    }

    pub fn get_block_json(&self, id: &str) -> Option<String> {
        self.state.read().unwrap().get_block_json(id)
    }

    pub fn list_children_json(&self, parent_id: &str) -> String {
        self.state.read().unwrap().list_children_json(parent_id)
    }

    pub fn list_backlinks_json(&self, target_id: &str) -> String {
        self.state.read().unwrap().list_backlinks_json(target_id)
    }

    pub fn type_defs_json(&self, workspace_id: &str) -> String {
        self.state.read().unwrap().type_defs_json(workspace_id)
    }

    pub fn last_op_id(&self, workspace_id: &str) -> i64 {
        self.state.read().unwrap().get_last_op_id(workspace_id)
    }

    pub fn set_last_op_id(&self, workspace_id: &str, id: i64) {
        self.state.write().unwrap().set_last_op_id(workspace_id, id);
    }

    // ── Bulk state population (consumed by JS Connect adapter callers
    // who fetched via the binary wire and need to push results into the
    // local cache). Each method accepts a JSON-serialized payload and
    // upserts into the SSOT state in a single critical section.

    pub fn replace_workspaces_json(&self, list_json: &str) -> Result<(), String> {
        let list: Vec<Workspace> = serde_json::from_str(list_json)
            .map_err(|e| format!("invalid workspaces JSON: {e}"))?;
        self.state.write().unwrap().replace_workspaces(list);
        Ok(())
    }

    pub fn upsert_workspace_json(&self, ws_json: &str) -> Result<(), String> {
        let ws: Workspace = serde_json::from_str(ws_json)
            .map_err(|e| format!("invalid workspace JSON: {e}"))?;
        self.state.write().unwrap().upsert_workspace(ws);
        Ok(())
    }

    pub fn upsert_blocks_json(&self, blocks_json: &str) -> Result<(), String> {
        let blocks: Vec<Block> = serde_json::from_str(blocks_json)
            .map_err(|e| format!("invalid blocks JSON: {e}"))?;
        let mut state = self.state.write().unwrap();
        for b in blocks { state.upsert_block(b); }
        Ok(())
    }

    pub fn upsert_refs_json(&self, refs_json: &str) -> Result<(), String> {
        let refs: Vec<BlockRef> = serde_json::from_str(refs_json)
            .map_err(|e| format!("invalid refs JSON: {e}"))?;
        let mut state = self.state.write().unwrap();
        for r in refs { state.upsert_ref(r); }
        Ok(())
    }

    /// Project an ApplyOps envelope/result pair into the local cache.
    /// Mirrors `apply_ops`'s side effect so JS callers using the Connect
    /// path can keep the same local-replay semantics.
    pub fn project_local_ops(&self, req_json: &str, res_json: &str) -> Result<(), String> {
        let req: ApplyOpsRequest = serde_json::from_str(req_json)
            .map_err(|e| format!("invalid ApplyOpsRequest JSON: {e}"))?;
        let res: ApplyOpsResult = serde_json::from_str(res_json)
            .map_err(|e| format!("invalid ApplyOpsResult JSON: {e}"))?;
        self.apply_local_ops(&req, &res);
        Ok(())
    }

    pub fn blocks_json(&self) -> String {
        self.state.read().unwrap().blocks_json()
    }

    pub fn refs_json(&self) -> String {
        self.state.read().unwrap().refs_json()
    }

    pub fn nest_children_json(&self) -> String {
        self.state.read().unwrap().nest_children_json()
    }

    pub fn backlinks_json(&self) -> String {
        self.state.read().unwrap().backlinks_json()
    }

    pub fn last_op_ids_json(&self) -> String {
        self.state.read().unwrap().last_op_ids_json()
    }
}

// =============================================================================
// Connect-RPC bridge methods. Binary in (prost-encoded), binary out — same wire
// the wasm/node-bridge layers speak.
// =============================================================================

macro_rules! connect_bridge {
    ($name:ident, $req:ident, $client_call:ident) => {
        pub async fn $name(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
            let req = blockstore_proto::$req::decode(request_bytes)
                .map_err(|e| format!("decode {}: {e}", stringify!($req)))?;
            let resp = self.client().$client_call(&req).await.map_err(crate::wire)?;
            Ok(resp.encode_to_vec())
        }
    };
}

impl BlockstoreService {
    connect_bridge!(apply_ops_connect, ApplyOpsRequest, blockstore_apply_ops_connect);
    connect_bridge!(list_workspaces_connect, ListWorkspacesRequest, blockstore_list_workspaces_connect);
    connect_bridge!(ensure_default_workspace_connect, EnsureDefaultWorkspaceRequest, blockstore_ensure_default_workspace_connect);
    connect_bridge!(create_workspace_connect, CreateWorkspaceRequest, blockstore_create_workspace_connect);
    connect_bridge!(delete_workspace_connect, DeleteWorkspaceRequest, blockstore_delete_workspace_connect);
    connect_bridge!(get_block_connect, GetBlockRequest, blockstore_get_block_connect);
    connect_bridge!(list_children_connect, ListChildrenRequest, blockstore_list_children_connect);
    connect_bridge!(list_backlinks_connect, ListBacklinksRequest, blockstore_list_backlinks_connect);
    connect_bridge!(get_subtree_connect, GetSubtreeRequest, blockstore_get_subtree_connect);
    connect_bridge!(stream_ops_connect, StreamOpsRequest, blockstore_stream_ops_connect);
    connect_bridge!(export_workspace_connect, ExportWorkspaceRequest, blockstore_export_workspace_connect);
    connect_bridge!(list_type_defs_connect, ListTypeDefsRequest, blockstore_list_type_defs_connect);
    connect_bridge!(get_block_at_connect, GetBlockAtRequest, blockstore_get_block_at_connect);
    connect_bridge!(semantic_search_connect, SemanticSearchRequest, blockstore_semantic_search_connect);
    connect_bridge!(memory_retrieve_connect, MemoryRetrieveRequest, blockstore_memory_retrieve_connect);
}
