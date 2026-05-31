mod connection;
pub mod dispatch;
pub mod error;
pub mod pool;
mod pool_connect;
mod pool_handlers;
pub mod retry;
pub mod types;

pub use error::RelayError;
pub use pool::RelayConnectionPool;
pub use types::{
    AcpCallback, ConnectionHandle, OutputCallback, RelayStatus, RelayStatusInfo, SnapshotData,
    StatusCallback,
};

#[cfg(test)]
mod connection_tests;
#[cfg(test)]
mod dispatch_tests;
#[cfg(test)]
mod handler_tests;
#[cfg(test)]
mod pool_tests;
