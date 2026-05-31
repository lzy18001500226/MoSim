use std::sync::Arc;

use agentsmesh_protocol::MsgType;
use agentsmesh_transport::runtime::{PlatformRuntime, Runtime, TaskHandle};
use futures::channel::mpsc;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RelayStatus {
    Connecting,
    Connected,
    Disconnected,
    Error,
}

impl std::fmt::Display for RelayStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Connecting => write!(f, "connecting"),
            Self::Connected => write!(f, "connected"),
            Self::Disconnected => write!(f, "disconnected"),
            Self::Error => write!(f, "error"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct SnapshotData {
    pub serialized_content: Option<String>,
    pub cols: u16,
    pub rows: u16,
}

pub type OutputCallback = Arc<dyn Fn(Vec<u8>) + Send + Sync>;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RelayStatusInfo {
    pub status: RelayStatus,
    pub runner_disconnected: bool,
}

pub type StatusCallback = Arc<dyn Fn(RelayStatusInfo) + Send + Sync>;
pub type AcpCallback = Arc<dyn Fn(MsgType, serde_json::Value) + Send + Sync>;

pub struct ConnectionHandle {
    pub pod_key: String,
    pub subscription_id: String,
    send_tx: mpsc::UnboundedSender<Vec<u8>>,
    unsubscribe_tx: mpsc::UnboundedSender<(String, String)>,
}

impl ConnectionHandle {
    pub fn new(
        pod_key: String,
        subscription_id: String,
        send_tx: mpsc::UnboundedSender<Vec<u8>>,
        unsubscribe_tx: mpsc::UnboundedSender<(String, String)>,
    ) -> Self {
        Self {
            pod_key,
            subscription_id,
            send_tx,
            unsubscribe_tx,
        }
    }

    pub fn send(&self, data: Vec<u8>) {
        let _ = self.send_tx.unbounded_send(data);
    }

    pub fn unsubscribe(&self) {
        let _ = self
            .unsubscribe_tx
            .unbounded_send((self.pod_key.clone(), self.subscription_id.clone()));
    }
}

pub(crate) struct ConnectionState<R: Runtime = PlatformRuntime> {
    pub status: RelayStatus,
    pub subscribers: std::collections::HashMap<String, OutputCallback>,
    pub reconnect_attempts: u32,
    pub snapshot_received: bool,
    pub pod_size: Option<(u16, u16)>,
    pub runner_disconnected: bool,
    pub relay_url: String,
    pub relay_token: String,
    pub ws_write_tx: Option<mpsc::UnboundedSender<Vec<u8>>>,
    pub reconnect_handle: Option<R::TaskHandle>,
    pub disconnect_handle: Option<R::TaskHandle>,
    pub snapshot_handle: Option<R::TaskHandle>,
    pub read_handle: Option<R::TaskHandle>,
    pub pending_resize: Option<(u16, u16)>,
}

impl<R: Runtime> ConnectionState<R> {
    pub fn new(relay_url: String, relay_token: String) -> Self {
        Self {
            status: RelayStatus::Connecting,
            subscribers: std::collections::HashMap::new(),
            reconnect_attempts: 0,
            snapshot_received: false,
            pod_size: None,
            runner_disconnected: false,
            relay_url,
            relay_token,
            ws_write_tx: None,
            reconnect_handle: None,
            disconnect_handle: None,
            snapshot_handle: None,
            read_handle: None,
            pending_resize: None,
        }
    }

    pub fn cancel_timers(&mut self) {
        if let Some(h) = self.reconnect_handle.take() {
            h.abort();
        }
        if let Some(h) = self.disconnect_handle.take() {
            h.abort();
        }
        if let Some(h) = self.snapshot_handle.take() {
            h.abort();
        }
    }
}
