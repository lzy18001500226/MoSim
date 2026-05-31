package agentconnect

import (
	"context"
	"encoding/json"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	agentservice "github.com/anthropics/agentsmesh/backend/internal/service/agent"
	agentv1 "github.com/anthropics/agentsmesh/proto/gen/go/agent/v1"
)

// UpdateCustomAgent mirrors REST `UpdateCustomAgent` (agents_custom.go:81).
// updates_json is the JSON-encoded `map[string]interface{}` of fields to
// update — matches the REST handler's free-form body shape.
func (s *Server) UpdateCustomAgent(
	ctx context.Context, req *connect.Request[agentv1.UpdateCustomAgentRequest],
) (*connect.Response[agentv1.Agent], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	var updates map[string]interface{}
	if u := req.Msg.GetUpdatesJson(); u != "" {
		if err := json.Unmarshal([]byte(u), &updates); err != nil {
			return nil, connect.NewError(connect.CodeInvalidArgument, err)
		}
	} else {
		updates = map[string]interface{}{}
	}

	tenant := middleware.GetTenant(ctx)
	customAgent, err := s.agentSvc.UpdateCustomAgent(
		ctx, tenant.OrganizationID, req.Msg.GetAgentSlug(), updates,
	)
	if err != nil {
		if errors.Is(err, agentservice.ErrAgentNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, err)
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoCustomAgent(customAgent)), nil
}

// DeleteCustomAgent mirrors REST `DeleteCustomAgent` (agents_custom.go:106).
// Returns FailedPrecondition when loops reference the agent (REST returns 409,
// but FailedPrecondition is the closest Connect code per conventions §10).
func (s *Server) DeleteCustomAgent(
	ctx context.Context, req *connect.Request[agentv1.DeleteCustomAgentRequest],
) (*connect.Response[agentv1.DeleteCustomAgentResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOrgAdmin(ctx); err != nil {
		return nil, err
	}

	tenant := middleware.GetTenant(ctx)
	if err := s.agentSvc.DeleteCustomAgent(
		ctx, tenant.OrganizationID, req.Msg.GetAgentSlug(),
	); err != nil {
		switch {
		case errors.Is(err, agentservice.ErrAgentNotFound):
			return nil, connect.NewError(connect.CodeNotFound, err)
		case errors.Is(err, agentservice.ErrAgentHasLoopRefs):
			return nil, connect.NewError(connect.CodeFailedPrecondition, err)
		default:
			return nil, connect.NewError(connect.CodeInternal, err)
		}
	}
	return connect.NewResponse(&agentv1.DeleteCustomAgentResponse{
		Message: "Custom agent deleted",
	}), nil
}
