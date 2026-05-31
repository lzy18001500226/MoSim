//! Connect-RPC server-stream envelope frame parser.
//!
//! Wire format (Connect protocol §5.2 — server streaming):
//! ```text
//!   ┌────────┬──────────────┬───────────────────────┐
//!   │ flags  │ length (u32) │ payload (length bytes)│
//!   │ 1 byte │ big-endian   │                       │
//!   └────────┴──────────────┴───────────────────────┘
//! ```
//! Flag bits:
//!   * bit 0 — compressed payload (via Streaming-Content-Encoding)
//!   * bit 1 — final `EndStreamResponse` frame; payload is JSON
//!             `{"error":{"code":"..."},"metadata":{...}}` (NOT a proto message)
//!   * bits 2–7 — reserved (must be 0)

use std::collections::VecDeque;

use bytes::{Buf, Bytes, BytesMut};
use futures::stream::{self, Stream, StreamExt};
use prost::Message;

use crate::error::ApiError;

const FLAG_COMPRESSED: u8 = 0b0000_0001;
const FLAG_FINAL: u8 = 0b0000_0010;
const HEADER_LEN: usize = 5;

#[derive(Debug, Default, serde::Deserialize)]
struct EndStreamPayload {
    error: Option<EndStreamError>,
}

#[derive(Debug, serde::Deserialize)]
struct EndStreamError {
    code: String,
    #[serde(default)]
    message: String,
}

struct ParserState<S, T> {
    upstream: S,
    buf: BytesMut,
    pending: VecDeque<Result<T, ApiError>>,
    terminal: Option<Result<(), ApiError>>,
    done: bool,
}

/// Pull frames out of a byte stream and decode each non-final frame's
/// payload as `T`. The final frame either terminates the stream cleanly
/// or surfaces an error (yielded as the last `Err` item).
pub fn parse_connect_frames<S, T>(byte_stream: S) -> impl Stream<Item = Result<T, ApiError>>
where
    S: Stream<Item = Result<Bytes, ApiError>> + Unpin + 'static,
    T: Message + Default + 'static,
{
    let state = ParserState {
        upstream: byte_stream,
        buf: BytesMut::new(),
        pending: VecDeque::new(),
        terminal: None,
        done: false,
    };

    stream::unfold(state, |mut s| async move {
        loop {
            if let Some(item) = s.pending.pop_front() {
                return Some((item, s));
            }
            if let Some(t) = s.terminal.take() {
                s.done = true;
                if let Err(e) = t {
                    return Some((Err(e), s));
                }
                return None;
            }
            if s.done {
                return None;
            }

            match s.upstream.next().await {
                Some(Ok(chunk)) => {
                    s.buf.extend_from_slice(&chunk);
                    while let Some(frame) = take_one_frame(&mut s.buf) {
                        match dispatch_frame::<T>(frame) {
                            FrameOutcome::Message(m) => s.pending.push_back(Ok(m)),
                            FrameOutcome::EndOk => {
                                s.terminal = Some(Ok(()));
                                break;
                            }
                            FrameOutcome::EndErr(e) => {
                                s.terminal = Some(Err(e));
                                break;
                            }
                            FrameOutcome::DecodeErr(e) => s.pending.push_back(Err(e)),
                        }
                    }
                }
                Some(Err(e)) => {
                    s.done = true;
                    return Some((Err(e), s));
                }
                None => {
                    // Stream ended without a final frame — treat as clean
                    // server close. The reconnect logic upstream decides
                    // whether to retry.
                    s.done = true;
                    return None;
                }
            }
        }
    })
}

enum FrameOutcome<T> {
    Message(T),
    EndOk,
    EndErr(ApiError),
    DecodeErr(ApiError),
}

