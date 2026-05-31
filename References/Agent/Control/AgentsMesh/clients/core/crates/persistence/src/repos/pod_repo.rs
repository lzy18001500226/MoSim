use std::sync::Arc;

use agentsmesh_types::proto_pod_v1::Pod;

use crate::backend::StorageBackend;
use crate::error::Result;

pub struct PodRepo {
    backend: Arc<dyn StorageBackend>,
}

impl PodRepo {
    pub fn new(backend: Arc<dyn StorageBackend>) -> Self {
        Self { backend }
    }

    pub fn save_pod(&self, pod: &Pod) -> Result<()> {
        let data = serde_json::to_vec(pod)?;
        let runner_id_str = pod.runner_id.map(|v| v.to_string()).unwrap_or_default();
        let indexed: Vec<(&str, &str)> = vec![("status", pod.status.as_str()), ("runner_id", &runner_id_str)];
        self.backend.put_raw("pods", &pod.pod_key, &indexed, &data)
    }

    pub fn get_pod(&self, key: &str) -> Result<Option<Pod>> {
        match self.backend.get_raw("pods", key)? {
            Some(data) => Ok(Some(serde_json::from_slice(&data)?)),
            None => Ok(None),
        }
    }

    pub fn list_pods(&self) -> Result<Vec<Pod>> {
        super::deserialize_rows(self.backend.list_raw("pods")?)
    }

    pub fn get_by_status(&self, status: &str) -> Result<Vec<Pod>> {
        super::deserialize_rows(self.backend.query_raw("pods", "status", status)?)
    }

    pub fn delete_pod(&self, key: &str) -> Result<()> {
        self.backend.delete_raw("pods", key)
    }

    pub fn clear(&self) -> Result<()> {
        self.backend.clear("pods")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::backend::InMemoryBackend;

    fn make_repo() -> PodRepo {
        PodRepo::new(Arc::new(InMemoryBackend::new()))
    }

    fn make_pod(key: &str, status: &str, runner_id: Option<i64>) -> Pod {
        Pod {
            pod_key: key.into(),
            status: status.into(),
            agent_slug: "claude".into(),
            runner_id,
            ..Default::default()
        }
    }

    #[test]
    fn save_and_get_roundtrip() {
        let repo = make_repo();
        repo.save_pod(&make_pod("p1", "running", Some(1))).unwrap();
        let loaded = repo.get_pod("p1").unwrap().unwrap();
        assert_eq!(loaded.status, "running");
    }

    #[test]
    fn get_nonexistent_returns_none() {
        let repo = make_repo();
        assert!(repo.get_pod("nope").unwrap().is_none());
    }

    #[test]
    fn delete_roundtrip() {
        let repo = make_repo();
        repo.save_pod(&make_pod("p1", "running", Some(1))).unwrap();
        repo.delete_pod("p1").unwrap();
        assert!(repo.get_pod("p1").unwrap().is_none());
    }

    #[test]
    fn delete_nonexistent_is_noop() {
        let repo = make_repo();
        repo.delete_pod("nope").unwrap();
    }

    #[test]
    fn list_pods() {
        let repo = make_repo();
        repo.save_pod(&make_pod("p1", "running", Some(1))).unwrap();
        repo.save_pod(&make_pod("p2", "terminated", Some(2))).unwrap();
        assert_eq!(repo.list_pods().unwrap().len(), 2);
    }

    #[test]
    fn list_empty() {
        let repo = make_repo();
        assert!(repo.list_pods().unwrap().is_empty());
    }

    #[test]
    fn filter_by_status() {
        let repo = make_repo();
        repo.save_pod(&make_pod("p1", "running", Some(1))).unwrap();
        repo.save_pod(&make_pod("p2", "terminated", Some(2))).unwrap();
        repo.save_pod(&make_pod("p3", "running", Some(3))).unwrap();
        assert_eq!(repo.get_by_status("running").unwrap().len(), 2);
        assert_eq!(repo.get_by_status("terminated").unwrap().len(), 1);
    }

    #[test]
    fn filter_by_status_no_match() {
        let repo = make_repo();
        repo.save_pod(&make_pod("p1", "running", Some(1))).unwrap();
        assert!(repo.get_by_status("error").unwrap().is_empty());
    }

    #[test]
    fn save_overwrites_existing() {
        let repo = make_repo();
        repo.save_pod(&make_pod("p1", "running", Some(1))).unwrap();
        repo.save_pod(&make_pod("p1", "terminated", Some(1))).unwrap();
        let loaded = repo.get_pod("p1").unwrap().unwrap();
        assert_eq!(loaded.status, "terminated");
        assert_eq!(repo.list_pods().unwrap().len(), 1);
    }

    #[test]
    fn clear_removes_all() {
        let repo = make_repo();
        repo.save_pod(&make_pod("p1", "running", Some(1))).unwrap();
        repo.save_pod(&make_pod("p2", "terminated", Some(2))).unwrap();
        repo.clear().unwrap();
        assert!(repo.list_pods().unwrap().is_empty());
    }

    #[test]
    fn clear_empty_table_is_noop() {
        let repo = make_repo();
        repo.clear().unwrap();
    }
}
