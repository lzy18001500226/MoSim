use agentsmesh_events::event_types::EventType;
use agentsmesh_events::types::RealtimeEvent;
use agentsmesh_types::proto_pod_v1::Pod;
use agentsmesh_types::proto_runner_api_v1::Runner;
use agentsmesh_types::proto_ticket_v1::Ticket;

use crate::app_state::AppState;
use crate::autopilot_state::{AutopilotController, AutopilotIteration};
use crate::channel_types::ChannelMessage;
use crate::loop_state::{LoopRunData, loop_run_status};

pub fn dispatch(state: &mut AppState, event: &RealtimeEvent) {
    match event.event_type {
        EventType::PodCreated | EventType::PodRestarting => {
            if let Ok(pod) = serde_json::from_value::<Pod>(event.data.clone()) {
                state.pods.upsert_pod(pod, Some(event.timestamp));
            }
        }
        EventType::PodStatusChanged => {
            if let Some(key) = event.data.get("pod_key").and_then(|v| v.as_str()) {
                let status = event.data.get("status").and_then(|v| v.as_str()).unwrap_or("");
                let agent = event.data.get("agent_status").and_then(|v| v.as_str());
                let code = event.data.get("error_code").and_then(|v| v.as_str());
                let msg = event.data.get("error_message").and_then(|v| v.as_str());
                state.pods.update_pod_status(key, status, agent, code, msg, Some(event.timestamp));
            }
        }
        EventType::PodAgentStatusChanged => {
            if let Some(key) = event.data.get("pod_key").and_then(|v| v.as_str()) {
                let status = event.data.get("status").and_then(|v| v.as_str()).unwrap_or("");
                let agent = event.data.get("agent_status").and_then(|v| v.as_str());
                state.pods.update_pod_status(key, status, agent, None, None, Some(event.timestamp));
            }
        }
        EventType::PodTerminated => {
            if let Some(key) = event.data.get("pod_key").and_then(|v| v.as_str()) {
                state.pods.update_pod_status(key, "terminated", None, None, None, Some(event.timestamp));
            }
        }
        EventType::PodTitleChanged => {
            if let Some(key) = event.data.get("pod_key").and_then(|v| v.as_str()) {
                if let Some(title) = event.data.get("title").and_then(|v| v.as_str()) {
                    state.pods.update_pod_title(key, title, Some(event.timestamp));
                }
            }
        }
        EventType::PodAliasChanged => {
            if let Some(key) = event.data.get("pod_key").and_then(|v| v.as_str()) {
                if let Some(alias) = event.data.get("alias").and_then(|v| v.as_str()) {
                    state.pods.update_pod_alias(key, alias);
                }
            }
        }
        EventType::PodInitProgress => {
            if let Some(key) = event.data.get("pod_key").and_then(|v| v.as_str()) {
                let phase = event.data.get("phase").and_then(|v| v.as_str()).unwrap_or("");
                let progress = event.data.get("progress").and_then(|v| v.as_f64()).unwrap_or(0.0);
                let message = event.data.get("message").and_then(|v| v.as_str());
                state.pods.update_init_progress(key, phase, progress, message);
            }
        }
        EventType::ChannelMessage => {
            if let Ok(msg) = serde_json::from_value::<ChannelMessage>(event.data.clone()) {
                state.channels.on_new_message(msg);
            }
        }
        EventType::ChannelMessageEdited => {
            if let Ok(msg) = serde_json::from_value::<ChannelMessage>(event.data.clone()) {
                state.channels.update_message(msg.channel_id, msg);
            }
        }
        EventType::ChannelMessageDeleted => {
            let ch = event.data.get("channel_id").and_then(|v| v.as_i64());
            let id = event.data.get("id").and_then(|v| v.as_i64());
            if let (Some(ch), Some(id)) = (ch, id) {
                state.channels.remove_message(ch, id);
            }
        }
        EventType::TicketCreated => {
            if let Ok(t) = serde_json::from_value::<Ticket>(event.data.clone()) {
                state.tickets.add_ticket(t);
            }
        }
        EventType::TicketUpdated | EventType::TicketStatusChanged | EventType::TicketMoved => {
            if let Ok(t) = serde_json::from_value::<Ticket>(event.data.clone()) {
                state.tickets.update_ticket(&t.slug.clone(), t);
            }
        }
        EventType::TicketDeleted => {
            if let Some(slug) = event.data.get("slug").and_then(|v| v.as_str()) {
                state.tickets.remove_ticket(slug);
            }
        }
        EventType::RunnerOnline => {
            if let Some(id) = event.data.get("id").and_then(|v| v.as_i64()) {
                state.runners.update_runner_status(id, "online");
            }
        }
        EventType::RunnerOffline => {
            if let Some(id) = event.data.get("id").and_then(|v| v.as_i64()) {
                state.runners.update_runner_status(id, "offline");
            }
        }
        EventType::RunnerUpdated => {
            if let Ok(r) = serde_json::from_value::<Runner>(event.data.clone()) {
                let status = r.status.clone();
                state.runners.update_runner_status(r.id, &status);
            }
        }
        EventType::LoopRunStarted => {
            if let Ok(run) = serde_json::from_value::<LoopRunData>(event.data.clone()) {
                state.loops.add_run(run);
            }
        }
        EventType::LoopRunCompleted => {
            if let Some(id) = event.data.get("id").and_then(|v| v.as_i64()) {
                state.loops.update_run_status(id, loop_run_status::COMPLETED);
            }
        }
        EventType::LoopRunFailed | EventType::LoopRunWarning => {
            if let Some(id) = event.data.get("id").and_then(|v| v.as_i64()) {
                state.loops.update_run_status(id, loop_run_status::FAILED);
            }
        }
        EventType::AutopilotStatusChanged => {
            if let Some(key) = event.data.get("autopilot_controller_key").and_then(|v| v.as_str()) {
                let ctrls: Vec<AutopilotController> = serde_json::from_value(
                    serde_json::Value::Array(
                        state.autopilot.controllers().iter()
                            .map(|c| serde_json::to_value(c).unwrap_or_default())
                            .collect()
                    )
                ).unwrap_or_default();
                if let Some(mut c) = ctrls.into_iter().find(|c| c.autopilot_controller_key == key) {
                    if let Some(phase) = event.data.get("phase").and_then(|v| v.as_str()) {
                        c.phase = Some(phase.to_string());
                    }
                    if let Some(cur) = event.data.get("current_iteration").and_then(|v| v.as_i64()) {
                        c.current_iteration = Some(cur);
                    }
                    if let Some(max) = event.data.get("max_iterations").and_then(|v| v.as_i64()) {
                        c.max_iterations = Some(max);
                    }
                    state.autopilot.update_controller(key, c);
                }
            }
        }
        EventType::AutopilotIteration => {
            if let Some(key) = event.data.get("autopilot_controller_key").and_then(|v| v.as_str()) {
                if let Ok(iter) = serde_json::from_value::<AutopilotIteration>(event.data.clone()) {
                    state.autopilot.add_iteration(key.to_string(), iter);
                }
            }
        }
        EventType::AutopilotCreated => {
            if let Ok(c) = serde_json::from_value::<AutopilotController>(event.data.clone()) {
                state.autopilot.add_controller(c);
            }
        }
        EventType::AutopilotTerminated => {
            if let Some(key) = event.data.get("autopilot_controller_key").and_then(|v| v.as_str()) {
                state.autopilot.remove_controller(key);
            }
        }
        EventType::AutopilotThinking => {
            if let Some(key) = event.data.get("autopilot_controller_key").and_then(|v| v.as_str()) {
                state.autopilot.update_thinking(key.to_string(), event.data.clone());
            }
        }
        _ => {}
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn make_event(event_type: EventType, data: serde_json::Value) -> RealtimeEvent {
        RealtimeEvent {
            event_type, category: None, organization_id: 1,
            target_user_id: None, target_user_ids: None,
            entity_type: None, entity_id: None, data, timestamp: 1000,
        }
    }

    #[test]
    fn pod_created() {
        let mut s = AppState::new();
        let e = make_event(EventType::PodCreated, json!({"pod_key":"p1","status":"running","agent_slug":"claude"}));
        dispatch(&mut s, &e);
        assert_eq!(s.pods.pods().len(), 1);
        assert_eq!(s.pods.get_pod("p1").unwrap().status, "running");
    }

    #[test]
    fn pod_terminated() {
        let mut s = AppState::new();
        s.pods.upsert_pod(Pod {
            pod_key: "p1".into(), status: "running".into(),
            agent_slug: "claude".into(), ..Default::default()
        }, Some(100));
        dispatch(&mut s, &make_event(EventType::PodTerminated, json!({"pod_key":"p1"})));
        assert_eq!(s.pods.get_pod("p1").unwrap().status, "terminated");
    }

    #[test]
    fn channel_message() {
        let mut s = AppState::new();
        dispatch(&mut s, &make_event(EventType::ChannelMessage, json!({"id":1,"channel_id":10,"content":"hi"})));
        assert_eq!(s.channels.get_messages(10).unwrap().messages.len(), 1);
    }

    #[test]
    fn ticket_created() {
        let mut s = AppState::new();
        dispatch(&mut s, &make_event(EventType::TicketCreated, json!({"slug":"T-1","title":"Fix","status":"todo","priority":"high"})));
        assert_eq!(s.tickets.get_tickets().len(), 1);
    }

    #[test]
    fn runner_online() {
        let mut s = AppState::new();
        s.runners.set_runners(vec![Runner {
            id: 1, node_id: "r1".into(), status: "offline".into(),
            max_concurrent_pods: 4, current_pods: 0,
            is_enabled: true, ..Default::default()
        }]);
        dispatch(&mut s, &make_event(EventType::RunnerOnline, json!({"id":1})));
        assert_eq!(s.runners.get_runner(1).unwrap().status, "online");
    }

    #[test]
    fn loop_run_started() {
        let mut s = AppState::new();
        dispatch(&mut s, &make_event(EventType::LoopRunStarted, json!({"id":1,"loop_slug":"l-1","status":"running"})));
        assert_eq!(s.loops.get_runs().len(), 1);
    }

    #[test]
    fn unknown_event_noop() {
        let mut s = AppState::new();
        dispatch(&mut s, &make_event(EventType::Ping, json!({})));
        assert!(s.pods.pods().is_empty());
    }
}
