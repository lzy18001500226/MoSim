use super::ChannelState;
use agentsmesh_types::proto_pod_v1::Pod;
use crate::channel_types::ChannelMember;

impl ChannelState {
    pub fn set_channel_members(&mut self, channel_id: i64, members: Vec<ChannelMember>) {
        self.members_by_channel.insert(channel_id, members);
    }

    pub fn get_channel_members(&self, channel_id: i64) -> Vec<ChannelMember> {
        self.members_by_channel.get(&channel_id).cloned().unwrap_or_default()
    }

    pub fn remove_channel_member(&mut self, channel_id: i64, user_id: i64) {
        if let Some(list) = self.members_by_channel.get_mut(&channel_id) {
            list.retain(|m| m.user_id != user_id);
        }
    }

    pub fn clear_channel_members(&mut self, channel_id: i64) {
        self.members_by_channel.remove(&channel_id);
    }

    pub fn set_channel_pods(&mut self, channel_id: i64, pods: Vec<Pod>) {
        self.pods_by_channel.insert(channel_id, pods);
    }

    pub fn get_channel_pods(&self, channel_id: i64) -> Vec<Pod> {
        self.pods_by_channel.get(&channel_id).cloned().unwrap_or_default()
    }

    pub fn clear_channel_pods(&mut self, channel_id: i64) {
        self.pods_by_channel.remove(&channel_id);
    }
}
