use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_services::ChannelService;
use agentsmesh_state::channel_state::ChannelState;
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmChannelService(pub(crate) ChannelService);

#[wasm_bindgen]
impl WasmChannelService {
    pub(crate) fn new(client: Arc<ApiClient>, state: ChannelState) -> Self {
        Self(ChannelService::new(client, state))
    }

    pub fn channels_json(&self) -> String { self.0.channels_json() }

    pub fn current_channel_json(&self) -> JsValue {
        match self.0.current_channel_json() {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn get_channel_json(&self, id: i64) -> JsValue {
        match self.0.get_channel_json(id) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn filter_channels_json(&self, query: &str, include_archived: bool) -> String {
        self.0.filter_channels_json(query, include_archived)
    }

    pub fn get_messages_json(&self, channel_id: i64) -> JsValue {
        match self.0.get_messages_json(channel_id) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn get_unread_count(&self, channel_id: i64) -> u32 { self.0.get_unread_count(channel_id) }
    pub fn total_unread_count(&self) -> u32 { self.0.total_unread_count() }
    pub fn unread_counts_json(&self) -> String { self.0.unread_counts_json() }
    pub fn get_mention_count(&self, channel_id: i64) -> u32 { self.0.get_mention_count(channel_id) }
    pub fn total_mention_count(&self) -> u32 { self.0.total_mention_count() }
    pub fn mention_counts_json(&self) -> String { self.0.mention_counts_json() }

    pub fn sorted_channel_ids_json(&self, mode: &str, include_archived: bool) -> String {
        self.0.sorted_channel_ids_json(mode, include_archived)
    }

    pub fn get_last_message_json(&self, channel_id: i64) -> JsValue {
        match self.0.get_last_message_json(channel_id) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn set_channels(&self, json: &str) { self.0.set_channels(json); }
    pub fn set_current_channel(&self, id: Option<i64>) { self.0.set_current_channel(id); }

    pub fn select_channel(&self, id: Option<i64>) -> JsValue {
        match self.0.select_channel(id) {
            Some(s) => JsValue::from_str(&s),
            None => JsValue::NULL,
        }
    }

    pub fn add_channel_local(&self, json: &str) { self.0.add_channel_local(json); }

    pub fn update_channel_local(&self, id: i64, json: &str) {
        self.0.update_channel_local(id, json);
    }

    pub fn remove_channel_local(&self, id: i64) { self.0.remove_channel_local(id); }

    pub fn set_channel_pods_local(&self, channel_id: i64, json: &str) {
        self.0.set_channel_pods_local(channel_id, json);
    }

    pub fn set_channel_members_local(&self, channel_id: i64, json: &str) {
        self.0.set_channel_members_local(channel_id, json);
    }

    pub fn remove_channel_member_local(&self, channel_id: i64, user_id: i64) {
        self.0.remove_channel_member_local(channel_id, user_id);
    }

    pub fn set_current_user(&self, user_json: &str) { self.0.set_current_user(user_json); }
    pub fn set_current_user_id(&self, user_id: Option<i64>) { self.0.set_current_user_id(user_id); }

    pub fn set_messages(&self, channel_id: i64, json: &str, has_more: bool) {
        self.0.set_messages(channel_id, json, has_more);
    }

    pub fn prepend_messages(&self, channel_id: i64, json: &str, has_more: bool) {
        self.0.prepend_messages(channel_id, json, has_more);
    }

    pub fn add_message(&self, channel_id: i64, json: &str) { self.0.add_message(channel_id, json); }
    pub fn on_new_message(&self, json: &str) -> bool { self.0.on_new_message(json) }

    pub fn update_message_local(&self, channel_id: i64, json: &str) {
        self.0.update_message_local(channel_id, json);
    }

    pub fn remove_message_local(&self, channel_id: i64, message_id: i64) {
        self.0.remove_message_local(channel_id, message_id);
    }

    pub fn set_unread_counts(&self, json: &str) { self.0.set_unread_counts(json); }
    pub fn increment_unread(&self, channel_id: i64) { self.0.increment_unread(channel_id); }
    pub fn clear_channel_unread(&self, channel_id: i64) { self.0.clear_channel_unread(channel_id); }
    pub fn set_mention_counts(&self, json: &str) { self.0.set_mention_counts(json); }
    pub fn increment_mention(&self, channel_id: i64) { self.0.increment_mention(channel_id); }

    pub fn clear_channel_mentions(&self, channel_id: i64) {
        self.0.clear_channel_mentions(channel_id);
    }

    pub fn set_last_message(&self, channel_id: i64, json: &str) {
        self.0.set_last_message(channel_id, json);
    }

    pub fn channel_pods_json(&self, id: i64) -> String {
        self.0.channel_pods_json(id)
    }

    pub fn channel_members_json(&self, id: i64) -> String {
        self.0.channel_members_json(id)
    }
}
