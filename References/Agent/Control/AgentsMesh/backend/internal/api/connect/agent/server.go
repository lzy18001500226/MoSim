// Package agentconnect hosts Connect-RPC handlers for the agent domain.
// Mirrors backend/internal/api/rest/v1/agents*.go but exposes the data
// plane via Connect (binary protobuf wire, see conventions.md §2.5). REST
// stays mounted in parallel; the migration runs dual-track until all
// 26 services have flipped.
//
// Two services share the package because they live in the same proto file
// (see proto/agent/v1/agent.proto):
//   * AgentService           — org-scoped agent catalog + custom CRUD
//   * UserAgentConfigService — user-scoped personal config per agent
//
// Handler shape follows runbook §3:
//   * AgentService RPCs use interceptors.ResolveOrgScope (org_slug = 1).
//   * UserAgentConfigService RPCs use requireUserID (conventions §3.5).
//   * Single-entity get/create/update return the entity directly.
//   * List response = §8 envelope EXCEPT AgentListResponse (§9 multi-field
//     exception) and UserAgentConfigListResponse (§9 sub-resource).
//   * Errors map to Connect codes (conventions §10).
package agentconnect

import (
	agentservice "github.com/anthropics/agentsmesh/backend/internal/service/agent"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
)

// AgentServiceName mirrors proto.agent.v1.AgentService exactly — Connect
// derives the URL from `<package>.<Service>` (conventions §1, §12).
const AgentServiceName = "proto.agent.v1.AgentService"

const (
	ListAgentsProcedure           = "/" + AgentServiceName + "/ListAgents"
	GetAgentProcedure             = "/" + AgentServiceName + "/GetAgent"
	GetAgentConfigSchemaProcedure = "/" + AgentServiceName + "/GetAgentConfigSchema"
	CreateCustomAgentProcedure    = "/" + AgentServiceName + "/CreateCustomAgent"
	UpdateCustomAgentProcedure    = "/" + AgentServiceName + "/UpdateCustomAgent"
	DeleteCustomAgentProcedure    = "/" + AgentServiceName + "/DeleteCustomAgent"
)

// UserAgentConfigServiceName — user-scoped personal config per agent.
const UserAgentConfigServiceName = "proto.agent.v1.UserAgentConfigService"

const (
	ListUserAgentConfigsProcedure  = "/" + UserAgentConfigServiceName + "/ListUserAgentConfigs"
	GetUserAgentConfigProcedure    = "/" + UserAgentConfigServiceName + "/GetUserAgentConfig"
	SetUserAgentConfigProcedure    = "/" + UserAgentConfigServiceName + "/SetUserAgentConfig"
	DeleteUserAgentConfigProcedure = "/" + UserAgentConfigServiceName + "/DeleteUserAgentConfig"
)

// Server implements both AgentService and UserAgentConfigService. They
// share two dependencies (agent + user-config services) so one struct
// keeps the dep wiring simple. The REST handler does the same
// (backend/internal/api/rest/v1/agents.go: AgentHandler).
type Server struct {
	agentSvc      *agentservice.AgentService
	userConfigSvc *agentservice.UserConfigService
	configBuilder *agentservice.ConfigBuilder
	orgSvc        middleware.OrganizationService
}

// NewServer constructs a Server. The ConfigBuilder is built from agentSvc
// (satisfies AgentConfigProvider) + envBundleSvc.
func NewServer(
	agentSvc *agentservice.AgentService,
	envBundleSvc agentservice.EnvBundleLoader,
	userConfigSvc *agentservice.UserConfigService,
	orgSvc middleware.OrganizationService,
) *Server {
	return &Server{
		agentSvc:      agentSvc,
		userConfigSvc: userConfigSvc,
		configBuilder: agentservice.NewConfigBuilder(agentSvc, envBundleSvc),
		orgSvc:        orgSvc,
	}
}
