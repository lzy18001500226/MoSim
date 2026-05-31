package ticket

import (
	"context"
	"fmt"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/ticket"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// Note: Uses setupTestDB from service_test.go

func TestGetBoard(t *testing.T) {
	ctx := context.Background()
	db := setupTestDB(t)
	service := newTestService(db)

	// Create tickets in different statuses
	statuses := []string{
		ticket.TicketStatusBacklog,
		ticket.TicketStatusTodo,
		ticket.TicketStatusInProgress,
		ticket.TicketStatusInReview,
		ticket.TicketStatusDone,
	}

	for i, status := range statuses {
		for j := 0; j < 2; j++ {
			tkt := &ticket.Ticket{
				OrganizationID: 1,
				Slug:     fmt.Sprintf("BRD-%d", i*10+j+1),
				Title:          "Ticket " + status,
				Status:         status,
				Priority:       ticket.TicketPriorityMedium,
			}
			db.Create(tkt)
		}
	}

	t.Run("returns board with all columns", func(t *testing.T) {
		filter := &ticket.TicketListFilter{
			OrganizationID: 1,
			Limit:          50,
			Offset:         0,
		}
		board, err := service.GetBoard(ctx, filter)
		require.NoError(t, err)
		assert.NotNil(t, board)
		assert.Len(t, board.Columns, 5)

		// Verify each column
		for i, col := range board.Columns {
			assert.Equal(t, statuses[i], col.Status)
			assert.Equal(t, 2, col.Count)
			assert.Len(t, col.Tickets, 2)
		}
	})

	t.Run("returns empty columns for new organization", func(t *testing.T) {
		filter := &ticket.TicketListFilter{
			OrganizationID: 999,
			Limit:          50,
			Offset:         0,
		}
		board, err := service.GetBoard(ctx, filter)
		require.NoError(t, err)
		assert.NotNil(t, board)
		assert.Len(t, board.Columns, 5)

		for _, col := range board.Columns {
			assert.Equal(t, 0, col.Count)
			assert.Empty(t, col.Tickets)
		}
	})
}

func TestGetSubTicketCounts(t *testing.T) {
	ctx := context.Background()
	db := setupTestDB(t)
	service := newTestService(db)

	// Create parent tickets
	parent1 := &ticket.Ticket{
		OrganizationID: 1,
		Slug:     "CNT-1",
		Title:          "Parent 1",
		Status:         ticket.TicketStatusInProgress,
		Priority:       ticket.TicketPriorityMedium,
	}
	parent2 := &ticket.Ticket{
		OrganizationID: 1,
		Slug:     "CNT-2",
		Title:          "Parent 2",
		Status:         ticket.TicketStatusTodo,
		Priority:       ticket.TicketPriorityMedium,
	}
	db.Create(parent1)
	db.Create(parent2)

	// Create child tickets for parent1
	children := []struct {
		parentID int64
		status   string
	}{
		{parent1.ID, ticket.TicketStatusTodo},
		{parent1.ID, ticket.TicketStatusTodo},
		{parent1.ID, ticket.TicketStatusInProgress},
		{parent1.ID, ticket.TicketStatusDone},
		{parent2.ID, ticket.TicketStatusBacklog},
	}

	for i, c := range children {
		child := &ticket.Ticket{
			OrganizationID: 1,
			ParentTicketID: &c.parentID,
			Slug:     fmt.Sprintf("CNT-%d", 100+i),
			Title:          "Child",
			Status:         c.status,
			Priority:       ticket.TicketPriorityMedium,
		}
		db.Create(child)
	}

	t.Run("returns sub-ticket counts by status", func(t *testing.T) {
		counts, err := service.GetSubTicketCounts(ctx, []int64{parent1.ID, parent2.ID})
		require.NoError(t, err)
		assert.NotNil(t, counts)

		// Check parent1 counts
		assert.Equal(t, int64(2), counts[parent1.ID][ticket.TicketStatusTodo])
		assert.Equal(t, int64(1), counts[parent1.ID][ticket.TicketStatusInProgress])
		assert.Equal(t, int64(1), counts[parent1.ID][ticket.TicketStatusDone])

		// Check parent2 counts
		assert.Equal(t, int64(1), counts[parent2.ID][ticket.TicketStatusBacklog])
	})

	t.Run("returns empty map for non-existent parents", func(t *testing.T) {
		counts, err := service.GetSubTicketCounts(ctx, []int64{9999})
		require.NoError(t, err)
		assert.Empty(t, counts)
	})
}

// Note: TestGetActiveTickets is defined in service_extended_test.go

func TestGetBoard_PriorityCounts(t *testing.T) {
	ctx := context.Background()
	db := setupTestDB(t)
	service := newTestService(db)

	// Create tickets with different priorities
	priorities := []struct {
		priority string
		count    int
	}{
		{ticket.TicketPriorityHigh, 3},
		{ticket.TicketPriorityMedium, 2},
		{ticket.TicketPriorityLow, 1},
	}

	idx := 0
	for _, p := range priorities {
		for j := 0; j < p.count; j++ {
			db.Create(&ticket.Ticket{
				OrganizationID: 1,
				Slug:           fmt.Sprintf("PRI-%d", idx),
				Title:          "Ticket",
				Status:         ticket.TicketStatusBacklog,
				Priority:       p.priority,
			})
			idx++
		}
	}

	board, err := service.GetBoard(ctx, &ticket.TicketListFilter{
		OrganizationID: 1, Limit: 50,
	})
	require.NoError(t, err)
	require.NotNil(t, board.PriorityCounts)

	assert.Equal(t, int64(3), board.PriorityCounts[ticket.TicketPriorityHigh])
	assert.Equal(t, int64(2), board.PriorityCounts[ticket.TicketPriorityMedium])
	assert.Equal(t, int64(1), board.PriorityCounts[ticket.TicketPriorityLow])
	assert.Equal(t, int64(0), board.PriorityCounts[ticket.TicketPriorityNone])
}

func TestGetBoard_FilterNotMutated(t *testing.T) {
	ctx := context.Background()
	db := setupTestDB(t)
	service := newTestService(db)

	filter := &ticket.TicketListFilter{
		OrganizationID: 1,
		Priority:       ticket.TicketPriorityHigh,
		Limit:          50,
	}
	originalStatus := filter.Status // should be ""

	_, err := service.GetBoard(ctx, filter)
	require.NoError(t, err)

	// Filter should not be mutated by GetBoard's internal loop
	assert.Equal(t, originalStatus, filter.Status, "GetBoard must not mutate the caller's filter.Status")
	assert.Equal(t, ticket.TicketPriorityHigh, filter.Priority)
}

func TestGetPriorityCounts(t *testing.T) {
	ctx := context.Background()
	db := setupTestDB(t)
	service := newTestService(db)

	tickets := []*ticket.Ticket{
		{OrganizationID: 1, Slug: "PC-1", Title: "T", Status: ticket.TicketStatusBacklog, Priority: ticket.TicketPriorityHigh},
		{OrganizationID: 1, Slug: "PC-2", Title: "T", Status: ticket.TicketStatusTodo, Priority: ticket.TicketPriorityHigh},
		{OrganizationID: 1, Slug: "PC-3", Title: "T", Status: ticket.TicketStatusDone, Priority: ticket.TicketPriorityLow},
		{OrganizationID: 2, Slug: "PC-4", Title: "T", Status: ticket.TicketStatusBacklog, Priority: ticket.TicketPriorityUrgent},
	}
	for _, tk := range tickets {
		db.Create(tk)
	}

	t.Run("counts for org 1", func(t *testing.T) {
		counts, err := service.GetTicketStats(ctx, 1, nil) // using stats as proxy
		require.NoError(t, err)
		assert.NotNil(t, counts)

		// Direct repo test
		board, err := service.GetBoard(ctx, &ticket.TicketListFilter{OrganizationID: 1, Limit: 50})
		require.NoError(t, err)
		assert.Equal(t, int64(2), board.PriorityCounts[ticket.TicketPriorityHigh])
		assert.Equal(t, int64(1), board.PriorityCounts[ticket.TicketPriorityLow])
		assert.Equal(t, int64(0), board.PriorityCounts[ticket.TicketPriorityUrgent]) // org 2's ticket
	})

	t.Run("isolates by organization", func(t *testing.T) {
		board, err := service.GetBoard(ctx, &ticket.TicketListFilter{OrganizationID: 2, Limit: 50})
		require.NoError(t, err)
		assert.Equal(t, int64(1), board.PriorityCounts[ticket.TicketPriorityUrgent])
		assert.Equal(t, int64(0), board.PriorityCounts[ticket.TicketPriorityHigh])
	})
}

func TestGetPriorityCounts_WithRepoID(t *testing.T) {
	ctx := context.Background()
	db := setupTestDB(t)
	service := newTestService(db)

	repo1 := int64(100)
	repo2 := int64(200)
	tks := []*ticket.Ticket{
		{OrganizationID: 1, RepositoryID: &repo1, Slug: "R-1", Title: "T", Status: ticket.TicketStatusBacklog, Priority: ticket.TicketPriorityHigh},
		{OrganizationID: 1, RepositoryID: &repo1, Slug: "R-2", Title: "T", Status: ticket.TicketStatusTodo, Priority: ticket.TicketPriorityHigh},
		{OrganizationID: 1, RepositoryID: &repo2, Slug: "R-3", Title: "T", Status: ticket.TicketStatusBacklog, Priority: ticket.TicketPriorityLow},
	}
	for _, tk := range tks {
		db.Create(tk)
	}

	t.Run("filters by repoID", func(t *testing.T) {
		board, err := service.GetBoard(ctx, &ticket.TicketListFilter{OrganizationID: 1, RepositoryID: &repo1, Limit: 50})
		require.NoError(t, err)
		assert.Equal(t, int64(2), board.PriorityCounts[ticket.TicketPriorityHigh])
		assert.Equal(t, int64(0), board.PriorityCounts[ticket.TicketPriorityLow]) // repo2 only
	})

	t.Run("nil repoID returns all", func(t *testing.T) {
		board, err := service.GetBoard(ctx, &ticket.TicketListFilter{OrganizationID: 1, Limit: 50})
		require.NoError(t, err)
		assert.Equal(t, int64(2), board.PriorityCounts[ticket.TicketPriorityHigh])
		assert.Equal(t, int64(1), board.PriorityCounts[ticket.TicketPriorityLow])
	})
}
