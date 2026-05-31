package agent

import (
	"context"

	agentDomain "github.com/anthropics/agentsmesh/backend/internal/domain/agent"
)

// AgentProvider is the minimal lookup interface depended on by services that
// only need to validate "does this agent exist" without taking a full
// AgentService dependency.
type AgentProvider interface {
	GetAgent(ctx context.Context, slug string) (*agentDomain.Agent, error)
}
