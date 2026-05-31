use crate::{EventType, EventCategory, ConnectionState, RealtimeEvent, PingMessage};

#[test]
fn test_all_event_types_serialize() {
    let cases: Vec<(EventType, &str)> = vec![
        (EventType::PodCreated, "\"pod:created\""),
        (EventType::PodStatusChanged, "\"pod:status_changed\""),
        (EventType::PodAgentStatusChanged, "\"pod:agent_status_changed\""),
        (EventType::PodTerminated, "\"pod:terminated\""),
        (EventType::PodTitleChanged, "\"pod:title_changed\""),
        (EventType::PodAliasChanged, "\"pod:alias_changed\""),
        (EventType::PodInitProgress, "\"pod:init_progress\""),
        (EventType::PodRestarting, "\"pod:restarting\""),
        (EventType::ChannelMessage, "\"channel:message\""),
        (EventType::ChannelMessageEdited, "\"channel:message_edited\""),
        (EventType::ChannelMessageDeleted, "\"channel:message_deleted\""),
        (EventType::TicketCreated, "\"ticket:created\""),
        (EventType::TicketUpdated, "\"ticket:updated\""),
        (EventType::TicketStatusChanged, "\"ticket:status_changed\""),
        (EventType::TicketMoved, "\"ticket:moved\""),
        (EventType::TicketDeleted, "\"ticket:deleted\""),
        (EventType::RunnerOnline, "\"runner:online\""),
        (EventType::RunnerOffline, "\"runner:offline\""),
        (EventType::RunnerUpdated, "\"runner:updated\""),
        (EventType::AutopilotStatusChanged, "\"autopilot:status_changed\""),
        (EventType::AutopilotIteration, "\"autopilot:iteration\""),
        (EventType::AutopilotCreated, "\"autopilot:created\""),
        (EventType::AutopilotTerminated, "\"autopilot:terminated\""),
        (EventType::AutopilotThinking, "\"autopilot:thinking\""),
        (EventType::MrCreated, "\"mr:created\""),
        (EventType::MrUpdated, "\"mr:updated\""),
        (EventType::MrMerged, "\"mr:merged\""),
        (EventType::MrClosed, "\"mr:closed\""),
        (EventType::PipelineUpdated, "\"pipeline:updated\""),
        (EventType::LoopRunStarted, "\"loop_run:started\""),
        (EventType::LoopRunCompleted, "\"loop_run:completed\""),
        (EventType::LoopRunFailed, "\"loop_run:failed\""),
        (EventType::LoopRunWarning, "\"loop_run:warning\""),
        (EventType::Notification, "\"notification\""),
        (EventType::SystemMaintenance, "\"system:maintenance\""),
        (EventType::Connected, "\"connected\""),
        (EventType::Ping, "\"ping\""),
        (EventType::Pong, "\"pong\""),
    ];

    for (event_type, expected_json) in &cases {
        let json = serde_json::to_string(event_type).unwrap();
        assert_eq!(&json, expected_json, "serialize {:?}", event_type);
    }
}

#[test]
fn test_all_event_types_deserialize() {
    let strings = [
        "pod:created", "pod:status_changed", "pod:agent_status_changed",
        "pod:terminated", "pod:title_changed", "pod:alias_changed",
        "pod:init_progress", "pod:restarting",
        "channel:message", "channel:message_edited", "channel:message_deleted",
        "ticket:created", "ticket:updated", "ticket:status_changed",
        "ticket:moved", "ticket:deleted",
        "runner:online", "runner:offline", "runner:updated",
        "autopilot:status_changed", "autopilot:iteration",
        "autopilot:created", "autopilot:terminated", "autopilot:thinking",
        "mr:created", "mr:updated", "mr:merged", "mr:closed",
        "pipeline:updated",
        "loop_run:started", "loop_run:completed", "loop_run:failed", "loop_run:warning",
        "notification", "system:maintenance",
        "connected", "ping", "pong",
    ];

    for s in &strings {
        let json = format!("\"{}\"", s);
        let result: Result<EventType, _> = serde_json::from_str(&json);
        assert!(result.is_ok(), "failed to deserialize: {}", s);
    }
}

