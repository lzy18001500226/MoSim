package websocket

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestHubBroadcastToOrg(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	client1 := mockClient(1, 100, "", 0, true) // Events channel
	client2 := mockClient(2, 100, "", 0, true) // Events channel
	client3 := mockClient(3, 200, "", 0, true) // Different org

	hub.Register(client1)
	hub.Register(client2)
	hub.Register(client3)
	time.Sleep(20 * time.Millisecond)

	hub.BroadcastToOrg(100, []byte(`{"event":"test"}`))

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

func TestHubSendToUser(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	client1 := mockClient(123, 1, "", 0, true) // Events for user 123
	client2 := mockClient(123, 1, "", 0, true) // Same user
	client3 := mockClient(456, 1, "", 0, true) // Different user

	hub.Register(client1)
	hub.Register(client2)
	hub.Register(client3)
	time.Sleep(20 * time.Millisecond)

	hub.SendToUser(123, []byte(`{"notification":"hello"}`))

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

func TestHubBroadcastToOrgJSON(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	client := mockClient(1, 100, "", 0, true)
	hub.Register(client)
	time.Sleep(10 * time.Millisecond)

	msg := map[string]interface{}{
		"type": "notification",
		"data": "hello",
	}
	err := hub.BroadcastToOrgJSON(100, msg)
	assert.NoError(t, err)

	select {
	case data := <-client.send:
		assert.Contains(t, string(data), "notification")
	case <-time.After(100 * time.Millisecond):
		t.Error("client didn't receive message")
	}
}

func TestHubSendToUserJSON(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	client := mockClient(123, 1, "", 0, true)
	hub.Register(client)
	time.Sleep(10 * time.Millisecond)

	msg := map[string]interface{}{
		"type": "alert",
		"data": "important",
	}
	err := hub.SendToUserJSON(123, msg)
	assert.NoError(t, err)

	select {
	case data := <-client.send:
		assert.Contains(t, string(data), "alert")
	case <-time.After(100 * time.Millisecond):
		t.Error("client didn't receive message")
	}
}

func TestHubBroadcastToOrgEmptyOrg(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Broadcast to non-existent org should not panic
	hub.BroadcastToOrg(99999, []byte(`{"test":"data"}`))
}

func TestHubSendToUserEmptyUser(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Send to non-existent user should not panic
	hub.SendToUser(99999, []byte(`{"test":"data"}`))
}

func TestHubBroadcastToOrgJSONError(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Test with invalid JSON data (channel that cannot be serialized)
	invalidData := make(chan int)
	err := hub.BroadcastToOrgJSON(1, invalidData)
	assert.Error(t, err)
}

func TestHubSendToUserJSONError(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Test with invalid JSON data
	invalidData := make(chan int)
	err := hub.SendToUserJSON(1, invalidData)
	assert.Error(t, err)
}
