use agentsmesh_types::proto_repository_v1::{Branch, Repository};

use crate::repo_state::RepoState;

fn make_repo(id: i64, name: &str) -> Repository {
    Repository {
        id, name: name.to_string(), slug: name.to_lowercase(),
        ..Default::default()
    }
}

fn make_branch(name: &str) -> Branch {
    Branch { name: name.to_string(), ..Default::default() }
}

#[test]
fn new_is_empty() {
    let s = RepoState::new();
    assert!(s.repositories().is_empty());
    assert!(s.current_repo().is_none());
    assert!(s.branches().is_empty());
}

#[test]
fn set_and_get_repositories() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "repo1")]);
    assert_eq!(s.repositories().len(), 1);
    assert_eq!(s.repositories()[0].slug, "repo1");
}

#[test]
fn set_repositories_replaces_previous() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "r1")]);
    s.set_repositories(vec![make_repo(2, "r2"), make_repo(3, "r3")]);
    assert_eq!(s.repositories().len(), 2);
    assert_eq!(s.repositories()[0].id, 2);
}

#[test]
fn set_current_repo() {
    let mut s = RepoState::new();
    s.set_current_repo(Some(make_repo(1, "my-repo")));
    assert_eq!(s.current_repo().unwrap().name, "my-repo");
    s.set_current_repo(None);
    assert!(s.current_repo().is_none());
}

#[test]
fn set_branches() {
    let mut s = RepoState::new();
    s.set_branches(vec![make_branch("main"), make_branch("dev")]);
    assert_eq!(s.branches().len(), 2);
    assert_eq!(s.branches()[0].name, "main");
}

#[test]
fn add_repository() {
    let mut s = RepoState::new();
    s.add_repository(make_repo(1, "r1"));
    s.add_repository(make_repo(2, "r2"));
    assert_eq!(s.repositories().len(), 2);
}

#[test]
fn update_repository() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "old")]);
    s.update_repository("1", make_repo(1, "new"));
    assert_eq!(s.repositories()[0].name, "new");
}

#[test]
fn update_repository_nonexistent_is_noop() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "old")]);
    s.update_repository("999", make_repo(999, "new"));
    assert_eq!(s.repositories()[0].name, "old");
}

#[test]
fn remove_repository() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "r1"), make_repo(2, "r2")]);
    s.remove_repository("1");
    assert_eq!(s.repositories().len(), 1);
    assert_eq!(s.repositories()[0].id, 2);
}

#[test]
fn remove_repository_clears_current_if_same() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "r1")]);
    s.set_current_repo(Some(make_repo(1, "r1")));
    s.remove_repository("1");
    assert!(s.current_repo().is_none());
}

#[test]
fn remove_repository_keeps_current_if_different() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "r1"), make_repo(2, "r2")]);
    s.set_current_repo(Some(make_repo(2, "r2")));
    s.remove_repository("1");
    assert_eq!(s.current_repo().unwrap().id, 2);
}

#[test]
fn remove_repository_nonexistent_is_noop() {
    let mut s = RepoState::new();
    s.set_repositories(vec![make_repo(1, "r1")]);
    s.remove_repository("999");
    assert_eq!(s.repositories().len(), 1);
}
