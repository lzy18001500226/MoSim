use std::sync::Arc;

use agentsmesh_types::proto_runner_api_v1::Runner;

use crate::backend::StorageBackend;
use crate::error::Result;

pub struct RunnerRepo {
    backend: Arc<dyn StorageBackend>,
}

impl RunnerRepo {
    pub fn new(backend: Arc<dyn StorageBackend>) -> Self {
        Self { backend }
    }

    pub fn get(&self, id: i64) -> Result<Option<Runner>> {
        match self.backend.get_raw("runners", &id.to_string())? {
            Some(data) => Ok(Some(serde_json::from_slice(&data)?)),
            None => Ok(None),
        }
    }

    pub fn save(&self, runner: &Runner) -> Result<()> {
        let data = serde_json::to_vec(runner)?;
        let fields: &[(&str, &str)] = &[("status", runner.status.as_str())];
        self.backend
            .put_raw("runners", &runner.id.to_string(), fields, &data)
    }

    pub fn delete(&self, id: i64) -> Result<()> {
        self.backend.delete_raw("runners", &id.to_string())
    }

    pub fn get_by_status(&self, status: &str) -> Result<Vec<Runner>> {
        super::deserialize_rows(self.backend.query_raw("runners", "status", status)?)
    }

    pub fn list_all(&self) -> Result<Vec<Runner>> {
        super::deserialize_rows(self.backend.list_raw("runners")?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::backend::InMemoryBackend;

    fn make_repo() -> RunnerRepo {
        RunnerRepo::new(Arc::new(InMemoryBackend::new()))
    }

    fn make_runner(id: i64, status: &str) -> Runner {
        Runner {
            id,
            node_id: format!("runner-{id}"),
            status: status.into(),
            max_concurrent_pods: 4,
            is_enabled: true,
            ..Default::default()
        }
    }

    #[test]
    fn crud_roundtrip() {
        let repo = make_repo();
        repo.save(&make_runner(1, "online")).unwrap();
        let loaded = repo.get(1).unwrap().unwrap();
        assert_eq!(loaded.node_id, "runner-1");
        repo.delete(1).unwrap();
        assert!(repo.get(1).unwrap().is_none());
    }

    #[test]
    fn filter_by_status() {
        let repo = make_repo();
        repo.save(&make_runner(1, "online")).unwrap();
        repo.save(&make_runner(2, "offline")).unwrap();
        repo.save(&make_runner(3, "online")).unwrap();
        assert_eq!(repo.get_by_status("online").unwrap().len(), 2);
    }

    #[test]
    fn list_all() {
        let repo = make_repo();
        repo.save(&make_runner(1, "online")).unwrap();
        repo.save(&make_runner(2, "offline")).unwrap();
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
        repo.save(&make_runner(1, "online")).unwrap();
        repo.save(&make_runner(1, "offline")).unwrap();
        let loaded = repo.get(1).unwrap().unwrap();
        assert_eq!(loaded.status, "offline");
        assert_eq!(repo.list_all().unwrap().len(), 1);
    }

    #[test]
    fn filter_by_status_empty() {
        let repo = make_repo();
        repo.save(&make_runner(1, "online")).unwrap();
        assert!(repo.get_by_status("offline").unwrap().is_empty());
    }

    #[test]
    fn delete_removes_from_status_index() {
        let repo = make_repo();
        repo.save(&make_runner(1, "online")).unwrap();
        repo.delete(1).unwrap();
        assert!(repo.get_by_status("online").unwrap().is_empty());
    }

    #[test]
    fn list_empty_table() {
        let repo = make_repo();
        assert!(repo.list_all().unwrap().is_empty());
    }
}
