mod traits;
pub mod memory;

#[cfg(not(target_arch = "wasm32"))]
pub mod sqlite;

pub use traits::StorageBackend;
pub use memory::InMemoryBackend;

#[cfg(not(target_arch = "wasm32"))]
pub use sqlite::SqliteBackend;
