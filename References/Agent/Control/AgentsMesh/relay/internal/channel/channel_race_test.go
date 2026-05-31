package channel

import (
	"bytes"
	"sync"
	"testing"
	"time"

	"github.com/gorilla/websocket"

	"github.com/anthropics/agentsmesh/relay/internal/protocol"
)

func TestChannel_SetPublisher_RapidReconnect(t *testing.T) {
	ch := NewChannelWithConfig("pod-rapid", testChannelConfig(), nil, nil)

	subServer, subClient := createWSPair(t)
	ch.AddSubscriber("s1", subServer)

	pub1Server, _ := createWSPair(t)
	ch.SetPublisher(pub1Server)

	pub2Server, pub2Client := createWSPair(t)
	ch.SetPublisher(pub2Server)

	outMsg := protocol.EncodeOutput([]byte("from-pub2"))
	if err := pub2Client.WriteMessage(websocket.BinaryMessage, outMsg); err != nil {
		t.Fatalf("write to pub2Client: %v", err)
	}

	_ = subClient.SetReadDeadline(time.Now().Add(2 * time.Second))

	for {
		_, data, err := subClient.ReadMessage()
		if err != nil {
			t.Fatalf("read from subClient: %v", err)
		}
		msg, _ := protocol.DecodeMessage(data)
		if msg != nil && msg.Type == protocol.MsgTypeRunnerReconnected {
			continue
		}
		if !bytes.Equal(data, outMsg) {
			t.Fatalf("expected output from pub2, got %v", data)
		}
		break
	}

	if ch.GetPublisher() != pub2Server {
		t.Fatal("expected publisher to be pub2Server")
	}
}

func TestChannel_SetPublisher_RapidReconnect_Multiple(t *testing.T) {
	ch := NewChannelWithConfig("pod-rapid-multi", testChannelConfig(), nil, nil)

	subServer, subClient := createWSPair(t)
	ch.AddSubscriber("s1", subServer)

	const iterations = 5
	var conns []*websocket.Conn

	for i := 0; i < iterations; i++ {
		server, _ := createWSPair(t)
		conns = append(conns, server)
		ch.SetPublisher(server)
	}

	lastConn := conns[iterations-1]
	if ch.GetPublisher() != lastConn {
		t.Fatal("expected publisher to be the last set connection")
	}

	ch.publisherMu.RLock()
	epoch := ch.publisherEpoch
	ch.publisherMu.RUnlock()

	if epoch != uint64(iterations) {
		t.Fatalf("expected epoch %d, got %d", iterations, epoch)
	}

	_ = subClient.SetReadDeadline(time.Now().Add(500 * time.Millisecond))
	for {
		_, _, err := subClient.ReadMessage()
		if err != nil {
			break
		}
	}
}

func TestChannel_Close_WaitsForGoroutine(t *testing.T) {
	ch := NewChannelWithConfig("pod-close-wait", testChannelConfig(), nil, nil)

	pubServer, _ := createWSPair(t)
	ch.SetPublisher(pubServer)

	closeDone := make(chan struct{})
	go func() {
		ch.Close()
		close(closeDone)
	}()

	select {
	case <-closeDone:
	case <-time.After(5 * time.Second):
		t.Fatal("Close() did not return within timeout")
	}

	if !ch.IsClosed() {
		t.Fatal("expected channel to be closed")
	}
}

func TestChannel_SetPublisher_EpochIncrement(t *testing.T) {
	ch := NewChannelWithConfig("pod-epoch", testChannelConfig(), nil, nil)

	var epochs []uint64

	for i := 0; i < 3; i++ {
		server, client := createWSPair(t)
		ch.SetPublisher(server)

		ch.publisherMu.RLock()
		epochs = append(epochs, ch.publisherEpoch)
		ch.publisherMu.RUnlock()

		_ = client.Close()
		waitFor(t, func() bool {
			return ch.IsPublisherDisconnected()
		}, 2*time.Second)
	}

	for i := 1; i < len(epochs); i++ {
		if epochs[i] <= epochs[i-1] {
			t.Fatalf("epoch not monotonically increasing: epochs[%d]=%d <= epochs[%d]=%d",
				i, epochs[i], i-1, epochs[i-1])
		}
	}

	newServer, _ := createWSPair(t)
	ch.SetPublisher(newServer)

	ch.publisherMu.RLock()
	currentEpoch := ch.publisherEpoch
	ch.publisherMu.RUnlock()

	ch.handlePublisherDisconnect(newServer, currentEpoch-1)
	if ch.IsPublisherDisconnected() {
		t.Fatal("stale epoch handlePublisherDisconnect should be a no-op")
	}
	if ch.GetPublisher() != newServer {
		t.Fatal("publisher should still be newServer after stale disconnect")
	}
}

func TestChannel_SetPublisher_ConcurrentAccess(t *testing.T) {
	ch := NewChannelWithConfig("pod-concurrent", testChannelConfig(), nil, nil)

	const goroutines = 4
	var wg sync.WaitGroup
	wg.Add(goroutines)

	for i := 0; i < goroutines; i++ {
		go func() {
			defer wg.Done()
			server, _ := createWSPair(t)
			ch.SetPublisher(server)
		}()
	}

	wg.Wait()

	ch.publisherMu.RLock()
	epoch := ch.publisherEpoch
	pub := ch.publisher
	ch.publisherMu.RUnlock()

	if epoch != uint64(goroutines) {
		t.Fatalf("expected epoch %d, got %d", goroutines, epoch)
	}
	if pub == nil {
		t.Fatal("expected publisher to be non-nil after concurrent SetPublisher calls")
	}
}
