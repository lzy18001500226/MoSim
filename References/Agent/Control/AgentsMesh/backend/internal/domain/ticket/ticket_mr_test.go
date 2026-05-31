package ticket

import (
	"testing"
)

// --- Test MR Constants ---

func TestMRStateConstants(t *testing.T) {
	if MRStateOpened != "opened" {
		t.Errorf("expected 'opened', got %s", MRStateOpened)
	}
	if MRStateMerged != "merged" {
		t.Errorf("expected 'merged', got %s", MRStateMerged)
	}
	if MRStateClosed != "closed" {
		t.Errorf("expected 'closed', got %s", MRStateClosed)
	}
}

func TestPipelineStatusConstants(t *testing.T) {
	statuses := []string{
		PipelineStatusPending, PipelineStatusRunning, PipelineStatusSuccess,
		PipelineStatusFailed, PipelineStatusCanceled, PipelineStatusSkipped, PipelineStatusManual,
	}
	expected := []string{"pending", "running", "success", "failed", "canceled", "skipped", "manual"}

	for i, s := range statuses {
		if s != expected[i] {
			t.Errorf("expected '%s', got '%s'", expected[i], s)
		}
	}
}

// --- Test MergeRequest ---

func TestMergeRequestTableName(t *testing.T) {
	mr := MergeRequest{}
	if mr.TableName() != "ticket_merge_requests" {
		t.Errorf("expected 'ticket_merge_requests', got %s", mr.TableName())
	}
}

func TestMergeRequestIsMerged(t *testing.T) {
	tests := []struct {
		state    string
		expected bool
	}{
		{MRStateMerged, true},
		{MRStateOpened, false},
		{MRStateClosed, false},
	}

	for _, tt := range tests {
		mr := &MergeRequest{State: tt.state}
		if mr.IsMerged() != tt.expected {
			t.Errorf("state %s: expected IsMerged() = %v", tt.state, tt.expected)
		}
	}
}

func TestMergeRequestIsOpen(t *testing.T) {
	tests := []struct {
		state    string
		expected bool
	}{
		{MRStateOpened, true},
		{MRStateMerged, false},
		{MRStateClosed, false},
	}

	for _, tt := range tests {
		mr := &MergeRequest{State: tt.state}
		if mr.IsOpen() != tt.expected {
			t.Errorf("state %s: expected IsOpen() = %v", tt.state, tt.expected)
		}
	}
}

func TestMergeRequestHasPipeline(t *testing.T) {
	status := PipelineStatusRunning
	mrWithPipeline := &MergeRequest{PipelineStatus: &status}
	if !mrWithPipeline.HasPipeline() {
		t.Error("expected HasPipeline() = true")
	}

	mrWithoutPipeline := &MergeRequest{}
	if mrWithoutPipeline.HasPipeline() {
		t.Error("expected HasPipeline() = false")
	}
}

func TestMergeRequestIsPipelineSuccess(t *testing.T) {
	success := PipelineStatusSuccess
	failed := PipelineStatusFailed

	tests := []struct {
		name     string
		status   *string
		expected bool
	}{
		{"success", &success, true},
		{"failed", &failed, false},
		{"nil", nil, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			mr := &MergeRequest{PipelineStatus: tt.status}
			if mr.IsPipelineSuccess() != tt.expected {
				t.Errorf("expected IsPipelineSuccess() = %v", tt.expected)
			}
		})
	}
}
