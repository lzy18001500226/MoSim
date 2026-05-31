use agentsmesh_types::proto_file_v1 as file_proto;
use agentsmesh_types::proto_grant_v1 as grant_proto;
use agentsmesh_types::proto_invitation_v1 as inv_proto;

// ── Invitation ────────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct InvitationDto {
    pub id: i64,
    pub email: String,
    pub role: String,
    pub status: Option<String>,
    pub token: Option<String>,
    pub organization_name: Option<String>,
    pub organization_slug: Option<String>,
    pub inviter_name: Option<String>,
    pub expires_at: Option<String>,
    pub created_at: Option<String>,
}

impl From<inv_proto::Invitation> for InvitationDto {
    fn from(i: inv_proto::Invitation) -> Self {
        // proto.invitation.v1.Invitation is the org-scoped admin entity —
        // no token, no joined org/inviter names. The legacy DTO surfaces
        // accepted_at as `status` so existing Swift callers keep working.
        let status = i.accepted_at.as_ref().map(|_| "accepted".to_string());
        Self {
            id: i.id,
            email: i.email,
            role: i.role,
            status,
            token: None,
            organization_name: None,
            organization_slug: None,
            inviter_name: None,
            expires_at: if i.expires_at.is_empty() { None } else { Some(i.expires_at) },
            created_at: if i.created_at.is_empty() { None } else { Some(i.created_at) },
        }
    }
}

impl From<inv_proto::InvitationInfo> for InvitationDto {
    fn from(i: inv_proto::InvitationInfo) -> Self {
        // Public unauth endpoint — invite-acceptance landing page payload.
        Self {
            id: i.id,
            email: i.email,
            role: i.role,
            status: None,
            token: None,
            organization_name: Some(i.organization_name),
            organization_slug: Some(i.organization_slug),
            inviter_name: Some(i.inviter_name),
            expires_at: if i.expires_at.is_empty() { None } else { Some(i.expires_at) },
            created_at: None,
        }
    }
}

impl From<inv_proto::PendingInvitation> for InvitationDto {
    fn from(i: inv_proto::PendingInvitation) -> Self {
        // User-scoped pending list — includes token so the UI can deep-link
        // straight into the accept flow.
        Self {
            id: i.id,
            email: String::new(),
            role: i.role,
            status: Some("pending".into()),
            token: Some(i.token),
            organization_name: Some(i.organization_name),
            organization_slug: Some(i.organization_slug),
            inviter_name: None,
            expires_at: if i.expires_at.is_empty() { None } else { Some(i.expires_at) },
            created_at: None,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct InvitationListResponseDto {
    pub invitations: Vec<InvitationDto>,
}

pub(crate) fn invitation_list_from_proto(
    resp: inv_proto::ListInvitationsResponse,
) -> InvitationListResponseDto {
    InvitationListResponseDto {
        invitations: resp.items.into_iter().map(InvitationDto::from).collect(),
    }
}

pub(crate) fn pending_invitation_list_from_proto(
    resp: inv_proto::ListPendingInvitationsResponse,
) -> InvitationListResponseDto {
    InvitationListResponseDto {
        invitations: resp.items.into_iter().map(InvitationDto::from).collect(),
    }
}

// ── File presign ──────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct PresignRequestDto {
    pub filename: String,
    pub content_type: String,
    pub size: i64,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct PresignResponseDto {
    pub put_url: String,
    pub get_url: String,
}

impl From<file_proto::PresignUploadResponse> for PresignResponseDto {
    fn from(r: file_proto::PresignUploadResponse) -> Self {
        Self { put_url: r.put_url, get_url: r.get_url }
    }
}

// ── Resource Grant ────────────────────────────────────────

#[derive(Clone, Debug, uniffi::Record)]
pub struct ResourceGrantUserBriefDto {
    pub id: i64,
    pub email: String,
    pub username: String,
    pub name: Option<String>,
}

impl From<grant_proto::ResourceGrantUser> for ResourceGrantUserBriefDto {
    fn from(u: grant_proto::ResourceGrantUser) -> Self {
        Self {
            id: u.id,
            email: u.email,
            username: u.username,
            name: u.name,
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ResourceGrantDto {
    pub id: i64,
    pub resource_type: String,
    pub resource_id: String,
    pub user_id: i64,
    pub granted_by: i64,
    pub created_at: String,
    pub user: Option<ResourceGrantUserBriefDto>,
    pub granted_by_user: Option<ResourceGrantUserBriefDto>,
}

impl From<grant_proto::ResourceGrant> for ResourceGrantDto {
    fn from(g: grant_proto::ResourceGrant) -> Self {
        Self {
            id: g.id,
            resource_type: g.resource_type,
            resource_id: g.resource_id,
            user_id: g.user_id,
            granted_by: g.granted_by,
            created_at: g.created_at,
            user: g.user.map(Into::into),
            granted_by_user: g.granted_by_user.map(Into::into),
        }
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ResourceGrantListResponseDto {
    pub grants: Vec<ResourceGrantDto>,
}

pub(crate) fn resource_grant_list_from_proto(
    resp: grant_proto::ListGrantsResponse,
) -> ResourceGrantListResponseDto {
    ResourceGrantListResponseDto {
        grants: resp.items.into_iter().map(ResourceGrantDto::from).collect(),
    }
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ResourceGrantResponseDto {
    pub grant: ResourceGrantDto,
}

impl From<grant_proto::ResourceGrant> for ResourceGrantResponseDto {
    fn from(g: grant_proto::ResourceGrant) -> Self {
        Self { grant: g.into() }
    }
}
