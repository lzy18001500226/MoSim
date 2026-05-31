use agentsmesh_auth::{BootstrapCleanupReason, BootstrapResult};
use agentsmesh_state::auth_types::{AuthSession, AuthTokens, Organization, SSOConfig, User, UserIdentity};
use agentsmesh_types::proto_user_v1 as user_proto;

#[derive(Clone, Debug, uniffi::Record)]
pub struct UserDto {
    pub id: i64,
    pub email: String,
    pub username: String,
    pub name: Option<String>,
    pub avatar_url: Option<String>,
    pub is_email_verified: Option<bool>,
}

impl From<User> for UserDto {
    fn from(u: User) -> Self {
        Self {
            id: u.id,
            email: u.email,
            username: u.username,
            name: u.name,
            avatar_url: u.avatar_url,
            is_email_verified: u.is_email_verified,
        }
    }
}

impl From<user_proto::User> for UserDto {
    fn from(u: user_proto::User) -> Self {
        Self {
            id: u.id,
            email: u.email,
            username: u.username,
            name: u.name,
            avatar_url: u.avatar_url,
            is_email_verified: Some(u.is_email_verified),
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct UserIdentityDto {
    pub id: i64,
    pub provider: String,
    pub provider_user_id: Option<String>,
    pub provider_username: Option<String>,
    pub created_at: Option<String>,
}

impl From<UserIdentity> for UserIdentityDto {
    fn from(i: UserIdentity) -> Self {
        Self {
            id: i.id,
            provider: i.provider,
            provider_user_id: i.provider_user_id,
            provider_username: i.provider_username,
            created_at: i.created_at,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct OrganizationDto {
    pub id: i64,
    pub name: String,
    pub slug: String,
    pub role: Option<String>,
    pub logo_url: Option<String>,
    pub subscription_plan: Option<String>,
    pub subscription_status: Option<String>,
}

impl From<Organization> for OrganizationDto {
    fn from(o: Organization) -> Self {
        Self {
            id: o.id,
            name: o.name,
            slug: o.slug,
            role: o.role,
            logo_url: o.logo_url,
            subscription_plan: o.subscription_plan,
            subscription_status: o.subscription_status,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct AuthSessionDto {
    pub token: String,
    pub refresh_token: String,
    pub user: UserDto,
    pub expires_in: Option<i64>,
}

impl From<AuthSession> for AuthSessionDto {
    fn from(s: AuthSession) -> Self {
        Self {
            token: s.token,
            refresh_token: s.refresh_token,
            user: s.user.into(),
            expires_in: s.expires_in,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct AuthTokensDto {
    pub token: String,
    pub refresh_token: String,
    pub expires_in: Option<i64>,
}

impl From<AuthTokens> for AuthTokensDto {
    fn from(t: AuthTokens) -> Self {
        Self {
            token: t.token,
            refresh_token: t.refresh_token,
            expires_in: t.expires_in,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct SSOConfigDto {
    pub domain: String,
    pub protocol: String,
    pub name: Option<String>,
    pub enforce_sso: Option<bool>,
}

impl From<SSOConfig> for SSOConfigDto {
    fn from(c: SSOConfig) -> Self {
        Self {
            domain: c.domain,
            protocol: c.protocol,
            name: c.name,
            enforce_sso: c.enforce_sso,
        }
    }
}

#[derive(Clone, Debug, uniffi::Enum)]
pub enum BootstrapCleanupReasonDto {
    BaseUrlMismatch,
    TokenExpiredAndRefreshFailed,
    UnauthorizedFromIdentityCall,
    StorageCorrupt,
    LegacyDataPurged,
}

impl From<BootstrapCleanupReason> for BootstrapCleanupReasonDto {
    fn from(r: BootstrapCleanupReason) -> Self {
        match r {
            BootstrapCleanupReason::BaseUrlMismatch => Self::BaseUrlMismatch,
            BootstrapCleanupReason::TokenExpiredAndRefreshFailed => Self::TokenExpiredAndRefreshFailed,
            BootstrapCleanupReason::UnauthorizedFromIdentityCall => Self::UnauthorizedFromIdentityCall,
            BootstrapCleanupReason::StorageCorrupt => Self::StorageCorrupt,
            BootstrapCleanupReason::LegacyDataPurged => Self::LegacyDataPurged,
        }
    }
}

#[derive(Clone, Debug, uniffi::Enum)]
pub enum BootstrapResultDto {
    Anonymous,
    Authenticated {
        user: UserDto,
        current_org: Option<OrganizationDto>,
    },
    AnonymousAfterCleanup {
        reason: BootstrapCleanupReasonDto,
    },
}

impl From<BootstrapResult> for BootstrapResultDto {
    fn from(r: BootstrapResult) -> Self {
        match r {
            BootstrapResult::Anonymous => Self::Anonymous,
            BootstrapResult::Authenticated { user, current_org } => Self::Authenticated {
                user: user.into(),
                current_org: current_org.map(Into::into),
            },
            BootstrapResult::AnonymousAfterCleanup { reason } => Self::AnonymousAfterCleanup {
                reason: reason.into(),
            },
        }
    }
}
