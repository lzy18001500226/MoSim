package blockstoreservice

import (
	"testing"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	blockstoreinfra "github.com/anthropics/agentsmesh/backend/internal/infra/blockstore"
	"github.com/anthropics/agentsmesh/backend/internal/testkit"
	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// TestBlockOps_TargetExclusive_DBCheck enforces the DB-level invariant
// added in migration 000115: every block_ops row has exactly one of
// target_block / target_ref set. This catches regressions in direct-SQL
// rescue scripts or future op kinds that forget to populate the right field.
func TestBlockOps_TargetExclusive_DBCheck(t *testing.T) {
	db := testkit.SetupTestDB(t)

	// Both nil → violates CHECK.
	err := db.Exec(`
		INSERT INTO block_ops
		  (workspace_id, actor_type, actor_id, op, payload, forward, inverse)
		VALUES (?, 'user', 1, 'createBlock', '{}', '{}', '{}')
	`, uuid.New()).Error
	require.Error(t, err, "both targets NULL must violate CHECK")

	// Both set → violates CHECK.
	err = db.Exec(`
		INSERT INTO block_ops
		  (workspace_id, actor_type, actor_id, op, payload, forward, inverse,
		   target_block, target_ref)
		VALUES (?, 'user', 1, 'createBlock', '{}', '{}', '{}', ?, ?)
	`, uuid.New(), uuid.New(), int64(1)).Error
	require.Error(t, err, "both targets set must violate CHECK")

	// Exactly one set → accepted.
	err = db.Exec(`
		INSERT INTO block_ops
		  (workspace_id, actor_type, actor_id, op, payload, forward, inverse, target_block)
		VALUES (?, 'user', 1, 'createBlock', '{}', '{}', '{}', ?)
	`, uuid.New(), uuid.New()).Error
	require.NoError(t, err, "single target set must pass CHECK")
}

// TestBlockOps_ContextFieldRoundTrip verifies the audit-context JSONB column
// holds a caller-supplied payload end-to-end. The current service layer
// leaves it empty; future middleware will populate it with request_id / ip /
// trace_id, so the persistence path must already be working.
func TestBlockOps_ContextFieldRoundTrip(t *testing.T) {
	db := testkit.SetupTestDB(t)

	opWSID := uuid.New()
	targetBlock := uuid.New()
	err := db.Exec(`
		INSERT INTO block_ops
		  (workspace_id, actor_type, actor_id, op, payload, forward, inverse,
		   context, target_block)
		VALUES (?, 'user', 1, 'createBlock', '{}', '{}', '{}', ?, ?)
	`, opWSID, `{"request_id":"req-42","ip":"10.0.0.1"}`, targetBlock).Error
	require.NoError(t, err)

	var gotContext string
	require.NoError(t, db.Raw(
		`SELECT context FROM block_ops WHERE workspace_id = ?`, opWSID,
	).Row().Scan(&gotContext))
	assert.Contains(t, gotContext, "req-42")
	assert.Contains(t, gotContext, "10.0.0.1")
}

// TestEnqueueAfterClose_NoInflightLeak is the B4 regression: calling
// enqueueEmbeddings after Close() must short-circuit and not add to
// embedInflight (no worker exists to Done the counter, so FlushEmbeddings
// would otherwise hang forever).
func TestEnqueueAfterClose_NoInflightLeak(t *testing.T) {
	db := testkit.SetupTestDB(t)
	repo := blockstoreinfra.NewRepository(db)
	svc := NewService(repo, nil)
	svc.Close()

	// Fabricate an op batch and enqueue — must be a no-op because the
	// worker has already exited.
	target := uuid.New()
	svc.enqueueEmbeddings([]*blockstore.BlockOp{
		{
			Op:          blockstore.OpCreateBlock,
			TargetBlock: &target,
		},
	})

	// If Add(1) leaked we'd hang here; bound the wait to catch regression
	// fast rather than stall the whole suite.
	done := make(chan struct{})
	go func() {
		svc.FlushEmbeddings()
		close(done)
	}()
	select {
	case <-done:
	case <-time.After(500 * time.Millisecond):
		t.Fatal("FlushEmbeddings hung — enqueue-after-Close leaked inflight counter")
	}
}
