package channel

import (
	"log/slog"
	"sync"
	"time"

	"github.com/gorilla/websocket"

	"github.com/anthropics/agentsmesh/relay/internal/protocol"
)

const writeWait = 5 * time.Second

const maxMessageSize = 4 * 1024 * 1024

func writeToConn(conn *websocket.Conn, data []byte) error {
	_ = conn.SetWriteDeadline(time.Now().Add(writeWait))
	return conn.WriteMessage(websocket.BinaryMessage, data)
}

type Subscriber struct {
	ID      string
	Conn    *websocket.Conn
	writeMu sync.Mutex
}

func (s *Subscriber) WriteMessage(data []byte) error {
	s.writeMu.Lock()
	defer s.writeMu.Unlock()
	return writeToConn(s.Conn, data)
}

type ChannelConfig struct {
	KeepAliveDuration          time.Duration
	PublisherReconnectTimeout   time.Duration
	SubscriberReconnectTimeout time.Duration
}

func DefaultChannelConfig() ChannelConfig {
	return ChannelConfig{
		KeepAliveDuration:          30 * time.Second,
		PublisherReconnectTimeout:   30 * time.Second,
		SubscriberReconnectTimeout: 30 * time.Second,
	}
}

type Channel struct {
	PodKey string

	config ChannelConfig

	publisher          *websocket.Conn
	publisherMu        sync.RWMutex
	publisherWriteMu   sync.Mutex
	publisherReplaceMu sync.Mutex

	subscribers   map[string]*Subscriber
	subscribersMu sync.RWMutex

	lastSubscriberDisconnect time.Time
	keepAliveTimer           *time.Timer

	publisherDisconnected   bool
	publisherReconnectTimer *time.Timer

	publisherEpoch uint64
	publisherWg    sync.WaitGroup

	onAllSubscribersGone func(podKey string)
	onChannelClosed      func(podKey string)

	closed   bool
	closedMu sync.RWMutex

	logger *slog.Logger
}

func NewChannel(podKey string, keepAliveDuration time.Duration, onAllSubscribersGone func(string), onChannelClosed func(string)) *Channel {
	cfg := DefaultChannelConfig()
	cfg.KeepAliveDuration = keepAliveDuration
	return NewChannelWithConfig(podKey, cfg, onAllSubscribersGone, onChannelClosed)
}

func NewChannelWithConfig(podKey string, cfg ChannelConfig, onAllSubscribersGone func(string), onChannelClosed func(string)) *Channel {
	return &Channel{
		PodKey:               podKey,
		config:               cfg,
		subscribers:          make(map[string]*Subscriber),
		onAllSubscribersGone: onAllSubscribersGone,
		onChannelClosed:      onChannelClosed,
		logger:               slog.With("pod_key", podKey),
	}
}

// SetPublisher sets the publisher (runner) connection.
// If an old publisher connection exists, it is closed and its forwarding goroutine
// is awaited before starting a new one, eliminating concurrent goroutine races.
// Serialized via publisherReplaceMu to prevent WaitGroup races on concurrent calls.
func (c *Channel) SetPublisher(conn *websocket.Conn) {
	c.publisherReplaceMu.Lock()
	defer c.publisherReplaceMu.Unlock()

	c.publisherMu.Lock()

	c.closedMu.RLock()
	if c.closed {
		c.closedMu.RUnlock()
		c.publisherMu.Unlock()
		_ = conn.Close()
		return
	}
	c.closedMu.RUnlock()

	oldConn := c.publisher
	wasDisconnected := c.publisherDisconnected

	if oldConn == conn {
		c.publisherMu.Unlock()
		return
	}

	c.publisher = conn
	c.publisherDisconnected = false
	c.publisherEpoch++
	epoch := c.publisherEpoch

	if c.publisherReconnectTimer != nil {
		c.publisherReconnectTimer.Stop()
		c.publisherReconnectTimer = nil
	}
	c.publisherMu.Unlock()

	if oldConn != nil {
		_ = oldConn.Close()
	}

	c.publisherWg.Wait()

	if wasDisconnected {
		c.logger.Info("Publisher reconnected")
		c.Broadcast(protocol.EncodeRunnerReconnected())
	} else {
		c.logger.Info("Publisher connected")
	}

	c.publisherWg.Add(1)
	go c.forwardPublisherToSubscribers(epoch)
}

func (c *Channel) GetPublisher() *websocket.Conn {
	c.publisherMu.RLock()
	defer c.publisherMu.RUnlock()
	return c.publisher
}

func (c *Channel) IsPublisherDisconnected() bool {
	c.publisherMu.RLock()
	defer c.publisherMu.RUnlock()
	return c.publisherDisconnected
}

func (c *Channel) IsClosed() bool {
	c.closedMu.RLock()
	defer c.closedMu.RUnlock()
	return c.closed
}
