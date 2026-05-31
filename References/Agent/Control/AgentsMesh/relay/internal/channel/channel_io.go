package channel

func (c *Channel) writeToPublisher(data []byte) error {
	c.publisherWriteMu.Lock()
	defer c.publisherWriteMu.Unlock()

	c.publisherMu.RLock()
	pub := c.publisher
	c.publisherMu.RUnlock()

	if pub == nil {
		c.logger.Debug("Dropping data, publisher not connected")
		return nil
	}
	return writeToConn(pub, data)
}

// Broadcast sends data to all connected subscribers.
// Uses snapshot-then-write pattern: subscribers are copied under lock, then
// writes happen without holding the lock. This prevents a slow/dead subscriber
// from blocking SubscriberCount(), Stats(), and the heartbeat goroutine.
func (c *Channel) Broadcast(data []byte) {
	c.subscribersMu.RLock()
	subscribers := make([]*Subscriber, 0, len(c.subscribers))
	for _, sub := range c.subscribers {
		subscribers = append(subscribers, sub)
	}
	c.subscribersMu.RUnlock()

	c.logger.Debug("Broadcasting to subscribers", "data_len", len(data), "subscriber_count", len(subscribers))

	var failedIDs []string
	for _, subscriber := range subscribers {
		if err := subscriber.WriteMessage(data); err != nil {
			c.logger.Warn("Failed to send to subscriber, removing",
				"subscriber_id", subscriber.ID, "error", err)
			failedIDs = append(failedIDs, subscriber.ID)
		} else {
			c.logger.Debug("Sent to subscriber", "subscriber_id", subscriber.ID, "data_len", len(data))
		}
	}

	for _, id := range failedIDs {
		c.RemoveSubscriber(id)
	}
}

func (c *Channel) forwardPublisherToSubscribers(epoch uint64) {
	defer c.publisherWg.Done()

	c.publisherMu.RLock()
	conn := c.publisher
	currentEpoch := c.publisherEpoch
	c.publisherMu.RUnlock()

	if conn == nil || currentEpoch != epoch {
		return
	}

	conn.SetReadLimit(maxMessageSize)

	for {
		_, data, err := conn.ReadMessage()
		if err != nil {
			c.logger.Info("Publisher disconnected", "error", err, "epoch", epoch)
			c.handlePublisherDisconnect(conn, epoch)
			break
		}
		c.Broadcast(data)
	}
}

func (c *Channel) forwardSubscriberToPublisher(subscriberID string) {
	c.subscribersMu.RLock()
	subscriber, ok := c.subscribers[subscriberID]
	c.subscribersMu.RUnlock()

	if !ok {
		return
	}

	subscriber.Conn.SetReadLimit(maxMessageSize)

	for {
		_, data, err := subscriber.Conn.ReadMessage()
		if err != nil {
			c.RemoveSubscriber(subscriberID)
			break
		}
		if err := c.writeToPublisher(data); err != nil {
			c.logger.Warn("Failed to forward to publisher", "error", err)
		}
	}
}
