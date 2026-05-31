//! Wasm Connect-RPC server-stream client (Phase E — real implementation).
//!
//! Drives a browser `fetch()` POST with an `application/connect+proto`
//! body, gets the response as a `ReadableStream`, reads each chunk via
//! `ReadableStreamDefaultReader.read()`, and pipes raw bytes into
//! `parse_connect_frames` (shared with the native client) to surface
//! decoded proto messages.
//!
//! Cancellation: the returned `WasmAbortHandle` wraps an
//! `AbortController.signal()` passed in via `RequestInit.signal`. Dropping
//! the abort handle (or calling `abort()` explicitly) lets the browser
//! tear down the in-flight fetch + reader pair cleanly.

#![cfg(target_arch = "wasm32")]

use std::cell::RefCell;
use std::rc::Rc;

use bytes::Bytes;
use futures::channel::mpsc;
use futures::stream::Stream;
use prost::Message as _;
use wasm_bindgen::{JsCast, JsValue};
use wasm_bindgen_futures::{spawn_local, JsFuture};
use web_sys::{
    AbortController, Headers, ReadableStreamDefaultReader, RequestInit, Response,
};

use agentsmesh_types::proto_events_v1::{Event, SubscribeRequest};

use crate::client::ApiClient;
use crate::connect_stream_frames::parse_connect_frames;
use crate::error::ApiError;

/// Abort handle for an in-flight Connect server stream. Drop to cancel
/// (via the underlying AbortController) — explicit `abort()` is also
/// available for callers that need pre-drop cancellation semantics.
pub struct WasmAbortHandle {
    ctrl: AbortController,
}

impl WasmAbortHandle {
    pub fn abort(&self) {
        // No way to surface a JS exception from AbortController.abort()
        // — it doesn't throw. The cancellation propagates through the
        // signal to the in-flight fetch and reader spawn task.
        self.ctrl.abort();
    }
}

impl Drop for WasmAbortHandle {
    fn drop(&mut self) {
        // Best-effort: if the consumer drops the stream without an
        // explicit abort, we still want to cancel the network IO and
        // release the reader. abort() is a no-op if the fetch already
        // settled.
        self.ctrl.abort();
    }
}

