use agentsmesh_types::proto_channel_v1 as channel_proto;
use serde_json::Value;

use crate::dto::{
    ChannelDto, ChannelMemberDto, ChannelMemberListResponseDto, ChannelMessageDto,
    ChannelMessageListResponseDto, ChannelUnreadResponseDto, PodDto, PodListResponseDto,
    PodStatusDto, SenderAgentInfoDto, SenderPodInfoDto, UserDto,
};

impl From<channel_proto::Channel> for ChannelDto {
    fn from(c: channel_proto::Channel) -> Self {
        Self {
            id: c.id,
            name: c.name,
            description: c.description,
            is_archived: c.is_archived,
            visibility: Some(c.visibility),
            is_member: c.is_member,
            member_count: Some(c.member_count),
            agent_count: Some(c.agent_count),
            organization_id: Some(c.organization_id),
            document: c.document,
            repository_id: c.repository_id,
            ticket_id: c.ticket_id,
            ticket_slug: c.ticket_slug,
            created_by_pod: c.created_by_pod,
            created_by_user_id: c.created_by_user_id,
            created_at: Some(c.created_at),
            updated_at: Some(c.updated_at),
        }
    }
}

impl From<channel_proto::ChannelMessage> for ChannelMessageDto {
    fn from(m: channel_proto::ChannelMessage) -> Self {
        Self {
            id: m.id,
            channel_id: m.channel_id,
            body: m.body,
            content_json: m.content_json,
            mentions_json: m.mentions_json,
            reply_to: m.reply_to,
            sender_user: m.sender_user.map(sender_user_to_user_dto),
            sender_user_id: m.sender_user_id,
            sender_pod: m.sender_pod,
            sender_pod_info: m.sender_pod_info.map(SenderPodInfoDto::from),
            message_type: Some(m.message_type),
            edited_at: m.edited_at,
            is_deleted: Some(m.is_deleted),
            created_at: Some(m.created_at),
        }
    }
}

fn sender_user_to_user_dto(u: channel_proto::ChannelMessageSenderUser) -> UserDto {
    UserDto {
        id: u.id,
        email: String::new(),
        username: u.username,
        name: u.name,
        avatar_url: u.avatar_url,
        is_email_verified: None,
    }
}

impl From<channel_proto::ChannelMessageSenderPod> for SenderPodInfoDto {
    fn from(p: channel_proto::ChannelMessageSenderPod) -> Self {
        Self {
            pod_key: p.pod_key,
            alias: p.alias,
            agent: p.agent.map(|a| SenderAgentInfoDto { name: a.name }),
        }
    }
}

impl From<channel_proto::ChannelMember> for ChannelMemberDto {
    fn from(m: channel_proto::ChannelMember) -> Self {
        Self {
            channel_id: m.channel_id,
            user_id: m.user_id,
            role: m.role,
            is_muted: m.is_muted,
            joined_at: m.joined_at,
        }
    }
}

pub(crate) fn channel_message_list_from_proto(
    resp: channel_proto::ListChannelMessagesResponse,
) -> ChannelMessageListResponseDto {
    ChannelMessageListResponseDto {
        messages: resp.items.into_iter().map(ChannelMessageDto::from).collect(),
    }
}

pub(crate) fn channel_unread_from_proto(
    resp: channel_proto::GetChannelUnreadCountsResponse,
) -> ChannelUnreadResponseDto {
    ChannelUnreadResponseDto {
        unread: resp.unread.into_iter().map(|(k, v)| (k, v as u32)).collect(),
    }
}

pub(crate) fn member_list_from_proto(
    resp: channel_proto::ListChannelMembersResponse,
) -> ChannelMemberListResponseDto {
    ChannelMemberListResponseDto {
        members: resp.items.into_iter().map(ChannelMemberDto::from).collect(),
        total: resp.total,
    }
}

pub(crate) fn pod_list_from_proto(resp: channel_proto::ListChannelPodsResponse) -> PodListResponseDto {
    let pods = resp
        .items
        .into_iter()
        .map(|p| PodDto {
            key: p.pod_key,
            id: Some(p.id),
            status: pod_status_from_string(&p.status),
            agent_status: Some(p.agent_status),
            alias: p.alias,
            title: None,
            agent_slug: String::new(),
            runner_id: None,
            runner_name: None,
            user_id: None,
            ticket_slug: None,
            channel_id: None,
            runner: None,
            agent: None,
            repository: None,
            ticket: None,
            loop_info: None,
            created_by: None,
            prompt: None,
            branch_name: None,
            sandbox_path: None,
            started_at: None,
            finished_at: None,
            last_activity: None,
            created_at: None,
            updated_at: None,
            interaction_mode: None,
            perpetual: None,
            restart_count: None,
            last_restart_at: None,
            error_code: None,
            error_message: None,
        })
        .collect();
    PodListResponseDto { pods, total: Some(resp.total) }
}

fn pod_status_from_string(s: &str) -> PodStatusDto {
    match s {
        "pending" => PodStatusDto::Pending,
        "creating" => PodStatusDto::Creating,
        "initializing" => PodStatusDto::Initializing,
        "running" | "ready" | "active" => PodStatusDto::Running,
        "paused" => PodStatusDto::Paused,
        "stopping" | "terminating" => PodStatusDto::Stopping,
        "disconnected" => PodStatusDto::Disconnected,
        "orphaned" => PodStatusDto::Orphaned,
        "completed" => PodStatusDto::Completed,
        "terminated" => PodStatusDto::Terminated,
        "error" => PodStatusDto::Error,
        "failed" => PodStatusDto::Failed,
        _ => PodStatusDto::Unknown,
    }
}

pub(crate) fn send_message_inputs(
    content_json: &str,
) -> Result<(Option<String>, Option<String>, Option<String>, Option<String>, Option<i64>), serde_json::Error> {
    let value: Value = serde_json::from_str(content_json)?;
    let Some(obj) = value.as_object() else {
        return Ok((None, Some(content_json.to_string()), None, None, None));
    };
    let has_wrapper = obj.contains_key("source")
        || obj.contains_key("content")
        || obj.contains_key("mentions")
        || obj.contains_key("attachment_key")
        || obj.contains_key("pod_key")
        || obj.contains_key("reply_to");
    if !has_wrapper {
        return Ok((None, Some(content_json.to_string()), None, None, None));
    }
    let source = obj.get("source").and_then(Value::as_str).map(str::to_owned);
    let content = obj.get("content").map(|v| serde_json::to_string(v).unwrap_or_default());
    let attachment_key = obj
        .get("attachment_key")
        .and_then(Value::as_str)
        .map(str::to_owned);
    let pod_key = obj.get("pod_key").and_then(Value::as_str).map(str::to_owned);
    let reply_to = obj.get("reply_to").and_then(Value::as_i64);
    Ok((source, content, attachment_key, pod_key, reply_to))
}
