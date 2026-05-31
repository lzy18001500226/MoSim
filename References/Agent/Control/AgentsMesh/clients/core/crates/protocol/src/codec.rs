use serde::{de::DeserializeOwned, Serialize};

use crate::error::ProtocolError;
use crate::msg_type::MsgType;

pub fn encode_message(msg_type: MsgType, payload: &[u8]) -> Vec<u8> {
    let mut buf = Vec::with_capacity(1 + payload.len());
    buf.push(msg_type as u8);
    buf.extend_from_slice(payload);
    buf
}

pub fn decode_message(data: &[u8]) -> Result<(MsgType, &[u8]), ProtocolError> {
    if data.is_empty() {
        return Err(ProtocolError::EmptyMessage);
    }
    let msg_type =
        MsgType::from_u8(data[0]).ok_or(ProtocolError::UnknownMsgType(data[0]))?;
    Ok((msg_type, &data[1..]))
}

pub fn encode_resize(cols: u16, rows: u16) -> Vec<u8> {
    let mut buf = Vec::with_capacity(5);
    buf.push(MsgType::Resize as u8);
    buf.extend_from_slice(&cols.to_be_bytes());
    buf.extend_from_slice(&rows.to_be_bytes());
    buf
}

pub fn decode_resize(payload: &[u8]) -> Result<(u16, u16), ProtocolError> {
    if payload.len() != 4 {
        return Err(ProtocolError::InvalidResizePayload(payload.len()));
    }
    let cols = u16::from_be_bytes([payload[0], payload[1]]);
    let rows = u16::from_be_bytes([payload[2], payload[3]]);
    Ok((cols, rows))
}

pub fn encode_json_message<T: Serialize>(
    msg_type: MsgType,
    obj: &T,
) -> Result<Vec<u8>, ProtocolError> {
    let json = serde_json::to_vec(obj)?;
    Ok(encode_message(msg_type, &json))
}

pub fn decode_json_payload<T: DeserializeOwned>(
    payload: &[u8],
) -> Result<T, ProtocolError> {
    Ok(serde_json::from_slice(payload)?)
}
