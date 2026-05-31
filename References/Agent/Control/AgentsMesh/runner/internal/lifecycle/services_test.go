package lifecycle

import (
	"context"
	"fmt"
	"sync/atomic"
	"testing"
	"time"
)

// mockConnection implements ConnectionStarter for testing.
type mockConnection struct {
	started atomic.Bool
	stopped atomic.Bool
}

func (m *mockConnection) Start() { m.started.Store(true) }
func (m *mockConnection) Stop()  { m.stopped.Store(true) }

// mockHTTPServer implements HTTPServerLike for testing.
type mockHTTPServer struct {
	started  atomic.Bool
	stopped  atomic.Bool
	startErr error
}

func (m *mockHTTPServer) Start() error {
	m.started.Store(true)
	return m.startErr
}

func (m *mockHTTPServer) Stop() error {
	m.stopped.Store(true)
	return nil
}

// mockMonitor implements MonitorStartStopper for testing.
type mockMonitor struct {
	started atomic.Bool
	stopped atomic.Bool
}

func (m *mockMonitor) Start() { m.started.Store(true) }
func (m *mockMonitor) Stop()  { m.stopped.Store(true) }

func TestConnectionService_StartsAndStops(t *testing.T) {
	conn := &mockConnection{}
	svc := &ConnectionService{Conn: conn}

	ctx, cancel := context.WithCancel(context.Background())

	done := make(chan error, 1)
	go func() {
		done <- svc.Serve(ctx)
	}()

	// Wait for Start to be called
	deadline := time.After(2 * time.Second)
	for !conn.started.Load() {
		select {
		case <-deadline:
			t.Fatal("timeout waiting for Start()")
		default:
			time.Sleep(10 * time.Millisecond)
		}
	}

	// Cancel context to trigger shutdown
	cancel()

	select {
	case err := <-done:
		if err != context.Canceled {
			t.Errorf("expected context.Canceled, got %v", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("timeout waiting for Serve to return")
	}

	if !conn.stopped.Load() {
		t.Error("expected Stop() to be called")
	}
}

func TestMCPServerService_StartsAndStops(t *testing.T) {
	server := &mockHTTPServer{}
	svc := &MCPServerService{Server: server}

	ctx, cancel := context.WithCancel(context.Background())

	done := make(chan error, 1)
	go func() {
		done <- svc.Serve(ctx)
	}()

	// Wait for Start
	deadline := time.After(2 * time.Second)
	for !server.started.Load() {
		select {
		case <-deadline:
			t.Fatal("timeout waiting for Start()")
		default:
			time.Sleep(10 * time.Millisecond)
		}
	}

	cancel()

	select {
	case <-done:
	case <-time.After(2 * time.Second):
		t.Fatal("timeout")
	}

	if !server.stopped.Load() {
		t.Error("expected Stop() to be called")
	}
}

func TestMonitorService_StartsAndStops(t *testing.T) {
	mon := &mockMonitor{}
	svc := &MonitorService{Monitor: mon}

	ctx, cancel := context.WithCancel(context.Background())

	done := make(chan error, 1)
	go func() {
		done <- svc.Serve(ctx)
	}()

	// Wait for Start
	deadline := time.After(2 * time.Second)
	for !mon.started.Load() {
		select {
		case <-deadline:
			t.Fatal("timeout waiting for Start()")
		default:
			time.Sleep(10 * time.Millisecond)
		}
	}

	cancel()

	select {
	case <-done:
	case <-time.After(2 * time.Second):
		t.Fatal("timeout")
	}

	if !mon.stopped.Load() {
		t.Error("expected Stop() to be called")
	}
}

func TestConsoleService_StartsAndStops(t *testing.T) {
	server := &mockHTTPServer{}
	svc := &ConsoleService{Server: server}

	ctx, cancel := context.WithCancel(context.Background())

	done := make(chan error, 1)
	go func() {
		done <- svc.Serve(ctx)
	}()

	// Wait for Start
	deadline := time.After(2 * time.Second)
	for !server.started.Load() {
		select {
		case <-deadline:
			t.Fatal("timeout waiting for Start()")
		default:
			time.Sleep(10 * time.Millisecond)
		}
	}

	cancel()

	select {
	case <-done:
	case <-time.After(2 * time.Second):
		t.Fatal("timeout")
	}

	if !server.stopped.Load() {
		t.Error("expected Stop() to be called")
	}
}

func TestConnectionService_String(t *testing.T) {
	svc := &ConnectionService{}
	if svc.String() != "ConnectionService" {
		t.Errorf("expected 'ConnectionService', got %q", svc.String())
	}
}

func TestMCPServerService_String(t *testing.T) {
	svc := &MCPServerService{}
	if svc.String() != "MCPServerService" {
		t.Errorf("expected 'MCPServerService', got %q", svc.String())
	}
}

func TestMonitorService_String(t *testing.T) {
	svc := &MonitorService{}
	if svc.String() != "MonitorService" {
		t.Errorf("expected 'MonitorService', got %q", svc.String())
	}
}

func TestConsoleService_String(t *testing.T) {
	svc := &ConsoleService{}
	if svc.String() != "ConsoleService" {
		t.Errorf("expected 'ConsoleService', got %q", svc.String())
	}
}

func TestMCPServerService_StartError(t *testing.T) {
	server := &mockHTTPServer{startErr: fmt.Errorf("bind address in use")}
	svc := &MCPServerService{Server: server}

	ctx := context.Background()
	err := svc.Serve(ctx)
	if err == nil {
		t.Fatal("expected error from Start()")
	}
	if err.Error() != "bind address in use" {
		t.Errorf("expected 'bind address in use', got %q", err.Error())
	}
	// Stop should NOT be called when Start fails
	if server.stopped.Load() {
		t.Error("Stop() should not be called when Start() fails")
	}
}

func TestConsoleService_StartError(t *testing.T) {
	server := &mockHTTPServer{startErr: fmt.Errorf("port unavailable")}
	svc := &ConsoleService{Server: server}

	ctx := context.Background()
	err := svc.Serve(ctx)
	if err == nil {
		t.Fatal("expected error from Start()")
	}
	if err.Error() != "port unavailable" {
		t.Errorf("expected 'port unavailable', got %q", err.Error())
	}
	if server.stopped.Load() {
		t.Error("Stop() should not be called when Start() fails")
	}
}
