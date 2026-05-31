package eventbus

import (
	"testing"
)

func TestNewEventBus(t *testing.T) {
	t.Run("with nil redis client and nil logger", func(t *testing.T) {
		eb := NewEventBus(nil, nil)
		if eb == nil {
			t.Fatal("expected non-nil EventBus")
		}
		if eb.logger == nil {
			t.Error("expected default logger to be set")
		}
		if eb.instanceID == "" {
			t.Error("expected instanceID to be generated")
		}
		if eb.handlers == nil {
			t.Error("expected handlers map to be initialized")
		}
		if eb.categoryHandlers == nil {
			t.Error("expected categoryHandlers map to be initialized")
		}
		if eb.subscribedOrgs == nil {
			t.Error("expected subscribedOrgs map to be initialized")
		}
		eb.Close()
	})

	t.Run("instanceID format contains hostname", func(t *testing.T) {
		eb := NewEventBus(nil, nil)
		defer eb.Close()

		// instanceID format: hostname-uuid8chars
		if len(eb.instanceID) < 10 {
			t.Errorf("instanceID too short: %s", eb.instanceID)
		}
	})
}

func TestEventBus_Registry(t *testing.T) {
	eb := NewEventBus(nil, nil)
	defer eb.Close()

	registry := eb.Registry()
	if registry == nil {
		t.Fatal("expected non-nil registry")
	}

	// Verify it's the default registry
	if registry != DefaultRegistry {
		t.Error("expected default registry")
	}
}

func TestEventBus_Close(t *testing.T) {
	eb := NewEventBus(nil, nil)

	// Subscribe a handler
	eb.Subscribe(EventPodCreated, func(e *Event) {})

	// Close should not panic
	eb.Close()

	// Verify context is cancelled
	select {
	case <-eb.ctx.Done():
		// Success - context was cancelled
	default:
		t.Error("context should be cancelled after Close()")
	}
}

func TestEventBus_redisChannel(t *testing.T) {
	eb := NewEventBus(nil, nil)
	defer eb.Close()

	channel := eb.redisChannel(42)
	expected := "events:org:42"

	if channel != expected {
		t.Errorf("expected channel %s, got %s", expected, channel)
	}
}
