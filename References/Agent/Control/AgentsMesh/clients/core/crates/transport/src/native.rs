use futures_util::{SinkExt, StreamExt};
use tokio::sync::mpsc;
use tokio_tungstenite::tungstenite::Message;
use tracing::{debug, warn};

use crate::error::TransportError;
use crate::message::WsMessage;

pub struct WebSocketConnection {
    write_tx: mpsc::UnboundedSender<Message>,
    read_rx: mpsc::UnboundedReceiver<WsMessage>,
}

#[derive(Clone)]
pub struct WsSender {
    write_tx: mpsc::UnboundedSender<Message>,
}

pub struct WsReceiver {
    read_rx: mpsc::UnboundedReceiver<WsMessage>,
}

impl WebSocketConnection {
    pub async fn connect(url: &str) -> Result<Self, TransportError> {
        let (ws_stream, _) = tokio_tungstenite::connect_async(url)
            .await
            .map_err(|e| TransportError::ConnectionFailed(e.to_string()))?;

        let (ws_write, ws_read) = ws_stream.split();
        let (write_tx, write_rx) = mpsc::unbounded_channel::<Message>();
        let (read_tx, read_rx) = mpsc::unbounded_channel::<WsMessage>();

        spawn_write_loop(ws_write, write_rx);
        spawn_read_loop(ws_read, read_tx);

        debug!("websocket connected to {url}");
        Ok(Self { write_tx, read_rx })
    }

    pub fn send_binary(&self, data: Vec<u8>) -> Result<(), TransportError> {
        self.write_tx
            .send(Message::Binary(data.into()))
            .map_err(|e| TransportError::SendFailed(e.to_string()))
    }

    pub fn send_text(&self, text: String) -> Result<(), TransportError> {
        self.write_tx
            .send(Message::Text(text.into()))
            .map_err(|e| TransportError::SendFailed(e.to_string()))
    }

    pub async fn recv(&mut self) -> Result<WsMessage, TransportError> {
        self.read_rx.recv().await.ok_or(TransportError::Closed)
    }

    pub fn close(&self) {
        let _ = self.write_tx.send(Message::Close(None));
    }

    pub fn is_closed(&self) -> bool {
        self.write_tx.is_closed()
    }

    pub fn into_split(self) -> (WsSender, WsReceiver) {
        (
            WsSender {
                write_tx: self.write_tx,
            },
            WsReceiver {
                read_rx: self.read_rx,
            },
        )
    }
}

impl WsSender {
    pub fn send_binary(&self, data: Vec<u8>) -> Result<(), TransportError> {
        self.write_tx
            .send(Message::Binary(data.into()))
            .map_err(|e| TransportError::SendFailed(e.to_string()))
    }

    pub fn send_text(&self, text: String) -> Result<(), TransportError> {
        self.write_tx
            .send(Message::Text(text.into()))
            .map_err(|e| TransportError::SendFailed(e.to_string()))
    }

    pub fn close(&self) {
        let _ = self.write_tx.send(Message::Close(None));
    }

    pub fn is_closed(&self) -> bool {
        self.write_tx.is_closed()
    }
}

impl WsReceiver {
    pub async fn recv(&mut self) -> Result<WsMessage, TransportError> {
        self.read_rx.recv().await.ok_or(TransportError::Closed)
    }
}

fn spawn_write_loop<S>(mut sink: S, mut rx: mpsc::UnboundedReceiver<Message>)
where
    S: futures_util::Sink<Message, Error = tokio_tungstenite::tungstenite::Error>
        + Unpin
        + Send
        + 'static,
{
    tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            if sink.send(msg).await.is_err() {
                debug!("websocket write loop ended");
                break;
            }
        }
    });
}

fn spawn_read_loop<S>(mut stream: S, tx: mpsc::UnboundedSender<WsMessage>)
where
    S: futures_util::Stream<Item = Result<Message, tokio_tungstenite::tungstenite::Error>>
        + Unpin
        + Send
        + 'static,
{
    tokio::spawn(async move {
        while let Some(result) = stream.next().await {
            match result {
                Ok(Message::Binary(data)) => {
                    if tx.send(WsMessage::Binary(data.into())).is_err() {
                        break;
                    }
                }
                Ok(Message::Text(text)) => {
                    if tx.send(WsMessage::Text(text.to_string())).is_err() {
                        break;
                    }
                }
                Ok(Message::Close(frame)) => {
                    let code = frame.as_ref().map(|f| f.code.into());
                    let _ = tx.send(WsMessage::Close(code));
                    break;
                }
                Ok(_) => {}
                Err(e) => {
                    warn!("websocket read error: {e}");
                    break;
                }
            }
        }
        debug!("websocket read loop ended");
    });
}
