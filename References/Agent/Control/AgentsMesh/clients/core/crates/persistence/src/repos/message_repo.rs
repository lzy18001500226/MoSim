use std::marker::PhantomData;
use std::sync::Arc;

use serde::Serialize;
use serde::de::DeserializeOwned;

use crate::backend::StorageBackend;
use crate::error::Result;

pub trait MessageRow: Serialize + DeserializeOwned {
    fn id(&self) -> i64;
    fn channel_id(&self) -> i64;
}

pub struct MessageRepo<M: MessageRow = ()> {
    backend: Arc<dyn StorageBackend>,
    _phantom: PhantomData<fn(M)>,
}

impl<M: MessageRow> MessageRepo<M> {
    pub fn new(backend: Arc<dyn StorageBackend>) -> Self {
        Self { backend, _phantom: PhantomData }
    }

    pub fn save_message(&self, msg: &M) -> Result<()> {
        let data = serde_json::to_vec(msg)?;
        let channel_id = msg.channel_id().to_string();
        let msg_id = msg.id().to_string();
        let indexed = vec![
            ("channel_id".to_string(), channel_id),
            ("msg_id".to_string(), msg_id),
        ];
        self.backend.put_raw(
            "channel_messages",
            &msg.id().to_string(),
            &indexed.iter().map(|(k, v)| (k.as_str(), v.as_str())).collect::<Vec<_>>(),
            &data,
        )
    }

    pub fn get_by_channel(&self, channel_id: i64, limit: usize, before_id: Option<i64>) -> Result<Vec<M>> {
        let rows = self
            .backend
            .query_raw("channel_messages", "channel_id", &channel_id.to_string())?;
        let mut msgs: Vec<M> = rows
            .iter()
            .filter_map(|(_, data)| serde_json::from_slice(data).ok())
            .collect();
        msgs.sort_by(|a, b| b.id().cmp(&a.id()));
        if let Some(bid) = before_id {
            msgs.retain(|m| m.id() < bid);
        }
        msgs.truncate(limit);
        Ok(msgs)
    }

    pub fn delete_message(&self, message_id: i64) -> Result<()> {
        self.backend.delete_raw("channel_messages", &message_id.to_string())
    }

    pub fn clear_channel(&self, channel_id: i64) -> Result<()> {
        let rows = self
            .backend
            .query_raw("channel_messages", "channel_id", &channel_id.to_string())?;
        for (id, _) in rows {
            self.backend.delete_raw("channel_messages", &id)?;
        }
        Ok(())
    }
}

impl MessageRow for () {
    fn id(&self) -> i64 { 0 }
    fn channel_id(&self) -> i64 { 0 }
}

// Blanket impl for the proto-generated state schema. Same rationale as
// `ChannelRow for proto Channel`.
impl MessageRow for agentsmesh_types::proto_channel_state_v1::ChannelMessage {
    fn id(&self) -> i64 {
        self.id
    }
    fn channel_id(&self) -> i64 {
        self.channel_id
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::backend::InMemoryBackend;
    use serde::{Deserialize, Serialize};

    #[derive(Debug, Clone, Serialize, Deserialize, Default)]
    struct TestMsg {
        id: i64,
        channel_id: i64,
        body: String,
    }
    impl MessageRow for TestMsg {
        fn id(&self) -> i64 { self.id }
        fn channel_id(&self) -> i64 { self.channel_id }
    }

    fn make_msg(id: i64, channel_id: i64, content: &str) -> TestMsg {
        TestMsg { id, channel_id, body: content.into() }
    }

    #[test]
    fn save_and_get_by_channel() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);

        repo.save_message(&make_msg(1, 10, "hello")).unwrap();
        repo.save_message(&make_msg(2, 10, "world")).unwrap();
        repo.save_message(&make_msg(3, 20, "other channel")).unwrap();

        let msgs = repo.get_by_channel(10, 50, None).unwrap();
        assert_eq!(msgs.len(), 2);
        assert_eq!(msgs[0].id, 2);
    }

    #[test]
    fn get_by_channel_with_limit() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);

        for i in 1..=10 {
            repo.save_message(&make_msg(i, 10, &format!("msg {i}"))).unwrap();
        }

        let msgs = repo.get_by_channel(10, 3, None).unwrap();
        assert_eq!(msgs.len(), 3);
    }

    #[test]
    fn delete_message() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);

        repo.save_message(&make_msg(1, 10, "hi")).unwrap();
        repo.delete_message(1).unwrap();
        assert!(repo.get_by_channel(10, 50, None).unwrap().is_empty());
    }

    #[test]
    fn empty_channel_returns_empty() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);
        assert!(repo.get_by_channel(999, 50, None).unwrap().is_empty());
    }

    #[test]
    fn clear_channel_removes_all() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);

        repo.save_message(&make_msg(1, 10, "a")).unwrap();
        repo.save_message(&make_msg(2, 10, "b")).unwrap();
        repo.clear_channel(10).unwrap();
        assert!(repo.get_by_channel(10, 50, None).unwrap().is_empty());
    }

    #[test]
    fn delete_nonexistent_message_is_noop() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);
        repo.delete_message(999).unwrap();
    }

    #[test]
    fn messages_sorted_newest_first() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);

        for i in 1..=5 {
            repo.save_message(&make_msg(i, 1, &format!("msg{i}"))).unwrap();
        }
        let msgs = repo.get_by_channel(1, 50, None).unwrap();
        for w in msgs.windows(2) {
            assert!(w[0].id > w[1].id);
        }
    }

    #[test]
    fn get_by_channel_with_before_id() {
        let backend = Arc::new(InMemoryBackend::new());
        backend.migrate().unwrap();
        let repo = MessageRepo::<TestMsg>::new(backend);

        for i in 1..=10 {
            repo.save_message(&make_msg(i, 1, &format!("msg{i}"))).unwrap();
        }
        let msgs = repo.get_by_channel(1, 50, Some(6)).unwrap();
        assert_eq!(msgs.len(), 5);
        assert_eq!(msgs[0].id, 5);
        assert_eq!(msgs[4].id, 1);

        let msgs = repo.get_by_channel(1, 2, Some(6)).unwrap();
        assert_eq!(msgs.len(), 2);
        assert_eq!(msgs[0].id, 5);
        assert_eq!(msgs[1].id, 4);
    }
}
