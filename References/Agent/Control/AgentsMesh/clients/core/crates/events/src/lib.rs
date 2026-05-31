pub(crate) mod connection_loop;
pub mod event_types;
pub mod heartbeat;
pub mod reconnect;
pub mod subscription_manager;
pub mod types;

#[cfg(test)]
mod tests;

pub use event_types::EventType;
pub use reconnect::ReconnectPolicy;
pub use subscription_manager::EventSubscriptionManager;
pub use types::{
    ConnectionState, EventCategory, EventHandler, EventSubscriptionManagerOptions,
    PingMessage, RealtimeEvent, StateListener, SubscriptionId,
};
