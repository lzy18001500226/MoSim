package eventbus

import (
	"context"
	"encoding/json"
	"testing"
	"time"
)

func TestEventBus_PublishToRedis(t *testing.T) {
	t.Run("publishes event to redis channel", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		defer mr.Close()
		defer client.Close()

		eb := NewEventBus(client, nil)
		defer eb.Close()

		// Subscribe to the channel in miniredis
		pubsub := client.Subscribe(context.Background(), "events:org:1")
		defer pubsub.Close()

		// Wait for subscription to be ready
		_, err := pubsub.Receive(context.Background())
		if err != nil {
			t.Fatalf("failed to subscribe: %v", err)
		}

		ch := pubsub.Channel()

		event := &Event{
			Type:           EventPodCreated,
			OrganizationID: 1,
			EntityType:     "pod",
			EntityID:       "pod-redis-test",
		}

		err = eb.Publish(context.Background(), event)
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		// Wait for message
		select {
		case msg := <-ch:
			var received Event
			if err := json.Unmarshal([]byte(msg.Payload), &received); err != nil {
				t.Fatalf("failed to unmarshal: %v", err)
			}
			if received.EntityID != "pod-redis-test" {
				t.Errorf("expected EntityID 'pod-redis-test', got '%s'", received.EntityID)
			}
			if received.SourceInstanceID != eb.instanceID {
				t.Errorf("expected SourceInstanceID '%s', got '%s'", eb.instanceID, received.SourceInstanceID)
			}
		case <-time.After(time.Second):
			t.Error("did not receive message from redis")
		}
	})
}

func TestEventBus_PublishToRedis_ErrorHandling(t *testing.T) {
	t.Run("logs error when redis publish fails", func(t *testing.T) {
		mr, client := setupMiniredis(t)
		eb := NewEventBus(client, nil)
		defer eb.Close()

		// Close miniredis to cause publish failure
		mr.Close()
		client.Close()

		event := &Event{
			Type:           EventPodCreated,
			OrganizationID: 1,
			EntityType:     "pod",
			EntityID:       "pod-error-test",
		}

		// Should not panic, just log error
		err := eb.Publish(context.Background(), event)
		// Publish returns nil even if Redis fails (local dispatch succeeds)
		if err != nil {
			t.Errorf("expected nil error, got %v", err)
		}
	})
}
