use std::time::Duration;

use crate::reconnect::{ReconnectPolicy, should_reconnect};

#[test]
fn test_policy_default_values() {
    let mut policy = ReconnectPolicy::new(1000, 30000, 10);
    assert_eq!(policy.attempts(), 0);
    assert_eq!(policy.max_attempts(), 10);
    assert!(!policy.is_exhausted());
    assert!(policy.next_delay().is_some());
}

#[test]
fn test_exponential_backoff_base_growth() {
    let mut policy = ReconnectPolicy::new(1000, 1_000_000, 10);
    let d1 = policy.next_delay().unwrap(); // 1000 * 2^0 + jitter
    let d2 = policy.next_delay().unwrap(); // 1000 * 2^1 + jitter
    let d3 = policy.next_delay().unwrap(); // 1000 * 2^2 + jitter

    assert!(d1.as_millis() >= 1000 && d1.as_millis() < 2100);
    assert!(d2.as_millis() >= 2000 && d2.as_millis() < 3100);
    assert!(d3.as_millis() >= 4000 && d3.as_millis() < 5100);
}

#[test]
fn test_delay_capped_at_max() {
    let mut policy = ReconnectPolicy::new(1000, 5000, 20);
    for _ in 0..15 {
        if let Some(d) = policy.next_delay() {
            let ms: u128 = d.as_millis();
            assert!(ms <= 5000, "delay {} exceeded max", ms);
        }
    }
}

#[test]
fn test_exhaustion_after_max_attempts() {
    let mut policy = ReconnectPolicy::new(100, 1000, 3);
    assert!(policy.next_delay().is_some()); // attempt 1
    assert!(policy.next_delay().is_some()); // attempt 2
    assert!(policy.next_delay().is_some()); // attempt 3
    assert!(policy.next_delay().is_none()); // exhausted
    assert!(policy.is_exhausted());
    assert_eq!(policy.attempts(), 3);
}

#[test]
fn test_reset_clears_attempts() {
    let mut policy = ReconnectPolicy::new(100, 1000, 2);
    let _ = policy.next_delay();
    let _ = policy.next_delay();
    assert!(policy.is_exhausted());

    policy.reset();
    assert_eq!(policy.attempts(), 0);
    assert!(!policy.is_exhausted());

    let d = policy.next_delay();
    assert!(d.is_some());
}

#[test]
fn test_reset_resets_backoff_level() {
    let mut policy = ReconnectPolicy::new(1000, 1_000_000, 10);
    for _ in 0..5 {
        let _ = policy.next_delay();
    }
    policy.reset();
    let d = policy.next_delay().unwrap();
    // after reset, first delay should be near initial (1000..2000)
    assert!(d.as_millis() < 2100);
}

#[test]
fn test_zero_max_attempts() {
    let mut policy = ReconnectPolicy::new(1000, 30000, 0);
    assert!(policy.is_exhausted());
    assert!(policy.next_delay().is_none());
}

#[test]
fn test_single_attempt() {
    let mut policy = ReconnectPolicy::new(500, 30000, 1);
    let d = policy.next_delay();
    assert!(d.is_some());
    assert!(d.unwrap() >= Duration::from_millis(500));
    assert!(policy.next_delay().is_none());
}

#[test]
fn test_should_reconnect_normal_close() {
    assert!(!should_reconnect(Some(1000)));
}

#[test]
fn test_should_reconnect_abnormal_codes() {
    assert!(should_reconnect(Some(1006)));
    assert!(should_reconnect(Some(4000)));
    assert!(should_reconnect(Some(1001)));
    assert!(should_reconnect(Some(1011)));
}

#[test]
fn test_should_reconnect_none() {
    assert!(should_reconnect(None));
}
