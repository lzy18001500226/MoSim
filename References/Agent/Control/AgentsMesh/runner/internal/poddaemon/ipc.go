package poddaemon

import "net"

// Listen creates a TCP loopback listener on an OS-assigned port.
// The actual address can be retrieved via listener.Addr().String().
//
// TCP loopback does not provide filesystem-based access control like Unix
// sockets; security relies on a per-session auth token validated during the
// MsgAttach handshake (see daemon_io.go handleClient).
func Listen() (net.Listener, error) {
	return net.Listen("tcp", "127.0.0.1:0")
}

// Dial connects to a daemon at the given TCP loopback address (e.g. "127.0.0.1:12345").
func Dial(addr string) (net.Conn, error) {
	return net.Dial("tcp", addr)
}
