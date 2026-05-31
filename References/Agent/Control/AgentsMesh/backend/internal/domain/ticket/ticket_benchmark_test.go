package ticket

import (
	"testing"
)

// --- Benchmark Tests ---

func BenchmarkTicketIsActive(b *testing.B) {
	ticket := &Ticket{Status: TicketStatusInProgress}
	for i := 0; i < b.N; i++ {
		ticket.IsActive()
	}
}

func BenchmarkIsValidEstimate(b *testing.B) {
	for i := 0; i < b.N; i++ {
		IsValidEstimate(5)
	}
}

func BenchmarkMergeRequestIsPipelineSuccess(b *testing.B) {
	status := PipelineStatusSuccess
	mr := &MergeRequest{PipelineStatus: &status}
	for i := 0; i < b.N; i++ {
		mr.IsPipelineSuccess()
	}
}
