// Package fixture provides test setup for MCP end-to-end tests against a
// running deploy/dev stack. Each fixture is a small struct that bundles the
// REST/MCP/DB clients and registers the appropriate t.Cleanup so failures
// still leave the dev stack clean for the next test.
package fixture

import (
	"fmt"
	"os"
	"strconv"
	"testing"
)

// Env carries the live ports and credentials of the local deploy/dev stack.
// Populated from environment variables that the Bazel test runner injects
// (see tests/mcp-e2e/README.md). Tests should never read os.Getenv directly
// so that the env contract stays in one place.
type Env struct {
	BackendBaseURL string
	MCPBaseURL     string
	// Secondary runner MCP endpoint — only populated when RUNNER_2_MCP_PORT
	// is set; pods placed on dev-runner-2 are reachable here. Used by the
	// cross-runner spec so NewEchoPod's `wait registered` poll hits the
	// right runner's /pods.
	SecondaryMCPBaseURL string
	PostgresDSN         string

	DevUser     string
	DevPassword string
	DevOrgSlug  string
	RunnerNode  string

	SecondaryUser     string
	SecondaryPassword string
}

const (
	defaultMCPPort         = 19000
	defaultBackendHTTPPort = 10015
	defaultPostgresPort    = 5432
)

func LoadEnv(t *testing.T) *Env {
	t.Helper()
	mcpPort := envInt("MCP_PORT", defaultMCPPort)
	backendPort := envInt("BACKEND_HTTP_PORT", defaultBackendHTTPPort)
	pgPort := envInt("POSTGRES_PORT", defaultPostgresPort)
	pgUser := envString("POSTGRES_USER", "agentsmesh")
	pgPwd := envString("POSTGRES_PASSWORD", "agentsmesh_dev")
	pgDB := envString("POSTGRES_DB", "agentsmesh")
	secMCPPort := envInt("RUNNER_2_MCP_PORT", 0)

	env := &Env{
		BackendBaseURL: fmt.Sprintf("http://127.0.0.1:%d/api/v1", backendPort),
		MCPBaseURL:     fmt.Sprintf("http://127.0.0.1:%d/mcp", mcpPort),
		PostgresDSN: fmt.Sprintf(
			"postgres://%s:%s@127.0.0.1:%d/%s?sslmode=disable",
			pgUser, pgPwd, pgPort, pgDB,
		),
		DevUser:           envString("E2E_DEV_USER", "dev@agentsmesh.local"),
		DevPassword:       envString("E2E_DEV_PASSWORD", "devpass123"),
		DevOrgSlug:        envString("E2E_DEV_ORG", "dev-org"),
		RunnerNode:        envString("E2E_RUNNER_NODE", "dev-runner"),
		SecondaryUser:     envString("E2E_DEV2_USER", "dev2@agentsmesh.local"),
		SecondaryPassword: envString("E2E_DEV2_PASSWORD", "devpass123"),
	}
	if secMCPPort > 0 {
		env.SecondaryMCPBaseURL = fmt.Sprintf("http://127.0.0.1:%d/mcp", secMCPPort)
	}
	return env
}

func envString(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func envInt(key string, def int) int {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return def
	}
	return n
}
