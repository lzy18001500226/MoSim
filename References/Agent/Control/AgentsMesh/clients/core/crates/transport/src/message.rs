#[derive(Debug, Clone)]
pub enum WsMessage {
    Binary(Vec<u8>),
    Text(String),
    Close(Option<u16>),
}
