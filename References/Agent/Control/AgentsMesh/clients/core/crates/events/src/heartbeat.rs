//! Application-level heartbeat — DEPRECATED after R5-11.
//!
//! The legacy WebSocket transport sent JSON `{"type":"ping"}` frames every
//! 30 s and waited 10 s for a `pong` reply. With Connect server-streaming
//! over HTTP/2 this is unnecessary:
//!   * HTTP/2 PING frames keep the connection alive at the transport layer.
//!   * `connection_loop.rs` now uses a stream-idle timeout (no events for N
//!     seconds → reconnect) as the application-level "are we still
//!     receiving?" detector.
//!
//! This file is retained as a minimal shim so subscription_manager and
//! external callers still resolve the old type names during the migration
//! window. Phase F deletes the module along with `agentsmesh_transport`.

#![allow(dead_code)]
