use std::sync::{Arc, Mutex};
use std::time::Duration;

use agentsmesh_protocol::MsgType;
use agentsmesh_transport::runtime::{PlatformRuntime, Runtime};
use futures::channel::mpsc;

use crate::error::RelayError;
use crate::pool::RelayConnectionPool;
use crate::types::{ConnectionState, OutputCallback, RelayStatus};

fn make_output_cb() -> (OutputCallback, Arc<Mutex<Vec<Vec<u8>>>>) {
    let buf = Arc::new(Mutex::new(Vec::new()));
    let r = buf.clone();
    let cb: OutputCallback = Arc::new(move |data| r.lock().unwrap().push(data));
    (cb, buf)
}

fn rt() -> PlatformRuntime {
    PlatformRuntime
}

async fn insert_conn(pool: &RelayConnectionPool, pod: &str) {
    let mut inner = pool.inner.write();
    inner
        .connections
        .insert(pod.to_string(), ConnectionState::new("ws://relay".into(), "tok".into()));
}

async fn insert_connected(
    pool: &RelayConnectionPool,
    pod: &str,
    cb: OutputCallback,
) -> mpsc::UnboundedReceiver<Vec<u8>> {
    let (tx, rx) = mpsc::unbounded();
    let mut inner = pool.inner.write();
    let mut conn = ConnectionState::new("ws://relay".into(), "tok".into());
    conn.status = RelayStatus::Connected;
    conn.ws_write_tx = Some(tx);
    conn.subscribers.insert("test-sub".to_string(), cb);
    inner.connections.insert(pod.to_string(), conn);
    rx
}

#[tokio::test]
async fn subscribe_existing_adds_subscriber() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;

    let (cb, _) = make_output_cb();
    let handle = pool
        .subscribe("pod1", "s1", "ws://relay", "tok", cb)
        .await;
    assert_eq!(handle.pod_key, "pod1");
    assert_eq!(handle.subscription_id, "s1");
}

#[tokio::test]
async fn subscribe_existing_multiple_subscribers() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;

    let (cb1, _) = make_output_cb();
    let (cb2, _) = make_output_cb();
    pool.subscribe("pod1", "s1", "ws://relay", "tok", cb1).await;
    pool.subscribe("pod1", "s2", "ws://relay", "tok", cb2).await;

    let inner = pool.inner.read();
    assert_eq!(inner.connections.get("pod1").unwrap().subscribers.len(), 2);
}

#[tokio::test]
async fn subscribe_sends_resync_when_connected() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (tx, mut ws_rx) = mpsc::unbounded();
    {
        let mut inner = pool.inner.write();
        let mut conn = ConnectionState::new("ws://relay".into(), "tok".into());
        conn.status = RelayStatus::Connected;
        conn.ws_write_tx = Some(tx);
        inner.connections.insert("pod1".to_string(), conn);
    }

    let (cb, _) = make_output_cb();
    pool.subscribe("pod1", "s1", "ws://relay", "tok", cb).await;

    let msg = ws_rx.recv().await.unwrap();
    let (mt, _) = agentsmesh_protocol::decode_message(&msg).unwrap();
    assert_eq!(mt, MsgType::Resync);
}

#[tokio::test]
async fn subscribe_cancels_pending_disconnect() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;

    let handle =
        rt().spawn(Box::pin(async { tokio::time::sleep(Duration::from_secs(3600)).await }));
    {
        let mut inner = pool.inner.write();
        inner.connections.get_mut("pod1").unwrap().disconnect_handle = Some(handle);
    }

    let (cb, _) = make_output_cb();
    pool.subscribe("pod1", "s1", "ws://relay", "tok", cb).await;

    let inner = pool.inner.read();
    assert!(inner.connections.get("pod1").unwrap().disconnect_handle.is_none());
}

#[tokio::test]
async fn subscribe_new_connection_starts_connecting() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    let handle = pool.subscribe("pod1", "s1", "ws://invalid:0", "tok", cb).await;
    assert_eq!(handle.pod_key, "pod1");
    let inner = pool.inner.read();
    assert!(inner.connections.contains_key("pod1"));
}

#[tokio::test]
async fn unsubscribe_removes_subscriber() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;
    {
        let (cb, _) = make_output_cb();
        let mut inner = pool.inner.write();
        inner.connections.get_mut("pod1").unwrap().subscribers.insert("s1".into(), cb);
    }
    pool.unsubscribe("pod1", "s1").await;
    let inner = pool.inner.read();
    assert!(inner.connections.get("pod1").unwrap().subscribers.is_empty());
}

#[tokio::test]
async fn unsubscribe_nonexistent_is_noop() {
    let (pool, _rx) = RelayConnectionPool::new();
    pool.unsubscribe("no-pod", "s1").await;
}

#[tokio::test]
async fn send_no_connection_is_noop() {
    let (pool, _rx) = RelayConnectionPool::new();
    pool.send("no-pod", "hello").await;
}