#[test]
fn test_event_type_roundtrip() {
    let event = EventType::AutopilotThinking;
    let json = serde_json::to_string(&event).unwrap();
    let back: EventType = serde_json::from_str(&json).unwrap();
    assert_eq!(event, back);
}

#[test]
fn test_event_type_as_str() {
    assert_eq!(EventType::PodCreated.as_str(), "pod:created");
    assert_eq!(EventType::Notification.as_str(), "notification");
    assert_eq!(EventType::LoopRunWarning.as_str(), "loop_run:warning");
}

#[test]
fn test_event_type_display() {
    assert_eq!(format!("{}", EventType::MrMerged), "mr:merged");
    assert_eq!(format!("{}", EventType::Ping), "ping");
}

#[test]
fn test_event_type_hash_eq() {
    use std::collections::HashSet;
    let mut set = HashSet::new();
    set.insert(EventType::PodCreated);
    set.insert(EventType::PodCreated);
    assert_eq!(set.len(), 1);
    set.insert(EventType::PodTerminated);
    assert_eq!(set.len(), 2);
}

#[test]
fn test_connection_state_serde() {
    let states = [
        (ConnectionState::Disconnected, "\"disconnected\""),
        (ConnectionState::Connecting, "\"connecting\""),
        (ConnectionState::Connected, "\"connected\""),
        (ConnectionState::Reconnecting, "\"reconnecting\""),
    ];
    for (state, expected) in &states {
        let json = serde_json::to_string(state).unwrap();
        assert_eq!(&json, expected);
        let back: ConnectionState = serde_json::from_str(expected).unwrap();
        assert_eq!(state, &back);
    }
}

#[test]
fn test_event_category_serde() {
    let cats = [
        (EventCategory::Entity, "\"entity\""),
        (EventCategory::Notification, "\"notification\""),
        (EventCategory::System, "\"system\""),
    ];
    for (cat, expected) in &cats {
        let json = serde_json::to_string(cat).unwrap();
        assert_eq!(&json, expected);
        let back: EventCategory = serde_json::from_str(expected).unwrap();
        assert_eq!(cat, &back);
    }
}

#[test]
fn test_realtime_event_full_json_roundtrip() {
    let json = r#"{
        "type": "pod:status_changed",
        "category": "entity",
        "organization_id": 42,
        "target_user_id": 7,
        "target_user_ids": [7, 8, 9],
        "entity_type": "pod",
        "entity_id": "pod-abc",
        "data": {"pod_key": "abc", "status": "running"},
        "timestamp": 1712345678000
    }"#;

    let event: RealtimeEvent = serde_json::from_str(json).unwrap();
    assert_eq!(event.event_type, EventType::PodStatusChanged);
    assert_eq!(event.category, Some(EventCategory::Entity));
    assert_eq!(event.organization_id, 42);
    assert_eq!(event.target_user_id, Some(7));
    assert_eq!(event.target_user_ids, Some(vec![7, 8, 9]));
    assert_eq!(event.entity_type.as_deref(), Some("pod"));
    assert_eq!(event.entity_id.as_deref(), Some("pod-abc"));
    assert_eq!(event.data["pod_key"], "abc");
    assert_eq!(event.timestamp, 1712345678000);

    let re_json = serde_json::to_string(&event).unwrap();
    let re_event: RealtimeEvent = serde_json::from_str(&re_json).unwrap();
    assert_eq!(re_event.event_type, event.event_type);
    assert_eq!(re_event.organization_id, event.organization_id);
}

#[test]
fn test_realtime_event_minimal_json() {
    let json = r#"{"type": "ping"}"#;
    let event: RealtimeEvent = serde_json::from_str(json).unwrap();
    assert_eq!(event.event_type, EventType::Ping);
    assert_eq!(event.category, None);
    assert_eq!(event.organization_id, 0);
    assert_eq!(event.target_user_id, None);
    assert!(event.data.is_null());
}

#[test]
fn test_ping_message_serialize() {
    let ping = PingMessage::new(1712345678000);
    let json = serde_json::to_string(&ping).unwrap();
    assert!(json.contains("\"type\":\"ping\""));
    assert!(json.contains("\"timestamp\":1712345678000"));
}

#[test]
fn test_invalid_event_type_deserialize() {
    let json = r#""invalid:event""#;
    let result: Result<EventType, _> = serde_json::from_str(json);
    assert!(result.is_err());
}
