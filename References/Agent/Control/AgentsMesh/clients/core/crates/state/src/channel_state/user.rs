use super::ChannelState;
use crate::channel_types::{ChannelMessage, User};

impl ChannelState {
    pub fn set_current_user_id(&mut self, user_id: Option<i64>) {
        match user_id {
            Some(id) => {
                if self.current_user.as_ref().map(|u| u.id) != Some(id) {
                    self.current_user = Some(User { id, ..Default::default() });
                }
            }
            None => self.current_user = None,
        }
    }

    pub fn set_current_user(&mut self, user: Option<User>) {
        self.current_user = user;
    }

    pub fn current_user_id(&self) -> Option<i64> {
        self.current_user.as_ref().map(|u| u.id)
    }

    pub fn current_user(&self) -> Option<&User> {
        self.current_user.as_ref()
    }

    /// If msg has no sender_user but sender_user_id matches current user, fill it in.
    /// Lets the handler-side enrichment stay generic while keeping per-row JSX cheap.
    pub fn enrich_sender(&self, msg: &mut ChannelMessage) {
        if msg.sender_user.is_some() {
            return;
        }
        if let (Some(sender_id), Some(user)) = (msg.sender_user_id, &self.current_user) {
            if sender_id == user.id && !user.username.is_empty() {
                msg.sender_user = Some(user.clone());
            }
        }
    }
}
