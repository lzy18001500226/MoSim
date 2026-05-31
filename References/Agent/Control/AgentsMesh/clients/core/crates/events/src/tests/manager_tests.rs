use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::Arc;

use agentsmesh_api_client::{ApiClient, AuthTokenStore};

use crate::{
    ConnectionState, EventHandler, EventSubscriptionManager, EventSubscriptionManagerOptions,
    EventType, RealtimeEvent, StateListener, SubscriptionId,
};

struct StubAuth;
impl AuthTokenStore for StubAuth {
    fn get_token(&self) -> Option<String> {
        Some("test-token".into())
    }
    fn get_refresh_token(&self) -> Option<String> {
        None
    }
    fn set_tokens(&self, _t: String, _r: String, _e: Option<i64>) {}
    fn clear_tokens(&self) {}
    fn get_current_org_slug(&self) -> Option<String> {
        Some("test-org".into())
    }
}

fn make_client() -> Arc<ApiClient> {
    Arc::new(ApiClient::new(
        "http://localhost:9999".into(),
        Arc::new(StubAuth),
    ))
}

fn make_event(event_type: EventType) -> RealtimeEvent {
    serde_json::from_value(serde_json::json!({
        "type": event_type.as_str(),
        "category": "entity",
        "organization_id": 1,
        "data": {},
        "timestamp": 1000
    }))
    .unwrap()
}

#[tokio::test]
async fn test_initial_state_is_disconnected() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    assert_eq!(mgr.get_connection_state().await, ConnectionState::Disconnected);
}

#[tokio::test]
async fn test_subscribe_and_unsubscribe() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    let counter = Arc::new(AtomicU32::new(0));
    let c = Arc::clone(&counter);
    let handler: EventHandler = Arc::new(move |_| {
        c.fetch_add(1, Ordering::SeqCst);
    });
    let id = mgr.subscribe(EventType::PodCreated, handler).await;
    mgr.unsubscribe(id).await;
}

#[tokio::test]
async fn test_subscribe_all_and_unsubscribe() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    let counter = Arc::new(AtomicU32::new(0));
    let c = Arc::clone(&counter);
    let handler: EventHandler = Arc::new(move |_| {
        c.fetch_add(1, Ordering::SeqCst);
    });
    let id = mgr.subscribe_all(handler).await;
    mgr.unsubscribe(id).await;
}

#[tokio::test]
async fn test_connection_state_listener_gets_initial() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    let received = Arc::new(std::sync::Mutex::new(Vec::new()));
    let r = Arc::clone(&received);
    let listener: StateListener = Arc::new(move |state| {
        r.lock().unwrap().push(state);
    });
    let _id = mgr.on_connection_state_change(listener).await;
    tokio::time::sleep(std::time::Duration::from_millis(10)).await;
    let states = received.lock().unwrap();
    assert_eq!(states.len(), 1);
    assert_eq!(states[0], ConnectionState::Disconnected);
}

#[tokio::test]
async fn test_multiple_subscriptions_different_types() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    let h1: EventHandler = Arc::new(|_| {});
    let h2: EventHandler = Arc::new(|_| {});
    let id1 = mgr.subscribe(EventType::PodCreated, h1).await;
    let id2 = mgr.subscribe(EventType::RunnerOnline, h2).await;
    assert_ne!(id1, id2);
    mgr.unsubscribe(id1).await;
    mgr.unsubscribe(id2).await;
}

#[tokio::test]
async fn test_unsubscribe_nonexistent_id_is_noop() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    mgr.unsubscribe(SubscriptionId::from_u64(99999)).await;
}

#[tokio::test]
async fn test_options_default() {
    let opts = EventSubscriptionManagerOptions::default();
    assert_eq!(opts.max_reconnect_attempts, 10);
    assert_eq!(opts.initial_reconnect_delay_ms, 1000);
    assert_eq!(opts.max_reconnect_delay_ms, 30000);
}

