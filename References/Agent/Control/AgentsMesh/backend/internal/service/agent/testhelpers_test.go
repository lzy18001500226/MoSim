package agent

import (
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/infra"
	"github.com/anthropics/agentsmesh/backend/internal/testkit"
	"gorm.io/gorm"
)

// setupTestDB returns a fresh in-memory SQLite DB seeded with the project
// schema and a small set of built-in agents so AgentService lookup tests
// always have data to find. Previously this seed lived in service_test.go
// alongside the credential-profile fixtures; after the EnvBundle refactor
// removed that file, the seeding moved here where every agent-package test
// can reuse it through one helper.
func setupTestDB(t *testing.T) *gorm.DB {
	t.Helper()
	db := testkit.SetupTestDB(t)
	seedBuiltinAgents(t, db)
	return db
}

// seedBuiltinAgents inserts the canonical builtin agents used by service
// tests (claude-code + codex-cli is enough for "first" / "list builtin"
// assertions without dragging in the full migrations file).
func seedBuiltinAgents(t *testing.T, db *gorm.DB) {
	t.Helper()
	stmt := `INSERT INTO agents (id, slug, name, launch_command, executable, is_builtin, is_active, supported_modes)
		VALUES (?, ?, ?, ?, ?, 1, 1, 'pty')`
	rows := []struct {
		id            int
		slug          string
		name          string
		launchCommand string
		executable    string
	}{
		{1, "claude-code", "Claude Code", "claude", "claude"},
		{2, "codex-cli", "OpenAI Codex", "codex", "codex"},
	}
	for _, r := range rows {
		if err := db.Exec(stmt, r.id, r.slug, r.name, r.launchCommand, r.executable).Error; err != nil {
			t.Fatalf("testhelpers: seed agent %s: %v", r.slug, err)
		}
	}
}

// newTestAgentService wires an AgentService against a test DB.
func newTestAgentService(db *gorm.DB) *AgentService {
	return NewAgentService(infra.NewAgentRepository(db))
}

// newTestMessageService wires a MessageService against a test DB.
func newTestMessageService(db *gorm.DB) *MessageService {
	return NewMessageService(infra.NewAgentMessageRepository(db))
}

// newTestUserConfigService wires a UserConfigService against a test DB.
// Accepts an optional AgentService; pass nil to auto-create one.
func newTestUserConfigService(db *gorm.DB, agentSvc *AgentService) *UserConfigService {
	if agentSvc == nil {
		agentSvc = newTestAgentService(db)
	}
	return NewUserConfigService(infra.NewUserConfigRepository(db), agentSvc)
}
