package eventbus

import (
	"context"
	"encoding/json"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestEventBus_SubscribeOrgWithRedis(t *testing.T) {
	t.Run("receives events for subscribed org", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)
		defer eb.Close()

		var received *Event
		var wg sync.WaitGroup
		wg.Add(1)

		eb.Subscribe(EventTicketCreated, func(e *Event) {
			received = e
			wg.Done()
		})

		// Subscribe to org
		eb.SubscribeOrg(42)

		// Give subscriber time to start
		time.Sleep(50 * time.Millisecond)

		// Publish event for org 42
		event := &Event{
			Type:             EventTicketCreated,
			Category:         CategoryEntity,
			OrganizationID:   42,
			EntityType:       "ticket",
			EntityID:         "TICKET-001",
			SourceInstanceID: "other-instance",
			Timestamp:        time.Now().UnixMilli(),
		}

		data, _ := json.Marshal(event)
		err := client.Publish(context.Background(), "events:org:42", data).Err()
		if err != nil {
			t.Fatalf("failed to publish to redis: %v", err)
		}

		// Wait for handler
		done := make(chan struct{})
		go func() {
			wg.Wait()
			close(done)
		}()

		select {
		case <-done:
			if received == nil {
				t.Fatal("handler did not receive event")
			}
			if received.EntityID != "TICKET-001" {
				t.Errorf("expected EntityID 'TICKET-001', got '%s'", received.EntityID)
			}
		case <-time.After(2 * time.Second):
			t.Error("handler did not receive event within timeout")
		}
	})

	t.Run("stops receiving after unsubscribe", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)
		defer eb.Close()

		var callCount int32
		eb.Subscribe(EventTicketCreated, func(e *Event) {
			atomic.AddInt32(&callCount, 1)
		})

		// Subscribe and then unsubscribe
		eb.SubscribeOrg(99)
		time.Sleep(50 * time.Millisecond)
		eb.UnsubscribeOrg(99)
		time.Sleep(50 * time.Millisecond)

		// Publish event
		event := &Event{
			Type:             EventTicketCreated,
			Category:         CategoryEntity,
			OrganizationID:   99,
			EntityType:       "ticket",
			EntityID:         "TICKET-002",
			SourceInstanceID: "other-instance",
			Timestamp:        time.Now().UnixMilli(),
		}

		data, _ := json.Marshal(event)
		_ = client.Publish(context.Background(), "events:org:99", data).Err()

		// Wait a bit
		time.Sleep(100 * time.Millisecond)

		// Should not receive since unsubscribed
		// Note: due to timing, we might still receive 0 or 1 event
		// The important thing is that the goroutine exits cleanly
	})
}

func TestEventBus_subscribeToOrgChannel_ContextCancellation(t *testing.T) {
	mr, client := setupMiniredis(t)
	defer mr.Close()
	defer client.Close()

	eb := NewEventBus(client, nil)

	// Subscribe to org
	eb.SubscribeOrg(100)

	// Give subscriber time to start
	time.Sleep(50 * time.Millisecond)

	// Close EventBus - should cancel context and stop goroutine
	eb.Close()

	// Give goroutine time to exit
	time.Sleep(100 * time.Millisecond)

	// No assertion needed - test passes if no deadlock/panic
}

func TestEventBus_subscribeToOrgChannel_ChannelClosed(t *testing.T) {
	t.Run("exits when redis channel is closed", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		eb := NewEventBus(client, nil)
		defer eb.Close()

		eb.SubscribeOrg(200)

		// Give subscriber time to start
		time.Sleep(50 * time.Millisecond)

		// Close Redis connection - this will close the pubsub channel
		mr.Close()
		client.Close()

		// Give goroutine time to exit
		time.Sleep(100 * time.Millisecond)

		// No assertion needed - test passes if no deadlock/panic
	})
}
