use agentsmesh_state::auth_types::RegisterRequest;

use crate::core::AgentsMeshCore;
use crate::dto::{AuthSessionDto, AuthTokensDto, OrganizationDto};
use crate::error::CoreError;

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    pub async fn login(&self, email: String, password: String) -> Result<AuthSessionDto, CoreError> {
        let session = self.auth.login(&email, &password).await?;
        Ok(session.into())
    }

    pub async fn register(
        &self,
        name: String,
        email: String,
        username: String,
        password: String,
    ) -> Result<AuthSessionDto, CoreError> {
        let req = RegisterRequest {
            name,
            email,
            username,
            password,
        };
        let session = self.auth.register(&req).await?;
        Ok(session.into())
    }

    pub async fn logout(&self) -> Result<(), CoreError> {
        self.auth.logout().await.map_err(CoreError::from)
    }

    pub async fn refresh_token(&self) -> Result<AuthTokensDto, CoreError> {
        let tokens = self.auth.refresh_token().await?;
        Ok(tokens.into())
    }

    pub async fn verify_email(&self, token: String) -> Result<AuthSessionDto, CoreError> {
        let session = self.auth.verify_email(&token).await?;
        Ok(session.into())
    }

    pub async fn forgot_password(&self, email: String) -> Result<(), CoreError> {
        self.auth
            .forgot_password(&email)
            .await
            .map_err(CoreError::from)
    }

    pub async fn reset_password(
        &self,
        token: String,
        new_password: String,
    ) -> Result<(), CoreError> {
        self.auth
            .reset_password(&token, &new_password)
            .await
            .map_err(CoreError::from)
    }

    pub async fn fetch_organizations(&self) -> Result<Vec<OrganizationDto>, CoreError> {
        let orgs = self.auth.fetch_organizations().await?;
        Ok(orgs.into_iter().map(OrganizationDto::from).collect())
    }

    pub fn switch_org(&self, slug: String) -> Result<(), CoreError> {
        self.auth.switch_org(&slug).map_err(CoreError::from)
    }
}
