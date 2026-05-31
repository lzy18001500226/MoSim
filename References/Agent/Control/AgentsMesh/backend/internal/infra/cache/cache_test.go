package cache

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// Tests for key generation functions (these don't require Redis connection)

func TestPodKey(t *testing.T) {
	t.Run("should generate correct pod key", func(t *testing.T) {
		key := PodKey("abc123")
		assert.Equal(t, "pod:abc123", key)
	})

	t.Run("should handle empty string", func(t *testing.T) {
		key := PodKey("")
		assert.Equal(t, "pod:", key)
	})
}

func TestUserKey(t *testing.T) {
	t.Run("should generate correct user key", func(t *testing.T) {
		key := UserKey(123)
		assert.Equal(t, "user:123", key)
	})

	t.Run("should handle zero ID", func(t *testing.T) {
		key := UserKey(0)
		assert.Equal(t, "user:0", key)
	})
}

func TestOrgKey(t *testing.T) {
	t.Run("should generate correct org key", func(t *testing.T) {
		key := OrgKey(456)
		assert.Equal(t, "org:456", key)
	})
}

func TestRunnerKey(t *testing.T) {
	t.Run("should generate correct runner key", func(t *testing.T) {
		key := RunnerKey(789)
		assert.Equal(t, "runner:789", key)
	})
}

func TestChannelKey(t *testing.T) {
	t.Run("should generate correct channel key", func(t *testing.T) {
		key := ChannelKey(101)
		assert.Equal(t, "channel:101", key)
	})
}

func TestRateLimitKey(t *testing.T) {
	t.Run("should generate correct rate limit key", func(t *testing.T) {
		key := RateLimitKey("user:123:api")
		assert.Equal(t, "ratelimit:user:123:api", key)
	})

	t.Run("should handle IP address", func(t *testing.T) {
		key := RateLimitKey("192.168.1.1")
		assert.Equal(t, "ratelimit:192.168.1.1", key)
	})
}

func TestLockKey(t *testing.T) {
	t.Run("should generate correct lock key", func(t *testing.T) {
		key := LockKey("resource:123")
		assert.Equal(t, "lock:resource:123", key)
	})
}

func TestPubSubChannel(t *testing.T) {
	t.Run("should generate correct pubsub channel", func(t *testing.T) {
		channel := PubSubChannel("pod", 123)
		assert.Equal(t, "pubsub:pod:123", channel)
	})

	t.Run("should handle different channel types", func(t *testing.T) {
		assert.Equal(t, "pubsub:terminal:456", PubSubChannel("terminal", 456))
		assert.Equal(t, "pubsub:notification:789", PubSubChannel("notification", 789))
	})
}

func TestPrefixConstants(t *testing.T) {
	// Verify prefix constants are defined correctly
	assert.Equal(t, "pod:", PrefixPod)
	assert.Equal(t, "user:", PrefixUser)
	assert.Equal(t, "org:", PrefixOrg)
	assert.Equal(t, "runner:", PrefixRunner)
	assert.Equal(t, "channel:", PrefixChannel)
	assert.Equal(t, "ratelimit:", PrefixRateLimit)
	assert.Equal(t, "lock:", PrefixLock)
	assert.Equal(t, "pubsub:", PrefixPubSub)
}

func TestErrNotFound(t *testing.T) {
	// Verify error is defined
	assert.NotNil(t, ErrNotFound)
	assert.Contains(t, ErrNotFound.Error(), "not found")
}
