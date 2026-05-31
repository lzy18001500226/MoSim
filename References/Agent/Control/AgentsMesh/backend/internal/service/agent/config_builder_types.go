package agent

import (
	"context"

	"github.com/anthropics/agentsmesh/backend/internal/domain/agent"
)

// AgentConfigProvider provides agent lookups for ConfigBuilder. Credential
// resolution moved out: EnvBundles are loaded directly through
// ConfigBuilder.envBundleSvc in buildEnvBundleContext, mirroring how MCP
// servers are exposed to AgentFile eval.
type AgentConfigProvider interface {
	GetAgent(ctx context.Context, slug string) (*agent.Agent, error)
}

// ConfigBuildRequest contains all the information needed to build a pod config
type ConfigBuildRequest struct {
	AgentSlug      string
	OrganizationID int64
	UserID         int64

	// RepositoryID is the repository this pod belongs to (for loading installed extensions)
	RepositoryID *int64

	// Repository configuration
	HttpCloneURL string // HTTPS clone URL
	SshCloneURL  string // SSH clone URL
	SourceBranch string // Branch to checkout

	// Git authentication
	// CredentialType determines how to authenticate:
	// - "runner_local": Use Runner's local git config, no credentials needed
	// - "oauth" or "pat": Use GitToken
	// - "ssh_key": Use SSHPrivateKey
	CredentialType string
	GitToken       string // For oauth/pat types
	SSHPrivateKey  string // For ssh_key type (private key content)

	// Ticket association
	TicketSlug string

	// Preparation script (from AgentFile SETUP or Repository fallback)
	PreparationScript  string
	PreparationTimeout int

	// Local path mode (resume from existing sandbox)
	LocalPath string

	// Prompt (from AgentFile PROMPT declaration)
	Prompt string

	// Runtime info (provided by Runner during handshake)
	MCPPort int
	PodKey  string

	// Terminal size (from browser)
	Cols int32
	Rows int32

	// RunnerAgentVersions maps agent slug to version string.
	// Populated from Runner.AgentVersions during pod creation.
	// Empty map or nil means Runner did not report version info (old Runner).
	RunnerAgentVersions map[string]string

	// MergedAgentfileSource is the merged AgentFile source (base + user layer, serialized).
	// Populated by orchestrator's extractFromAgentfileLayer when AgentfileLayer is provided.
	// When empty (resume mode or no layer): buildFromAgentfile falls back to agent's base AgentFile.
	MergedAgentfileSource string
}

// ConfigSchemaResponse is the config schema returned to frontend
// Frontend is responsible for i18n translation using slug + field.name as key
type ConfigSchemaResponse struct {
	Fields []ConfigFieldResponse `json:"fields"`
}

// ConfigFieldResponse is a config field returned to frontend
type ConfigFieldResponse struct {
	Name    string                `json:"name"`
	Type    string                `json:"type"`
	Default interface{}           `json:"default,omitempty"`
	Options []FieldOptionResponse `json:"options,omitempty"`
}

// FieldOptionResponse is a field option returned to frontend
type FieldOptionResponse struct {
	Value string `json:"value"`
}
