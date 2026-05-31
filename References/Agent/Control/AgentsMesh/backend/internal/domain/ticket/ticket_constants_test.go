package ticket

import (
	"testing"
)

// --- Test Constants ---

func TestTicketStatusConstants(t *testing.T) {
	if TicketStatusBacklog != "backlog" {
		t.Errorf("expected 'backlog', got %s", TicketStatusBacklog)
	}
	if TicketStatusTodo != "todo" {
		t.Errorf("expected 'todo', got %s", TicketStatusTodo)
	}
	if TicketStatusInProgress != "in_progress" {
		t.Errorf("expected 'in_progress', got %s", TicketStatusInProgress)
	}
	if TicketStatusInReview != "in_review" {
		t.Errorf("expected 'in_review', got %s", TicketStatusInReview)
	}
	if TicketStatusDone != "done" {
		t.Errorf("expected 'done', got %s", TicketStatusDone)
	}
}

func TestTicketPriorityConstants(t *testing.T) {
	priorities := []string{TicketPriorityNone, TicketPriorityLow, TicketPriorityMedium, TicketPriorityHigh, TicketPriorityUrgent}
	expected := []string{"none", "low", "medium", "high", "urgent"}

	for i, p := range priorities {
		if p != expected[i] {
			t.Errorf("expected '%s', got '%s'", expected[i], p)
		}
	}
}

func TestTicketSeverityConstants(t *testing.T) {
	severities := []string{TicketSeverityCritical, TicketSeverityMajor, TicketSeverityMinor, TicketSeverityTrivial}
	expected := []string{"critical", "major", "minor", "trivial"}

	for i, s := range severities {
		if s != expected[i] {
			t.Errorf("expected '%s', got '%s'", expected[i], s)
		}
	}
}

func TestValidEstimates(t *testing.T) {
	expected := []int{1, 2, 3, 5, 8, 13, 21}
	if len(ValidEstimates) != len(expected) {
		t.Errorf("expected %d estimates, got %d", len(expected), len(ValidEstimates))
	}
	for i, v := range expected {
		if ValidEstimates[i] != v {
			t.Errorf("expected estimate[%d] = %d, got %d", i, v, ValidEstimates[i])
		}
	}
}

func TestIsValidEstimate(t *testing.T) {
	validEstimates := []int{1, 2, 3, 5, 8, 13, 21}
	for _, v := range validEstimates {
		if !IsValidEstimate(v) {
			t.Errorf("expected %d to be valid", v)
		}
	}

	invalidEstimates := []int{0, 4, 6, 7, 10, 100}
	for _, v := range invalidEstimates {
		if IsValidEstimate(v) {
			t.Errorf("expected %d to be invalid", v)
		}
	}
}
