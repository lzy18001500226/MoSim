use agentsmesh_types::proto_channel_v1 as channel_proto;

use crate::core::AgentsMeshCore;
use crate::dto::{
    ChannelDto, ChannelListResponseDto, ChannelMemberListResponseDto, CreateChannelRequestDto,
    PodListResponseDto, UpdateChannelRequestDto,
};
use crate::error::CoreError;
use crate::services::channel_proto_convert::{member_list_from_proto, pod_list_from_proto};

#[uniffi::export(async_runtime = "tokio")]
impl AgentsMeshCore {
    pub async fn list_channels(
        &self,
        include_archived: Option<bool>,
    ) -> Result<ChannelListResponseDto, CoreError> {
        let req = channel_proto::ListChannelsRequest {
            org_slug: self.org_slug()?,
            include_archived,
            ..Default::default()
        };
        let resp = self.api.list_channels_connect(&req).await?;
        Ok(ChannelListResponseDto {
            channels: resp.items.into_iter().map(ChannelDto::from).collect(),
        })
    }

    pub async fn get_channel(&self, id: i64) -> Result<ChannelDto, CoreError> {
        let req = channel_proto::GetChannelRequest { org_slug: self.org_slug()?, id };
        let ch = self.api.get_channel_connect(&req).await?;
        Ok(ch.into())
    }

    pub async fn create_channel(
        &self,
        req: CreateChannelRequestDto,
    ) -> Result<ChannelDto, CoreError> {
        let proto_req = channel_proto::CreateChannelRequest {
            org_slug: self.org_slug()?,
            name: req.name,
            description: req.description,
            document: req.document,
            repository_id: req.repository_id,
            ticket_slug: req.ticket_slug,
            visibility: None,
            member_ids: Vec::new(),
        };
        let ch = self.api.create_channel_connect(&proto_req).await?;
        Ok(ch.into())
    }

    pub async fn update_channel(
        &self,
        id: i64,
        req: UpdateChannelRequestDto,
    ) -> Result<ChannelDto, CoreError> {
        let proto_req = channel_proto::UpdateChannelRequest {
            org_slug: self.org_slug()?,
            id,
            name: req.name,
            description: req.description,
            document: None,
        };
        let ch = self.api.update_channel_connect(&proto_req).await?;
        Ok(ch.into())
    }

    pub async fn archive_channel(&self, id: i64) -> Result<(), CoreError> {
        let req = channel_proto::ArchiveChannelRequest { org_slug: self.org_slug()?, id };
        self.api.archive_channel_connect(&req).await?;
        Ok(())
    }

    pub async fn unarchive_channel(&self, id: i64) -> Result<(), CoreError> {
        let req = channel_proto::UnarchiveChannelRequest { org_slug: self.org_slug()?, id };
        self.api.unarchive_channel_connect(&req).await?;
        Ok(())
    }

    pub async fn mute_channel(&self, id: i64, muted: bool) -> Result<(), CoreError> {
        let req = channel_proto::MuteChannelRequest {
            org_slug: self.org_slug()?,
            id,
            muted,
        };
        self.api.mute_channel_connect(&req).await?;
        Ok(())
    }

    pub async fn get_channel_pods(&self, id: i64) -> Result<PodListResponseDto, CoreError> {
        let req = channel_proto::ListChannelPodsRequest { org_slug: self.org_slug()?, id };
        let resp = self.api.list_channel_pods_connect(&req).await?;
        Ok(pod_list_from_proto(resp))
    }

    pub async fn join_channel_pod(&self, id: i64, pod_key: String) -> Result<(), CoreError> {
        let req = channel_proto::JoinChannelPodRequest {
            org_slug: self.org_slug()?,
            id,
            pod_key,
        };
        self.api.join_channel_pod_connect(&req).await?;
        Ok(())
    }

    pub async fn leave_channel_pod(
        &self,
        id: i64,
        pod_key: String,
    ) -> Result<(), CoreError> {
        let req = channel_proto::LeaveChannelPodRequest {
            org_slug: self.org_slug()?,
            id,
            pod_key,
        };
        self.api.leave_channel_pod_connect(&req).await?;
        Ok(())
    }

    pub async fn list_channel_members(
        &self,
        id: i64,
    ) -> Result<ChannelMemberListResponseDto, CoreError> {
        let req = channel_proto::ListChannelMembersRequest {
            org_slug: self.org_slug()?,
            id,
            limit: None,
            offset: None,
        };
        let resp = self.api.list_channel_members_connect(&req).await?;
        Ok(member_list_from_proto(resp))
    }

    pub async fn invite_channel_members(
        &self,
        id: i64,
        user_ids: Vec<i64>,
    ) -> Result<(), CoreError> {
        let req = channel_proto::InviteChannelMembersRequest {
            org_slug: self.org_slug()?,
            id,
            user_ids,
        };
        self.api.invite_channel_members_connect(&req).await?;
        Ok(())
    }

    pub async fn remove_channel_member(
        &self,
        id: i64,
        user_id: i64,
    ) -> Result<(), CoreError> {
        let req = channel_proto::RemoveChannelMemberRequest {
            org_slug: self.org_slug()?,
            id,
            user_id,
        };
        self.api.remove_channel_member_connect(&req).await?;
        Ok(())
    }
}
