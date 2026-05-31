package channel

import (
	"bytes"
	"testing"
	"time"

	"github.com/gorilla/websocket"

	"github.com/anthropics/agentsmesh/relay/internal/protocol"
)

func TestChannel_AddSubscriber_PubDisconnected(t *testing.T) {
	ch := NewChannelWithConfig("pod-sub-disc", testChannelConfig(), nil, nil)

	pubServer, pubClient := createWSPair(t)
	ch.SetPublisher(pubServer)

	_ = pubClient.Close()

	waitFor(t, func() bool {
		return ch.IsPublisherDisconnected()
	}, 2*time.Second)

	subServer, subClient := createWSPair(t)
	ch.AddSubscriber("s1", subServer)

	_ = subClient.SetReadDeadline(time.Now().Add(2 * time.Second))
	_, data, err := subClient.ReadMessage()
	if err != nil {
		t.Fatalf("failed to read RunnerDisconnected: %v", err)
	}
	msg, err := protocol.DecodeMessage(data)
	if err != nil {
		t.Fatalf("decode RunnerDisconnected: %v", err)
	}
	if msg.Type != protocol.MsgTypeRunnerDisconnected {
		t.Fatalf("expected MsgTypeRunnerDisconnected (0x%02x), got 0x%02x", protocol.MsgTypeRunnerDisconnected, msg.Type)
	}
}

func TestChannel_ForwardSubToPub_EmptyMessage(t *testing.T) {
	ch := NewChannelWithConfig("pod-inv-msg", testChannelConfig(), nil, nil)

	pubServer, pubClient := createWSPair(t)
	subServer, subClient := createWSPair(t)

	ch.SetPublisher(pubServer)
	ch.AddSubscriber("s1", subServer)

	emptyMsg := []byte{}
	if err := subClient.WriteMessage(websocket.BinaryMessage, emptyMsg); err != nil {
		t.Fatalf("write empty message: %v", err)
	}

	_ = pubClient.SetReadDeadline(time.Now().Add(2 * time.Second))
	_, data, err := pubClient.ReadMessage()
	if err != nil {
		t.Fatalf("read from pubClient: %v", err)
	}
	if !bytes.Equal(data, emptyMsg) {
		t.Fatalf("expected empty message forwarded, got %v", data)
	}
}

func TestChannel_ForwardSubToPub_PublisherWriteError(t *testing.T) {
	ch := NewChannelWithConfig("pod-pub-werr", testChannelConfig(), nil, nil)

	pubServer, pubClient := createWSPair(t)
	subServer, subClient := createWSPair(t)

	ch.SetPublisher(pubServer)
	ch.AddSubscriber("s1", subServer)

	_ = pubClient.Close()

	waitFor(t, func() bool {
		return ch.IsPublisherDisconnected()
	}, 2*time.Second)

	brokenPubServer, brokenPubClient := createWSPair(t)
	_ = brokenPubServer.Close()
	_ = brokenPubClient.Close()

	ch.publisherMu.Lock()
	ch.publisher = brokenPubServer
	ch.publisherDisconnected = false
	ch.publisherMu.Unlock()

	inputMsg := protocol.EncodeInput([]byte("will-fail-to-forward"))
	if err := subClient.WriteMessage(websocket.BinaryMessage, inputMsg); err != nil {
		t.Fatalf("write input: %v", err)
	}

	time.Sleep(200 * time.Millisecond)
}

func TestChannel_AddSubscriber_PubDisconnectedWriteError(t *testing.T) {
	ch := NewChannelWithConfig("pod-disc-err", testChannelConfig(), nil, nil)

	pubServer, pubClient := createWSPair(t)
	ch.SetPublisher(pubServer)

	_ = pubClient.Close()
	waitFor(t, func() bool {
		return ch.IsPublisherDisconnected()
	}, 2*time.Second)

	subServer, _ := createWSPair(t)
	_ = subServer.Close()

	ch.AddSubscriber("s1", subServer)

	time.Sleep(100 * time.Millisecond)
}

func TestChannel_ForwardPubToSub_NilPublisher(t *testing.T) {
	ch := NewChannelWithConfig("pod-nil-pub", testChannelConfig(), nil, nil)

	ch.publisherWg.Add(1)
	done := make(chan struct{})
	go func() {
		ch.forwardPublisherToSubscribers(0)
		close(done)
	}()

	select {
	case <-done:
	case <-time.After(2 * time.Second):
		t.Fatal("forwardPublisherToSubscribers did not exit when publisher is nil")
	}
}
