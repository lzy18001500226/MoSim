use std::collections::HashMap;

use super::UserDto;

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChannelDto {
    pub id: i64,
    pub name: String,
    pub description: Option<String>,
    pub is_archived: bool,
    pub visibility: Option<String>,
    pub is_member: bool,
    pub member_count: Option<i64>,
    pub agent_count: Option<i64>,
    pub organization_id: Option<i64>,
    pub document: Option<String>,
    pub repository_id: Option<i64>,
    pub ticket_id: Option<i64>,
    pub ticket_slug: Option<String>,
    pub created_by_pod: Option<String>,
    pub created_by_user_id: Option<i64>,
    pub created_at: Option<String>,
    pub updated_at: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChannelListResponseDto {
    pub channels: Vec<ChannelDto>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct SenderAgentInfoDto {
    pub name: String,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct SenderPodInfoDto {
    pub pod_key: String,
    pub alias: Option<String>,
    pub agent: Option<SenderAgentInfoDto>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChannelMessageDto {
    pub id: i64,
    pub channel_id: i64,
    pub body: String,
    /// Structured AST (schema_version/kind/blocks) — opaque JSON, Swift decodes.
    pub content_json: Option<String>,
    /// Structured mentions — opaque JSON.
    pub mentions_json: Option<String>,
    pub reply_to: Option<i64>,
    pub sender_user: Option<UserDto>,
    pub sender_user_id: Option<i64>,
    pub sender_pod: Option<String>,
    pub sender_pod_info: Option<SenderPodInfoDto>,
    pub message_type: Option<String>,
    pub edited_at: Option<String>,
    pub is_deleted: Option<bool>,
    pub created_at: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChannelMessageListResponseDto {
    pub messages: Vec<ChannelMessageDto>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct MessagePreviewDto {
    pub sender_name: String,
    pub content_preview: String,
    pub message_type: Option<String>,
    pub timestamp: String,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct CreateChannelRequestDto {
    pub name: String,
    pub description: Option<String>,
    pub document: Option<String>,
    pub repository_id: Option<i64>,
    pub ticket_slug: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct UpdateChannelRequestDto {
    pub name: Option<String>,
    pub description: Option<String>,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChannelMemberDto {
    pub channel_id: i64,
    pub user_id: i64,
    pub role: String,
    pub is_muted: bool,
    pub joined_at: String,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChannelMemberListResponseDto {
    pub members: Vec<ChannelMemberDto>,
    pub total: i64,
}

#[derive(Clone, Debug, uniffi::Record)]
pub struct ChannelUnreadResponseDto {
    pub unread: HashMap<String, u32>,
}