#[tokio::test]
async fn test_custom_options() {
    let opts = EventSubscriptionManagerOptions {
        max_reconnect_attempts: 5,
        initial_reconnect_delay_ms: 500,
        max_reconnect_delay_ms: 15000,
        ping_interval_ms: 10000,
        pong_timeout_ms: 5000,
    };
    let mgr = EventSubscriptionManager::new(make_client(), opts);
    assert_eq!(mgr.get_connection_state().await, ConnectionState::Disconnected);
}

#[test]
fn test_realtime_event_deserialization_variations() {
    let json = r#"{
        "type": "notification",
        "category": "notification",
        "organization_id": 5,
        "target_user_id": 42,
        "data": {"title": "Hello"},
        "timestamp": 2000
    }"#;
    let event: RealtimeEvent = serde_json::from_str(json).unwrap();
    assert_eq!(event.event_type, EventType::Notification);
    assert_eq!(event.target_user_id, Some(42));
    assert!(event.entity_type.is_none());

    let json = r#"{
        "type": "system:maintenance",
        "category": "system",
        "organization_id": 0,
        "data": {"message": "downtime"},
        "timestamp": 3000
    }"#;
    let event: RealtimeEvent = serde_json::from_str(json).unwrap();
    assert_eq!(event.event_type, EventType::SystemMaintenance);
}

#[tokio::test]
async fn test_disconnect_without_connect() {
    let mut mgr = EventSubscriptionManager::with_default_options(make_client());
    mgr.disconnect().await;
    assert_eq!(mgr.get_connection_state().await, ConnectionState::Disconnected);
}

#[test]
fn test_make_event_pod_created() {
    let event = make_event(EventType::PodCreated);
    assert_eq!(event.event_type, EventType::PodCreated);
    assert_eq!(event.organization_id, 1);
    assert_eq!(event.timestamp, 1000);
}

#[tokio::test]
async fn test_subscribe_receives_dispatched_event() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    let counter = Arc::new(AtomicU32::new(0));
    let c = counter.clone();
    let handler: EventHandler = Arc::new(move |evt| {
        assert_eq!(evt.event_type, EventType::PodCreated);
        c.fetch_add(1, Ordering::SeqCst);
    });
    let _id = mgr.subscribe(EventType::PodCreated, handler).await;
    let event = make_event(EventType::PodCreated);
    crate::subscription_manager::dispatch_event(&mgr.inner, &event);
    assert_eq!(counter.load(Ordering::SeqCst), 1);
}

#[tokio::test]
async fn test_subscribe_all_receives_any_event() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    let counter = Arc::new(AtomicU32::new(0));
    let c = counter.clone();
    let handler: EventHandler = Arc::new(move |_| {
        c.fetch_add(1, Ordering::SeqCst);
    });
    let _id = mgr.subscribe_all(handler).await;
    let evt1 = make_event(EventType::PodCreated);
    let evt2 = make_event(EventType::RunnerOnline);
    crate::subscription_manager::dispatch_event(&mgr.inner, &evt1);
    crate::subscription_manager::dispatch_event(&mgr.inner, &evt2);
    assert_eq!(counter.load(Ordering::SeqCst), 2);
}

#[tokio::test]
async fn test_unsubscribe_stops_delivery() {
    let mgr = EventSubscriptionManager::with_default_options(make_client());
    let counter = Arc::new(AtomicU32::new(0));
    let c = counter.clone();
    let handler: EventHandler = Arc::new(move |_| {
        c.fetch_add(1, Ordering::SeqCst);
    });
    let id = mgr.subscribe(EventType::PodCreated, handler).await;
    mgr.unsubscribe(id).await;
    let event = make_event(EventType::PodCreated);
    crate::subscription_manager::dispatch_event(&mgr.inner, &event);
    assert_eq!(counter.load(Ordering::SeqCst), 0);
}
