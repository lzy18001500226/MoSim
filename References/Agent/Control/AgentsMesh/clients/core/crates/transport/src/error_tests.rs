use crate::TransportError;

#[test]
fn connection_failed_display() {
    let e = TransportError::ConnectionFailed("timeout".into());
    assert_eq!(e.to_string(), "connection failed: timeout");
}

#[test]
fn send_failed_display() {
    let e = TransportError::SendFailed("channel closed".into());
    assert_eq!(e.to_string(), "send failed: channel closed");
}

#[test]
fn receive_failed_display() {
    let e = TransportError::ReceiveFailed("broken pipe".into());
    assert_eq!(e.to_string(), "receive failed: broken pipe");
}

#[test]
fn closed_display() {
    let e = TransportError::Closed;
    assert_eq!(e.to_string(), "connection closed");
}

#[test]
fn debug_includes_variant_name() {
    let e = TransportError::ConnectionFailed("x".into());
    let dbg = format!("{e:?}");
    assert!(dbg.contains("ConnectionFailed"));
}

#[test]
fn is_std_error() {
    let e: Box<dyn std::error::Error> = Box::new(TransportError::Closed);
    assert_eq!(e.to_string(), "connection closed");
}
