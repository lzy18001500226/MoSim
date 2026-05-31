package channel

import (
	"time"

	"github.com/gorilla/websocket"

	"github.com/anthropics/agentsmesh/relay/internal/protocol"
)

// handlePublisherDisconnect handles publisher disconnect with double identity check
// (pointer + epoch). If SetPublisher already replaced the publisher, this is a no-op.
func (c *Channel) handlePublisherDisconnect(disconnectedConn *websocket.Conn, epoch uint64) {
	c.publisherMu.Lock()

	if c.publisher != disconnectedConn || c.publisherEpoch != epoch {
		c.publisherMu.Unlock()
		return
	}

	conn := c.publisher
	c.publisher = nil
	c.publisherDisconnected = true

	c.logger.Info("Publisher disconnected, waiting for reconnection",
		"timeout", c.config.PublisherReconnectTimeout, "epoch", epoch)

	c.publisherReconnectTimer = time.AfterFunc(c.config.PublisherReconnectTimeout, func() {
		c.publisherReplaceMu.Lock()

		c.publisherMu.Lock()
		stillDisconnected := c.publisherDisconnected
		c.publisherMu.Unlock()

		if !stillDisconnected {
			c.publisherReplaceMu.Unlock()
			return
		}

		c.logger.Info("Publisher reconnect timeout, closing channel")
		c.closeInternal()
		c.publisherReplaceMu.Unlock()
	})
	c.publisherMu.Unlock()

	_ = conn.Close()

	c.Broadcast(protocol.EncodeRunnerDisconnected())
}
