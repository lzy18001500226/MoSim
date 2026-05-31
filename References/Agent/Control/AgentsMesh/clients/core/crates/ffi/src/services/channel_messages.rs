use std::collections::HashMap;

use agentsmesh_types::proto_channel_v1 as channel_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{ChannelMessageDto, ChannelMessageListResponseDto, ChannelUnreadResponseDto};
use crate::error::CoreError;
use crate::services::channel_proto_convert::{
    channel_message_list_from_proto, channel_unread_from_proto, send_message_inputs,
};

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    pub async fn get_channel_messages(
        &self,
        id: i64,
        limit: Option<u32>,
        before_id: Option<i64>,
    ) -> Result<ChannelMessageListResponseDto, CoreError> {
        let req = channel_proto::ListChannelMessagesRequest {
            org_slug: self.org_slug()?,
            channel_id: id,
            before_id,
            limit: limit.map(|l| l as i32),
        };
        let resp = self.api.list_channel_messages_connect(&req).await?;
        Ok(channel_message_list_from_proto(resp))
    }

    /// Send a channel message. `content_json` is the AST string (validated
    /// by the server; frontend builds it via the agentfile/block editor).
    pub async fn send_channel_message(
        &self,
        id: i64,
        content_json: String,
        pod_key: Option<String>,
        reply_to: Option<i64>,
    ) -> Result<ChannelMessageDto, CoreError> {
        let (source, content_json, attachment_key, override_pod_key, override_reply_to) =
            send_message_inputs(&content_json)?;
        let req = channel_proto::SendChannelMessageRequest {
            org_slug: self.org_slug()?,
            channel_id: id,
            source,
            mentions: HashMap::new(),
            content_json,
            attachment_key,
            pod_key: override_pod_key.or(pod_key),
            reply_to: override_reply_to.or(reply_to),
        };
        let msg = self.api.send_channel_message_connect(&req).await?;
        Ok(msg.into())
    }

    pub async fn edit_channel_message(
        &self,
        channel_id: i64,
        message_id: i64,
        content_json: String,
    ) -> Result<ChannelMessageDto, CoreError> {
        let (source, content_json, attachment_key, _, _) = send_message_inputs(&content_json)?;
        let req = channel_proto::EditChannelMessageRequest {
            org_slug: self.org_slug()?,
            channel_id,
            message_id,
            source,
            mentions: HashMap::new(),
            content_json,
            attachment_key,
        };
        let msg = self.api.edit_channel_message_connect(&req).await?;
        Ok(msg.into())
    }

    pub async fn delete_channel_message(
        &self,
        channel_id: i64,
        message_id: i64,
    ) -> Result<(), CoreError> {
        let req = channel_proto::DeleteChannelMessageRequest {
            org_slug: self.org_slug()?,
            channel_id,
            message_id,
        };
        self.api.delete_channel_message_connect(&req).await?;
        Ok(())
    }

    pub async fn mark_channel_read(
        &self,
        id: i64,
        message_id: i64,
    ) -> Result<(), CoreError> {
        let req = channel_proto::MarkChannelReadRequest {
            org_slug: self.org_slug()?,
            channel_id: id,
            message_id,
        };
        self.api.mark_channel_read_connect(&req).await?;
        Ok(())
    }

    pub async fn get_channel_unread_counts(&self) -> Result<ChannelUnreadResponseDto, CoreError> {
        let req = channel_proto::GetChannelUnreadCountsRequest { org_slug: self.org_slug()? };
        let resp = self.api.get_channel_unread_counts_connect(&req).await?;
        Ok(channel_unread_from_proto(resp))
    }
}
