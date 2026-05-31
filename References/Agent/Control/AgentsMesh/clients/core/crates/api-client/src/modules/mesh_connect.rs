use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_mesh_v1 as mp;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================

impl ApiClient {
    pub async fn get_mesh_topology_connect(
        &self,
        req: &mp::GetMeshTopologyRequest,
    ) -> Result<mp::MeshTopology, ApiError> {
        connect_call(self, "/proto.mesh.v1.MeshService/GetMeshTopology", req).await
    }

    pub async fn get_ticket_pods_connect(
        &self,
        req: &mp::GetTicketPodsRequest,
    ) -> Result<mp::GetTicketPodsResponse, ApiError> {
        connect_call(self, "/proto.mesh.v1.MeshService/GetTicketPods", req).await
    }

    pub async fn batch_get_ticket_pods_connect(
        &self,
        req: &mp::BatchGetTicketPodsRequest,
    ) -> Result<mp::BatchGetTicketPodsResponse, ApiError> {
        connect_call(self, "/proto.mesh.v1.MeshService/BatchGetTicketPods", req).await
    }

    pub async fn create_pod_for_ticket_connect(
        &self,
        req: &mp::CreatePodForTicketRequest,
    ) -> Result<mp::MeshNode, ApiError> {
        connect_call(self, "/proto.mesh.v1.MeshService/CreatePodForTicket", req).await
    }
}
