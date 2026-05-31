package runner

import (
	"testing"
	"time"
)

func TestSandboxStatus_Fields(t *testing.T) {
	status := SandboxStatus{
		PodKey:                "test-pod",
		Exists:                true,
		CanResume:             true,
		SandboxPath:           "/path/to/sandbox",
		RepositoryURL:         "https://github.com/test/repo",
		BranchName:            "feature-branch",
		CurrentCommit:         "abc12345",
		SizeBytes:             1024,
		LastModified:          1234567890,
		HasUncommittedChanges: true,
		Error:                 "",
	}

	if status.PodKey != "test-pod" {
		t.Errorf("PodKey = %s, want test-pod", status.PodKey)
	}
	if !status.Exists {
		t.Error("Exists should be true")
	}
	if !status.CanResume {
		t.Error("CanResume should be true")
	}
	if status.SandboxPath != "/path/to/sandbox" {
		t.Errorf("SandboxPath = %s, want /path/to/sandbox", status.SandboxPath)
	}
}

func TestSandboxQueryResult_Fields(t *testing.T) {
	result := SandboxQueryResult{
		RequestID: "req-123",
		RunnerID:  42,
		Sandboxes: []*SandboxStatus{
			{PodKey: "pod-1", Exists: true},
		},
		Error: "",
	}

	if result.RequestID != "req-123" {
		t.Errorf("RequestID = %s, want req-123", result.RequestID)
	}
	if result.RunnerID != 42 {
		t.Errorf("RunnerID = %d, want 42", result.RunnerID)
	}
	if len(result.Sandboxes) != 1 {
		t.Errorf("Sandboxes len = %d, want 1", len(result.Sandboxes))
	}
}

func TestSandboxQueryResult_WithError(t *testing.T) {
	result := SandboxQueryResult{
		RequestID: "req-456",
		RunnerID:  1,
		Sandboxes: nil,
		Error:     "runner offline",
	}

	if result.Error != "runner offline" {
		t.Errorf("Error = %s, want 'runner offline'", result.Error)
	}
}

func TestSandboxQueryService_CleanupLoop(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping cleanup loop test in short mode")
	}

	svc := NewSandboxQueryService(nil)
	defer svc.Stop()

	// Register a query with a very short timeout (already expired)
	// Use RegisterQueryWithTimeout to avoid data race
	requestID := "expired-query"
	ch := svc.RegisterQueryWithTimeout(requestID, -time.Second) // Already expired

	// Wait for cleanup loop to run (it runs every 10 seconds)
	time.Sleep(11 * time.Second)

	// Check if we got a timeout error on the channel
	select {
	case result := <-ch:
		if result == nil {
			t.Error("Expected non-nil result")
		} else if result.Error != "query timeout" {
			t.Errorf("Expected 'query timeout' error, got: %s", result.Error)
		}
	default:
		t.Error("Expected cleanup loop to send timeout result")
	}

	// Verify query was removed
	_, exists := svc.pendingQueries.Load(requestID)
	if exists {
		t.Error("Query should be removed after cleanup")
	}
}
