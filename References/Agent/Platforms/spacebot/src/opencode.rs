//! OpenCode subprocess integration for coding workers.
//!
//! Manages persistent OpenCode server processes and drives coding sessions
//! through their HTTP API + SSE event stream. This module provides an
//! alternative worker backend that delegates to OpenCode's full agent
//! capabilities instead of running a Rig agent loop with basic tools.

pub mod server;
pub mod types;
pub mod worker;

pub use server::{OpenCodeServer, OpenCodeServerPool};
pub use types::{OpenCodePermissions, QuestionAnswer, QuestionInfo, QuestionOption};
pub use worker::{OpenCodeWorker, OpenCodeWorkerResult};
