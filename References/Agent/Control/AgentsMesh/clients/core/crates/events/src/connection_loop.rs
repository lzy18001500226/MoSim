use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_transport::runtime::Runtime;
use agentsmesh_types::proto_events_v1::{Event as ProtoEvent, SubscribeRequest};
use futures::channel::mpsc;
use futures::stream::StreamExt;
use futures::FutureExt;
use parking_lot::RwLock;
use std::time::Duration;
use tracing::{debug, error, info, warn};

use crate::event_types::EventType;
use crate::reconnect::{self, ReconnectPolicy};
use crate::subscription_manager::{dispatch_event, set_state, Inner};
use crate::types::{ConnectionState, EventCategory, EventSubscriptionManagerOptions, RealtimeEvent};

/// Idle-timeout for the Connect server stream. When `idle_ms` elapses
/// without a single inbound event, we treat the stream as stalled and
/// trigger reconnect. HTTP/2 PING keeps the connection alive at the
/// transport layer; this is application-level "are we still receiving
/// events?" detection.
const DEFAULT_IDLE_MS: u64 = 60_000;

pub(crate) struct ManagerOpts {
    pub max_reconnect_attempts: u32,
    pub initial_reconnect_delay_ms: u64,
    pub max_reconnect_delay_ms: u64,
    pub idle_timeout_ms: u64,
}

impl ManagerOpts {
    pub fn from_options(o: &EventSubscriptionManagerOptions) -> Self {
        // Reuse pong_timeout_ms as the idle threshold so existing callers
        // don't need a new knob. Fallback to the conservative default.
        let idle_ms = if o.pong_timeout_ms == 0 {
            DEFAULT_IDLE_MS
        } else {
            o.pong_timeout_ms.max(o.ping_interval_ms) + o.pong_timeout_ms
        };
        Self {
            max_reconnect_attempts: o.max_reconnect_attempts,
            initial_reconnect_delay_ms: o.initial_reconnect_delay_ms,
            max_reconnect_delay_ms: o.max_reconnect_delay_ms,
            idle_timeout_ms: idle_ms,
        }
    }
}

pub(crate) async fn connection_loop<R: Runtime>(
    runtime: R,
    inner: Arc<RwLock<Inner>>,
    api_client: Arc<ApiClient>,
    opts: ManagerOpts,
    mut shutdown_rx: mpsc::UnboundedReceiver<()>,
) {
    let mut reconnect_policy = ReconnectPolicy::new(
        opts.initial_reconnect_delay_ms,
        opts.max_reconnect_delay_ms,
        opts.max_reconnect_attempts,
    );

    loop {
        set_state(&inner, ConnectionState::Connecting);
        let org_slug = api_client.current_org_slug();
        info!("events: subscribing via Connect stream (org={})", org_slug);

        let session_close = run_session(
            &runtime,
            &inner,
            &api_client,
            &org_slug,
            &opts,
            &mut shutdown_rx,
        )
        .await;

        match session_close {
            SessionClose::Shutdown => {
                set_state(&inner, ConnectionState::Disconnected);
                break;
            }
            SessionClose::ConnectFailed | SessionClose::StreamError | SessionClose::IdleTimeout => {
                if !schedule_reconnect(&runtime, &inner, &mut reconnect_policy, &mut shutdown_rx)
                    .await
                {
                    break;
                }
            }
            SessionClose::ServerClosed => {
                // Clean server close — reset backoff and reconnect immediately.
                reconnect_policy.reset();
                if !schedule_reconnect(&runtime, &inner, &mut reconnect_policy, &mut shutdown_rx)
                    .await
                {
                    break;
                }
            }
        }
    }
}

enum SessionClose {
    /// User called `disconnect()` — exit cleanly, no reconnect.
    Shutdown,
    /// `subscribe_events_connect` returned an error before yielding the
    /// first frame (auth, network, server down).
    ConnectFailed,
    /// Stream yielded an error mid-flight (network reset, 5xx).
    StreamError,
    /// No events for `idle_timeout_ms` — server likely silent or proxy
    /// buffered the response.
    IdleTimeout,
    /// Stream ended cleanly with EndStreamResponse{error: None}.
    ServerClosed,
}

