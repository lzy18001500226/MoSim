use agentsmesh_protocol::{encode_message, MsgType};
use agentsmesh_transport::runtime::{Runtime, TaskHandle};
use futures::channel::mpsc;
use futures::stream::StreamExt;
use tracing::{debug, warn};

use crate::connection;
use crate::pool::RelayConnectionPool;
use crate::retry;
use crate::types::{RelayStatus, RelayStatusInfo};

impl<R: Runtime> RelayConnectionPool<R> {
    pub(crate) async fn connect_pod(&self, pod_key: &str) -> Result<(), crate::error::RelayError> {
        let (relay_url, relay_token) = {
            let inner = self.inner.read();
            let conn = inner
                .connections
                .get(pod_key)
                .ok_or_else(|| crate::error::RelayError::NotConnected(pod_key.into()))?;
            (conn.relay_url.clone(), conn.relay_token.clone())
        };

        let (msg_tx, msg_rx) = mpsc::unbounded();
        let (close_tx, close_rx) = mpsc::unbounded();
        let (error_tx, error_rx) = mpsc::unbounded();

        let ws_conn = connection::connect(
            &self.runtime,
            &relay_url,
            &relay_token,
            msg_tx,
            pod_key.to_string(),
            close_tx,
            error_tx,
        )
        .await?;

        {
            let mut inner = self.inner.write();
            if let Some(conn) = inner.connections.get_mut(pod_key) {
                conn.ws_write_tx = Some(ws_conn.write_tx);
                conn.status = RelayStatus::Connected;
                conn.reconnect_attempts = 0;
                conn.snapshot_received = false;
                if let Some((cols, rows)) = conn.pending_resize.take() {
                    Self::do_send_resize(conn, cols, rows);
                }
            }
        }

        self.notify_status(pod_key, RelayStatus::Connected).await;
        self.schedule_snapshot_retry(pod_key);
        self.spawn_event_loop(pod_key, msg_rx, close_rx, error_rx);
        Ok(())
    }

    fn spawn_event_loop(
        &self,
        pod_key: &str,
        mut msg_rx: mpsc::UnboundedReceiver<(String, Vec<u8>)>,
        mut close_rx: mpsc::UnboundedReceiver<String>,
        mut error_rx: mpsc::UnboundedReceiver<String>,
    ) {
        let pool = self.clone();
        let pk = pod_key.to_string();
        let handle = self.runtime.spawn(Box::pin(async move {
            loop {
                futures::select! {
                    msg = msg_rx.next() => {
                        match msg {
                            Some((_, data)) => pool.handle_ws_message(&pk, &data).await,
                            None => break,
                        }
                    }
                    closed = close_rx.next() => {
                        if closed.is_some() {
                            debug!("ws closed for {pk}");
                            pool.handle_disconnect(&pk, RelayStatus::Disconnected).await;
                        }
                        break;
                    }
                    err = error_rx.next() => {
                        if err.is_some() {
                            debug!("ws error for {pk}");
                            pool.handle_disconnect(&pk, RelayStatus::Error).await;
                        }
                        break;
                    }
                }
            }
        }));

        let pool = self.clone();
        let pk = pod_key.to_string();
        self.runtime.spawn(Box::pin(async move {
            let mut inner = pool.inner.write();
            if let Some(conn) = inner.connections.get_mut(&pk) {
                conn.read_handle = Some(handle);
            }
        }));
    }

    async fn handle_disconnect(&self, pod_key: &str, status: RelayStatus) {
        let should_reconnect = {
            let mut inner = self.inner.write();
            let Some(conn) = inner.connections.get_mut(pod_key) else {
                return;
            };
            conn.status = status;
            conn.ws_write_tx = None;
            !conn.subscribers.is_empty()
                && retry::should_reconnect(conn.reconnect_attempts)
        };

        self.notify_status(pod_key, status).await;
        if should_reconnect {
            self.schedule_reconnect(pod_key);
        }
    }

    pub(crate) fn schedule_reconnect(&self, pod_key: &str) {
        let pool = self.clone();
        let pk = pod_key.to_string();
        let inner_ref = self.inner.clone();
        let rt = self.runtime.clone();

        self.runtime.spawn(Box::pin(async move {
            let delay = {
                let mut inner = inner_ref.write();
                let Some(conn) = inner.connections.get_mut(&pk) else {
                    return;
                };
                if let Some(h) = conn.reconnect_handle.take() {
                    h.abort();
                }
                let d = retry::compute_reconnect_delay(
                    conn.reconnect_attempts,
                    retry::BASE_RECONNECT_DELAY_MS,
                );
                conn.reconnect_attempts += 1;
                d
            };

            rt.sleep(delay).await;
            if let Err(e) = pool.connect_pod(&pk).await {
                warn!("reconnect failed for {pk}: {e}");
                pool.schedule_reconnect(&pk);
            }
        }));
    }

    fn schedule_snapshot_retry(&self, pod_key: &str) {
        let pool = self.clone();
        let pk = pod_key.to_string();
        let rt = self.runtime.clone();
        let handle = self.runtime.spawn(Box::pin(async move {
            for attempt in 0..retry::MAX_SNAPSHOT_RETRIES {
                rt.sleep(std::time::Duration::from_millis(retry::SNAPSHOT_TIMEOUT_MS))
                    .await;
                let inner = pool.inner.read();
                let Some(conn) = inner.connections.get(&pk) else {
                    return;
                };
                if conn.snapshot_received || conn.status != RelayStatus::Connected {
                    return;
                }
                debug!("snapshot retry {attempt} for {pk}");
                if let Some(tx) = &conn.ws_write_tx {
                    let _ = tx.unbounded_send(encode_message(MsgType::Resync, &[]));
                }
            }
        }));

        let pool2 = self.clone();
        let pk2 = pod_key.to_string();
        self.runtime.spawn(Box::pin(async move {
            let mut inner = pool2.inner.write();
            if let Some(conn) = inner.connections.get_mut(&pk2) {
                if let Some(h) = conn.snapshot_handle.take() {
                    h.abort();
                }
                conn.snapshot_handle = Some(handle);
            }
        }));
    }

    pub(crate) async fn notify_status(&self, pod_key: &str, status: RelayStatus) {
        let inner = self.inner.read();
        let runner_disconnected = inner
            .connections
            .get(pod_key)
            .map(|c| c.runner_disconnected)
            .unwrap_or(false);
        let info = RelayStatusInfo {
            status,
            runner_disconnected,
        };
        Self::notify_status_info(&inner.status_listeners, pod_key, &info);
    }
}
