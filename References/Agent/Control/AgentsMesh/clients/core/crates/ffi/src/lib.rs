uniffi::setup_scaffolding!();

mod auth_ffi;
mod callbacks;
mod core;
mod dto;
mod error;
mod relay_ffi;
mod services;
mod storage_bridge;

pub use callbacks::{EventCallback, OutputCallback, StatusCallback, StorageCallback};
pub use self::core::AgentsMeshCore;
pub use error::CoreError;

#[cfg(test)]
mod tests;
