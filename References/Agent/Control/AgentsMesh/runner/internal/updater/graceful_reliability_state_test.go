package updater

import (
	"sync/atomic"
	"testing"

	"github.com/stretchr/testify/assert"
)

// Tests for state management

func TestSetState_AtomicUpdate(t *testing.T) {
	u := New("1.0.0")

	var callbackCount int32
	var lastState State
	var lastInfo *UpdateInfo

	cb := func(state State, info *UpdateInfo, activePods int) {
		atomic.AddInt32(&callbackCount, 1)
		lastState = state
		lastInfo = info
	}

	g := NewGracefulUpdater(u, func() int { return 5 }, WithStatusCallback(cb))

	// Set pending info first
	g.mu.Lock()
	g.pendingInfo = &UpdateInfo{LatestVersion: "v2.0.0", CurrentVersion: "v1.0.0"}
	g.mu.Unlock()

	// Set state - should atomically capture info and call callback
	g.setState(StateDownloading)

	assert.Equal(t, int32(1), atomic.LoadInt32(&callbackCount))
	assert.Equal(t, StateDownloading, lastState)
	assert.NotNil(t, lastInfo)
	assert.Equal(t, "v2.0.0", lastInfo.LatestVersion)
}

func TestSetState_ConcurrentAccess(t *testing.T) {
	u := New("1.0.0")

	var callbackCount int32
	cb := func(state State, info *UpdateInfo, activePods int) {
		atomic.AddInt32(&callbackCount, 1)
	}

	g := NewGracefulUpdater(u, func() int { return 0 }, WithStatusCallback(cb))

	// Run multiple goroutines setting state concurrently
	done := make(chan struct{})
	for i := 0; i < 10; i++ {
		go func(state State) {
			for j := 0; j < 100; j++ {
				g.setState(state)
			}
			done <- struct{}{}
		}(State(i % 6))
	}

	// Wait for all goroutines to complete
	for i := 0; i < 10; i++ {
		<-done
	}

	// Verify all callbacks were called (1000 total)
	assert.Equal(t, int32(1000), atomic.LoadInt32(&callbackCount))
}
