use thiserror::Error;

#[derive(Debug, Error)]
pub enum ProtocolError {
    #[error("empty message")]
    EmptyMessage,

    #[error("unknown message type: 0x{0:02x}")]
    UnknownMsgType(u8),

    #[error("invalid resize payload: expected 4 bytes, got {0}")]
    InvalidResizePayload(usize),

    #[error("json error: {0}")]
    Json(#[from] serde_json::Error),
}
