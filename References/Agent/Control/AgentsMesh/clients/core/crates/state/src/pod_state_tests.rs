use agentsmesh_types::proto_pod_v1::Pod;

use crate::pod_state::PodState;

fn make_pod(key: &str, status: &str) -> Pod {
    Pod {
        pod_key: key.into(),
        status: status.into(),
        agent_slug: "claude-code".into(),
        ..Default::default()
    }
}

#[test]
fn new_state_is_empty() {
    let s = PodState::new();
    assert!(s.pods().is_empty());
    assert!(s.current_pod().is_none());
}

#[test]
fn upsert_inserts_new_pod() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), Some(100));
    assert_eq!(s.pods().len(), 1);
    assert_eq!(s.get_pod("p1").unwrap().status, "running");
}

#[test]
fn upsert_updates_existing_pod() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "pending"), Some(100));
    s.upsert_pod(make_pod("p1", "running"), Some(200));
    assert_eq!(s.pods().len(), 1);
    assert_eq!(s.get_pod("p1").unwrap().status, "running");
}

#[test]
fn timestamp_guard_rejects_stale_update() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), Some(200));
    s.upsert_pod(make_pod("p1", "pending"), Some(100));
    assert_eq!(s.get_pod("p1").unwrap().status, "running");
}

#[test]
fn timestamp_guard_rejects_equal_timestamp() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), Some(100));
    s.upsert_pod(make_pod("p1", "terminated"), Some(100));
    assert_eq!(s.get_pod("p1").unwrap().status, "running");
}

#[test]
fn upsert_without_timestamp_always_applies() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), Some(999));
    s.upsert_pod(make_pod("p1", "terminated"), None);
    assert_eq!(s.get_pod("p1").unwrap().status, "terminated");
}

#[test]
fn upsert_syncs_current_pod() {
    let mut s = PodState::new();
    s.set_current_pod(Some(make_pod("p1", "running")));
    s.upsert_pod(make_pod("p1", "terminated"), Some(200));
    assert_eq!(s.current_pod().unwrap().status, "terminated");
}

#[test]
fn upsert_does_not_touch_unrelated_current_pod() {
    let mut s = PodState::new();
    s.set_current_pod(Some(make_pod("other", "running")));
    s.upsert_pod(make_pod("p1", "terminated"), None);
    assert_eq!(s.current_pod().unwrap().pod_key, "other");
    assert_eq!(s.current_pod().unwrap().status, "running");
}

#[test]
fn update_pod_status_with_timestamp_guard() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), Some(100));
    s.update_pod_status("p1", "terminated", None, None, None, Some(50));
    assert_eq!(s.get_pod("p1").unwrap().status, "running");

    s.update_pod_status(
        "p1",
        "terminated",
        Some("done"),
        Some("E001"),
        Some("timeout"),
        Some(200),
    );
    let p = s.get_pod("p1").unwrap();
    assert_eq!(p.status, "terminated");
    assert_eq!(p.agent_status, "done");
    assert_eq!(p.error_code.as_deref(), Some("E001"));
    assert_eq!(p.error_message.as_deref(), Some("timeout"));
}

#[test]
fn update_pod_status_syncs_current_pod() {
    let mut s = PodState::new();
    let pod = make_pod("p1", "running");
    s.upsert_pod(pod.clone(), None);
    s.set_current_pod(Some(pod));
    s.update_pod_status("p1", "terminated", None, None, None, None);
    assert_eq!(s.current_pod().unwrap().status, "terminated");
}

#[test]
fn update_title_with_guard() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), Some(100));
    s.update_pod_title("p1", "New Title", Some(50));
    assert!(s.get_pod("p1").unwrap().title.is_none());

    s.update_pod_title("p1", "New Title", Some(200));
    assert_eq!(s.get_pod("p1").unwrap().title.as_deref(), Some("New Title"));
}

#[test]
fn update_alias_no_guard() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), Some(999));
    s.update_pod_alias("p1", "my-alias");
    assert_eq!(s.get_pod("p1").unwrap().alias.as_deref(), Some("my-alias"));
}

#[test]
fn update_alias_syncs_current_pod() {
    let mut s = PodState::new();
    let pod = make_pod("p1", "running");
    s.upsert_pod(pod.clone(), None);
    s.set_current_pod(Some(pod));
    s.update_pod_alias("p1", "alias2");
    assert_eq!(s.current_pod().unwrap().alias.as_deref(), Some("alias2"));
}

#[test]
fn init_progress_lifecycle() {
    let mut s = PodState::new();
    assert!(s.get_init_progress("p1").is_none());

    s.update_init_progress("p1", "pulling", 0.5, Some("50%"));
    let prog = s.get_init_progress("p1").unwrap();
    assert_eq!(prog.phase, "pulling");
    assert!((prog.progress - 0.5).abs() < f64::EPSILON);
    assert_eq!(prog.message.as_deref(), Some("50%"));

    s.clear_init_progress("p1");
    assert!(s.get_init_progress("p1").is_none());
}

#[test]
fn remove_pod_cleans_up_everything() {
    let mut s = PodState::new();
    let pod = make_pod("p1", "running");
    s.upsert_pod(pod.clone(), Some(100));
    s.set_current_pod(Some(pod));
    s.update_init_progress("p1", "ready", 1.0, None);

    s.remove_pod("p1");
    assert!(s.get_pod("p1").is_none());
    assert!(s.current_pod().is_none());
    assert!(s.get_init_progress("p1").is_none());
    assert!(s.should_update("p1", 0));
}

#[test]
fn remove_pod_preserves_unrelated_current() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("p1", "running"), None);
    s.set_current_pod(Some(make_pod("other", "running")));
    s.remove_pod("p1");
    assert!(s.current_pod().is_some());
}

#[test]
fn set_pods_replaces_list() {
    let mut s = PodState::new();
    s.upsert_pod(make_pod("old", "running"), None);
    s.set_pods(vec![make_pod("a", "running"), make_pod("b", "pending")]);
    assert_eq!(s.pods().len(), 2);
    assert!(s.get_pod("old").is_none());
}

#[test]
fn should_update_returns_true_for_unknown_key() {
    let s = PodState::new();
    assert!(s.should_update("unknown", 0));
}

#[test]
fn get_pod_returns_none_for_missing() {
    let s = PodState::new();
    assert!(s.get_pod("nope").is_none());
}
