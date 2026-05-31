use std::sync::Arc;

use agentsmesh_persistence::StorageBackend;
use serde::de::DeserializeOwned;
use serde::Serialize;

pub(crate) struct JsonStore {
    backend: Arc<dyn StorageBackend>,
    table: String,
}

impl JsonStore {
    pub fn new(backend: Arc<dyn StorageBackend>, table: impl Into<String>) -> Self {
        Self { backend, table: table.into() }
    }

    pub fn save<T: Serialize>(&self, key: &str, value: &T) {
        let data = serde_json::to_vec(value).unwrap_or_default();
        let _ = self.backend.put_raw(&self.table, key, &[], &data);
    }

    pub fn load_all<T: DeserializeOwned>(&self) -> Vec<T> {
        self.backend
            .list_raw(&self.table)
            .unwrap_or_default()
            .into_iter()
            .filter_map(|(_, data)| serde_json::from_slice(&data).ok())
            .collect()
    }

    pub fn load_one<T: DeserializeOwned>(&self, key: &str) -> Option<T> {
        self.backend
            .get_raw(&self.table, key)
            .ok()
            .flatten()
            .and_then(|data| serde_json::from_slice(&data).ok())
    }

    pub fn delete(&self, key: &str) {
        let _ = self.backend.delete_raw(&self.table, key);
    }

    pub fn replace_all<T: Serialize>(&self, items: &[T], id_extractor: impl Fn(&T) -> String) {
        let _ = self.backend.clear(&self.table);
        for item in items {
            let id = id_extractor(item);
            self.save(&id, item);
        }
    }
}
