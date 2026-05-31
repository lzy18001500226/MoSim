package websocket

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestHubUnregisterNonExistentClient(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Try to unregister a client that was never registered
	client := mockClient(999, 1, "", 0, true)
	hub.Unregister(client)
	time.Sleep(10 * time.Millisecond)

	// Should not panic, count should be 0
	assert.Equal(t, 0, hub.GetTotalClientCount())
}

func TestHubUnregisterWithPodKey(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Register client with pod key
	client := mockClient(1, 1, "pod-test-123", 0, false)
	hub.Register(client)
	time.Sleep(10 * time.Millisecond)

	assert.Equal(t, 1, hub.GetPodClientCount("pod-test-123"))

	// Unregister
	hub.Unregister(client)
	time.Sleep(10 * time.Millisecond)

	assert.Equal(t, 0, hub.GetPodClientCount("pod-test-123"))
}

func TestHubUnregisterWithChannel(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Register client with channel
	client := mockClient(1, 1, "", 500, false)
	hub.Register(client)
	time.Sleep(10 * time.Millisecond)

	// Unregister
	hub.Unregister(client)
	time.Sleep(10 * time.Millisecond)

	assert.Equal(t, 0, hub.GetTotalClientCount())
}

func TestHubGetShardByPod(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Test pod key sharding
	shard1 := hub.getShardByPod("pod-abc-123")
	shard2 := hub.getShardByPod("pod-abc-123")
	shard3 := hub.getShardByPod("pod-xyz-456")

	// Same pod should always go to same shard
	assert.Equal(t, shard1, shard2)
	// Different pods may or may not go to different shards (depends on hash)
	_ = shard3 // Just verify it doesn't panic
}

func TestHubGetShardByOrg(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	shard := hub.getShardByOrg(100)
	assert.True(t, shard < hubShards)
}

func TestHubGetShardByChannel(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	shard := hub.getShardByChannel(200)
	assert.True(t, shard < hubShards)
}

func TestHubClientWithNoUserAndNoOrg(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Client with userID=0 and orgID=0 should use fallback shard
	client := mockClient(0, 0, "", 0, false)
	hub.Register(client)
	time.Sleep(10 * time.Millisecond)

	assert.Equal(t, 1, hub.GetTotalClientCount())

	hub.Unregister(client)
	time.Sleep(10 * time.Millisecond)

	assert.Equal(t, 0, hub.GetTotalClientCount())
}

func TestHubClientWithOnlyOrgID(t *testing.T) {
	hub := NewHub()
	defer hub.Close()

	// Client with userID=0 but orgID set should use org-based sharding
	client := mockClient(0, 100, "", 0, false)
	hub.Register(client)
	time.Sleep(10 * time.Millisecond)

	assert.Equal(t, 1, hub.GetTotalClientCount())
}
