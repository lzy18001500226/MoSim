use std::sync::Arc;

use agentsmesh_types::proto_ticket_v1::Ticket;

use crate::backend::StorageBackend;
use crate::error::Result;

pub struct TicketRepo {
    backend: Arc<dyn StorageBackend>,
}

impl TicketRepo {
    pub fn new(backend: Arc<dyn StorageBackend>) -> Self {
        Self { backend }
    }

    pub fn save_ticket(&self, ticket: &Ticket) -> Result<()> {
        let data = serde_json::to_vec(ticket)?;
        let indexed: Vec<(&str, &str)> =
            vec![("status", ticket.status.as_str()), ("priority", ticket.priority.as_str())];
        self.backend.put_raw("tickets", &ticket.slug, &indexed, &data)
    }

    pub fn get_ticket(&self, slug: &str) -> Result<Option<Ticket>> {
        match self.backend.get_raw("tickets", slug)? {
            Some(data) => Ok(Some(serde_json::from_slice(&data)?)),
            None => Ok(None),
        }
    }

    pub fn list_tickets(&self) -> Result<Vec<Ticket>> {
        super::deserialize_rows(self.backend.list_raw("tickets")?)
    }

    pub fn get_by_status(&self, status: &str) -> Result<Vec<Ticket>> {
        super::deserialize_rows(self.backend.query_raw("tickets", "status", status)?)
    }

    pub fn delete_ticket(&self, slug: &str) -> Result<()> {
        self.backend.delete_raw("tickets", slug)
    }

    pub fn clear(&self) -> Result<()> {
        self.backend.clear("tickets")
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::backend::InMemoryBackend;

    fn make_repo() -> TicketRepo {
        TicketRepo::new(Arc::new(InMemoryBackend::new()))
    }

    fn make_ticket(slug: &str, status: &str, priority: &str) -> Ticket {
        Ticket {
            slug: slug.into(),
            title: slug.into(),
            content: None,
            status: status.into(),
            priority: priority.into(),
            ..Default::default()
        }
    }

    #[test]
    fn save_and_get_roundtrip() {
        let repo = make_repo();
        repo.save_ticket(&make_ticket("t-1", "todo", "high")).unwrap();
        let loaded = repo.get_ticket("t-1").unwrap().unwrap();
        assert_eq!(loaded.status, "todo");
        assert_eq!(loaded.priority, "high");
    }

    #[test]
    fn get_nonexistent_returns_none() {
        let repo = make_repo();
        assert!(repo.get_ticket("nope").unwrap().is_none());
    }

    #[test]
    fn delete_roundtrip() {
        let repo = make_repo();
        repo.save_ticket(&make_ticket("t-1", "todo", "high")).unwrap();
        repo.delete_ticket("t-1").unwrap();
        assert!(repo.get_ticket("t-1").unwrap().is_none());
    }

    #[test]
    fn delete_nonexistent_is_noop() {
        let repo = make_repo();
        repo.delete_ticket("nope").unwrap();
    }

    #[test]
    fn list_tickets() {
        let repo = make_repo();
        repo.save_ticket(&make_ticket("t-1", "todo", "high")).unwrap();
        repo.save_ticket(&make_ticket("t-2", "done", "low")).unwrap();
        assert_eq!(repo.list_tickets().unwrap().len(), 2);
    }

    #[test]
    fn list_empty() {
        let repo = make_repo();
        assert!(repo.list_tickets().unwrap().is_empty());
    }

    #[test]
    fn filter_by_status() {
        let repo = make_repo();
        repo.save_ticket(&make_ticket("t-1", "todo", "high")).unwrap();
        repo.save_ticket(&make_ticket("t-2", "done", "low")).unwrap();
        repo.save_ticket(&make_ticket("t-3", "todo", "medium")).unwrap();
        assert_eq!(repo.get_by_status("todo").unwrap().len(), 2);
        assert_eq!(repo.get_by_status("done").unwrap().len(), 1);
    }

    #[test]
    fn filter_by_status_no_match() {
        let repo = make_repo();
        repo.save_ticket(&make_ticket("t-1", "todo", "high")).unwrap();
        assert!(repo.get_by_status("in_progress").unwrap().is_empty());
    }

    #[test]
    fn save_overwrites_existing() {
        let repo = make_repo();
        repo.save_ticket(&make_ticket("t-1", "todo", "high")).unwrap();
        repo.save_ticket(&make_ticket("t-1", "done", "low")).unwrap();
        let loaded = repo.get_ticket("t-1").unwrap().unwrap();
        assert_eq!(loaded.status, "done");
        assert_eq!(repo.list_tickets().unwrap().len(), 1);
    }

    #[test]
    fn clear_removes_all() {
        let repo = make_repo();
        repo.save_ticket(&make_ticket("t-1", "todo", "high")).unwrap();
        repo.save_ticket(&make_ticket("t-2", "done", "low")).unwrap();
        repo.clear().unwrap();
        assert!(repo.list_tickets().unwrap().is_empty());
    }
}
