package eventbus

import (
	"context"
	"encoding/json"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestEventBus_StartRedisSubscriber(t *testing.T) {
	t.Run("subscribes to pattern and dispatches events", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)
		defer eb.Close()

		var received *Event
		var wg sync.WaitGroup
		wg.Add(1)

		eb.Subscribe(EventPodCreated, func(e *Event) {
			received = e
			wg.Done()
		})

		// Start subscriber
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		eb.StartRedisSubscriber(ctx)

		// Give subscriber time to start
		time.Sleep(50 * time.Millisecond)

		// Publish directly to Redis (simulating another instance)
		event := &Event{
			Type:             EventPodCreated,
			Category:         CategoryEntity,
			OrganizationID:   1,
			EntityType:       "pod",
			EntityID:         "pod-from-other-instance",
			SourceInstanceID: "other-instance-123", // Different instance
			Timestamp:        time.Now().UnixMilli(),
		}

		data, _ := json.Marshal(event)
		err := client.Publish(context.Background(), "events:org:1", data).Err()
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
			if received.EntityID != "pod-from-other-instance" {
				t.Errorf("expected EntityID 'pod-from-other-instance', got '%s'", received.EntityID)
			}
		case <-time.After(2 * time.Second):
			t.Error("handler did not receive event within timeout")
		}
	})

	t.Run("skips events from same instance", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)
		defer eb.Close()

		var callCount int32
		eb.Subscribe(EventPodCreated, func(e *Event) {
			atomic.AddInt32(&callCount, 1)
		})

		// Start subscriber
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		eb.StartRedisSubscriber(ctx)

		// Give subscriber time to start
		time.Sleep(50 * time.Millisecond)

		// Publish event with same instance ID (should be skipped)
		event := &Event{
			Type:             EventPodCreated,
			Category:         CategoryEntity,
			OrganizationID:   1,
			EntityType:       "pod",
			EntityID:         "pod-same-instance",
			SourceInstanceID: eb.instanceID, // Same instance - should be skipped
			Timestamp:        time.Now().UnixMilli(),
		}

		data, _ := json.Marshal(event)
		err := client.Publish(context.Background(), "events:org:1", data).Err()
		if err != nil {
			t.Fatalf("failed to publish to redis: %v", err)
		}

		// Wait a bit
		time.Sleep(100 * time.Millisecond)

		if atomic.LoadInt32(&callCount) != 0 {
			t.Errorf("expected 0 calls (event from same instance should be skipped), got %d", callCount)
		}
	})

	t.Run("handles invalid JSON gracefully", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)
		defer eb.Close()

		var callCount int32
		eb.Subscribe(EventPodCreated, func(e *Event) {
			atomic.AddInt32(&callCount, 1)
		})

		// Start subscriber
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		eb.StartRedisSubscriber(ctx)

		// Give subscriber time to start
		time.Sleep(50 * time.Millisecond)

		// Publish invalid JSON
		err := client.Publish(context.Background(), "events:org:1", "invalid json {{{").Err()
		if err != nil {
			t.Fatalf("failed to publish to redis: %v", err)
		}

		// Wait a bit - should not crash
		time.Sleep(100 * time.Millisecond)

		if atomic.LoadInt32(&callCount) != 0 {
			t.Errorf("expected 0 calls (invalid JSON should be skipped), got %d", callCount)
		}
	})

	t.Run("does nothing without redis client", func(t *testing.T) {
		eb := NewEventBus(nil, nil)
		defer eb.Close()

		// Should not panic
		ctx, cancel := context.WithCancel(context.Background())
		defer cancel()
		eb.StartRedisSubscriber(ctx)
	})
}

func TestEventBus_StartRedisSubscriber_ContextDone(t *testing.T) {
	t.Run("exits when context is cancelled", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)
		defer eb.Close()

		ctx, cancel := context.WithCancel(context.Background())
		eb.StartRedisSubscriber(ctx)

		// Give subscriber time to start
		time.Sleep(50 * time.Millisecond)

		// Cancel context
		cancel()

		// Give goroutine time to exit
		time.Sleep(100 * time.Millisecond)

		// No assertion needed - test passes if no deadlock/panic
	})

	t.Run("exits when eventbus context is cancelled", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)

		ctx := context.Background()
		eb.StartRedisSubscriber(ctx)

		// Give subscriber time to start
		time.Sleep(50 * time.Millisecond)

		// Close EventBus (cancels internal context)
		eb.Close()

		// Give goroutine time to exit
		time.Sleep(100 * time.Millisecond)

		// No assertion needed - test passes if no deadlock/panic
	})
}
