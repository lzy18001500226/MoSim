package poddaemon

import (
	"bytes"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"log/slog"
	"net"
	"sync"
	"time"
)

// attachAckPayload is the JSON payload for MsgAttachAck.
type attachAckPayload struct {
	PID   int  `json:"pid"`
	Cols  int  `json:"cols"`
	Rows  int  `json:"rows"`
	Alive bool `json:"alive"`
}

// protocolVersion is the current attach protocol version.
// Version 2 adds token-based authentication for TCP loopback security.
const protocolVersion = 2

// daemonPTY implements ptyProcess by communicating with a daemon over IPC.
// Close sends Detach but does NOT kill the daemon process.
type daemonPTY struct {
	conn net.Conn
	pid  int
	cols int
	rows int
	log  *slog.Logger

	// sizeMu protects cols/rows from concurrent Resize/GetSize access.
	sizeMu sync.RWMutex

	// Write serialization - only one goroutine may write at a time.
	writeMu sync.Mutex

	// Output channel from recvLoop (closed when recvLoop exits).
	// Exit code is delivered via exitCh, consumed only by Wait().
	outputCh chan []byte
	exitCh   chan int

	// Read buffering with deadline support
	readBuf    bytes.Buffer
	readMu     sync.Mutex
	deadlineMu sync.Mutex
	deadline   time.Time

	closeOnce sync.Once
	closedCh  chan struct{}
}

// connectOpts holds the parameters for connecting to a daemon.
type connectOpts struct {
	Addr      string // TCP loopback address (e.g. "127.0.0.1:12345")
	AuthToken string // hex-encoded auth token
}

// connectDaemon dials the IPC address, performs the Attach handshake
// with token authentication, and returns a ready daemonPTY.
func connectDaemon(opts connectOpts) (*daemonPTY, error) {
	conn, err := Dial(opts.Addr)
	if err != nil {
		return nil, fmt.Errorf("dial daemon: %w", err)
	}

	// Build Attach payload: [version uint8][token bytes]
	tokenBytes, err := hex.DecodeString(opts.AuthToken)
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("decode auth token: %w", err)
	}
	attachPayload := make([]byte, 1+len(tokenBytes))
	attachPayload[0] = protocolVersion
	copy(attachPayload[1:], tokenBytes)

	// Send Attach message
	if err := WriteMessage(conn, MsgAttach, attachPayload); err != nil {
		conn.Close()
		return nil, fmt.Errorf("send attach: %w", err)
	}

	// Wait for AttachAck (with timeout)
	conn.SetReadDeadline(time.Now().Add(5 * time.Second))
	msgType, payload, err := ReadMessage(conn)
	conn.SetReadDeadline(time.Time{}) // clear deadline
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("read attach ack: %w", err)
	}
	if msgType != MsgAttachAck {
		conn.Close()
		return nil, fmt.Errorf("expected AttachAck (0x%02x), got 0x%02x", MsgAttachAck, msgType)
	}

	var ack attachAckPayload
	if err := json.Unmarshal(payload, &ack); err != nil {
		conn.Close()
		return nil, fmt.Errorf("unmarshal attach ack: %w", err)
	}

	return newDaemonPTY(conn, ack.PID, ack.Cols, ack.Rows), nil
}

// newDaemonPTY creates a daemonPTY after a successful handshake.
func newDaemonPTY(conn net.Conn, pid, cols, rows int) *daemonPTY {
	d := &daemonPTY{
		conn:     conn,
		pid:      pid,
		cols:     cols,
		rows:     rows,
		log:      slog.Default().With("component", "daemon-pty", "pid", pid),
		outputCh: make(chan []byte, 64),
		exitCh:   make(chan int, 1),
		closedCh: make(chan struct{}),
	}
	go d.recvLoop()
	return d
}
