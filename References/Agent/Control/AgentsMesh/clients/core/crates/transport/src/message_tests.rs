use crate::WsMessage;

#[test]
fn binary_construction() {
    let msg = WsMessage::Binary(vec![1, 2, 3]);
    match &msg {
        WsMessage::Binary(data) => assert_eq!(data, &[1, 2, 3]),
        _ => panic!("expected Binary"),
    }
}

#[test]
fn text_construction() {
    let msg = WsMessage::Text("hello".into());
    match &msg {
        WsMessage::Text(s) => assert_eq!(s, "hello"),
        _ => panic!("expected Text"),
    }
}

#[test]
fn close_with_code() {
    let msg = WsMessage::Close(Some(1000));
    match &msg {
        WsMessage::Close(code) => assert_eq!(*code, Some(1000)),
        _ => panic!("expected Close"),
    }
}

#[test]
fn close_without_code() {
    let msg = WsMessage::Close(None);
    match &msg {
        WsMessage::Close(code) => assert!(code.is_none()),
        _ => panic!("expected Close"),
    }
}

#[test]
fn clone_preserves_data() {
    let original = WsMessage::Binary(vec![10, 20]);
    let cloned = original.clone();
    match (&original, &cloned) {
        (WsMessage::Binary(a), WsMessage::Binary(b)) => assert_eq!(a, b),
        _ => panic!("clone mismatch"),
    }
}

#[test]
fn clone_text() {
    let original = WsMessage::Text("test".into());
    let cloned = original.clone();
    match (&original, &cloned) {
        (WsMessage::Text(a), WsMessage::Text(b)) => assert_eq!(a, b),
        _ => panic!("clone mismatch"),
    }
}

#[test]
fn debug_format() {
    let msg = WsMessage::Text("hi".into());
    let dbg = format!("{msg:?}");
    assert!(dbg.contains("Text"));
    assert!(dbg.contains("hi"));
}

#[test]
fn binary_empty() {
    let msg = WsMessage::Binary(vec![]);
    match &msg {
        WsMessage::Binary(data) => assert!(data.is_empty()),
        _ => panic!("expected Binary"),
    }
}

#[test]
fn text_empty() {
    let msg = WsMessage::Text(String::new());
    match &msg {
        WsMessage::Text(s) => assert!(s.is_empty()),
        _ => panic!("expected Text"),
    }
}
