use agentsmesh_types::proto_pod_v1 as pod_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{
    build_create_pod_proto_request, CreatePodRequestDto, CreatePodResponseDto,
    PodConnectionInfoDto, PodDto, PodListResponseDto,
};
use crate::error::CoreError;

/// Pod lifecycle — list/create/terminate/alias, plus relay connection info
/// for terminal attach. Input/resize/signals go via the relay WebSocket
/// (Swift side uses `relay_encode_*` + SwiftTerm delegate, not through FFI).
///
/// Connect-RPC binary wire (proto.pod.v1.PodService). REST is gone from the
/// client surface — backend mirrors are scheduled for removal once auth /
/// runner-auth catch up (the only callers still on REST in this crate).
#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    pub async fn list_pods(
        &self,
        status: Option<String>,
        runner_id: Option<i64>,
        created_by_id: Option<i64>,
        limit: Option<i64>,
        offset: Option<i64>,
    ) -> Result<PodListResponseDto, CoreError> {
        let req = pod_proto::ListPodsRequest {
            org_slug: self.org_slug()?,
            status,
            created_by_id,
            limit: limit.map(|v| v as i32),
            offset: offset.map(|v| v as i32),
            runner_id,
        };
        let resp = self.api.list_pods_connect(&req).await?;
        Ok(resp.into())
    }

    pub async fn get_pod(&self, pod_key: String) -> Result<PodDto, CoreError> {
        let req = pod_proto::GetPodRequest {
            org_slug: self.org_slug()?,
            pod_key,
        };
        let pod = self.api.get_pod_connect(&req).await?;
        Ok(pod.into())
    }

    pub async fn create_pod(
        &self,
        req: CreatePodRequestDto,
    ) -> Result<CreatePodResponseDto, CoreError> {
        let proto_req = build_create_pod_proto_request(self.org_slug()?, req);
        let resp = self.api.create_pod_connect(&proto_req).await?;
        Ok(resp.into())
    }

    pub async fn terminate_pod(&self, pod_key: String) -> Result<(), CoreError> {
        let req = pod_proto::TerminatePodRequest {
            org_slug: self.org_slug()?,
            pod_key,
        };
        self.api.terminate_pod_connect(&req).await?;
        Ok(())
    }

    pub async fn update_pod_alias(
        &self,
        pod_key: String,
        alias: Option<String>,
    ) -> Result<PodDto, CoreError> {
        let req = pod_proto::UpdatePodAliasRequest {
            org_slug: self.org_slug()?,
            pod_key: pod_key.clone(),
            alias,
        };
        self.api.update_pod_alias_connect(&req).await?;
        // UpdatePodAlias proto returns only `message`; re-fetch the pod so
        // FFI callers still get the strongly-typed updated record.
        let get = pod_proto::GetPodRequest {
            org_slug: self.org_slug()?,
            pod_key,
        };
        let pod = self.api.get_pod_connect(&get).await?;
        Ok(pod.into())
    }

    /// Relay WS connection info. The proto service collapses the two REST
    /// variants (direct vs relay-hop) into a single `GetPodConnection` —
    /// the response carries both `relay_url` and `local_relay_url`. We
    /// expose them via the same FFI methods for source compat; both go to
    /// the same RPC.
    pub async fn get_pod_connection_info(
        &self,
        pod_key: String,
    ) -> Result<PodConnectionInfoDto, CoreError> {
        let req = pod_proto::GetPodConnectionRequest {
            org_slug: self.org_slug()?,
            pod_key,
        };
        let info = self.api.get_pod_connection_connect(&req).await?;
        Ok(info.into())
    }

    pub async fn get_pod_relay_connection(
        &self,
        pod_key: String,
    ) -> Result<PodConnectionInfoDto, CoreError> {
        self.get_pod_connection_info(pod_key).await
    }
}
