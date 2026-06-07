//! Tests for OpenCode SSE event parsing against real captured events.

use spacebot::opencode::types::*;

/// Parse a raw SSE data line into an SseEvent.
fn parse_sse_line(line: &str) -> SseEvent {
    let json_str = line
        .strip_prefix("data: ")
        .expect("expected 'data: ' prefix");
    let envelope: SseEventEnvelope = serde_json::from_str(json_str)
        .unwrap_or_else(|e| panic!("failed to parse envelope: {e}\njson: {json_str}"));
    SseEvent::from_envelope(envelope)
}

#[test]
fn parse_server_connected() {
    let event = parse_sse_line(r#"data: {"type":"server.connected","properties":{}}"#);
    assert!(matches!(event, SseEvent::Unknown(ref s) if s == "server.connected"));
}

#[test]
fn parse_message_updated_user() {
    let event = parse_sse_line(
        r#"data: {"type":"message.updated","properties":{"info":{"id":"msg_123","sessionID":"ses_456","role":"user","time":{"created":1770927523031},"agent":"build","model":{"providerID":"openrouter","modelID":"google/gemini-3-pro-preview"}}}}"#,
    );
    match event {
        SseEvent::MessageUpdated { info } => {
            let info = info.expect("expected info");
            assert_eq!(info.role, "user");
            assert_eq!(info.session_id.as_deref(), Some("ses_456"));
        }
        other => panic!("expected MessageUpdated, got {other:?}"),
    }
}

#[test]
fn parse_message_updated_assistant() {
    let event = parse_sse_line(
        r#"data: {"type":"message.updated","properties":{"info":{"id":"msg_789","sessionID":"ses_456","role":"assistant","time":{"created":1770927523033},"parentID":"msg_123","modelID":"google/gemini-3-pro-preview","providerID":"openrouter","mode":"build","agent":"build","path":{"cwd":"/tmp","root":"/"},"cost":0,"tokens":{"input":0,"output":0,"reasoning":0,"cache":{"read":0,"write":0}}}}}"#,
    );
    match event {
        SseEvent::MessageUpdated { info } => {
            let info = info.expect("expected info");
            assert_eq!(info.role, "assistant");
        }
        other => panic!("expected MessageUpdated, got {other:?}"),
    }
}

#[test]
fn parse_text_part() {
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_abc","sessionID":"ses_456","messageID":"msg_789","type":"text","text":"Hello world","time":{"start":1770927529701}},"delta":"Hello world"}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, delta } => {
            assert_eq!(delta.as_deref(), Some("Hello world"));
            match part {
                Part::Text {
                    text, session_id, ..
                } => {
                    assert_eq!(text, "Hello world");
                    assert_eq!(session_id.as_deref(), Some("ses_456"));
                }
                other => panic!("expected Part::Text, got {other:?}"),
            }
        }
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}

#[test]
fn parse_tool_pending() {
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_tool1","sessionID":"ses_456","messageID":"msg_789","type":"tool","callID":"tool_bash_abc","tool":"bash","state":{"status":"pending","input":{},"raw":""}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => match part {
            Part::Tool {
                tool,
                state,
                session_id,
                ..
            } => {
                assert_eq!(tool.as_deref(), Some("bash"));
                assert_eq!(session_id.as_deref(), Some("ses_456"));
                let state = state.expect("expected state");
                assert!(matches!(state, ToolState::Pending { .. }));
            }
            other => panic!("expected Part::Tool, got {other:?}"),
        },
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}

#[test]
fn parse_tool_running() {
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_tool1","sessionID":"ses_456","messageID":"msg_789","type":"tool","callID":"tool_bash_abc","tool":"bash","state":{"status":"running","input":{"command":"ls -F","description":"List files"},"time":{"start":1770927526652}}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => match part {
            Part::Tool { tool, state, .. } => {
                assert_eq!(tool.as_deref(), Some("bash"));
                let state = state.expect("expected state");
                match state {
                    ToolState::Running { input, .. } => {
                        assert!(input.is_some());
                    }
                    other => panic!("expected ToolState::Running, got {other:?}"),
                }
            }
            other => panic!("expected Part::Tool, got {other:?}"),
        },
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}

#[test]
fn parse_tool_completed() {
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_tool1","sessionID":"ses_456","messageID":"msg_789","type":"tool","callID":"tool_bash_abc","tool":"bash","state":{"status":"completed","input":{"command":"ls -F","description":"List files"},"output":"file1\nfile2\n","title":"List files","metadata":{"exit":0},"time":{"start":1770927526652,"end":1770927526660}}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => match part {
            Part::Tool { tool, state, .. } => {
                assert_eq!(tool.as_deref(), Some("bash"));
                let state = state.expect("expected state");
                match state {
                    ToolState::Completed { output, title, .. } => {
                        assert_eq!(output.as_deref(), Some("file1\nfile2\n"));
                        assert_eq!(title.as_deref(), Some("List files"));
                    }
                    other => panic!("expected ToolState::Completed, got {other:?}"),
                }
            }
            other => panic!("expected Part::Tool, got {other:?}"),
        },
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}

#[test]
fn parse_tool_error() {
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_tool1","sessionID":"ses_456","messageID":"msg_789","type":"tool","callID":"tool_bash_abc","tool":"bash","state":{"status":"error","input":{"command":"bad_cmd"},"error":"command not found","time":{"start":100,"end":200}}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => match part {
            Part::Tool { state, .. } => {
                let state = state.expect("expected state");
                match state {
                    ToolState::Error { error, .. } => {
                        assert_eq!(error.as_deref(), Some("command not found"));
                    }
                    other => panic!("expected ToolState::Error, got {other:?}"),
                }
            }
            other => panic!("expected Part::Tool, got {other:?}"),
        },
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}

