use serde_json::json;

use crate::acp_dispatch::{dispatch_event, dispatch_snapshot};
use crate::acp_session::AcpSessionManager;
use crate::acp_types::*;

#[test]
fn dispatch_content_chunk() {
    let mut mgr = AcpSessionManager::new();
    let data = json!({"type": "contentChunk", "text": "hello", "role": "assistant"});
    dispatch_event(&mut mgr, "p", "s1", "contentChunk", &data);
    let s = mgr.get_session("p").unwrap();
    assert_eq!(s.messages.len(), 1);
    assert_eq!(s.messages[0].text, "hello");
}

#[test]
fn dispatch_tool_call_update() {
    let mut mgr = AcpSessionManager::new();
    let data = json!({
        "type": "toolCallUpdate",
        "toolCallId": "tc1",
        "toolName": "bash",
        "status": "running",
        "argumentsJson": "{\"cmd\":\"ls\"}"
    });
    dispatch_event(&mut mgr, "p", "s1", "toolCallUpdate", &data);
    let s = mgr.get_session("p").unwrap();
    assert!(s.tool_calls.contains_key("tc1"));
    assert_eq!(s.tool_calls["tc1"].name, "bash");
    assert_eq!(s.tool_calls["tc1"].args, Some(json!({"cmd": "ls"})));
}

#[test]
fn dispatch_tool_call_result() {
    let mut mgr = AcpSessionManager::new();
    let create = json!({"toolCallId": "tc1", "toolName": "bash", "status": "running"});
    dispatch_event(&mut mgr, "p", "s1", "toolCallUpdate", &create);

    let result = json!({
        "toolCallId": "tc1",
        "success": true,
        "resultText": "output",
        "errorMessage": null
    });
    dispatch_event(&mut mgr, "p", "s1", "toolCallResult", &result);

    let tc = &mgr.get_session("p").unwrap().tool_calls["tc1"];
    assert_eq!(tc.status, "completed");
    assert_eq!(tc.success, Some(true));
    assert_eq!(tc.result_text.as_deref(), Some("output"));
}

#[test]
fn dispatch_plan_update() {
    let mut mgr = AcpSessionManager::new();
    let data = json!({
        "type": "planUpdate",
        "steps": [
            {"title": "Step 1", "status": "done"},
            {"title": "Step 2", "status": "pending"}
        ]
    });
    dispatch_event(&mut mgr, "p", "s1", "planUpdate", &data);
    let s = mgr.get_session("p").unwrap();
    assert_eq!(s.plan.len(), 2);
    assert_eq!(s.plan[0].title, "Step 1");
    assert_eq!(s.plan[1].status, "pending");
}

#[test]
fn dispatch_thinking_update() {
    let mut mgr = AcpSessionManager::new();
    let data = json!({"type": "thinkingUpdate", "text": "hmm"});
    dispatch_event(&mut mgr, "p", "s1", "thinkingUpdate", &data);
    let s = mgr.get_session("p").unwrap();
    assert_eq!(s.thinkings.len(), 1);
    assert_eq!(s.thinkings[0].text, "hmm");
}

#[test]
fn dispatch_permission_request() {
    let mut mgr = AcpSessionManager::new();
    let data = json!({
        "type": "permissionRequest",
        "requestId": "r1",
        "toolName": "bash",
        "argumentsJson": "{\"cmd\":\"rm\"}",
        "description": "dangerous op"
    });
    dispatch_event(&mut mgr, "p", "s1", "permissionRequest", &data);
    let s = mgr.get_session("p").unwrap();
    assert_eq!(s.pending_permissions.len(), 1);
    assert_eq!(s.pending_permissions[0].id, "r1");
    assert_eq!(
        s.pending_permissions[0].description.as_deref(),
        Some("dangerous op")
    );
}

#[test]
fn dispatch_session_state() {
    let mut mgr = AcpSessionManager::new();
    mgr.add_content_chunk("p", "test", "assistant");
    let data = json!({"type": "sessionState", "state": "idle"});
    dispatch_event(&mut mgr, "p", "s1", "sessionState", &data);
    let s = mgr.get_session("p").unwrap();
    assert_eq!(s.state, AcpState::Idle);
    assert!(s.messages[0].complete);
}

