package agentconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/agentfile/extract"
	"github.com/anthropics/agentsmesh/agentfile/parser"
	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	agentservice "github.com/anthropics/agentsmesh/backend/internal/service/agent"
	agentv1 "github.com/anthropics/agentsmesh/proto/gen/go/agent/v1"
)

// ListAgents mirrors REST `ListAgents` (agents_types.go:12). Returns the
// §9 multi-field envelope: builtin + custom slices separated, plus the
// merged `agents` slice for convenience.
func (s *Server) ListAgents(
	ctx context.Context, req *connect.Request[agentv1.ListAgentsRequest],
) (*connect.Response[agentv1.AgentListResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)

	builtin, err := s.agentSvc.ListBuiltinAgents(ctx)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	custom, err := s.agentSvc.ListCustomAgents(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	builtinProto := make([]*agentv1.Agent, 0, len(builtin))
	for _, b := range builtin {
		builtinProto = append(builtinProto, ToProtoAgent(b))
	}
	customProto := make([]*agentv1.Agent, 0, len(custom))
	for _, c := range custom {
		customProto = append(customProto, toProtoCustomAgent(c))
	}
	merged := make([]*agentv1.Agent, 0, len(builtinProto)+len(customProto))
	merged = append(merged, builtinProto...)
	merged = append(merged, customProto...)

	return connect.NewResponse(&agentv1.AgentListResponse{
		BuiltinAgents: builtinProto,
		CustomAgents:  customProto,
		Agents:        merged,
	}), nil
}

// GetAgent mirrors REST `GetAgent` (agents_types.go:34).
func (s *Server) GetAgent(
	ctx context.Context, req *connect.Request[agentv1.GetAgentRequest],
) (*connect.Response[agentv1.Agent], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}

	agentDef, err := s.agentSvc.GetAgent(ctx, req.Msg.GetAgentSlug())
	if err != nil {
		if errors.Is(err, agentservice.ErrAgentNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, err)
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(ToProtoAgent(agentDef)), nil
}

// GetAgentConfigSchema mirrors REST `GetAgentConfigSchema` (agents_types.go:47).
func (s *Server) GetAgentConfigSchema(
	ctx context.Context, req *connect.Request[agentv1.GetAgentConfigSchemaRequest],
) (*connect.Response[agentv1.ConfigSchema], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}

	schema, err := agentservice.ResolveConfigSchema(ctx, s.agentSvc, req.Msg.GetAgentSlug())
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoConfigSchema(schema)), nil
}

// CreateCustomAgent mirrors REST `CreateCustomAgent` (agents_custom.go:16).
// Either agentfile_source or launch_command must be provided; if
// agentfile_source is set, launch_command is extracted from AGENT command.
func (s *Server) CreateCustomAgent(
	ctx context.Context, req *connect.Request[agentv1.CreateCustomAgentRequest],
) (*connect.Response[agentv1.Agent], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	createReq, err := buildCreateRequest(req.Msg)
	if err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	customAgent, err := s.agentSvc.CreateCustomAgent(ctx, tenant.OrganizationID, createReq)
	if err != nil {
		if errors.Is(err, agentservice.ErrAgentSlugExists) {
			return nil, connect.NewError(connect.CodeAlreadyExists, err)
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoCustomAgent(customAgent)), nil
}

// buildCreateRequest replicates the launch-command extraction from REST's
// CreateCustomAgent (agents_custom.go:38-58).
func buildCreateRequest(
	req *agentv1.CreateCustomAgentRequest,
) (*agentservice.CreateCustomAgentRequest, error) {
	out := &agentservice.CreateCustomAgentRequest{
		Slug: req.GetSlug(),
		Name: req.GetName(),
	}
	if d := req.GetDescription(); d != "" {
		out.Description = &d
	}
	if a := req.GetDefaultArgs(); a != "" {
		out.DefaultArgs = &a
	}

	launchCommand := req.GetLaunchCommand()
	if src := req.GetAgentfileSource(); src != "" {
		out.AgentfileSource = &src
		if launchCommand == "" {
			prog, parseErrs := parser.Parse(src)
			if len(parseErrs) > 0 {
				return nil, connect.NewError(connect.CodeInvalidArgument,
					errors.New("Invalid AgentFile: "+parseErrs[0]))
			}
			spec := extract.Extract(prog)
			launchCommand = spec.Agent.Command
			if launchCommand == "" {
				return nil, connect.NewError(connect.CodeInvalidArgument,
					errors.New("AgentFile must declare AGENT command"))
			}
		}
	} else if launchCommand == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("either agentfile_source or launch_command is required"))
	}
	out.LaunchCommand = launchCommand
	return out, nil
}
