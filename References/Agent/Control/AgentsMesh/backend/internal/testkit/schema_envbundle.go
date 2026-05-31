package testkit

// envBundleTableDDLs returns DDLs for env_bundles. Matches migration 000145.
// SQLite-friendly (no JSONB; uses TEXT for the data column — gorm
// driver.Valuer / sql.Scanner still round-trips JSON through it).
func envBundleTableDDLs() []string {
	return []string{
		`CREATE TABLE IF NOT EXISTS env_bundles (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			owner_scope TEXT NOT NULL,
			owner_id INTEGER NOT NULL,
			agent_slug TEXT,
			name TEXT NOT NULL,
			description TEXT,
			kind TEXT NOT NULL,
			kind_primary INTEGER NOT NULL DEFAULT 0,
			data TEXT NOT NULL DEFAULT '{}',
			is_active INTEGER NOT NULL DEFAULT 1,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			UNIQUE(owner_scope, owner_id, name)
		)`,
		`CREATE UNIQUE INDEX IF NOT EXISTS env_bundles_primary_per_kind
			ON env_bundles(owner_scope, owner_id, agent_slug, kind)
			WHERE kind_primary = 1`,
	}
}
