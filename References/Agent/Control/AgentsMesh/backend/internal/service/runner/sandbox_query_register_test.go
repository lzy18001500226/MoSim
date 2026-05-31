package runner

import (
	"testing"
	"time"
)

func TestSandboxQueryService_RegisterQuery(t *testing.T) {
	svc := NewSandboxQueryService(nil)
	defer svc.Stop()

	requestID := "test-request-123"
	ch := svc.RegisterQuery(requestID)

	if ch == nil {
		t.Fatal("Expected non-nil channel")
	}

	// Verify query was stored
	_, ok := svc.pendingQueries.Load(requestID)
	if !ok {
		t.Error("Query should be stored in pending queries")
	}
}

func TestSandboxQueryService_RegisterQueryWithTimeout(t *testing.T) {
	svc := NewSandboxQueryService(nil)
	defer svc.Stop()

	requestID := "custom-timeout"
	ch := svc.RegisterQueryWithTimeout(requestID, 5*time.Second)

	if ch == nil {
		t.Fatal("Expected non-nil channel")
	}

	// Verify query was stored
	_, ok := svc.pendingQueries.Load(requestID)
	if !ok {
		t.Error("Query should be stored in pending queries")
	}
}
