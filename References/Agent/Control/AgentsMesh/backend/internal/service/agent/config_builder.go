package agent

import (
	"context"
	"fmt"

	"github.com/anthropics/agentsmesh/backend/internal/domain/extension"
	envbundleservice "github.com/anthropics/agentsmesh/backend/internal/service/envbundle"
	extensionservice "github.com/anthropics/agentsmesh/backend/internal/service/extension"
	runnerv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner/v1"
)

// ExtensionProvider provides installed extension capabilities for a repository
type ExtensionProvider interface {
	GetEffectiveMcpServers(ctx context.Context, orgID, userID, repoID int64, agentSlug string) ([]*extension.InstalledMcpServer, error)
	GetEffectiveSkills(ctx context.Context, orgID, userID, repoID int64, agentSlug string) ([]*extensionservice.ResolvedSkill, error)
}

// EnvBundleLoader is the minimal slice of envbundle.Service that
// ConfigBuilder depends on. Declared as an interface here so tests can
// inject a fake without standing up a full service + repo + encryptor.
type EnvBundleLoader interface {
	GetEffectiveForUser(ctx context.Context, userID, orgID int64, agentSlug string) ([]*envbundleservice.EffectiveBundle, error)
}

// ConfigBuilder builds pod configurations by evaluating AgentFile scripts.
// All collaborators that the build path requires must be supplied at
// construction time — nil here is a wiring bug, not a transient state.
type ConfigBuilder struct {
	provider          AgentConfigProvider
	envBundleSvc      EnvBundleLoader
	extensionProvider ExtensionProvider
}

// NewConfigBuilder creates a new ConfigBuilder. envBundleSvc is mandatory;
// USE_ENV_BUNDLE declarations would silently no-op without it, which is a
// fail-silent footgun in production. Tests can pass a tiny fake.
func NewConfigBuilder(provider AgentConfigProvider, envBundleSvc EnvBundleLoader) *ConfigBuilder {
	if provider == nil {
		panic("agent: ConfigBuilder requires a non-nil AgentConfigProvider")
	}
	if envBundleSvc == nil {
		panic("agent: ConfigBuilder requires a non-nil EnvBundleLoader")
	}
	return &ConfigBuilder{provider: provider, envBundleSvc: envBundleSvc}
}

// SetExtensionProvider sets the extension provider for loading MCP servers and skills.
// Extensions are optional — repos without enabled extensions evaluate fine without one.
func (b *ConfigBuilder) SetExtensionProvider(ep ExtensionProvider) {
	b.extensionProvider = ep
}

// BuildPodCommand evaluates the agent's AgentFile and produces a CreatePodCommand.
func (b *ConfigBuilder) BuildPodCommand(ctx context.Context, req *ConfigBuildRequest) (*runnerv1.CreatePodCommand, error) {
	agentDef, err := b.provider.GetAgent(ctx, req.AgentSlug)
	if err != nil {
		return nil, fmt.Errorf("failed to get agent: %w", err)
	}

	if agentDef.AgentfileSource == nil || *agentDef.AgentfileSource == "" {
		return nil, fmt.Errorf("agent %q has no AgentFile defined", agentDef.Slug)
	}

	return b.buildFromAgentfile(ctx, req, agentDef)
}
