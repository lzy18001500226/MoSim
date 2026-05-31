package ticket

import (
	"testing"
	"time"
)

// --- Test Relation ---

func TestRelationTypeConstants(t *testing.T) {
	if RelationTypeBlocks != "blocks" {
		t.Errorf("expected 'blocks', got %s", RelationTypeBlocks)
	}
	if RelationTypeBlockedBy != "blocked_by" {
		t.Errorf("expected 'blocked_by', got %s", RelationTypeBlockedBy)
	}
	if RelationTypeRelates != "relates_to" {
		t.Errorf("expected 'relates_to', got %s", RelationTypeRelates)
	}
	if RelationTypeDuplicate != "duplicates" {
		t.Errorf("expected 'duplicates', got %s", RelationTypeDuplicate)
	}
}

func TestRelationTableName(t *testing.T) {
	r := Relation{}
	if r.TableName() != "ticket_relations" {
		t.Errorf("expected 'ticket_relations', got %s", r.TableName())
	}
}

// --- Test Commit ---

func TestCommitTableName(t *testing.T) {
	c := Commit{}
	if c.TableName() != "ticket_commits" {
		t.Errorf("expected 'ticket_commits', got %s", c.TableName())
	}
}

func TestCommitStruct(t *testing.T) {
	now := time.Now()
	url := "https://github.com/org/repo/commit/abc123"
	author := "Test User"
	email := "test@example.com"

	c := Commit{
		ID:             1,
		OrganizationID: 100,
		TicketID:       10,
		RepositoryID:   5,
		CommitSHA:      "abc123def456",
		CommitMessage:  "Fix bug",
		CommitURL:      &url,
		AuthorName:     &author,
		AuthorEmail:    &email,
		CommittedAt:    &now,
		CreatedAt:      now,
	}

	if c.CommitSHA != "abc123def456" {
		t.Errorf("expected CommitSHA 'abc123def456', got %s", c.CommitSHA)
	}
	if *c.AuthorName != "Test User" {
		t.Errorf("expected AuthorName 'Test User', got %s", *c.AuthorName)
	}
}

// --- Test Board ---

func TestBoardColumnStruct(t *testing.T) {
	col := BoardColumn{
		Status:  TicketStatusInProgress,
		Count:   5,
		Tickets: []Ticket{{ID: 1}, {ID: 2}},
	}

	if col.Status != TicketStatusInProgress {
		t.Errorf("expected Status 'in_progress', got %s", col.Status)
	}
	if col.Count != 5 {
		t.Errorf("expected Count 5, got %d", col.Count)
	}
	if len(col.Tickets) != 2 {
		t.Errorf("expected 2 tickets, got %d", len(col.Tickets))
	}
}

func TestBoardStruct(t *testing.T) {
	board := Board{
		Columns: []BoardColumn{
			{Status: TicketStatusBacklog, Count: 3},
			{Status: TicketStatusInProgress, Count: 2},
		},
	}

	if len(board.Columns) != 2 {
		t.Errorf("expected 2 columns, got %d", len(board.Columns))
	}
}
