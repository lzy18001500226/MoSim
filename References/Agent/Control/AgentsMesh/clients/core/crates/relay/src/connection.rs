use agentsmesh_transport::runtime::Runtime;
use agentsmesh_transport::{WebSocketConnection, WsMessage as TransportMsg};
use futures::channel::mpsc;
use futures::stream::StreamExt;
use tracing::{debug, warn};

use crate::error::RelayError;

pub type WsMessage = Vec<u8>;

pub struct WsConnection<R: Runtime> {
    pub write_tx: mpsc::UnboundedSender<WsMessage>,
    #[allow(dead_code)]
    pub read_handle: R::TaskHandle,
    #[allow(dead_code)]
    pub write_handle: R::TaskHandle,
}

pub async fn connect<R: Runtime>(
    runtime: &R,
    relay_url: &str,
    token: &str,
    on_message: mpsc::UnboundedSender<(String, Vec<u8>)>,
    pod_key: String,
    on_close: mpsc::UnboundedSender<String>,
    on_error: mpsc::UnboundedSender<String>,
) -> Result<WsConnection<R>, RelayError> {
    let url = format!(
        "{}/browser/relay?token={}",
        relay_url,
        urlencoding::encode(token)
    );

    let conn = WebSocketConnection::connect(&url)
        .await
        .map_err(|e| RelayError::Connection(e.to_string()))?;

    let (sender, mut receiver) = conn.into_split();
    let (write_tx, mut write_rx) = mpsc::unbounded::<WsMessage>();

    let write_handle = runtime.spawn(Box::pin(async move {
        while let Some(data) = write_rx.next().await {
            if sender.send_binary(data).is_err() {
                break;
            }
        }
    }));

    let pk_read = pod_key.clone();
    let pk_err = pod_key.clone();
    let read_handle = runtime.spawn(Box::pin(async move {
        loop {
            match receiver.recv().await {
                Ok(TransportMsg::Binary(data)) => {
                    let _ = on_message.unbounded_send((pk_read.clone(), data));
                }
                Ok(TransportMsg::Close(_)) => {
                    debug!("relay ws closed for {pk_read}");
                    break;
                }
                Err(_) => {
                    warn!("relay ws error for {pk_read}");
                    let _ = on_error.unbounded_send(pk_err.clone());
                    break;
                }
                _ => {}
            }
        }
        let _ = on_close.unbounded_send(pk_read);
    }));

    Ok(WsConnection {
        write_tx,
        read_handle,
        write_handle,
    })
}