fn dispatch_frame<T: Message + Default>(frame: ParsedFrame) -> FrameOutcome<T> {
    if frame.flags & FLAG_COMPRESSED != 0 {
        return FrameOutcome::DecodeErr(ApiError::Decode(
            "connect stream: compressed frames not supported".into(),
        ));
    }
    if frame.flags & FLAG_FINAL != 0 {
        return match serde_json::from_slice::<EndStreamPayload>(&frame.payload) {
            Ok(end) => match end.error {
                Some(err) => FrameOutcome::EndErr(ApiError::Http {
                    status: 0,
                    status_text: format!("connect error: {}", err.code),
                    code: Some(err.code),
                    server_message: Some(err.message),
                    data: None,
                    url: None,
                }),
                None => FrameOutcome::EndOk,
            },
            Err(_) if frame.payload.is_empty() => FrameOutcome::EndOk,
            Err(e) => FrameOutcome::DecodeErr(ApiError::Decode(format!(
                "connect end-stream payload: {e}"
            ))),
        };
    }
    match T::decode(frame.payload.as_ref()) {
        Ok(m) => FrameOutcome::Message(m),
        Err(e) => FrameOutcome::DecodeErr(ApiError::Decode(format!("prost decode: {e}"))),
    }
}

struct ParsedFrame {
    flags: u8,
    payload: Bytes,
}

fn take_one_frame(buf: &mut BytesMut) -> Option<ParsedFrame> {
    if buf.len() < HEADER_LEN {
        return None;
    }
    let flags = buf[0];
    let len = u32::from_be_bytes([buf[1], buf[2], buf[3], buf[4]]) as usize;
    if buf.len() < HEADER_LEN + len {
        return None;
    }
    buf.advance(HEADER_LEN);
    let payload = buf.split_to(len).freeze();
    Some(ParsedFrame { flags, payload })
}

#[cfg(test)]
mod tests {
    use super::*;
    use agentsmesh_types::proto_events_v1::Event;
    use futures::stream;

    fn frame(flags: u8, payload: &[u8]) -> Bytes {
        let mut v = Vec::with_capacity(HEADER_LEN + payload.len());
        v.push(flags);
        v.extend_from_slice(&(payload.len() as u32).to_be_bytes());
        v.extend_from_slice(payload);
        Bytes::from(v)
    }

    fn ok_stream(items: Vec<Bytes>) -> impl Stream<Item = Result<Bytes, ApiError>> + Unpin {
        Box::pin(stream::iter(items.into_iter().map(Ok)))
    }

    #[tokio::test]
    async fn single_message_then_clean_end() {
        let msg = Event {
            r#type: "pod:status_changed".into(),
            ..Default::default()
        };
        let chunks = vec![frame(0, &msg.encode_to_vec()), frame(FLAG_FINAL, b"{}")];
        let stream = parse_connect_frames::<_, Event>(ok_stream(chunks));
        futures::pin_mut!(stream);
        let got = stream.next().await.unwrap().unwrap();
        assert_eq!(got.r#type, "pod:status_changed");
        assert!(stream.next().await.is_none());
    }

    #[tokio::test]
    async fn handles_partial_chunks_across_boundary() {
        let msg = Event { r#type: "ticket:updated".into(), ..Default::default() };
        let full = frame(0, &msg.encode_to_vec());
        let mid = full.len() / 2;
        let chunks = vec![full.slice(..mid), full.slice(mid..), frame(FLAG_FINAL, b"{}")];
        let stream = parse_connect_frames::<_, Event>(ok_stream(chunks));
        futures::pin_mut!(stream);
        let got = stream.next().await.unwrap().unwrap();
        assert_eq!(got.r#type, "ticket:updated");
    }

    #[tokio::test]
    async fn surfaces_end_stream_error() {
        let err_payload = br#"{"error":{"code":"unauthenticated","message":"token expired"}}"#;
        let chunks = vec![frame(FLAG_FINAL, err_payload)];
        let stream = parse_connect_frames::<_, Event>(ok_stream(chunks));
        futures::pin_mut!(stream);
        let err = stream.next().await.unwrap().unwrap_err();
        match err {
            ApiError::Http { code, .. } => assert_eq!(code.as_deref(), Some("unauthenticated")),
            other => panic!("wrong error variant: {other:?}"),
        }
    }

    #[tokio::test]
    async fn rejects_compressed_frames() {
        let chunks = vec![frame(FLAG_COMPRESSED, b"\x01\x02\x03")];
        let stream = parse_connect_frames::<_, Event>(ok_stream(chunks));
        futures::pin_mut!(stream);
        let err = stream.next().await.unwrap().unwrap_err();
        match err {
            ApiError::Decode(_) => {}
            other => panic!("expected Decode err, got {other:?}"),
        }
    }
}