impl ApiClient {
    /// Wasm Connect server-stream subscriber. Returns a stream of decoded
    /// events plus an abort handle. The stream terminates when the server
    /// closes cleanly (None) or yields an `Err(ApiError)` for transport /
    /// frame parsing / Connect-end-stream errors. The abort handle's Drop
    /// cancels the underlying fetch — keep it alive for the duration of
    /// the subscription.
    pub async fn subscribe_events_connect_wasm(
        &self,
        req: &SubscribeRequest,
    ) -> Result<(impl Stream<Item = Result<Event, ApiError>>, WasmAbortHandle), ApiError> {
        // Connect server-streaming wants the REQUEST body framed too —
        // even though there's only one request message. Frame is
        // `<flags=0 u8><len u32 BE><payload>`; without it the server
        // sees `protocol error: promised <random> bytes in enveloped
        // message` and the response we read back is an EOS trailer
        // carrying the error envelope (not the realtime events the
        // caller subscribed to).
        let payload = req.encode_to_vec();
        let len = u32::try_from(payload.len()).map_err(|_| {
            ApiError::Decode(format!("subscribe payload too large: {}", payload.len()))
        })?;
        let mut body_bytes = Vec::with_capacity(5 + payload.len());
        body_bytes.push(0u8); // flags: not compressed, not end-of-stream
        body_bytes.extend_from_slice(&len.to_be_bytes());
        body_bytes.extend_from_slice(&payload);
        let url = format!(
            "{}/proto.events.v1.EventsService/Subscribe",
            self.base_url
        );

        let headers = Headers::new().map_err(js_err("Headers::new"))?;
        headers
            .set("Content-Type", "application/connect+proto")
            .map_err(js_err("Headers.set content-type"))?;
        headers
            .set("Connect-Protocol-Version", "1")
            .map_err(js_err("Headers.set connect-protocol-version"))?;
        if let Some(token) = self.auth_store.get_token() {
            headers
                .set("Authorization", &format!("Bearer {token}"))
                .map_err(js_err("Headers.set authorization"))?;
        }

        let abort_ctrl = AbortController::new().map_err(js_err("AbortController::new"))?;
        let signal = abort_ctrl.signal();

        // RequestInit: web-sys 0.3 exposes setters on the JS object via the
        // generated setter wrappers. body wants a Uint8Array (not a Rust
        // Vec) so that the browser keeps the request body buffer separately
        // from the fetch response stream — otherwise undici (Node) and
        // Chromium occasionally trip on ArrayBuffer detachment.
        let opts = RequestInit::new();
        opts.set_method("POST");
        opts.set_headers(&headers.into());
        opts.set_signal(Some(&signal));
        let body_u8 = js_sys::Uint8Array::new_with_length(body_bytes.len() as u32);
        body_u8.copy_from(&body_bytes);
        opts.set_body(&body_u8.into());

        let window = web_sys::window()
            .ok_or_else(|| ApiError::Decode("wasm fetch: no window".into()))?;
        let resp_val = JsFuture::from(window.fetch_with_str_and_init(&url, &opts))
            .await
            .map_err(js_err("fetch"))?;
        let response: Response = resp_val
            .dyn_into()
            .map_err(|_| ApiError::Decode("wasm fetch: response not a Response".into()))?;

        if !response.ok() {
            // Server rejected before opening the stream — surface as an
            // HTTP error so the reconnect path can decide whether to back
            // off (5xx) or escalate (4xx auth).
            return Err(ApiError::Http {
                status: response.status() as u16,
                status_text: response.status_text(),
                code: None,
                server_message: None,
                data: None,
                url: Some(url),
            });
        }

        // body() returns Option<ReadableStream>; a streaming-incompatible
        // server (some old proxies strip the body) leaves it None.
        let body = response
            .body()
            .ok_or_else(|| ApiError::Decode("wasm fetch: response has no body".into()))?;
        let reader: ReadableStreamDefaultReader = body
            .get_reader()
            .dyn_into()
            .map_err(|_| ApiError::Decode("wasm fetch: get_reader did not return a default reader".into()))?;

        let (tx, rx) = mpsc::unbounded::<Result<Bytes, ApiError>>();
        let reader = Rc::new(RefCell::new(reader));

        // Pump JS ReadableStream chunks into the mpsc channel on the
        // local task queue. The spawn_local task owns the reader; once
        // the receiver drops, send fails and the loop exits, releasing
        // the reader. AbortController triggers the JS-side error path
        // which surfaces here as a reader.read() rejection.
        let reader_pump = reader.clone();
        spawn_local(async move {
            loop {
                let read_promise = reader_pump.borrow().read();
                let chunk_obj = match JsFuture::from(read_promise).await {
                    Ok(v) => v,
                    Err(e) => {
                        let _ = tx.unbounded_send(Err(ApiError::Decode(format!(
                            "reader.read rejected: {e:?}"
                        ))));
                        return;
                    }
                };

                let done_v = js_sys::Reflect::get(&chunk_obj, &JsValue::from_str("done"))
                    .unwrap_or(JsValue::FALSE);
                if done_v.as_bool().unwrap_or(false) {
                    return;
                }

                let value_v = match js_sys::Reflect::get(&chunk_obj, &JsValue::from_str("value")) {
                    Ok(v) => v,
                    Err(e) => {
                        let _ = tx.unbounded_send(Err(ApiError::Decode(format!(
                            "reader.read value missing: {e:?}"
                        ))));
                        return;
                    }
                };
                let arr = js_sys::Uint8Array::new(&value_v);
                let mut buf = vec![0u8; arr.length() as usize];
                arr.copy_to(&mut buf);
                if tx.unbounded_send(Ok(Bytes::from(buf))).is_err() {
                    // Consumer dropped the stream — we're done.
                    return;
                }
            }
        });

        let frames = parse_connect_frames::<_, Event>(rx);
        Ok((frames, WasmAbortHandle { ctrl: abort_ctrl }))
    }
}

fn js_err(ctx: &'static str) -> impl FnOnce(JsValue) -> ApiError + 'static {
    move |e| ApiError::Decode(format!("wasm {ctx}: {e:?}"))
}
