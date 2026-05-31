package poddaemon

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestListenAndDial(t *testing.T) {
	listener, err := Listen()
	require.NoError(t, err)
	defer listener.Close()
	addr := listener.Addr().String()

	connCh := make(chan struct{}, 1)
	go func() {
		conn, err := Dial(addr)
		if err == nil {
			conn.Close()
		}
		connCh <- struct{}{}
	}()

	conn, err := listener.Accept()
	require.NoError(t, err)
	conn.Close()

	<-connCh
}

func TestDialNonexistentAddr(t *testing.T) {
	_, err := Dial("127.0.0.1:1")
	assert.Error(t, err)
}

func TestListenAndDialBidirectional(t *testing.T) {
	listener, err := Listen()
	require.NoError(t, err)
	defer listener.Close()
	addr := listener.Addr().String()

	serverReady := make(chan struct{})
	serverDone := make(chan string, 1)

	go func() {
		conn, err := listener.Accept()
		if err != nil {
			return
		}
		defer conn.Close()
		close(serverReady)

		buf := make([]byte, 64)
		n, err := conn.Read(buf)
		if err == nil {
			serverDone <- string(buf[:n])
		}
	}()

	clientConn, err := Dial(addr)
	require.NoError(t, err)
	defer clientConn.Close()

	<-serverReady

	_, err = clientConn.Write([]byte("hello"))
	require.NoError(t, err)

	got := <-serverDone
	assert.Equal(t, "hello", got)
}

func TestListenAssignsDifferentPorts(t *testing.T) {
	l1, err := Listen()
	require.NoError(t, err)
	defer l1.Close()

	l2, err := Listen()
	require.NoError(t, err)
	defer l2.Close()

	assert.NotEqual(t, l1.Addr().String(), l2.Addr().String())
}
