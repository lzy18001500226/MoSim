package ticket

import (
	"testing"
)

// --- Test Assignee ---

func TestAssigneeTableName(t *testing.T) {
	a := Assignee{}
	if a.TableName() != "ticket_assignees" {
		t.Errorf("expected 'ticket_assignees', got %s", a.TableName())
	}
}

func TestAssigneeStruct(t *testing.T) {
	a := Assignee{TicketID: 1, UserID: 100}
	if a.TicketID != 1 {
		t.Errorf("expected TicketID 1, got %d", a.TicketID)
	}
	if a.UserID != 100 {
		t.Errorf("expected UserID 100, got %d", a.UserID)
	}
}

// --- Test Label ---

func TestLabelTableName(t *testing.T) {
	l := Label{}
	if l.TableName() != "labels" {
		t.Errorf("expected 'labels', got %s", l.TableName())
	}
}

func TestLabelStruct(t *testing.T) {
	repoID := int64(10)
	l := Label{
		ID:             1,
		OrganizationID: 100,
		RepositoryID:   &repoID,
		Name:           "bug",
		Color:          "#FF0000",
	}

	if l.Name != "bug" {
		t.Errorf("expected Name 'bug', got %s", l.Name)
	}
	if l.Color != "#FF0000" {
		t.Errorf("expected Color '#FF0000', got %s", l.Color)
	}
}

// --- Test TicketLabel ---

func TestTicketLabelTableName(t *testing.T) {
	tl := TicketLabel{}
	if tl.TableName() != "ticket_labels" {
		t.Errorf("expected 'ticket_labels', got %s", tl.TableName())
	}
}
