//! Native Connect-RPC server-stream client (tokio / reqwest path).
//!
//! `subscribe_events_connect_native` wraps `reqwest::Response::bytes_stream`
//! with the frame parser. The wasm equivalent (`connect_stream_wasm.rs`)
//! constructs an `impl Stream<Item = Result<Bytes, ApiError>>` from
//! `web_sys::ReadableStream` + the same parser.
//!
//! Both expose the cross-platform `subscribe_events` API in `connect_stream.rs`.

#![cfg(not(target_arch = "wasm32"))]

use agentsmesh_types::proto_events_v1::{Event, SubscribeRequest};
use bytes::Bytes;
use futures::stream::Stream;
use futures::TryStreamExt;
use prost::Message;
use reqwest::header::{HeaderName, HeaderValue};

use crate::client::ApiClient;
use crate::connect_stream_frames::parse_connect_frames;
use crate::error::ApiError;

const PROCEDURE: &str = "/proto.events.v1.EventsService/Subscribe";

impl ApiClient {
    /// Open a Connect-RPC server stream for real-time events. The returned
    /// stream yields one decoded `Event` per server frame; the inner future
    /// completes (cleanly or with an error) when the server sends the final
    /// frame or the connection drops.
    pub async fn subscribe_events_connect_native(
        &self,
        req: &SubscribeRequest,
    ) -> Result<impl Stream<Item = Result<Event, ApiError>>, ApiError> {
        let url = format!("{}{}", self.base_url, PROCEDURE);
        let payload = req.encode_to_vec();

        let mut builder = self
            .http
            .post(&url)
            .header(
                HeaderName::from_static("content-type"),
                HeaderValue::from_static("application/connect+proto"),
            )
            .header(
                HeaderName::from_static("connect-protocol-version"),
                HeaderValue::from_static("1"),
            )
            .body(payload);

        if let Some(token) = self.auth_store.get_token() {
            if let Ok(v) = HeaderValue::from_str(&format!("Bearer {token}")) {
                builder = builder.header(HeaderName::from_static("authorization"), v);
            }
        }

        let resp = builder.send().await?;
        let status = resp.status();
        if !status.is_success() {
            let status_code = status.as_u16();
            if status_code == 401 {
                return Err(ApiError::AuthExpired);
            }
            let status_text = status.canonical_reason().unwrap_or("Unknown").to_string();
            let body = resp.bytes().await.ok();
            let server_message = body
                .as_ref()
                .and_then(|b| std::str::from_utf8(b).ok())
                .filter(|s| !s.is_empty())
                .map(String::from);
            return Err(ApiError::Http {
                status: status_code,
                status_text,
                code: None,
                server_message,
                data: None,
                url: Some(url),
            });
        }

        // `bytes_stream()` requires the `stream` feature on reqwest, which is
        // already enabled in MODULE.bazel.
        let byte_stream = resp
            .bytes_stream()
            .map_err(|e| ApiError::Http {
                status: 0,
                status_text: format!("transport: {e}"),
                code: None,
                server_message: None,
                data: None,
                url: None,
            })
            .map_ok(Bytes::from);
        Ok(parse_connect_frames::<_, Event>(Box::pin(byte_stream)))
    }
}
