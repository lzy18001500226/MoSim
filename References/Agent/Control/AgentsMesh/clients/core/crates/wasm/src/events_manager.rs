use std::cell::RefCell;
use std::rc::Rc;
use std::sync::Arc;

use agentsmesh_api_client::ApiClient;
use agentsmesh_events::{
    EventSubscriptionManager, EventSubscriptionManagerOptions, EventType, SubscriptionId,
};
use agentsmesh_transport::runtime::PlatformRuntime;
use wasm_bindgen::prelude::*;

use crate::js_bridge::{make_event_handler, make_state_listener};

/// Events manager exposed to JavaScript via wasm-bindgen.
///
/// Owns an `EventSubscriptionManager` backed by the shared `ApiClient`
/// — Connect server-streaming over HTTP, NOT WebSocket (see R5-11). The
/// `ws_url` constructor parameter is gone; the auth token, base URL,
/// and org slug all come from the `ApiClient` / auth store.
#[wasm_bindgen]
pub struct WasmEventsManager {
    inner: Rc<RefCell<EventSubscriptionManager<PlatformRuntime>>>,
}

impl WasmEventsManager {
    pub(crate) fn new_internal(client: Arc<ApiClient>) -> Self {
        let manager = EventSubscriptionManager::with_runtime(
            PlatformRuntime,
            client,
            EventSubscriptionManagerOptions::default(),
        );
        Self {
            inner: Rc::new(RefCell::new(manager)),
        }
    }

    pub(crate) fn new_internal_with_options(
        client: Arc<ApiClient>,
        options: EventSubscriptionManagerOptions,
    ) -> Self {
        let manager =
            EventSubscriptionManager::with_runtime(PlatformRuntime, client, options);
        Self {
            inner: Rc::new(RefCell::new(manager)),
        }
    }
}

#[wasm_bindgen]
impl WasmEventsManager {
    pub async fn connect(&self) {
        self.inner.borrow_mut().connect().await;
    }

    pub async fn disconnect(&self) {
        self.inner.borrow_mut().disconnect().await;
    }

    pub async fn subscribe(
        &self,
        event_type: String,
        callback: js_sys::Function,
    ) -> Result<f64, String> {
        let et = parse_event_type(&event_type)?;
        let handler = make_event_handler(callback);
        let id = self.inner.borrow().subscribe(et, handler).await;
        Ok(sub_id_to_f64(id))
    }

    pub async fn subscribe_all(&self, callback: js_sys::Function) -> f64 {
        let handler = make_event_handler(callback);
        let id = self.inner.borrow().subscribe_all(handler).await;
        sub_id_to_f64(id)
    }

    pub async fn unsubscribe(&self, id: f64) {
        let sid = f64_to_sub_id(id);
        self.inner.borrow().unsubscribe(sid).await;
    }

    pub async fn on_connection_state_change(&self, callback: js_sys::Function) -> f64 {
        let listener = make_state_listener(callback);
        let id = self
            .inner
            .borrow()
            .on_connection_state_change(listener)
            .await;
        sub_id_to_f64(id)
    }

    pub async fn get_connection_state(&self) -> String {
        self.inner
            .borrow()
            .get_connection_state()
            .await
            .to_string()
    }
}

fn sub_id_to_f64(id: SubscriptionId) -> f64 {
    id.as_u64() as f64
}

fn f64_to_sub_id(id: f64) -> SubscriptionId {
    SubscriptionId::from_u64(id as u64)
}

fn parse_event_type(s: &str) -> Result<EventType, String> {
    let parsed: std::result::Result<EventType, _> =
        serde_json::from_value(serde_json::Value::String(s.to_string()));
    parsed.map_err(|e| format!("unknown event type '{s}': {e}"))
}
