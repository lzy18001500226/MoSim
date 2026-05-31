package websocket

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestHubBroadcastToPod(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Create clients connected to same pod
	client1 := mockClient(1, 1, "pod-abc", 0, false)
	client2 := mockClient(2, 1, "pod-abc", 0, false)
	client3 := mockClient(3, 1, "pod-xyz", 0, false) // Different pod

	hub.Register(client1)
	hub.Register(client2)
	hub.Register(client3)
	time.Sleep(20 * time.Millisecond)

	// Broadcast to pod-abc
	msg := &Message{Type: "test", Data: []byte(`"hello"`)}
	hub.BroadcastToPod("pod-abc", msg)

	// client1 and client2 should receive
	select {
	case data := <-client1.send:
		assert.Contains(t, string(data), "test")
	case <-time.After(100 * time.Millisecond):
		t.Error("client1 didn't receive message")
	}

	select {
	case data := <-client2.send:
		assert.Contains(t, string(data), "test")
	case <-time.After(100 * time.Millisecond):
		t.Error("client2 didn't receive message")
	}

	// client3 should NOT receive
	select {
	case <-client3.send:
		t.Error("client3 should not receive message for different pod")
	case <-time.After(50 * time.Millisecond):
		// Expected
	}
}

func TestHubBroadcastToChannel(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	client1 := mockClient(1, 1, "", 100, false)
	client2 := mockClient(2, 1, "", 100, false)
	client3 := mockClient(3, 1, "", 200, false) // Different channel

	hub.Register(client1)
	hub.Register(client2)
	hub.Register(client3)
	time.Sleep(20 * time.Millisecond)

	msg := &Message{Type: "channel_msg", Data: []byte(`"hello"`)}
	hub.BroadcastToChannel(100, msg)

	// client1 and client2 should receive
	select {
	case <-client1.send:
	case <-time.After(100 * time.Millisecond):
		t.Error("client1 didn't receive message")
	}

	select {
	case <-client2.send:
	case <-time.After(100 * time.Millisecond):
		t.Error("client2 didn't receive message")
	}

	// client3 should NOT receive
	select {
	case <-client3.send:
		t.Error("client3 should not receive message")
	case <-time.After(50 * time.Millisecond):
	}
}

func TestHubBroadcastToPodEmptyPod(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Broadcast to non-existent pod should not panic
	msg := &Message{Type: "test", Data: []byte(`"hello"`)}
	hub.BroadcastToPod("non-existent-pod", msg)
}

func TestHubBroadcastToChannelEmptyChannel(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Broadcast to non-existent channel should not panic
	msg := &Message{Type: "test", Data: []byte(`"hello"`)}
	hub.BroadcastToChannel(99999, msg)
}
