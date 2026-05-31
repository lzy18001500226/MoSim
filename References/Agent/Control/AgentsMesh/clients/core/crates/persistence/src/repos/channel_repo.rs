use std::marker::PhantomData;
use std::sync::Arc;

use serde::Serialize;
use serde::de::DeserializeOwned;

use crate::backend::StorageBackend;
use crate::error::Result;

pub trait ChannelRow: Serialize + DeserializeOwned {
    fn id(&self) -> i64;
}

pub struct ChannelRepo<C: ChannelRow = ()> {
    backend: Arc<dyn StorageBackend>,
    _phantom: PhantomData<fn(C)>,
}

impl<C: ChannelRow> ChannelRepo<C> {
    pub fn new(backend: Arc<dyn StorageBackend>) -> Self {
        Self { backend, _phantom: PhantomData }
    }

    pub fn get(&self, id: i64) -> Result<Option<C>> {
        match self.backend.get_raw("channels", &id.to_string())? {
            Some(data) => Ok(Some(serde_json::from_slice(&data)?)),
            None => Ok(None),
        }
    }

    pub fn save(&self, channel: &C) -> Result<()> {
        let data = serde_json::to_vec(channel)?;
        self.backend
            .put_raw("channels", &channel.id().to_string(), &[], &data)
    }

    pub fn delete(&self, id: i64) -> Result<()> {
        self.backend.delete_raw("channels", &id.to_string())
    }

    pub fn list_all(&self) -> Result<Vec<C>> {
        super::deserialize_rows(self.backend.list_raw("channels")?)
    }
}

// () marker default lets callers use type inference if they're only constructing.
impl ChannelRow for () {
    fn id(&self) -> i64 { 0 }
}

// Blanket impl for the proto-generated state schema so callers can plug
// `ChannelRepo<Channel>` directly without re-declaring the trait at every
// crate boundary (the orphan rule blocks downstream impls).
impl ChannelRow for agentsmesh_types::proto_channel_state_v1::Channel {
    fn id(&self) -> i64 {
        self.id
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::backend::InMemoryBackend;
    use serde::{Deserialize, Serialize};

    #[derive(Debug, Clone, Serialize, Deserialize, Default)]
    struct TestChannel {
        id: i64,
        name: String,
    }
    impl ChannelRow for TestChannel {
        fn id(&self) -> i64 { self.id }
    }

    fn make_repo() -> ChannelRepo<TestChannel> {
        ChannelRepo::new(Arc::new(InMemoryBackend::new()))
    }

    #[test]
    fn crud_roundtrip() {
        let repo = make_repo();
        repo.save(&TestChannel { id: 1, name: "general".into() }).unwrap();
        let loaded = repo.get(1).unwrap().unwrap();
        assert_eq!(loaded.name, "general");
        repo.delete(1).unwrap();
        assert!(repo.get(1).unwrap().is_none());
    }

    #[test]
    fn list_all() {
        let repo = make_repo();
        repo.save(&TestChannel { id: 1, name: "a".into() }).unwrap();
        repo.save(&TestChannel { id: 2, name: "b".into() }).unwrap();
        assert_eq!(repo.list_all().unwrap().len(), 2);
    }

    #[test]
    fn get_nonexistent_returns_none() {
        let repo = make_repo();
        assert!(repo.get(999).unwrap().is_none());
    }

    #[test]
    fn delete_nonexistent_is_noop() {
        let repo = make_repo();
        repo.delete(999).unwrap();
    }

    #[test]
    fn save_overwrites_existing() {
        let repo = make_repo();
        repo.save(&TestChannel { id: 1, name: "old".into() }).unwrap();
        repo.save(&TestChannel { id: 1, name: "new".into() }).unwrap();
        let loaded = repo.get(1).unwrap().unwrap();
        assert_eq!(loaded.name, "new");
        assert_eq!(repo.list_all().unwrap().len(), 1);
    }

    #[test]
    fn list_empty_table() {
        let repo = make_repo();
        assert!(repo.list_all().unwrap().is_empty());
    }
}
