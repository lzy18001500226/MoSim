use std::sync::Arc;

use agentsmesh_auth::PersistentStorage;

use crate::callbacks::StorageCallback;

pub(crate) struct StorageBridge {
    inner: Arc<dyn StorageCallback>,
}

impl StorageBridge {
    pub fn new(callback: Arc<dyn StorageCallback>) -> Self {
        Self { inner: callback }
    }
}

impl PersistentStorage for StorageBridge {
    fn get(&self, key: &str) -> Option<String> {
        self.inner.get(key.to_string())
    }

    fn set(&self, key: &str, value: &str) {
        self.inner.set(key.to_string(), value.to_string());
    }

    fn remove(&self, key: &str) {
        self.inner.remove(key.to_string());
    }
}