#[test]
fn parse_session_status_busy() {
    let event = parse_sse_line(
        r#"data: {"type":"session.status","properties":{"sessionID":"ses_456","status":{"type":"busy"}}}"#,
    );
    match event {
        SseEvent::SessionStatus { session_id, status } => {
            assert_eq!(session_id, "ses_456");
            assert!(matches!(status, SessionStatusPayload::Busy));
        }
        other => panic!("expected SessionStatus, got {other:?}"),
    }
}

#[test]
fn parse_session_status_idle() {
    let event = parse_sse_line(
        r#"data: {"type":"session.status","properties":{"sessionID":"ses_456","status":{"type":"idle"}}}"#,
    );
    match event {
        SseEvent::SessionStatus { session_id, status } => {
            assert_eq!(session_id, "ses_456");
            assert!(matches!(status, SessionStatusPayload::Idle));
        }
        other => panic!("expected SessionStatus, got {other:?}"),
    }
}

#[test]
fn parse_session_idle() {
    let event =
        parse_sse_line(r#"data: {"type":"session.idle","properties":{"sessionID":"ses_456"}}"#);
    match event {
        SseEvent::SessionIdle { session_id } => {
            assert_eq!(session_id, "ses_456");
        }
        other => panic!("expected SessionIdle, got {other:?}"),
    }
}

#[test]
fn parse_session_error() {
    let event = parse_sse_line(
        r#"data: {"type":"session.error","properties":{"sessionID":"ses_456","error":{"message":"something broke"}}}"#,
    );
    match event {
        SseEvent::SessionError { session_id, error } => {
            assert_eq!(session_id.as_deref(), Some("ses_456"));
            let msg = error
                .unwrap()
                .get("message")
                .unwrap()
                .as_str()
                .unwrap()
                .to_string();
            assert_eq!(msg, "something broke");
        }
        other => panic!("expected SessionError, got {other:?}"),
    }
}

#[test]
fn parse_step_start() {
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_step","sessionID":"ses_456","messageID":"msg_789","type":"step-start"}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => {
            assert!(matches!(part, Part::StepStart { .. }));
        }
        other => panic!("expected MessagePartUpdated with StepStart, got {other:?}"),
    }
}

#[test]
fn parse_step_finish() {
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_step","sessionID":"ses_456","messageID":"msg_789","type":"step-finish","reason":"tool-calls","cost":0.003,"tokens":{"total":12474,"input":113,"output":143,"reasoning":116,"cache":{"read":12218,"write":0}}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => match part {
            Part::StepFinish { reason, .. } => {
                assert_eq!(reason.as_deref(), Some("tool-calls"));
            }
            other => panic!("expected Part::StepFinish, got {other:?}"),
        },
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}

#[test]
fn parse_reasoning_part_as_other() {
    // Reasoning parts should parse as Part::Other (we don't model them)
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_reason","sessionID":"ses_456","messageID":"msg_789","type":"reasoning","text":"thinking...","metadata":{},"time":{"start":1234}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => {
            assert!(matches!(part, Part::Other));
        }
        other => panic!("expected MessagePartUpdated with Other, got {other:?}"),
    }
}

#[test]
fn parse_unknown_event_type() {
    let event = parse_sse_line(
        r#"data: {"type":"session.updated","properties":{"info":{"id":"ses_456"}}}"#,
    );
    assert!(matches!(event, SseEvent::Unknown(ref s) if s == "session.updated"));
}

#[test]
fn parse_real_tool_running_with_metadata() {
    // Real captured event from OpenCode with nested metadata
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_c538192fb001Smcd2MxgeTNrsm","sessionID":"ses_3ac7e9e73ffe8gBgAoQgY2H3Ox","messageID":"msg_c538184d9001PScCJV37rRtvWQ","type":"tool","callID":"tool_bash_5JX7ByegJUebrvJmqyLO","tool":"bash","state":{"status":"running","input":{"command":"ls -F","description":"List files in the current directory"},"time":{"start":1770927526652}},"metadata":{"openrouter":{"reasoning_details":[]}}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => match part {
            Part::Tool { tool, state, .. } => {
                assert_eq!(tool.as_deref(), Some("bash"));
                let state = state.expect("expected state");
                assert!(state.is_running());
            }
            other => panic!("expected Part::Tool, got {other:?}"),
        },
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}

#[test]
fn parse_tool_with_part_level_metadata() {
    // Real event: Part::Tool has a `metadata` field at the part level (sibling of `state`)
    let event = parse_sse_line(
        r#"data: {"type":"message.part.updated","properties":{"part":{"id":"prt_x","sessionID":"ses_y","messageID":"msg_z","type":"tool","callID":"call_1","tool":"bash","state":{"status":"running","input":{"command":"ls -F","description":"List files"},"time":{"start":1770927526652}},"metadata":{"openrouter":{"reasoning_details":[{"type":"reasoning.text","text":"thinking...","format":"google-gemini-v1","index":0}]}}}}}"#,
    );
    match event {
        SseEvent::MessagePartUpdated { part, .. } => match part {
            Part::Tool { tool, state, .. } => {
                assert_eq!(tool.as_deref(), Some("bash"));
                let state = state.expect("expected state");
                assert!(state.is_running());
            }
            other => panic!("expected Part::Tool, got {other:?}"),
        },
        other => panic!("expected MessagePartUpdated, got {other:?}"),
    }
}
