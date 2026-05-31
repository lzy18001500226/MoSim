use agentsmesh_types::proto_sso_v1 as sso_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{AuthSessionDto, SSOConfigDto, UserDto};
use crate::error::CoreError;

/// SSO discovery + LDAP sign-in for enterprise tenants.
/// Connect-RPC binary wire (proto.sso.v1.SSOService).
/// OAuth / SAML flows are handled via `SSOAuthUrlParams` on the browser;
/// iOS defers those to ASWebAuthenticationSession and does not need FFI
/// support for the redirect leg.
#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    /// Discover which SSO providers are configured for an email's domain.
    /// Returns an empty vec if no enterprise SSO is configured.
    pub async fn sso_discover(&self, email: String) -> Result<Vec<SSOConfigDto>, CoreError> {
        let req = sso_proto::DiscoverRequest { email };
        let resp = self.api.sso_discover_connect(&req).await?;
        Ok(resp.items.into_iter().map(SSOConfigDto::from).collect())
    }

    /// LDAP credential-based sign-in.
    pub async fn sso_ldap_login(
        &self,
        domain: String,
        username: String,
        password: String,
    ) -> Result<AuthSessionDto, CoreError> {
        let req = sso_proto::LdapAuthRequest {
            domain,
            username,
            password,
        };
        let resp = self.api.sso_ldap_auth_connect(&req).await?;
        Ok(resp.into())
    }
}

impl From<sso_proto::SsoDiscoverConfig> for SSOConfigDto {
    fn from(c: sso_proto::SsoDiscoverConfig) -> Self {
        Self {
            domain: c.domain,
            protocol: c.protocol,
            name: if c.name.is_empty() { None } else { Some(c.name) },
            enforce_sso: Some(c.enforce_sso),
        }
    }
}

impl From<sso_proto::LdapAuthResponse> for AuthSessionDto {
    fn from(r: sso_proto::LdapAuthResponse) -> Self {
        let user = r.user.map(UserDto::from).unwrap_or(UserDto {
            id: 0,
            email: String::new(),
            username: String::new(),
            name: None,
            avatar_url: None,
            is_email_verified: None,
        });
        Self {
            token: r.token,
            refresh_token: r.refresh_token,
            user,
            // LdapAuthResponse carries `expires_at` (RFC3339 string), not
            // `expires_in` (seconds). The Swift side does not consume it
            // for LDAP — token refresh runs against the bearer's exp claim.
            expires_in: None,
        }
    }
}

impl From<sso_proto::LdapAuthUser> for UserDto {
    fn from(u: sso_proto::LdapAuthUser) -> Self {
        Self {
            id: u.id,
            email: u.email,
            username: u.username,
            name: u.name,
            avatar_url: None,
            is_email_verified: None,
        }
    }
}
