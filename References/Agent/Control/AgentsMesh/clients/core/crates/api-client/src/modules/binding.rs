// proto.binding.v1.BindingService Connect-RPC client bindings. Procedure
// paths derive from `proto.binding.v1.BindingService.<Method>` (conventions
// §12). The legacy REST surface was retired; Connect handlers in
// backend/internal/api/connect/binding/ now own the data plane.

use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_binding_v1 as bp;

impl ApiClient {
    pub async fn request_binding_connect(
        &self,
        req: &bp::RequestBindingRequest,
    ) -> Result<bp::PodBinding, ApiError> {
        connect_call(
            self,
            "/proto.binding.v1.BindingService/RequestBinding",
            req,
        )
        .await
    }

    pub async fn accept_binding_connect(
        &self,
        req: &bp::AcceptBindingRequest,
    ) -> Result<bp::PodBinding, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/AcceptBinding", req).await
    }

    pub async fn reject_binding_connect(
        &self,
        req: &bp::RejectBindingRequest,
    ) -> Result<bp::PodBinding, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/RejectBinding", req).await
    }

    pub async fn unbind_connect(
        &self,
        req: &bp::UnbindRequest,
    ) -> Result<bp::UnbindResponse, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/Unbind", req).await
    }

    pub async fn request_binding_scopes_connect(
        &self,
        req: &bp::RequestScopesRequest,
    ) -> Result<bp::PodBinding, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/RequestScopes", req).await
    }

    pub async fn approve_binding_scopes_connect(
        &self,
        req: &bp::ApproveScopesRequest,
    ) -> Result<bp::PodBinding, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/ApproveScopes", req).await
    }

    pub async fn list_bindings_connect(
        &self,
        req: &bp::ListBindingsRequest,
    ) -> Result<bp::ListBindingsResponse, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/ListBindings", req).await
    }

    pub async fn get_pending_bindings_connect(
        &self,
        req: &bp::GetPendingBindingsRequest,
    ) -> Result<bp::ListBindingsResponse, ApiError> {
        connect_call(
            self,
            "/proto.binding.v1.BindingService/GetPendingBindings",
            req,
        )
        .await
    }

    pub async fn get_bound_pods_connect(
        &self,
        req: &bp::GetBoundPodsRequest,
    ) -> Result<bp::GetBoundPodsResponse, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/GetBoundPods", req).await
    }

    pub async fn check_binding_connect(
        &self,
        req: &bp::CheckBindingRequest,
    ) -> Result<bp::CheckBindingResponse, ApiError> {
        connect_call(self, "/proto.binding.v1.BindingService/CheckBinding", req).await
    }
}
