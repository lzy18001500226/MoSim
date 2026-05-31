//! Shared test fixtures. Previously each of the four test modules redefined
//! the same `InMemoryStorage` mock — same shape, same `PersistentStorage`
//! impl, copy-pasted four times. Extracting once removes the drift risk:
//! when the trait grows a method (or shrinks one — see the `clear()`
//! removal), only this module needs an update.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use crate::storage::PersistentStorage;

pub(crate) struct InMemoryStorage {
    data: Mutex<HashMap<String, String>>,
}

impl InMemoryStorage {
    pub(crate) fn new() -> Arc<Self> {
        Arc::new(Self { data: Mutex::new(HashMap::new()) })
    }

    /// Snapshot for tests that need to inspect every stored key (e.g. the
    /// multi-base_url isolation case).
    pub(crate) fn snapshot(&self) -> HashMap<String, String> {
        self.data.lock().unwrap().clone()
    }
}

impl PersistentStorage for InMemoryStorage {
    fn get(&self, key: &str) -> Option<String> {
        self.data.lock().unwrap().get(key).cloned()
    }
    fn set(&self, key: &str, value: &str) {
        self.data.lock().unwrap().insert(key.into(), value.into());
    }
    fn remove(&self, key: &str) {
        self.data.lock().unwrap().remove(key);
    }
}
