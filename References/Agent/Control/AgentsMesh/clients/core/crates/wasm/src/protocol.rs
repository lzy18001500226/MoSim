use agentsmesh_protocol::{decode_message, encode_message, encode_resize, MsgType};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn relay_encode_input(data: &[u8]) -> Vec<u8> {
    encode_message(MsgType::Input, data)
}

#[wasm_bindgen]
pub fn relay_encode_resize(cols: u16, rows: u16) -> Vec<u8> {
    encode_resize(cols, rows)
}

#[wasm_bindgen]
pub fn relay_encode_ping() -> Vec<u8> {
    encode_message(MsgType::Ping, &[])
}

#[wasm_bindgen]
pub fn relay_encode_control(data: &[u8]) -> Vec<u8> {
    encode_message(MsgType::Control, data)
}

#[wasm_bindgen]
pub fn relay_encode_resync() -> Vec<u8> {
    encode_message(MsgType::Resync, &[])
}

#[wasm_bindgen]
pub fn relay_encode_acp_command(data: &[u8]) -> Vec<u8> {
    encode_message(MsgType::AcpCommand, data)
}

#[wasm_bindgen]
pub fn relay_decode_message(data: &[u8]) -> JsValue {
    match decode_message(data) {
        Ok((msg_type, payload)) => {
            let obj = js_sys::Object::new();
            let _ = js_sys::Reflect::set(
                &obj,
                &"type".into(),
                &(msg_type as u8).into(),
            );
            let _ = js_sys::Reflect::set(
                &obj,
                &"payload".into(),
                &js_sys::Uint8Array::from(payload).into(),
            );
            obj.into()
        }
        Err(_) => JsValue::NULL,
    }
}
