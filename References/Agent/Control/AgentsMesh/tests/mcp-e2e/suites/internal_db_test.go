package suites

import (
	"context"
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

// queryMostRecentBlockID returns the latest non-deleted block id under a
// workspace. Helper kept here (suite-internal) rather than client/db.go
// because it exists solely to prop up the linear CRUD test's id-recovery
// pattern; production code should never need "the most recent block".
func queryMostRecentBlockID(ctx context.Context, dsn, wsID string) (string, error) {
	conn, err := sql.Open("postgres", dsn)
	if err != nil {
		return "", err
	}
	defer conn.Close()
	var id string
	err = conn.QueryRowContext(ctx,
		`SELECT id::text FROM blocks
		   WHERE workspace_id = $1 AND deleted_at IS NULL
		   ORDER BY created_at DESC LIMIT 1`,
		wsID,
	).Scan(&id)
	if err == sql.ErrNoRows {
		return "", fmt.Errorf("no blocks in workspace %s", wsID)
	}
	return id, err
}

func queryMostRecentRefID(ctx context.Context, dsn, wsID string) (int64, error) {
	conn, err := sql.Open("postgres", dsn)
	if err != nil {
		return 0, err
	}
	defer conn.Close()
	var id int64
	err = conn.QueryRowContext(ctx,
		`SELECT id FROM block_refs
		   WHERE workspace_id = $1
		   ORDER BY id DESC LIMIT 1`,
		wsID,
	).Scan(&id)
	if err == sql.ErrNoRows {
		return 0, fmt.Errorf("no refs in workspace %s", wsID)
	}
	return id, err
}
