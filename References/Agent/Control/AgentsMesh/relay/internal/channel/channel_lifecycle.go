package channel

import (
	"fmt"
	"time"

	"github.com/gorilla/websocket"

	"github.com/anthropics/agentsmesh/relay/internal/protocol"
)

func (c *Channel) AddSubscriber(subscriberID string, conn *websocket.Conn) {
	_ = c.addSubscriberInternal(subscriberID, conn, 0)
}

// AddSubscriberWithLimit atomically checks subscriber count and adds if under limit.
// Returns MaxSubscribersError if at capacity. Use maxSubscribers=0 for no limit.
func (c *Channel) AddSubscriberWithLimit(subscriberID string, conn *websocket.Conn, maxSubscribers int) error {
	return c.addSubscriberInternal(subscriberID, conn, maxSubscribers)
}

func (c *Channel) addSubscriberInternal(subscriberID string, conn *websocket.Conn, maxSubscribers int) error {
	subscriber := &Subscriber{ID: subscriberID, Conn: conn}

	c.subscribersMu.Lock()

	// Check closed INSIDE subscribersMu to prevent TOCTOU race with Close().
	c.closedMu.RLock()
	if c.closed {
		c.closedMu.RUnlock()
		c.subscribersMu.Unlock()
		_ = conn.Close()
		return fmt.Errorf("channel closed")
	}
	c.closedMu.RUnlock()

	if maxSubscribers > 0 && len(c.subscribers) >= maxSubscribers {
		c.subscribersMu.Unlock()
		return &MaxSubscribersError{Max: maxSubscribers}
	}
	c.subscribers[subscriberID] = subscriber

	if c.keepAliveTimer != nil {
		c.keepAliveTimer.Stop()
		c.keepAliveTimer = nil
	}
	count := len(c.subscribers)
	c.subscribersMu.Unlock()

	c.logger.Info("Subscriber connected", "subscriber_id", subscriberID, "total_subscribers", count)

	if c.IsPublisherDisconnected() {
		if err := subscriber.WriteMessage(protocol.EncodeRunnerDisconnected()); err != nil {
			c.logger.Warn("Failed to send publisher disconnected status to new subscriber",
				"subscriber_id", subscriberID, "error", err)
		}
	}

	go c.forwardSubscriberToPublisher(subscriberID)
	return nil
}

func (c *Channel) RemoveSubscriber(subscriberID string) {
	c.subscribersMu.Lock()
	subscriber, ok := c.subscribers[subscriberID]
	if !ok {
		c.subscribersMu.Unlock()
		return
	}
	_ = subscriber.Conn.Close()
	delete(c.subscribers, subscriberID)
	count := len(c.subscribers)
	c.subscribersMu.Unlock()

	c.logger.Info("Subscriber disconnected", "subscriber_id", subscriberID, "remaining_subscribers", count)

	if count == 0 {
		c.handleLastSubscriberGone()
	}
}

func (c *Channel) handleLastSubscriberGone() {
	c.subscribersMu.Lock()

	if len(c.subscribers) != 0 {
		c.subscribersMu.Unlock()
		return
	}

	if c.keepAliveTimer != nil {
		c.keepAliveTimer.Stop()
	}

	c.lastSubscriberDisconnect = time.Now()
	c.keepAliveTimer = time.AfterFunc(c.config.KeepAliveDuration, func() {
		if c.IsClosed() {
			return
		}

		c.subscribersMu.RLock()
		stillEmpty := len(c.subscribers) == 0
		c.subscribersMu.RUnlock()

		if stillEmpty {
			c.logger.Info("Keep-alive timeout, notifying backend")
			if c.onAllSubscribersGone != nil {
				c.onAllSubscribersGone(c.PodKey)
			}
		}
	})
	c.subscribersMu.Unlock()
}

func (c *Channel) SubscriberCount() int {
	c.subscribersMu.RLock()
	defer c.subscribersMu.RUnlock()
	return len(c.subscribers)
}

// Close closes the channel and all connections.
// Safe for concurrent callers -- only the first call performs cleanup.
func (c *Channel) Close() {
	c.publisherReplaceMu.Lock()
	c.closeInternal()
	c.publisherReplaceMu.Unlock()
}

// closeInternal performs the actual close logic.
// MUST be called with publisherReplaceMu held.
func (c *Channel) closeInternal() {
	c.closedMu.Lock()
	if c.closed {
		c.closedMu.Unlock()
		return
	}
	c.closed = true
	c.closedMu.Unlock()

	c.logger.Info("Closing channel")

	c.subscribersMu.Lock()
	if c.keepAliveTimer != nil {
		c.keepAliveTimer.Stop()
	}
	c.subscribersMu.Unlock()

	c.publisherMu.Lock()
	if c.publisherReconnectTimer != nil {
		c.publisherReconnectTimer.Stop()
		c.publisherReconnectTimer = nil
	}
	if c.publisher != nil {
		_ = c.publisher.Close()
		c.publisher = nil
	}
	c.publisherMu.Unlock()

	c.publisherWg.Wait()

	c.subscribersMu.Lock()
	for _, subscriber := range c.subscribers {
		_ = subscriber.Conn.Close()
	}
	c.subscribers = make(map[string]*Subscriber)
	c.subscribersMu.Unlock()

	if c.onChannelClosed != nil {
		c.onChannelClosed(c.PodKey)
	}
}
