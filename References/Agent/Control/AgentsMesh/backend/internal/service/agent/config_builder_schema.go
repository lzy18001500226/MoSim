package agent

import (
	"context"
	"fmt"

	"github.com/anthropics/agentsmesh/agentfile/extract"
	"github.com/anthropics/agentsmesh/agentfile/parser"
)

// ResolveConfigSchema returns the config schema for an agent. After the
// EnvBundle refactor it serves only AgentFile CONFIG declarations — credential
// field schemas live entirely in the frontend's per-agent form spec.
//
// It only needs to look up the agent + parse its AgentFile, so it lives at
// package scope instead of on ConfigBuilder. This lets callers (e.g.
// AgentHandler) ask for schemas without standing up the full Pod-build
// dependency graph (EnvBundle loader, extension provider).
func ResolveConfigSchema(ctx context.Context, provider AgentConfigProvider, agentSlug string) (*ConfigSchemaResponse, error) {
	agentDef, err := provider.GetAgent(ctx, agentSlug)
	if err != nil {
		return nil, err
	}
	if agentDef.AgentfileSource == nil || *agentDef.AgentfileSource == "" {
		return &ConfigSchemaResponse{Fields: []ConfigFieldResponse{}}, nil
	}
	return configSchemaFromAgentfile(*agentDef.AgentfileSource)
}

func configSchemaFromAgentfile(source string) (*ConfigSchemaResponse, error) {
	prog, errs := parser.Parse(source)
	if len(errs) > 0 {
		return nil, fmt.Errorf("agentfile parse errors: %v", errs)
	}

	spec := extract.Extract(prog)
	result := &ConfigSchemaResponse{
		Fields: make([]ConfigFieldResponse, 0, len(spec.Config)),
	}
	for _, cfg := range spec.Config {
		field := ConfigFieldResponse{
			Name:    cfg.Name,
			Type:    cfg.Type,
			Default: cfg.Default,
		}
		if len(cfg.Options) > 0 {
			field.Options = make([]FieldOptionResponse, 0, len(cfg.Options))
			for _, opt := range cfg.Options {
				field.Options = append(field.Options, FieldOptionResponse{Value: opt})
			}
		}
		result.Fields = append(result.Fields, field)
	}
	return result, nil
}
