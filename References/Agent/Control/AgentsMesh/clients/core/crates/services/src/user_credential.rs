// proto.user_credential.v1 — three sub-services (UserGitCredentialService,
// UserAgentCredentialService, UserRepositoryProviderService) share this
// thin owner of the ApiClient. Each method decodes the prost request,
// forwards to the api-client `*_connect` method, and re-encodes the
// response — binary wire (conventions §2.5).

use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_types::proto_user_credential_v1 as uc_proto;
use prost::Message;

pub struct UserCredentialService {
    client: Arc<ApiClient>,
}

impl UserCredentialService {
    pub fn new(client: Arc<ApiClient>) -> Self {
        Self { client }
    }

    pub(crate) fn client(&self) -> &ApiClient {
        &self.client
    }
}

// -------- UserGitCredentialService (8 RPCs) --------

impl UserCredentialService {
    pub async fn list_git_credentials_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let _ = uc_proto::ListGitCredentialsRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_git_credentials request: {e}"))?;
        let resp = self.client().list_git_credentials_connect().await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_git_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::GetGitCredentialRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_git_credential request: {e}"))?;
        let resp = self.client().get_git_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn create_git_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::CreateGitCredentialRequest::decode(request_bytes)
            .map_err(|e| format!("decode create_git_credential request: {e}"))?;
        let resp = self.client().create_git_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_git_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::UpdateGitCredentialRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_git_credential request: {e}"))?;
        let resp = self.client().update_git_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn delete_git_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::DeleteGitCredentialRequest::decode(request_bytes)
            .map_err(|e| format!("decode delete_git_credential request: {e}"))?;
        let resp = self.client().delete_git_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_default_git_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let _ = uc_proto::GetDefaultGitCredentialRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_default_git_credential request: {e}"))?;
        let resp = self.client().get_default_git_credential_connect().await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn set_default_git_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::SetDefaultGitCredentialRequest::decode(request_bytes)
            .map_err(|e| format!("decode set_default_git_credential request: {e}"))?;
        let resp = self.client().set_default_git_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn clear_default_git_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let _ = uc_proto::ClearDefaultGitCredentialRequest::decode(request_bytes)
            .map_err(|e| format!("decode clear_default_git_credential request: {e}"))?;
        let resp = self.client().clear_default_git_credential_connect().await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }
}

// -------- UserAgentCredentialService (7 RPCs) --------

impl UserCredentialService {
    pub async fn list_agent_credentials_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let _ = uc_proto::ListAgentCredentialProfilesRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_agent_credentials request: {e}"))?;
        let resp = self.client().list_agent_credentials_connect().await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_agent_credentials_for_agent_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::ListAgentCredentialProfilesForAgentRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_agent_credentials_for_agent request: {e}"))?;
        let resp = self.client().list_agent_credentials_for_agent_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_agent_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::GetAgentCredentialProfileRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_agent_credential request: {e}"))?;
        let resp = self.client().get_agent_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn create_agent_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::CreateAgentCredentialProfileRequest::decode(request_bytes)
            .map_err(|e| format!("decode create_agent_credential request: {e}"))?;
        let resp = self.client().create_agent_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_agent_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::UpdateAgentCredentialProfileRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_agent_credential request: {e}"))?;
        let resp = self.client().update_agent_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn delete_agent_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::DeleteAgentCredentialProfileRequest::decode(request_bytes)
            .map_err(|e| format!("decode delete_agent_credential request: {e}"))?;
        let resp = self.client().delete_agent_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn set_default_agent_credential_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::SetDefaultAgentCredentialProfileRequest::decode(request_bytes)
            .map_err(|e| format!("decode set_default_agent_credential request: {e}"))?;
        let resp = self.client().set_default_agent_credential_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }
}

// -------- UserRepositoryProviderService (8 RPCs) --------

impl UserCredentialService {
    pub async fn list_repository_providers_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let _ = uc_proto::ListRepositoryProvidersRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_repository_providers request: {e}"))?;
        let resp = self.client().list_repository_providers_connect().await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn get_repository_provider_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::GetRepositoryProviderRequest::decode(request_bytes)
            .map_err(|e| format!("decode get_repository_provider request: {e}"))?;
        let resp = self.client().get_repository_provider_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn create_repository_provider_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::CreateRepositoryProviderRequest::decode(request_bytes)
            .map_err(|e| format!("decode create_repository_provider request: {e}"))?;
        let resp = self.client().create_repository_provider_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn update_repository_provider_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::UpdateRepositoryProviderRequest::decode(request_bytes)
            .map_err(|e| format!("decode update_repository_provider request: {e}"))?;
        let resp = self.client().update_repository_provider_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn delete_repository_provider_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::DeleteRepositoryProviderRequest::decode(request_bytes)
            .map_err(|e| format!("decode delete_repository_provider request: {e}"))?;
        let resp = self.client().delete_repository_provider_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn set_default_repository_provider_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::SetDefaultRepositoryProviderRequest::decode(request_bytes)
            .map_err(|e| format!("decode set_default_repository_provider request: {e}"))?;
        let resp = self.client().set_default_repository_provider_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn test_repository_provider_connection_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::TestRepositoryProviderConnectionRequest::decode(request_bytes)
            .map_err(|e| format!("decode test_repository_provider_connection request: {e}"))?;
        let resp = self.client().test_repository_provider_connection_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }

    pub async fn list_provider_repositories_connect(&self, request_bytes: &[u8]) -> Result<Vec<u8>, String> {
        let req = uc_proto::ListProviderRepositoriesRequest::decode(request_bytes)
            .map_err(|e| format!("decode list_provider_repositories request: {e}"))?;
        let resp = self.client().list_provider_repositories_connect(&req).await.map_err(crate::wire)?;
        Ok(resp.encode_to_vec())
    }
}
