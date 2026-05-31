use serde_json::json;

use crate::autopilot_state::{AutopilotController, AutopilotIteration, AutopilotState};

fn make_controller(key: &str, phase: &str) -> AutopilotController {
    AutopilotController {
        autopilot_controller_key: key.to_string(),
        pod_key: format!("pod-{key}"),
        status: None,
        phase: Some(phase.to_string()),
        prompt: None,
        max_iterations: None,
        iteration_timeout_sec: None,
        no_progress_threshold: None,
        same_error_threshold: None,
        approval_timeout_min: None,
        current_iteration: None,
        control_agent_slug: None,
        circuit_breaker_state: None,
        circuit_breaker_reason: None,
        created_at: None,
        updated_at: None,
    }
}

fn make_iteration(id: i64, key: &str) -> AutopilotIteration {
    AutopilotIteration {
        id,
        controller_key: key.to_string(),
        iteration_number: Some(id),
        status: None,
        result: None,
        started_at: None,
        completed_at: None,
    }
}

#[test]
fn new_is_empty() {
    let s = AutopilotState::new();
    assert!(s.controllers().is_empty());
    assert!(s.current_controller().is_none());
}

#[test]
fn set_and_get_controllers() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running")]);
    assert_eq!(s.controllers().len(), 1);
}

#[test]
fn set_current_controller() {
    let mut s = AutopilotState::new();
    s.set_current_controller(Some(make_controller("c1", "running")));
    assert_eq!(s.current_controller().unwrap().autopilot_controller_key, "c1");
    s.set_current_controller(None);
    assert!(s.current_controller().is_none());
}

#[test]
fn add_controller() {
    let mut s = AutopilotState::new();
    s.add_controller(make_controller("c1", "running"));
    s.add_controller(make_controller("c2", "paused"));
    assert_eq!(s.controllers().len(), 2);
}

#[test]
fn update_controller_replaces() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running")]);
    let mut updated = make_controller("c1", "running");
    updated.phase = Some("paused".to_string());
    updated.current_iteration = Some(50);
    s.update_controller("c1", updated);
    let c = &s.controllers()[0];
    assert_eq!(c.phase.as_deref(), Some("paused"));
    assert_eq!(c.current_iteration, Some(50));
}

#[test]
fn update_controller_also_updates_current() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running")]);
    s.set_current_controller(Some(make_controller("c1", "running")));
    let mut updated = make_controller("c1", "running");
    updated.current_iteration = Some(99);
    s.update_controller("c1", updated);
    assert_eq!(s.current_controller().unwrap().current_iteration, Some(99));
}

#[test]
fn update_controller_nonexistent_is_noop() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running")]);
    s.update_controller("no-such-key", make_controller("no-such-key", "running"));
    assert_eq!(s.controllers().len(), 1);
    assert_eq!(s.controllers()[0].autopilot_controller_key, "c1");
}

#[test]
fn remove_controller() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running"), make_controller("c2", "paused")]);
    s.remove_controller("c1");
    assert_eq!(s.controllers().len(), 1);
    assert_eq!(s.controllers()[0].autopilot_controller_key, "c2");
}

#[test]
fn remove_controller_clears_current_if_same() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running")]);
    s.set_current_controller(Some(make_controller("c1", "running")));
    s.remove_controller("c1");
    assert!(s.current_controller().is_none());
}

#[test]
fn remove_controller_keeps_current_if_different() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running"), make_controller("c2", "paused")]);
    s.set_current_controller(Some(make_controller("c2", "paused")));
    s.remove_controller("c1");
    assert!(s.current_controller().is_some());
}

#[test]
fn iterations_crud() {
    let mut s = AutopilotState::new();
    assert!(s.get_iterations("k1").is_none());
    s.set_iterations("k1".into(), vec![make_iteration(1, "k1"), make_iteration(2, "k1")]);
    assert_eq!(s.get_iterations("k1").unwrap().len(), 2);
    s.add_iteration("k1".into(), make_iteration(3, "k1"));
    assert_eq!(s.get_iterations("k1").unwrap().len(), 3);
}

#[test]
fn iterations_cap() {
    let mut s = AutopilotState::new();
    for i in 0..210 {
        s.add_iteration("k".into(), make_iteration(i, "k"));
    }
    assert_eq!(s.get_iterations("k").unwrap().len(), 200);
}

#[test]
fn thinking_crud() {
    let mut s = AutopilotState::new();
    assert!(s.get_thinking("k1").is_none());
    s.update_thinking("k1".into(), json!({"step": 1}));
    assert_eq!(s.get_thinking("k1").unwrap()["step"], 1);
    s.update_thinking("k1".into(), json!({"step": 2}));
    assert_eq!(s.get_thinking("k1").unwrap()["step"], 2);
}

#[test]
fn thinking_history_cap() {
    let mut s = AutopilotState::new();
    for i in 0..110 {
        s.update_thinking("k".into(), json!({"i": i}));
    }
    assert_eq!(s.get_thinking_history("k").unwrap().len(), 100);
}

#[test]
fn get_controller_by_pod_key_finds_active() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![
        make_controller("c1", "completed"),
        make_controller("c2", "running"),
    ]);
    let found = s.get_controller_by_pod_key("pod-c2").unwrap();
    assert_eq!(found.autopilot_controller_key, "c2");
}

#[test]
fn get_controller_by_pod_key_ignores_inactive() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![
        make_controller("c1", "completed"),
        make_controller("c2", "failed"),
        make_controller("c3", "cancelled"),
    ]);
    assert!(s.get_controller_by_pod_key("pod-c1").is_none());
    assert!(s.get_controller_by_pod_key("pod-c2").is_none());
    assert!(s.get_controller_by_pod_key("pod-c3").is_none());
}

#[test]
fn get_controller_by_pod_key_active_phases() {
    let mut s = AutopilotState::new();
    let phases = ["initializing", "running", "paused", "user_takeover", "waiting_approval"];
    for (i, phase) in phases.iter().enumerate() {
        let mut c = make_controller(&format!("c{i}"), phase);
        c.pod_key = format!("pod-{i}");
        s.add_controller(c);
    }
    for i in 0..phases.len() {
        assert!(
            s.get_controller_by_pod_key(&format!("pod-{i}")).is_some(),
            "phase '{}' should be active",
            phases[i]
        );
    }
}

#[test]
fn get_controller_by_pod_key_not_found() {
    let mut s = AutopilotState::new();
    s.set_controllers(vec![make_controller("c1", "running")]);
    assert!(s.get_controller_by_pod_key("nonexistent").is_none());
}

#[test]
fn get_controller_by_pod_key_missing_phase_field() {
    let mut s = AutopilotState::new();
    let mut c = make_controller("c1", "running");
    c.phase = None;
    c.pod_key = "pod-1".to_string();
    s.set_controllers(vec![c]);
    assert!(s.get_controller_by_pod_key("pod-1").is_none());
}
