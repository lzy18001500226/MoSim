package channel

import (
	"bytes"
	"testing"
	"time"

	"github.com/gorilla/websocket"

	"github.com/anthropics/agentsmesh/relay/internal/protocol"
)

func TestChannel_ForwardPubToSub(t *testing.T) {
	ch := NewChannelWithConfig("pod-fwd-ps", testChannelConfig(), nil, nil)

	pubServer, pubClient := createWSPair(t)
	subServer, subClient := createWSPair(t)

	ch.SetPublisher(pubServer)
	ch.AddSubscriber("s1", subServer)

	payload := []byte("terminal output data")
	outMsg := protocol.EncodeOutput(payload)
	if err := pubClient.WriteMessage(websocket.BinaryMessage, outMsg); err != nil {
		t.Fatalf("write to pubClient: %v", err)
	}

	_ = subClient.SetReadDeadline(time.Now().Add(2 * time.Second))
	_, data, err := subClient.ReadMessage()
	if err != nil {
		t.Fatalf("read from subClient: %v", err)
	}
	if !bytes.Equal(data, outMsg) {
		t.Fatalf("forwarded data mismatch: got %v, want %v", data, outMsg)
	}
}

func TestChannel_ForwardSubToPub(t *testing.T) {
	ch := NewChannelWithConfig("pod-fwd-sp", testChannelConfig(), nil, nil)

	pubServer, pubClient := createWSPair(t)
	subServer, subClient := createWSPair(t)

	ch.SetPublisher(pubServer)
	ch.AddSubscriber("s1", subServer)

	inputPayload := []byte("user input")
	inputMsg := protocol.EncodeInput(inputPayload)
	if err := subClient.WriteMessage(websocket.BinaryMessage, inputMsg); err != nil {
		t.Fatalf("write input to subClient: %v", err)
	}

	_ = pubClient.SetReadDeadline(time.Now().Add(2 * time.Second))
	_, data, err := pubClient.ReadMessage()
	if err != nil {
		t.Fatalf("read input from pubClient: %v", err)
	}
	if !bytes.Equal(data, inputMsg) {
		t.Fatalf("forwarded input mismatch: got %v, want %v", data, inputMsg)
	}
}
