use std::sync::Arc;

use serde::{Deserialize, Serialize};

use crate::event_types::EventType;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ConnectionState {
    Disconnected,
    Connecting,
    Connected,
    Reconnecting,
}

impl std::fmt::Display for ConnectionState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Disconnected => f.write_str("disconnected"),
            Self::Connecting => f.write_str("connecting"),
            Self::Connected => f.write_str("connected"),
            Self::Reconnecting => f.write_str("reconnecting"),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum EventCategory {
    Entity,
    Notification,
    System,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RealtimeEvent {
    #[serde(rename = "type")]
    pub event_type: EventType,
    #[serde(default)]
    pub category: Option<EventCategory>,
    #[serde(default)]
    pub organization_id: i64,
    pub target_user_id: Option<i64>,
    pub target_user_ids: Option<Vec<i64>>,
    pub entity_type: Option<String>,
    pub entity_id: Option<String>,
    #[serde(default)]
    pub data: serde_json::Value,
    #[serde(default)]
    pub timestamp: i64,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct SubscriptionId(pub(crate) u64);

impl SubscriptionId {
    pub fn as_u64(self) -> u64 {
        self.0
    }

    pub fn from_u64(val: u64) -> Self {
        Self(val)
    }
}

pub type EventHandler = Arc<dyn Fn(&RealtimeEvent) + Send + Sync>;
pub type StateListener = Arc<dyn Fn(ConnectionState) + Send + Sync>;

#[derive(Debug, Clone, Serialize)]
pub struct PingMessage {
    #[serde(rename = "type")]
    pub msg_type: String,
    pub timestamp: i64,
}

impl PingMessage {
    pub fn new(timestamp: i64) -> Self {
        Self {
            msg_type: "ping".to_string(),
            timestamp,
        }
    }
}

pub struct EventSubscriptionManagerOptions {
    pub max_reconnect_attempts: u32,
    pub initial_reconnect_delay_ms: u64,
    pub max_reconnect_delay_ms: u64,
    pub ping_interval_ms: u64,
    pub pong_timeout_ms: u64,
}

impl Default for EventSubscriptionManagerOptions {
    fn default() -> Self {
        Self {
            max_reconnect_attempts: 10,
            initial_reconnect_delay_ms: 1000,
            max_reconnect_delay_ms: 30000,
            ping_interval_ms: 30000,
            pong_timeout_ms: 10000,
        }
    }
}
