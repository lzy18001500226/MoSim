use std::collections::HashSet;

use super::{ChannelMessageCache, ChannelState, MAX_CACHED_CHANNELS, MAX_MESSAGES_PER_CHANNEL};
use crate::channel_types::ChannelMessage;

impl ChannelState {
    pub fn add_message(&mut self, channel_id: i64, message: ChannelMessage) -> bool {
        let cache = self
            .message_cache
            .entry(channel_id)
            .or_insert_with(|| ChannelMessageCache { messages: Vec::new(), has_more: false });

        if cache.messages.iter().any(|m| m.id == message.id) {
            return false;
        }
        if let Some(repo) = &self.message_repo {
            let _ = repo.save_message(&message);
        }
        cache.messages.push(message);
        if cache.messages.len() > MAX_MESSAGES_PER_CHANNEL {
            cache.messages.drain(..cache.messages.len() - MAX_MESSAGES_PER_CHANNEL);
            cache.has_more = true;
        }
        self.evict_stale_channels(channel_id);
        true
    }

    /// Handle a new incoming message (from realtime event).
    /// Enriches sender, updates preview/last_activity_at on the Channel, adds to cache.
    /// Unread increment stays with the handler — it has first-hand knowledge of
    /// `isSelf` and `isViewing` which this layer would have to reconstruct.
    pub fn on_new_message(&mut self, mut msg: ChannelMessage) -> bool {
        let channel_id = msg.channel_id;
        self.enrich_sender(&mut msg);
        let preview = Self::make_preview(&msg);
        self.set_last_message(channel_id, preview);
        self.add_message(channel_id, msg)
    }

    pub fn update_message(&mut self, channel_id: i64, message: ChannelMessage) {
        if let Some(cache) = self.message_cache.get_mut(&channel_id) {
            if let Some(m) = cache.messages.iter_mut().find(|m| m.id == message.id) {
                if !message.body.is_empty() { m.body = message.body; }
                if message.content_json.is_some() { m.content_json = message.content_json; }
                if message.mentions_json.is_some() { m.mentions_json = message.mentions_json; }
                if message.reply_to.is_some() { m.reply_to = message.reply_to; }
                if message.edited_at.is_some() { m.edited_at = message.edited_at; }
                if message.metadata_json.is_some() { m.metadata_json = message.metadata_json; }
                if message.sender_user.is_some() { m.sender_user = message.sender_user; }
                if message.sender_user_id.is_some() { m.sender_user_id = message.sender_user_id; }
                if message.sender_pod.is_some() { m.sender_pod = message.sender_pod; }
                if message.sender_pod_info.is_some() { m.sender_pod_info = message.sender_pod_info; }
                if message.message_type.is_some() { m.message_type = message.message_type; }
                if message.is_deleted.is_some() { m.is_deleted = message.is_deleted; }
                if let Some(repo) = &self.message_repo { let _ = repo.save_message(m); }
            }
        }
    }

    pub fn remove_message(&mut self, channel_id: i64, message_id: i64) {
        if let Some(cache) = self.message_cache.get_mut(&channel_id) {
            cache.messages.retain(|m| m.id != message_id);
            if let Some(repo) = &self.message_repo {
                let _ = repo.delete_message(message_id);
            }
        }
    }

    pub fn get_messages(&self, channel_id: i64) -> Option<&ChannelMessageCache> {
        self.message_cache.get(&channel_id)
    }

    pub fn set_messages(&mut self, channel_id: i64, messages: Vec<ChannelMessage>, has_more: bool) {
        if let Some(repo) = &self.message_repo {
            for msg in &messages {
                let _ = repo.save_message(msg);
            }
        }
        if let Some(newest) = messages.last() {
            let preview = Self::make_preview(newest);
            self.set_last_message(channel_id, preview);
        }
        let msg_len = messages.len();
        let (truncated, overflow) = if msg_len > MAX_MESSAGES_PER_CHANNEL {
            (messages[msg_len - MAX_MESSAGES_PER_CHANNEL..].to_vec(), true)
        } else {
            (messages, false)
        };
        self.message_cache.insert(
            channel_id,
            ChannelMessageCache { messages: truncated, has_more: has_more || overflow },
        );
        self.evict_stale_channels(channel_id);
    }

    pub fn prepend_messages(&mut self, channel_id: i64, older: Vec<ChannelMessage>, has_more: bool) {
        let cache = self
            .message_cache
            .entry(channel_id)
            .or_insert_with(|| ChannelMessageCache { messages: Vec::new(), has_more: false });

        let existing_ids: HashSet<i64> = cache.messages.iter().map(|m| m.id).collect();
        let mut merged: Vec<ChannelMessage> = older
            .into_iter()
            .filter(|m| !existing_ids.contains(&m.id))
            .collect();
        merged.extend(cache.messages.drain(..));
        merged.sort_by_key(|m| m.id);

        if let Some(repo) = &self.message_repo {
            for msg in &merged {
                if !existing_ids.contains(&msg.id) {
                    let _ = repo.save_message(msg);
                }
            }
        }

        if merged.len() > MAX_MESSAGES_PER_CHANNEL {
            merged.drain(..merged.len() - MAX_MESSAGES_PER_CHANNEL);
        }

        cache.messages = merged;
        cache.has_more = has_more;
        self.evict_stale_channels(channel_id);
    }

    pub(crate) fn evict_stale_channels(&mut self, keep_id: i64) {
        while self.message_cache.len() > MAX_CACHED_CHANNELS {
            let evict_key = self.message_cache.keys().find(|&&k| k != keep_id).copied();
            match evict_key {
                Some(k) => { self.message_cache.remove(&k); }
                None => break,
            }
        }
    }
}
