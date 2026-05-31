use std::collections::HashMap;

use agentsmesh_types::proto_mesh_v1 as mesh_proto;
use agentsmesh_types::proto_notification_v1 as notification_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{
    notification_list_from_proto, BlockDto, ChildrenResultDto,
    MeshTopologyDto, NotificationPreferenceListResponseDto, SearchHitDto, SemanticSearchRequestDto,
    SetNotificationPreferenceRequestDto, WorkspaceDto,
};
use crate::error::CoreError;

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    // ── Mesh ──────────────────────────────────────────────

    pub async fn get_mesh_topology(&self) -> Result<MeshTopologyDto, CoreError> {
        let req = mesh_proto::GetMeshTopologyRequest { org_slug: self.org_slug()? };
        let resp = self.api.get_mesh_topology_connect(&req).await?;
        Ok(resp.into())
    }

    // ── Notifications ─────────────────────────────────────

    pub async fn get_notification_preferences(
        &self,
    ) -> Result<NotificationPreferenceListResponseDto, CoreError> {
        let req = notification_proto::ListPreferencesRequest { org_slug: self.org_slug()? };
        let resp = self.api.list_notification_preferences_connect(&req).await?;
        Ok(notification_list_from_proto(resp))
    }

    pub async fn set_notification_preference(
        &self,
        req: SetNotificationPreferenceRequestDto,
    ) -> Result<(), CoreError> {
        // Legacy DTO `channels` is Vec<String> (the channels to enable). Proto
        // SetPreferenceRequest carries a HashMap<String,bool> — each enabled
        // channel maps to true. Empty channels list → empty map (server defaults).
        let channels: HashMap<String, bool> = req
            .channels
            .unwrap_or_default()
            .into_iter()
            .map(|k| (k, true))
            .collect();
        let proto_req = notification_proto::SetPreferenceRequest {
            org_slug: self.org_slug()?,
            source: req.source,
            entity_id: req.entity_id,
            is_muted: req.is_muted.unwrap_or(false),
            channels,
        };
        self.api.set_notification_preference_connect(&proto_req).await?;
        Ok(())
    }

    // ── Blockstore ─ all routes the local SSOT (`self.blockstore`) ──
    // Mutations land in service state; sync flat-map readers below
    // serve from the same state without a backend round-trip — same
    // contract the WebView-embedded `BlockstoreService` expects.

    // ── Connect-RPC (binary wire) — forwarded to the underlying
    // `BlockstoreService::*_connect` macro-generated bridges. iOS embed
    // mode's `RpcBlockstoreService` (web/lib/ios-bridge) routes web
    // `blockstoreConnect` calls through amBridge into these methods.

    pub async fn blocks_apply_ops_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.apply_ops_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_list_workspaces_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.list_workspaces_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_ensure_default_workspace_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.ensure_default_workspace_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_create_workspace_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.create_workspace_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_delete_workspace_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.delete_workspace_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_get_block_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.get_block_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_list_children_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.list_children_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_list_backlinks_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.list_backlinks_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_get_subtree_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.get_subtree_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_stream_ops_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.stream_ops_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_list_type_defs_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.list_type_defs_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub async fn blocks_semantic_search_connect(&self, request: Vec<u8>) -> Result<Vec<u8>, CoreError> {
        self.blockstore.semantic_search_connect(&request).await.map_err(|m| CoreError::Unknown { message: m })
    }

    pub fn blocks_apply_remote_op(&self, op_json: String) -> Result<(), CoreError> {
        self.blockstore.apply_remote_op(&op_json).map_err(|m| CoreError::Unknown { message: m })
    }

    // Sync flat-map readers — return string snapshots of the in-process
    // state. WebView's RpcBlockstoreService caches these and serves
    // synchronous reads (`blocks_json()` etc.) from cache.
    pub fn blocks_workspaces_json(&self) -> String { self.blockstore.workspaces_json() }
    pub fn blocks_blocks_json(&self) -> String { self.blockstore.blocks_json() }
    pub fn blocks_refs_json(&self) -> String { self.blockstore.refs_json() }
    pub fn blocks_nest_children_json(&self) -> String { self.blockstore.nest_children_json() }
    pub fn blocks_backlinks_json(&self) -> String { self.blockstore.backlinks_json() }
    pub fn blocks_last_op_ids_json(&self) -> String { self.blockstore.last_op_ids_json() }

    pub fn blocks_get_block_json(&self, id: String) -> Option<String> {
        self.blockstore.get_block_json(&id)
    }
    pub fn blocks_list_children_json(&self, parent_id: String) -> String {
        self.blockstore.list_children_json(&parent_id)
    }
    pub fn blocks_list_backlinks_json(&self, target_id: String) -> String {
        self.blockstore.list_backlinks_json(&target_id)
    }
    pub fn blocks_type_defs_json(&self, workspace_id: String) -> String {
        self.blockstore.type_defs_json(&workspace_id)
    }
    pub fn blocks_last_op_id(&self, workspace_id: String) -> i64 {
        self.blockstore.last_op_id(&workspace_id)
    }
    pub fn blocks_set_last_op_id(&self, workspace_id: String, id: i64) {
        self.blockstore.set_last_op_id(&workspace_id, id);
    }

    // Bulk state-cache mutators — webview RPC bridge (iOS embed mode)
    // calls these after fetching via the binary-wire `_connect` methods
    // above, so the Rust SSOT cache stays warm without an extra fetch.

    pub fn blocks_replace_workspaces_json(&self, list_json: String) -> Result<(), CoreError> {
        self.blockstore.replace_workspaces_json(&list_json).map_err(|m| CoreError::Unknown { message: m })
    }

    pub fn blocks_upsert_workspace_json(&self, ws_json: String) -> Result<(), CoreError> {
        self.blockstore.upsert_workspace_json(&ws_json).map_err(|m| CoreError::Unknown { message: m })
    }

    pub fn blocks_upsert_blocks_json(&self, blocks_json: String) -> Result<(), CoreError> {
        self.blockstore.upsert_blocks_json(&blocks_json).map_err(|m| CoreError::Unknown { message: m })
    }

    pub fn blocks_upsert_refs_json(&self, refs_json: String) -> Result<(), CoreError> {
        self.blockstore.upsert_refs_json(&refs_json).map_err(|m| CoreError::Unknown { message: m })
    }

    /// Search-hit DTO export — kept typed so a Swift caller (e.g. a
    /// future native semantic-search UI) doesn't have to JSON-parse.
    pub async fn blocks_semantic_search(
        &self, workspace_id: String, req: SemanticSearchRequestDto,
    ) -> Result<Vec<SearchHitDto>, CoreError> {
        let req: agentsmesh_state::blockstore_types::SemanticSearchRequest = req.into();
        let req_json = serde_json::to_string(&req).unwrap_or_else(|_| "{}".into());
        let resp = self.blockstore
            .semantic_search(&workspace_id, &req_json).await
            .map_err(|m| CoreError::Unknown { message: m })?;
        let hits: Vec<agentsmesh_state::blockstore_types::SearchHit> = serde_json::from_str(&resp)
            .map_err(|e| CoreError::Unknown { message: format!("decode hits: {e}") })?;
        Ok(hits.into_iter().map(SearchHitDto::from).collect())
    }

    // ── Typed wrappers — for native TCA reducers that prefer Swift
    // structs over JSON strings. Each one fans out the JSON call and
    // decodes once on the Rust side; saves 2 JSON parses on Swift side.

    pub async fn blocks_ensure_default_workspace(&self) -> Result<WorkspaceDto, CoreError> {
        let json = self.blockstore.ensure_default_workspace().await
            .map_err(|m| CoreError::Unknown { message: m })?;
        let ws: agentsmesh_state::blockstore_types::Workspace = serde_json::from_str(&json)
            .map_err(|e| CoreError::Unknown { message: format!("decode workspace: {e}") })?;
        Ok(ws.into())
    }

    pub async fn blocks_list_workspaces(&self) -> Result<Vec<WorkspaceDto>, CoreError> {
        let json = self.blockstore.list_workspaces().await.map_err(|m| CoreError::Unknown { message: m })?;
        #[derive(serde::Deserialize)]
        struct Resp { workspaces: Vec<agentsmesh_state::blockstore_types::Workspace> }
        let r: Resp = serde_json::from_str(&json)
            .map_err(|e| CoreError::Unknown { message: format!("decode workspaces: {e}") })?;
        Ok(r.workspaces.into_iter().map(WorkspaceDto::from).collect())
    }

    pub async fn blocks_get_block(&self, id: String) -> Result<BlockDto, CoreError> {
        let json = self.blockstore.get_block_json(&id)
            .ok_or_else(|| CoreError::Unknown { message: format!("block not found: {id}") })?;
        let b: agentsmesh_state::blockstore_types::Block = serde_json::from_str(&json)
            .map_err(|e| CoreError::Unknown { message: format!("decode block: {e}") })?;
        Ok(b.into())
    }

    pub async fn blocks_get_subtree(
        &self, workspace_id: String, root_id: String, _max_depth: u32,
    ) -> Result<ChildrenResultDto, CoreError> {
        self.blockstore.load_subtree(&workspace_id, &root_id).await
            .map_err(|m| CoreError::Unknown { message: m })?;
        let children_json = self.blockstore.list_children_json(&root_id);
        let children: agentsmesh_state::blockstore_types::ChildrenResult = serde_json::from_str(&children_json)
            .unwrap_or(agentsmesh_state::blockstore_types::ChildrenResult { blocks: vec![], refs: vec![] });
        Ok(children.into())
    }
}