#[tokio::test]
async fn send_not_connected_is_noop() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;
    pool.send("pod1", "hello").await;
}

#[tokio::test]
async fn send_forwards_to_ws() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    let mut ws_rx = insert_connected(&pool, "pod1", cb).await;

    pool.send("pod1", "hello").await;
    let msg = ws_rx.recv().await.unwrap();
    let (mt, payload) = agentsmesh_protocol::decode_message(&msg).unwrap();
    assert_eq!(mt, MsgType::Input);
    assert_eq!(payload, b"hello");
}

#[tokio::test]
async fn send_dedup_within_window() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    let mut ws_rx = insert_connected(&pool, "pod1", cb).await;

    pool.send("pod1", "hello").await;
    pool.send("pod1", "hello").await;
    let _first = ws_rx.recv().await.unwrap();
    assert!(ws_rx.try_recv().is_err());
}

#[tokio::test]
async fn send_different_data_not_deduped() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    let mut ws_rx = insert_connected(&pool, "pod1", cb).await;

    pool.send("pod1", "aaa").await;
    pool.send("pod1", "bbb").await;
    let _m1 = ws_rx.recv().await.unwrap();
    let _m2 = ws_rx.recv().await.unwrap();
}

#[tokio::test]
async fn send_single_char_bypasses_dedup() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    let mut ws_rx = insert_connected(&pool, "pod1", cb).await;

    pool.send("pod1", "a").await;
    pool.send("pod1", "a").await;
    let _m1 = ws_rx.recv().await.unwrap();
    let _m2 = ws_rx.recv().await.unwrap();
}

#[tokio::test]
async fn send_resize_zero_ignored() {
    let (pool, _rx) = RelayConnectionPool::new();
    pool.send_resize("pod1", 0, 0).await;
    pool.send_resize("pod1", 80, 0).await;
    pool.send_resize("pod1", 0, 24).await;
}

#[tokio::test]
async fn send_resize_creates_debounce_entry() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;
    pool.send_resize("pod1", 80, 24).await;
    let inner = pool.inner.read();
    assert!(inner.resize_debounce.contains_key("pod1"));
}

#[tokio::test]
async fn send_acp_not_connected() {
    let (pool, _rx) = RelayConnectionPool::new();
    let cmd = serde_json::json!({"action": "test"});
    assert!(matches!(
        pool.send_acp_command("no-pod", &cmd).await,
        Err(RelayError::NotConnected(_))
    ));
}

#[tokio::test]
async fn send_acp_connected() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    let mut ws_rx = insert_connected(&pool, "pod1", cb).await;

    let cmd = serde_json::json!({"action": "test"});
    assert!(pool.send_acp_command("pod1", &cmd).await.is_ok());
    let msg = ws_rx.recv().await.unwrap();
    let (mt, _) = agentsmesh_protocol::decode_message(&msg).unwrap();
    assert_eq!(mt, MsgType::AcpCommand);
}

#[tokio::test]
async fn send_acp_no_ws_tx() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;
    let cmd = serde_json::json!({"x": 1});
    assert!(matches!(
        pool.send_acp_command("pod1", &cmd).await,
        Err(RelayError::NotConnected(_))
    ));
}

#[tokio::test]
async fn disconnect_removes_connection() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;
    pool.disconnect("pod1").await;
    assert_eq!(pool.get_status("pod1").await, RelayStatus::Disconnected);
}

#[tokio::test]
async fn disconnect_all_clears_everything() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;
    insert_conn(&pool, "pod2").await;
    pool.disconnect_all().await;
    assert_eq!(pool.get_status("pod1").await, RelayStatus::Disconnected);
    assert_eq!(pool.get_status("pod2").await, RelayStatus::Disconnected);
}

#[tokio::test]
async fn disconnect_cleans_resize_debounce() {
    let (pool, _rx) = RelayConnectionPool::new();
    insert_conn(&pool, "pod1").await;
    pool.send_resize("pod1", 80, 24).await;
    pool.disconnect("pod1").await;
    let inner = pool.inner.read();
    assert!(!inner.resize_debounce.contains_key("pod1"));
}

#[tokio::test]
async fn pool_default_impl() {
    let pool = RelayConnectionPool::default();
    assert_eq!(pool.get_status("any").await, RelayStatus::Disconnected);
}

#[tokio::test]
async fn force_resize_zero_ignored() {
    let (pool, _rx) = RelayConnectionPool::new();
    pool.force_resize("pod1", 0, 0).await;
    pool.force_resize("pod1", 80, 0).await;
}

#[tokio::test]
async fn force_resize_sends_immediately() {
    let (pool, _rx) = RelayConnectionPool::new();
    let (cb, _) = make_output_cb();
    let mut ws_rx = insert_connected(&pool, "pod1", cb).await;

    pool.force_resize("pod1", 120, 40).await;
    let msg = ws_rx.recv().await.unwrap();
    assert!(!msg.is_empty());
}
