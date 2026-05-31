use std::collections::HashMap;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_transport::runtime::{PlatformRuntime, Runtime};
use futures::channel::mpsc;
use parking_lot::RwLock;

use crate::event_types::EventType;
use crate::types::{
    ConnectionState, EventHandler, EventSubscriptionManagerOptions, RealtimeEvent, StateListener,
    SubscriptionId,
};

static NEXT_SUB_ID: AtomicU64 = AtomicU64::new(1);

fn next_subscription_id() -> SubscriptionId {
    SubscriptionId(NEXT_SUB_ID.fetch_add(1, Ordering::Relaxed))
}

pub(crate) type HandlerMap = HashMap<EventType, HashMap<SubscriptionId, EventHandler>>;

pub(crate) struct Inner {
    pub handlers: HandlerMap,
    pub global_handlers: HashMap<SubscriptionId, EventHandler>,
    pub state_listeners: HashMap<SubscriptionId, StateListener>,
    pub connection_state: ConnectionState,
}

pub struct EventSubscriptionManager<R: Runtime = PlatformRuntime> {
    pub(crate) inner: Arc<RwLock<Inner>>,
    pub(crate) options: EventSubscriptionManagerOptions,
    api_client: Arc<ApiClient>,
    shutdown_tx: Option<mpsc::UnboundedSender<()>>,
    runtime: R,
}

impl EventSubscriptionManager<PlatformRuntime> {
    pub fn new(api_client: Arc<ApiClient>, options: EventSubscriptionManagerOptions) -> Self {
        Self::with_runtime(PlatformRuntime, api_client, options)
    }

    pub fn with_default_options(api_client: Arc<ApiClient>) -> Self {
        Self::new(api_client, EventSubscriptionManagerOptions::default())
    }
}

impl<R: Runtime> EventSubscriptionManager<R> {
    pub fn with_runtime(
        runtime: R,
        api_client: Arc<ApiClient>,
        options: EventSubscriptionManagerOptions,
    ) -> Self {
        Self {
            inner: Arc::new(RwLock::new(Inner {
                handlers: HashMap::new(),
                global_handlers: HashMap::new(),
                state_listeners: HashMap::new(),
                connection_state: ConnectionState::Disconnected,
            })),
            options,
            api_client,
            shutdown_tx: None,
            runtime,
        }
    }

    pub async fn connect(&mut self) {
        let state = self.inner.read().connection_state;
        if state == ConnectionState::Connected || state == ConnectionState::Connecting {
            return;
        }

        let (shutdown_tx, shutdown_rx) = mpsc::unbounded();
        self.shutdown_tx = Some(shutdown_tx);

        let inner = Arc::clone(&self.inner);
        let api_client = Arc::clone(&self.api_client);
        let opts = crate::connection_loop::ManagerOpts::from_options(&self.options);
        let rt = self.runtime.clone();

        self.runtime.spawn(Box::pin(
            crate::connection_loop::connection_loop(rt, inner, api_client, opts, shutdown_rx),
        ));
    }

    pub async fn disconnect(&mut self) {
        if let Some(tx) = self.shutdown_tx.take() {
            let _ = tx.unbounded_send(());
        }
        set_state(&self.inner, ConnectionState::Disconnected);
    }

    pub async fn subscribe(
        &self,
        event_type: EventType,
        handler: EventHandler,
    ) -> SubscriptionId {
        let id = next_subscription_id();
        let mut inner = self.inner.write();
        inner.handlers.entry(event_type).or_default().insert(id, handler);
        id
    }

    pub async fn subscribe_all(&self, handler: EventHandler) -> SubscriptionId {
        let id = next_subscription_id();
        self.inner.write().global_handlers.insert(id, handler);
        id
    }

    pub async fn unsubscribe(&self, id: SubscriptionId) {
        let mut inner = self.inner.write();
        for handlers in inner.handlers.values_mut() {
            handlers.remove(&id);
        }
        inner.global_handlers.remove(&id);
        inner.state_listeners.remove(&id);
    }

    pub async fn on_connection_state_change(
        &self,
        listener: StateListener,
    ) -> SubscriptionId {
        let id = next_subscription_id();
        let mut inner = self.inner.write();
        let current = inner.connection_state;
        inner.state_listeners.insert(id, Arc::clone(&listener));
        listener(current);
        id
    }

    pub async fn get_connection_state(&self) -> ConnectionState {
        self.inner.read().connection_state
    }
}

pub(crate) fn set_state(inner: &Arc<RwLock<Inner>>, state: ConnectionState) {
    let listeners: Vec<StateListener> = {
        let mut guard = inner.write();
        if guard.connection_state == state {
            return;
        }
        guard.connection_state = state;
        guard.state_listeners.values().cloned().collect()
    };
    for listener in listeners {
        listener(state);
    }
}

pub(crate) fn dispatch_event(inner: &Arc<RwLock<Inner>>, event: &RealtimeEvent) {
    let (typed, global): (Vec<EventHandler>, Vec<EventHandler>) = {
        let guard = inner.read();
        let typed = guard
            .handlers
            .get(&event.event_type)
            .map(|m| m.values().cloned().collect())
            .unwrap_or_default();
        let global = guard.global_handlers.values().cloned().collect();
        (typed, global)
    };
    for handler in typed.iter().chain(global.iter()) {
        handler(event);
    }
}
