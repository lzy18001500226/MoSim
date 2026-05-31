use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_pod_v1 as pod_proto;

// =============================================================================
// Connect-RPC (binary wire). See proto-naming-conventions.md §2.5.
// =============================================================================
//
// These methods call the Connect handlers in backend/internal/api/connect/pod/.
// Procedure paths derive from `proto.pod.v1.PodService.<Method>` (§12).

impl ApiClient {
    pub async fn list_pods_connect(
        &self,
        req: &pod_proto::ListPodsRequest,
    ) -> Result<pod_proto::ListPodsResponse, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/ListPods", req).await
    }

    pub async fn get_pod_connect(
        &self,
        req: &pod_proto::GetPodRequest,
    ) -> Result<pod_proto::Pod, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/GetPod", req).await
    }

    pub async fn create_pod_connect(
        &self,
        req: &pod_proto::CreatePodRequest,
    ) -> Result<pod_proto::CreatePodResponse, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/CreatePod", req).await
    }

    pub async fn terminate_pod_connect(
        &self,
        req: &pod_proto::TerminatePodRequest,
    ) -> Result<pod_proto::TerminatePodResponse, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/TerminatePod", req).await
    }

    pub async fn update_pod_alias_connect(
        &self,
        req: &pod_proto::UpdatePodAliasRequest,
    ) -> Result<pod_proto::UpdatePodAliasResponse, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/UpdatePodAlias", req).await
    }

    pub async fn update_pod_perpetual_connect(
        &self,
        req: &pod_proto::UpdatePodPerpetualRequest,
    ) -> Result<pod_proto::UpdatePodPerpetualResponse, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/UpdatePodPerpetual", req).await
    }

    pub async fn get_pod_connection_connect(
        &self,
        req: &pod_proto::GetPodConnectionRequest,
    ) -> Result<pod_proto::PodConnectionInfo, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/GetPodConnection", req).await
    }

    pub async fn send_pod_prompt_connect(
        &self,
        req: &pod_proto::SendPodPromptRequest,
    ) -> Result<pod_proto::SendPodPromptResponse, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/SendPodPrompt", req).await
    }

    pub async fn list_pods_by_ticket_connect(
        &self,
        req: &pod_proto::ListPodsByTicketRequest,
    ) -> Result<pod_proto::ListPodsByTicketResponse, ApiError> {
        connect_call(self, "/proto.pod.v1.PodService/ListPodsByTicket", req).await
    }
}
