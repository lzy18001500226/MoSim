use agentsmesh_protocol::MsgType;
use serde::Deserialize;
use tracing::warn;

use crate::types::OutputCallback;

pub(crate) const ANSI_CLEAR: &[u8] = b"\x1b[2J\x1b[H\x1b[3J";

#[derive(Debug, PartialEq)]
pub enum DispatchAction {
    None,
    Snapshot(SnapshotPayload),
    PodResized { cols: u16, rows: u16 },
    RunnerDisconnected,
    RunnerReconnected,
    AcpMessage { msg_type: MsgType, payload: serde_json::Value },
}

#[derive(Debug, PartialEq)]
pub struct SnapshotPayload {
    pub content: Option<String>,
    pub cols: u16,
    pub rows: u16,
}

#[derive(Deserialize)]
struct SnapshotJson {
    serialized_content: Option<String>,
    #[serde(default)]
    cols: u16,
    #[serde(default)]
    rows: u16,
}

#[derive(Deserialize)]
struct ControlJson {
    #[serde(rename = "type")]
    msg_type: Option<String>,
    #[serde(default)]
    cols: u16,
    #[serde(default)]
    rows: u16,
}

pub fn dispatch_message(
    msg_type: MsgType,
    payload: &[u8],
    subscribers: &[&OutputCallback],
) -> DispatchAction {
    match msg_type {
        MsgType::Output => {
            broadcast(subscribers, payload);
            DispatchAction::None
        }
        MsgType::Snapshot => handle_snapshot(payload, subscribers),
        MsgType::Control => handle_control(payload),
        MsgType::RunnerDisconnected => {
            let msg = b"\r\n\x1b[33mRunner disconnected. Waiting for reconnection...\x1b[0m\r\n";
            broadcast(subscribers, msg);
            DispatchAction::RunnerDisconnected
        }
        MsgType::RunnerReconnected => {
            let msg = b"\r\n\x1b[32mRunner reconnected.\x1b[0m\r\n";
            broadcast(subscribers, msg);
            DispatchAction::RunnerReconnected
        }
        MsgType::AcpEvent | MsgType::AcpSnapshot | MsgType::AcpCommand => {
            match serde_json::from_slice::<serde_json::Value>(payload) {
                Ok(val) => DispatchAction::AcpMessage {
                    msg_type,
                    payload: val,
                },
                Err(e) => {
                    warn!("failed to parse ACP payload: {e}");
                    DispatchAction::None
                }
            }
        }
        MsgType::Pong | MsgType::Ping => DispatchAction::None,
        _ => {
            warn!("unhandled relay message type: {msg_type:?}");
            DispatchAction::None
        }
    }
}

fn handle_snapshot(payload: &[u8], subscribers: &[&OutputCallback]) -> DispatchAction {
    match serde_json::from_slice::<SnapshotJson>(payload) {
        Ok(snap) => {
            if let Some(content) = &snap.serialized_content {
                broadcast(subscribers, ANSI_CLEAR);
                broadcast(subscribers, content.as_bytes());
            }
            DispatchAction::Snapshot(SnapshotPayload {
                content: snap.serialized_content,
                cols: snap.cols,
                rows: snap.rows,
            })
        }
        Err(e) => {
            warn!("failed to parse snapshot: {e}");
            DispatchAction::None
        }
    }
}

fn handle_control(payload: &[u8]) -> DispatchAction {
    match serde_json::from_slice::<ControlJson>(payload) {
        Ok(ctrl) if ctrl.msg_type.as_deref() == Some("pod_resized") => {
            DispatchAction::PodResized {
                cols: ctrl.cols,
                rows: ctrl.rows,
            }
        }
        Ok(_) => DispatchAction::None,
        Err(e) => {
            warn!("failed to parse control message: {e}");
            DispatchAction::None
        }
    }
}

fn broadcast(subscribers: &[&OutputCallback], data: &[u8]) {
    let owned = data.to_vec();
    for cb in subscribers {
        cb(owned.clone());
    }
}
