// EnvBundle client: Connect-RPC only. The REST wrappers were retired in R6
// alongside the backend REST handlers; everything routes through prost +
// connect_call now.

use crate::ApiClient;
use crate::connect_call::connect_call;
use crate::error::ApiError;
use agentsmesh_types::proto_env_bundle_v1 as eb_proto;

impl ApiClient {
    pub async fn list_user_env_bundles_connect(
        &self, req: &eb_proto::ListEnvBundlesRequest,
    ) -> Result<eb_proto::ListEnvBundlesResponse, ApiError> {
        connect_call(
            self,
            "/proto.env_bundle.v1.EnvBundleService/ListEnvBundles",
            req,
        )
        .await
    }

    pub async fn get_user_env_bundle_connect(
        &self, req: &eb_proto::GetEnvBundleRequest,
    ) -> Result<eb_proto::EnvBundle, ApiError> {
        connect_call(
            self,
            "/proto.env_bundle.v1.EnvBundleService/GetEnvBundle",
            req,
        )
        .await
    }

    pub async fn create_user_env_bundle_connect(
        &self, req: &eb_proto::CreateEnvBundleRequest,
    ) -> Result<eb_proto::EnvBundle, ApiError> {
        connect_call(
            self,
            "/proto.env_bundle.v1.EnvBundleService/CreateEnvBundle",
            req,
        )
        .await
    }

    pub async fn update_user_env_bundle_connect(
        &self, req: &eb_proto::UpdateEnvBundleRequest,
    ) -> Result<eb_proto::EnvBundle, ApiError> {
        connect_call(
            self,
            "/proto.env_bundle.v1.EnvBundleService/UpdateEnvBundle",
            req,
        )
        .await
    }

    pub async fn delete_user_env_bundle_connect(
        &self, req: &eb_proto::DeleteEnvBundleRequest,
    ) -> Result<eb_proto::DeleteEnvBundleResponse, ApiError> {
        connect_call(
            self,
            "/proto.env_bundle.v1.EnvBundleService/DeleteEnvBundle",
            req,
        )
        .await
    }

    pub async fn set_primary_env_bundle_connect(
        &self, req: &eb_proto::SetPrimaryEnvBundleRequest,
    ) -> Result<eb_proto::SetPrimaryEnvBundleResponse, ApiError> {
        connect_call(
            self,
            "/proto.env_bundle.v1.EnvBundleService/SetPrimaryEnvBundle",
            req,
        )
        .await
    }
}
