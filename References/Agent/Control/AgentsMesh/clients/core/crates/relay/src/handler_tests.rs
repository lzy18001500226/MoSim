use std::sync::{Arc, Mutex};

use agentsmesh_protocol::{encode_message, MsgType};
use agentsmesh_transport::runtime::{PlatformRuntime, Runtime};
use futures::channel::mpsc;

use crate::error::RelayError;
use crate::pool::RelayConnectionPool;
use crate::types::{ConnectionHandle, ConnectionState, OutputCallback, RelayStatus, RelayStatusInfo};

fn make_output_cb() -> (OutputCallback, Arc<Mutex<Vec<Vec<u8>>>>) {
    let buf = Arc::new(Mutex::new(Vec::new()));
    let r = buf.clone();
    let cb: OutputCallback = Arc::new(move |data| r.lock().unwrap().push(data));
    (cb, buf)
}

async fn insert_with_subscriber(
    pool: &RelayConnectionPool,
    pod: &str,
    cb: OutputCallback,
) {
    let mut inner = pool.inner.write();
    let mut conn = ConnectionState::new("ws://relay".into(), "tok".into());
    conn.subscribers.insert("test-sub".to_string(), cb);
    inner.connections.insert(pod.to_string(), conn);
}

fn rt() -> PlatformRuntime {
    PlatformRuntime
}

#[tokio::test]
async fn handle_output_broadcasts() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, received) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let data = encode_message(MsgType::Output, b"terminal data");
    pool.handle_ws_message("pod1", &data).await;

    let msgs = received.lock().unwrap();
    assert_eq!(msgs.len(), 1);
    assert_eq!(msgs[0], b"terminal data");
}

#[tokio::test]
async fn handle_snapshot_sets_state() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, received) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let json = serde_json::json!({
        "serialized_content": "screen",
        "cols": 80, "rows": 24
    });
    let data = encode_message(MsgType::Snapshot, &serde_json::to_vec(&json).unwrap());
    pool.handle_ws_message("pod1", &data).await;

    let msgs = received.lock().unwrap();
    assert_eq!(msgs.len(), 2);

    let inner = pool.inner.read();
    let conn = inner.connections.get("pod1").unwrap();
    assert!(conn.snapshot_received);
    assert_eq!(conn.pod_size, Some((80, 24)));
}

#[tokio::test]
async fn handle_snapshot_zero_size_skips_pod_size() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let json = serde_json::json!({"serialized_content": "x", "cols": 0, "rows": 0});
    let data = encode_message(MsgType::Snapshot, &serde_json::to_vec(&json).unwrap());
    pool.handle_ws_message("pod1", &data).await;

    assert_eq!(pool.get_pod_size("pod1").await, None);
}

#[tokio::test]
async fn handle_snapshot_aborts_snapshot_handle() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let handle = rt().spawn(Box::pin(async {
        tokio::time::sleep(std::time::Duration::from_secs(3600)).await;
    }));
    {
        let mut inner = pool.inner.write();
        inner.connections.get_mut("pod1").unwrap().snapshot_handle = Some(handle);
    }

    let json = serde_json::json!({"cols": 80, "rows": 24});
    let data = encode_message(MsgType::Snapshot, &serde_json::to_vec(&json).unwrap());
    pool.handle_ws_message("pod1", &data).await;

    let inner = pool.inner.read();
    assert!(inner.connections.get("pod1").unwrap().snapshot_handle.is_none());
}

#[tokio::test]
async fn handle_pod_resized() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let json = serde_json::json!({"type": "pod_resized", "cols": 120, "rows": 40});
    let data = encode_message(MsgType::Control, &serde_json::to_vec(&json).unwrap());
    pool.handle_ws_message("pod1", &data).await;

    assert_eq!(pool.get_pod_size("pod1").await, Some((120, 40)));
}

#[tokio::test]
async fn handle_runner_disconnected_notifies_listeners() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let statuses = Arc::new(Mutex::new(Vec::<RelayStatusInfo>::new()));
    let sr = statuses.clone();
    pool.on_status_change(
        "pod1",
        Arc::new(move |info| sr.lock().unwrap().push(info)),
    )
    .await;

    let data = encode_message(MsgType::RunnerDisconnected, &[]);
    pool.handle_ws_message("pod1", &data).await;

    assert!(pool.is_runner_disconnected("pod1").await);
    let s = statuses.lock().unwrap();
    assert_eq!(s.len(), 2);
    assert!(s[1].runner_disconnected);
}

#[tokio::test]
async fn handle_runner_reconnected() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let data = encode_message(MsgType::RunnerDisconnected, &[]);
    pool.handle_ws_message("pod1", &data).await;
    assert!(pool.is_runner_disconnected("pod1").await);

    let data = encode_message(MsgType::RunnerReconnected, &[]);
    pool.handle_ws_message("pod1", &data).await;
    assert!(!pool.is_runner_disconnected("pod1").await);
}

