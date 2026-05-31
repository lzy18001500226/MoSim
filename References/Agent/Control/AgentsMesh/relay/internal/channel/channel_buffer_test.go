package channel

import (
	"testing"
	"time"
)

func TestChannel_AddSubscriber_CancelsKeepAliveTimer(t *testing.T) {
	ch := NewChannelWithConfig("pod-ka-cancel", testChannelConfig(), nil, nil)

	s1Server, _ := createWSPair(t)
	ch.AddSubscriber("s1", s1Server)

	ch.RemoveSubscriber("s1")

	if ch.SubscriberCount() != 0 {
		t.Fatalf("expected 0 subscribers after removal, got %d", ch.SubscriberCount())
	}

	s2Server, _ := createWSPair(t)
	ch.AddSubscriber("s2", s2Server)

	if ch.SubscriberCount() != 1 {
		t.Fatalf("expected 1 subscriber after re-add, got %d", ch.SubscriberCount())
	}

	time.Sleep(300 * time.Millisecond)

	if ch.SubscriberCount() != 1 {
		t.Fatalf("expected 1 subscriber after waiting, got %d", ch.SubscriberCount())
	}
}

func TestChannel_RemoveSubscriber_OnAllSubscribersGoneCallback(t *testing.T) {
	callbackCalled := make(chan string, 1)
	onGone := func(podKey string) {
		callbackCalled <- podKey
	}

	cfg := testChannelConfig()
	cfg.KeepAliveDuration = 50 * time.Millisecond
	ch := NewChannelWithConfig("pod-gone-cb", cfg, onGone, nil)

	subServer, _ := createWSPair(t)
	ch.AddSubscriber("s1", subServer)

	ch.RemoveSubscriber("s1")

	select {
	case key := <-callbackCalled:
		if key != "pod-gone-cb" {
			t.Fatalf("callback podKey: got %q, want %q", key, "pod-gone-cb")
		}
	case <-time.After(2 * time.Second):
		t.Fatal("onAllSubscribersGone callback was not called within timeout")
	}
}
