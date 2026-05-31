//! Cross-platform Connect-RPC server-stream API.
//!
//! Two transports under the hood:
//!   * native (`connect_stream_native.rs`) — reqwest::Response::bytes_stream
//!   * wasm (`connect_stream_wasm.rs`) — web_sys::ReadableStream via fetch
//!
//! Both feed the shared parser in `connect_stream_frames.rs`.

#[cfg(not(target_arch = "wasm32"))]
pub use crate::connect_stream_native::*;

#[cfg(target_arch = "wasm32")]
pub use crate::connect_stream_wasm::*;