#[test]
fn dispatch_log_only_error_and_warn() {
    let mut mgr = AcpSessionManager::new();
    let warn = json!({"type": "log", "level": "warn", "message": "w"});
    let error = json!({"type": "log", "level": "error", "message": "e"});
    let info = json!({"type": "log", "level": "info", "message": "i"});
    dispatch_event(&mut mgr, "p", "s1", "log", &warn);
    dispatch_event(&mut mgr, "p", "s1", "log", &error);
    dispatch_event(&mut mgr, "p", "s1", "log", &info);
    let s = mgr.get_session("p").unwrap();
    assert_eq!(s.logs.len(), 2);
}

#[test]
fn dispatch_unknown_event_does_not_panic() {
    let mut mgr = AcpSessionManager::new();
    let data = json!({"type": "unknown"});
    dispatch_event(&mut mgr, "p", "s1", "unknown", &data);
}

// --- Snapshot ---

#[test]
fn snapshot_restores_full_session() {
    let mut mgr = AcpSessionManager::new();
    mgr.add_content_chunk("p", "stale", "assistant");

    let snapshot = json!({
        "state": "processing",
        "plan": [{"title": "Plan A", "status": "done"}],
        "toolCalls": [
            {
                "toolCallId": "tc1",
                "toolName": "read",
                "status": "completed",
                "argumentsJson": "{}",
                "success": true,
                "resultText": "file content"
            },
            {
                "toolCallId": "tc2",
                "toolName": "bash",
                "status": "running"
            }
        ],
        "messages": [
            {"text": "hello", "role": "user"},
            {"text": "hi there", "role": "assistant"}
        ],
        "pendingPermissions": [
            {
                "requestId": "perm1",
                "toolName": "bash",
                "argumentsJson": "{}",
                "description": "run cmd"
            }
        ]
    });

    dispatch_snapshot(&mut mgr, "p", "s1", &snapshot);

    let s = mgr.get_session("p").unwrap();
    assert_eq!(s.state, AcpState::Processing);
    assert_eq!(s.plan.len(), 1);
    assert_eq!(s.plan[0].title, "Plan A");
    assert_eq!(s.tool_calls.len(), 2);
    assert_eq!(s.tool_calls["tc1"].status, "completed");
    assert_eq!(s.tool_calls["tc1"].success, Some(true));
    assert_eq!(
        s.tool_calls["tc1"].result_text.as_deref(),
        Some("file content")
    );
    assert_eq!(s.tool_calls["tc2"].status, "running");
    assert!(s.tool_calls["tc2"].success.is_none());
    assert_eq!(s.messages.len(), 2);
    assert_eq!(s.messages[0].role, "user");
    assert!(s.messages[0].complete);
    assert_eq!(s.pending_permissions.len(), 1);
    assert_eq!(s.pending_permissions[0].id, "perm1");
}

#[test]
fn snapshot_clears_previous_data() {
    let mut mgr = AcpSessionManager::new();
    mgr.add_content_chunk("p", "old", "assistant");
    mgr.add_log("p", "error", "old error");

    let snapshot = json!({"state": "idle"});
    dispatch_snapshot(&mut mgr, "p", "s1", &snapshot);

    let s = mgr.get_session("p").unwrap();
    assert!(s.logs.is_empty());
    assert!(s.messages.is_empty());
}

#[test]
fn snapshot_with_empty_fields() {
    let mut mgr = AcpSessionManager::new();
    let snapshot = json!({});
    dispatch_snapshot(&mut mgr, "p", "s1", &snapshot);
    assert!(mgr.get_session("p").is_none());
}

#[test]
fn snapshot_tool_call_without_success_skips_result() {
    let mut mgr = AcpSessionManager::new();
    let snapshot = json!({
        "toolCalls": [{
            "toolCallId": "tc1",
            "toolName": "bash",
            "status": "running"
        }]
    });
    dispatch_snapshot(&mut mgr, "p", "s1", &snapshot);
    let tc = &mgr.get_session("p").unwrap().tool_calls["tc1"];
    assert_eq!(tc.status, "running");
    assert!(tc.success.is_none());
}
