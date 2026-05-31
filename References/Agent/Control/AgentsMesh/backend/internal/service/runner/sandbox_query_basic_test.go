package runner

import (
	"testing"
	"time"
)

func TestNewSandboxQueryService(t *testing.T) {
	svc := NewSandboxQueryService(nil)
	if svc == nil {
		t.Fatal("Expected non-nil service")
	}
	defer svc.Stop()

	if svc.done == nil {
		t.Error("done channel should be initialized")
	}
}

func TestSandboxQueryService_Stop(t *testing.T) {
	svc := NewSandboxQueryService(nil)

	// Stop should not block
	done := make(chan struct{})
	go func() {
		svc.Stop()
		close(done)
	}()

	select {
	case <-done:
		// Success
	case <-time.After(time.Second):
		t.Error("Stop should not block")
	}
}

func TestSandboxQueryTimeout_Constant(t *testing.T) {
	if SandboxQueryTimeout != 30*time.Second {
		t.Errorf("SandboxQueryTimeout = %v, want 30s", SandboxQueryTimeout)
	}
}

func TestSandboxQueryService_NewWithConnectionManager(t *testing.T) {
	// Test creating service with nil connection manager
	svc := NewSandboxQueryService(nil)
	defer svc.Stop()

	if svc == nil {
		t.Fatal("Expected non-nil service")
	}
}