#[tokio::test]
async fn handle_acp_event() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let acp_msgs = Arc::new(Mutex::new(Vec::<(MsgType, serde_json::Value)>::new()));
    let am = acp_msgs.clone();
    pool.on_acp_message(
        "pod1",
        Arc::new(move |mt, val| am.lock().unwrap().push((mt, val))),
    )
    .await;

    let json = serde_json::json!({"event": "test_ev"});
    let data = encode_message(MsgType::AcpEvent, &serde_json::to_vec(&json).unwrap());
    pool.handle_ws_message("pod1", &data).await;

    let msgs = acp_msgs.lock().unwrap();
    assert_eq!(msgs.len(), 1);
    assert_eq!(msgs[0].0, MsgType::AcpEvent);
    assert_eq!(msgs[0].1["event"], "test_ev");
}

#[tokio::test]
async fn handle_nonexistent_pod() {
    let (pool, _rx) = RelayConnectionPool::new();
    let data = encode_message(MsgType::Output, b"x");
    pool.handle_ws_message("no-pod", &data).await;
}

#[tokio::test]
async fn handle_invalid_data() {
    let (pool, _rx) = RelayConnectionPool::new();
    pool.handle_ws_message("pod1", &[]).await;
    pool.handle_ws_message("pod1", &[0xFF]).await;
}

#[tokio::test]
async fn on_status_change_fires_immediately_with_current() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    insert_with_subscriber(&pool, "pod1", cb).await;

    let statuses = Arc::new(Mutex::new(Vec::<RelayStatusInfo>::new()));
    let sr = statuses.clone();
    pool.on_status_change(
        "pod1",
        Arc::new(move |info| sr.lock().unwrap().push(info)),
    )
    .await;

    let s = statuses.lock().unwrap();
    assert_eq!(s.len(), 1);
    assert_eq!(s[0].status, RelayStatus::Connecting);
    assert!(!s[0].runner_disconnected);
}

#[tokio::test]
async fn on_status_change_no_connection_gives_disconnected() {
    let (pool, _rx) = RelayConnectionPool::new();
    let statuses = Arc::new(Mutex::new(Vec::<RelayStatusInfo>::new()));
    let sr = statuses.clone();
    pool.on_status_change(
        "no-pod",
        Arc::new(move |info| sr.lock().unwrap().push(info)),
    )
    .await;

    let s = statuses.lock().unwrap();
    assert_eq!(s.len(), 1);
    assert_eq!(s[0].status, RelayStatus::Disconnected);
}

#[tokio::test]
async fn get_status_default() {
    let (pool, _rx) = RelayConnectionPool::new();
    assert_eq!(pool.get_status("any").await, RelayStatus::Disconnected);
}

#[tokio::test]
async fn is_runner_disconnected_default() {
    let (pool, _rx) = RelayConnectionPool::new();
    assert!(!pool.is_runner_disconnected("any").await);
}

#[tokio::test]
async fn get_pod_size_default() {
    let (pool, _rx) = RelayConnectionPool::new();
    assert_eq!(pool.get_pod_size("any").await, None);
}

#[tokio::test]
async fn connection_handle_send_delivers() {
    let (tx, mut rx) = mpsc::unbounded();
    let (unsub_tx, _) = mpsc::unbounded();
    let h = ConnectionHandle::new("pod1".into(), "s1".into(), tx, unsub_tx);
    h.send(vec![1, 2, 3]);
    assert_eq!(rx.recv().await.unwrap(), vec![1, 2, 3]);
}

#[tokio::test]
async fn connection_handle_unsubscribe_sends_pair() {
    let (tx, _) = mpsc::unbounded();
    let (unsub_tx, mut unsub_rx) = mpsc::unbounded();
    let h = ConnectionHandle::new("pod1".into(), "s1".into(), tx, unsub_tx);
    h.unsubscribe();
    let (pk, sid) = unsub_rx.recv().await.unwrap();
    assert_eq!(pk, "pod1");
    assert_eq!(sid, "s1");
}

#[test]
fn relay_status_display() {
    assert_eq!(RelayStatus::Connecting.to_string(), "connecting");
    assert_eq!(RelayStatus::Connected.to_string(), "connected");
    assert_eq!(RelayStatus::Disconnected.to_string(), "disconnected");
    assert_eq!(RelayStatus::Error.to_string(), "error");
}

#[test]
fn connection_state_defaults() {
    let s = ConnectionState::<PlatformRuntime>::new("ws://relay".into(), "tok".into());
    assert_eq!(s.status, RelayStatus::Connecting);
    assert!(s.subscribers.is_empty());
    assert_eq!(s.reconnect_attempts, 0);
    assert!(!s.snapshot_received);
    assert_eq!(s.pod_size, None);
    assert!(!s.runner_disconnected);
    assert!(s.ws_write_tx.is_none());
}

#[test]
fn relay_error_display_variants() {
    let e = RelayError::Connection("timeout".into());
    assert!(e.to_string().contains("timeout"));
    let e = RelayError::NotConnected("pod1".into());
    assert!(e.to_string().contains("pod1"));
    let e = RelayError::Send("closed".into());
    assert!(e.to_string().contains("closed"));
}

#[test]
fn relay_status_info_equality() {
    let a = RelayStatusInfo {
        status: RelayStatus::Connected,
        runner_disconnected: false,
    };
    let b = a.clone();
    assert_eq!(a, b);
    let c = RelayStatusInfo {
        status: RelayStatus::Error,
        runner_disconnected: true,
    };
    assert_ne!(a, c);
}
