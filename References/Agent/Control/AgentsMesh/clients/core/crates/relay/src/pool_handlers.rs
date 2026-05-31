use std::collections::HashMap;

use agentsmesh_transport::runtime::{Runtime, TaskHandle};
use tracing::warn;

use crate::dispatch::{dispatch_message, DispatchAction};
use crate::pool::{PoolInner, RelayConnectionPool};
use crate::types::{AcpCallback, ConnectionState, RelayStatus, RelayStatusInfo, StatusCallback};

impl<R: Runtime> RelayConnectionPool<R> {
    pub async fn handle_ws_message(&self, pod_key: &str, data: &[u8]) {
        let (msg_type, payload) = match agentsmesh_protocol::decode_message(data) {
            Ok(v) => v,
            Err(e) => {
                warn!("failed to decode relay message: {e}");
                return;
            }
        };

        let mut inner = self.inner.write();
        let Some(conn) = inner.connections.get_mut(pod_key) else {
            return;
        };

        let subs: Vec<_> = conn.subscribers.values().collect();
        let action = dispatch_message(msg_type, payload, &subs);

        match action {
            DispatchAction::Snapshot(snap) => {
                conn.snapshot_received = true;
                if let Some(h) = conn.snapshot_handle.take() {
                    h.abort();
                }
                if snap.cols > 0 && snap.rows > 0 {
                    conn.pod_size = Some((snap.cols, snap.rows));
                }
            }
            DispatchAction::PodResized { cols, rows } => {
                conn.pod_size = Some((cols, rows));
            }
            DispatchAction::RunnerDisconnected => {
                conn.runner_disconnected = true;
                let info = RelayStatusInfo {
                    status: conn.status,
                    runner_disconnected: true,
                };
                Self::notify_status_info(&inner.status_listeners, pod_key, &info);
            }
            DispatchAction::RunnerReconnected => {
                conn.runner_disconnected = false;
                let info = RelayStatusInfo {
                    status: conn.status,
                    runner_disconnected: false,
                };
                Self::notify_status_info(&inner.status_listeners, pod_key, &info);
            }
            DispatchAction::AcpMessage { msg_type, payload } => {
                if let Some(listeners) = inner.acp_listeners.get(pod_key) {
                    for l in listeners {
                        l(msg_type, payload.clone());
                    }
                }
            }
            DispatchAction::None => {}
        }
    }

    pub async fn on_status_change(&self, pod_key: &str, listener: StatusCallback) {
        let mut inner = self.inner.write();
        let info = inner
            .connections
            .get(pod_key)
            .map(|c| RelayStatusInfo {
                status: c.status,
                runner_disconnected: c.runner_disconnected,
            })
            .unwrap_or(RelayStatusInfo {
                status: RelayStatus::Disconnected,
                runner_disconnected: false,
            });
        listener(info);
        inner
            .status_listeners
            .entry(pod_key.to_string())
            .or_default()
            .push(listener);
    }

    pub async fn on_acp_message(&self, pod_key: &str, listener: AcpCallback) {
        let mut inner = self.inner.write();
        inner
            .acp_listeners
            .entry(pod_key.to_string())
            .or_default()
            .push(listener);
    }

    pub async fn get_status(&self, pod_key: &str) -> RelayStatus {
        self.inner
            .read()
            .connections
            .get(pod_key)
            .map(|c| c.status)
            .unwrap_or(RelayStatus::Disconnected)
    }

    pub async fn is_runner_disconnected(&self, pod_key: &str) -> bool {
        self.inner
            .read()
            .connections
            .get(pod_key)
            .map(|c| c.runner_disconnected)
            .unwrap_or(false)
    }

    pub async fn get_pod_size(&self, pod_key: &str) -> Option<(u16, u16)> {
        self.inner
            .read()
            .connections
            .get(pod_key)
            .and_then(|c| c.pod_size)
    }

    pub async fn disconnect(&self, pod_key: &str) {
        let mut inner = self.inner.write();
        Self::disconnect_inner(&mut inner, pod_key);
    }

    pub async fn force_resize(&self, pod_key: &str, cols: u16, rows: u16) {
        if cols == 0 || rows == 0 {
            return;
        }
        let mut inner = self.inner.write();
        if let Some(h) = inner.resize_debounce.remove(pod_key) {
            h.abort();
        }
        if let Some(conn) = inner.connections.get(pod_key) {
            Self::do_send_resize(conn, cols, rows);
        }
    }

    pub async fn disconnect_all(&self) {
        let mut inner = self.inner.write();
        let keys: Vec<_> = inner.connections.keys().cloned().collect();
        for key in keys {
            Self::disconnect_inner(&mut inner, &key);
        }
    }

    pub(crate) fn do_send_resize(conn: &ConnectionState<R>, cols: u16, rows: u16) {
        if let Some(tx) = &conn.ws_write_tx {
            let _ = tx.unbounded_send(agentsmesh_protocol::encode_resize(cols, rows));
        }
    }

    pub(crate) fn disconnect_inner(inner: &mut PoolInner<R>, pod_key: &str) {
        if let Some(mut conn) = inner.connections.remove(pod_key) {
            conn.cancel_timers();
            if let Some(h) = conn.read_handle.take() {
                h.abort();
            }
            conn.ws_write_tx = None;
        }
        inner.last_inputs.remove(pod_key);
        inner.acp_listeners.remove(pod_key);
        if let Some(h) = inner.resize_debounce.remove(pod_key) {
            h.abort();
        }
    }

    pub(crate) fn notify_status_info(
        listeners: &HashMap<String, Vec<StatusCallback>>,
        pod_key: &str,
        info: &RelayStatusInfo,
    ) {
        if let Some(cbs) = listeners.get(pod_key) {
            for cb in cbs {
                cb(info.clone());
            }
        }
    }
}