async fn run_session<R: Runtime>(
    runtime: &R,
    inner: &Arc<RwLock<Inner>>,
    api_client: &Arc<ApiClient>,
    org_slug: &str,
    opts: &ManagerOpts,
    shutdown_rx: &mut mpsc::UnboundedReceiver<()>,
) -> SessionClose {
    let req = SubscribeRequest {
        org_slug: org_slug.to_string(),
        event_types: Vec::new(),
    };
    let stream = match subscribe(api_client, &req).await {
        Ok(s) => s,
        Err(e) => {
            error!("events: subscribe failed: {:?}", e);
            return SessionClose::ConnectFailed;
        }
    };
    futures::pin_mut!(stream);

    set_state(inner, ConnectionState::Connected);
    info!("events: connected");

    let idle = Duration::from_millis(opts.idle_timeout_ms);

    loop {
        let next_fut = stream.next().fuse();
        let sleep_fut = runtime.sleep(idle).fuse();
        futures::pin_mut!(next_fut);
        futures::pin_mut!(sleep_fut);

        futures::select! {
            item = next_fut => {
                match item {
                    Some(Ok(evt)) => {
                        if let Some(re) = proto_to_realtime(evt) {
                            dispatch_event(inner, &re);
                        }
                    }
                    Some(Err(e)) => {
                        warn!("events: stream error: {:?}", e);
                        return SessionClose::StreamError;
                    }
                    None => {
                        debug!("events: server closed stream");
                        return SessionClose::ServerClosed;
                    }
                }
            }
            _ = sleep_fut => {
                warn!("events: idle timeout ({}ms) — reconnecting", opts.idle_timeout_ms);
                return SessionClose::IdleTimeout;
            }
            _ = shutdown_rx.next() => {
                return SessionClose::Shutdown;
            }
        }
    }
}

#[cfg(not(target_arch = "wasm32"))]
async fn subscribe(
    api_client: &Arc<ApiClient>,
    req: &SubscribeRequest,
) -> Result<impl futures::Stream<Item = Result<ProtoEvent, agentsmesh_api_client::ApiError>>, agentsmesh_api_client::ApiError>
{
    api_client.subscribe_events_connect_native(req).await
}

#[cfg(target_arch = "wasm32")]
async fn subscribe(
    api_client: &Arc<ApiClient>,
    req: &SubscribeRequest,
) -> Result<impl futures::Stream<Item = Result<ProtoEvent, agentsmesh_api_client::ApiError>>, agentsmesh_api_client::ApiError>
{
    let (stream, abort) = api_client.subscribe_events_connect_wasm(req).await?;
    // Keep the abort handle alive for the lifetime of the stream — its
    // Drop calls AbortController.abort() which kills the in-flight fetch
    // and surfaces a reader.read() rejection. Previously the handle was
    // discarded immediately, so every connect attempt aborted itself
    // before the first frame arrived → `Reconnecting → Connected →
    // Reconnecting` flapping with zero events delivered to the page.
    let stream = Box::pin(stream);
    Ok(futures::stream::unfold((stream, abort), |(mut s, abort)| async move {
        use futures::StreamExt as _;
        s.next().await.map(|item| (item, (s, abort)))
    }))
}

fn proto_to_realtime(p: ProtoEvent) -> Option<RealtimeEvent> {
    let event_type = match serde_json::from_str::<EventType>(&format!("\"{}\"", p.r#type)) {
        Ok(t) => t,
        Err(_) => {
            debug!("events: unknown type from server: {}", p.r#type);
            return None;
        }
    };
    let category = match p.category.as_str() {
        "entity" => Some(EventCategory::Entity),
        "notification" => Some(EventCategory::Notification),
        "system" => Some(EventCategory::System),
        _ => None,
    };
    let data: serde_json::Value = serde_json::from_str(&p.data_json).unwrap_or(serde_json::Value::Null);
    Some(RealtimeEvent {
        event_type,
        category,
        organization_id: p.organization_id,
        target_user_id: p.target_user_id,
        target_user_ids: if p.target_user_ids.is_empty() { None } else { Some(p.target_user_ids) },
        entity_type: p.entity_type,
        entity_id: p.entity_id,
        data,
        timestamp: p.timestamp,
    })
}

async fn schedule_reconnect<R: Runtime>(
    runtime: &R,
    inner: &Arc<RwLock<Inner>>,
    policy: &mut ReconnectPolicy,
    shutdown_rx: &mut mpsc::UnboundedReceiver<()>,
) -> bool {
    match policy.next_delay() {
        Some(delay) => {
            set_state(inner, ConnectionState::Reconnecting);
            info!(
                "events: reconnecting in {:?} (attempt {}/{})",
                delay,
                policy.attempts(),
                policy.max_attempts()
            );
            let sleep_fut = runtime.sleep(delay).fuse();
            futures::pin_mut!(sleep_fut);
            futures::select! {
                _ = sleep_fut => true,
                _ = shutdown_rx.next() => {
                    set_state(inner, ConnectionState::Disconnected);
                    false
                }
            }
        }
        None => {
            error!("events: max reconnect attempts reached");
            set_state(inner, ConnectionState::Disconnected);
            false
        }
    }
}

// Suppress unused-import warning when `reconnect::should_reconnect` is
// not referenced after the WebSocket close-code logic moved to the
// idle-timeout + stream-error decision.
#[allow(dead_code)]
fn _suppress_reconnect_dead_code() {
    let _ = reconnect::should_reconnect(None);
}
