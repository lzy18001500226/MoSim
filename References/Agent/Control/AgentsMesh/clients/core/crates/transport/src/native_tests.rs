use crate::{TransportError, WebSocketConnection};

#[tokio::test]
async fn connect_invalid_url_fails() {
    let result = WebSocketConnection::connect("not-a-valid-url").await;
    match result {
        Err(TransportError::ConnectionFailed(_)) => {}
        Err(e) => panic!("expected ConnectionFailed, got: {e}"),
        Ok(_) => panic!("expected error, got Ok"),
    }
}

#[tokio::test]
async fn connect_refused_port_fails() {
    let result = WebSocketConnection::connect("ws://127.0.0.1:1").await;
    match result {
        Err(TransportError::ConnectionFailed(_)) => {}
        Err(e) => panic!("expected ConnectionFailed, got: {e}"),
        Ok(_) => panic!("expected error, got Ok"),
    }
}

#[tokio::test]
async fn connect_failure_message_contains_detail() {
    let result = WebSocketConnection::connect("ws://127.0.0.1:1").await;
    let msg = match result {
        Err(e) => e.to_string(),
        Ok(_) => panic!("expected error"),
    };
    assert!(msg.starts_with("connection failed:"));
    assert!(msg.len() > "connection failed: ".len());
}
