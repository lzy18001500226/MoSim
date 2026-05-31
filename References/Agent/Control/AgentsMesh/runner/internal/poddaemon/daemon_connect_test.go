package poddaemon

import (
	"encoding/hex"
	"encoding/json"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

const testAuthToken = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

// TestConnectDaemonMalformedAttachAck verifies connectDaemon handles
// corrupted JSON in AttachAck gracefully.
func TestConnectDaemonMalformedAttachAck(t *testing.T) {
	listener, err := Listen()
	require.NoError(t, err)
	defer listener.Close()
	addr := listener.Addr().String()

	go func() {
		conn, err := listener.Accept()
		if err != nil {
			return
		}
		defer conn.Close()

		ReadMessage(conn) // consume Attach
		WriteMessage(conn, MsgAttachAck, []byte("{broken json"))
	}()

	_, err = connectDaemon(connectOpts{Addr: addr, AuthToken: testAuthToken})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "unmarshal attach ack")
}

// TestConnectDaemonWrongMessageType verifies connectDaemon handles
// unexpected message type instead of AttachAck.
func TestConnectDaemonWrongMessageType(t *testing.T) {
	listener, err := Listen()
	require.NoError(t, err)
	defer listener.Close()
	addr := listener.Addr().String()

	go func() {
		conn, err := listener.Accept()
		if err != nil {
			return
		}
		defer conn.Close()

		ReadMessage(conn) // consume Attach
		WriteMessage(conn, MsgOutput, []byte("surprise"))
	}()

	_, err = connectDaemon(connectOpts{Addr: addr, AuthToken: testAuthToken})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "expected AttachAck")
}

// TestConnectDaemonHandshakeTimeout verifies the 5-second timeout on
// AttachAck response.
func TestConnectDaemonHandshakeTimeout(t *testing.T) {
	listener, err := Listen()
	require.NoError(t, err)
	defer listener.Close()
	addr := listener.Addr().String()

	go func() {
		conn, err := listener.Accept()
		if err != nil {
			return
		}
		defer conn.Close()

		ReadMessage(conn)
		time.Sleep(10 * time.Second)
	}()

	start := time.Now()
	_, err = connectDaemon(connectOpts{Addr: addr, AuthToken: testAuthToken})
	elapsed := time.Since(start)

	require.Error(t, err)
	assert.Contains(t, err.Error(), "read attach ack")
	assert.InDelta(t, 5.0, elapsed.Seconds(), 1.0,
		"should timeout around 5 seconds, got %v", elapsed)
}

// TestConnectDaemonDialFailure verifies connectDaemon returns clear error
// when no daemon is listening.
func TestConnectDaemonDialFailure(t *testing.T) {
	_, err := connectDaemon(connectOpts{Addr: "127.0.0.1:1", AuthToken: testAuthToken})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "dial daemon")
}

// TestConnectDaemonInvalidToken verifies connectDaemon rejects invalid hex tokens.
func TestConnectDaemonInvalidToken(t *testing.T) {
	listener, err := Listen()
	require.NoError(t, err)
	defer listener.Close()
	addr := listener.Addr().String()

	_, err = connectDaemon(connectOpts{Addr: addr, AuthToken: "not-a-hex-string!"})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "decode auth token")
}

// TestConnectDaemonSuccess verifies the full connectDaemon happy path.
func TestConnectDaemonSuccess(t *testing.T) {
	listener, err := Listen()
	require.NoError(t, err)
	defer listener.Close()
	addr := listener.Addr().String()

	// Mock daemon: accept, read Attach (with token), send AttachAck
	go func() {
		conn, err := listener.Accept()
		if err != nil {
			return
		}
		defer conn.Close()

		msgType, payload, err := ReadMessage(conn)
		if err != nil || msgType != MsgAttach {
			return
		}

		// Verify token in payload: [version][token_bytes]
		if len(payload) < 1 {
			return
		}
		tokenBytes := payload[1:]
		expectedToken, _ := hex.DecodeString(testAuthToken)
		if len(tokenBytes) != len(expectedToken) {
			return
		}

		ack := attachAckPayload{PID: 99, Cols: 80, Rows: 24, Alive: true}
		data, _ := json.Marshal(ack)
		WriteMessage(conn, MsgAttachAck, data)

		// Keep connection open for client
		time.Sleep(500 * time.Millisecond)
	}()

	d, err := connectDaemon(connectOpts{Addr: addr, AuthToken: testAuthToken})
	require.NoError(t, err)
	defer d.Close()

	assert.Equal(t, 99, d.Pid())
	cols, rows, _ := d.GetSize()
	assert.Equal(t, 80, cols)
	assert.Equal(t, 24, rows)
}
