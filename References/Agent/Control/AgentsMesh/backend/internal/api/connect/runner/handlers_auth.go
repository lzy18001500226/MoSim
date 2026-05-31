package runnerconnect

import (
	"context"
	"errors"
	"time"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
	runnerapiv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner_api/v1"
)

// AuthorizeRunner mirrors REST POST /api/v1/organizations/:slug/runners/grpc/authorize.
// Owner/admin only — completes a pending Tailscale-style registration that
// the runner CLI initiated via the public `/runners/grpc/auth-url` REST
// bootstrap.
func (s *Server) AuthorizeRunner(
	ctx context.Context, req *connect.Request[runnerapiv1.AuthorizeRunnerRequest],
) (*connect.Response[runnerapiv1.AuthorizeRunnerResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if tenant.UserRole != "owner" && tenant.UserRole != "admin" {
		return nil, connect.NewError(connect.CodePermissionDenied,
			errors.New("owner or admin role required"))
	}
	if req.Msg.GetAuthKey() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("auth_key is required"))
	}
	r, err := s.runnerSvc.AuthorizeRunner(
		ctx, req.Msg.GetAuthKey(), tenant.OrganizationID, tenant.UserID, req.Msg.GetNodeId(),
	)
	if err != nil {
		return nil, mapAuthorizeError(err)
	}
	return connect.NewResponse(&runnerapiv1.AuthorizeRunnerResponse{
		RunnerId: r.ID,
		NodeId:   r.NodeID,
		Message:  "Runner authorized successfully",
	}), nil
}

// GetRunnerAuthStatus is the public RunnerPublicService entry — the runner
// CLI polls with its auth_key (opaque credential issued by the public
// REST `/runners/grpc/auth-url`). The browser calls the same RPC to gate
// the "Authorize this runner?" UI on the pending request.
func (s *Server) GetRunnerAuthStatus(
	ctx context.Context, req *connect.Request[runnerapiv1.GetRunnerAuthStatusRequest],
) (*connect.Response[runnerapiv1.RunnerAuthStatus], error) {
	if s.pkiSvc == nil {
		return nil, connect.NewError(connect.CodeUnavailable,
			errors.New("PKI service not configured"))
	}
	if req.Msg.GetAuthKey() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("auth_key is required"))
	}
	resp, err := s.runnerSvc.GetAuthStatus(ctx, req.Msg.GetAuthKey(), s.pkiSvc)
	if err != nil {
		if errors.Is(err, runner.ErrAuthRequestNotFound) {
			return nil, connect.NewError(connect.CodeNotFound, err)
		}
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	out := &runnerapiv1.RunnerAuthStatus{Status: resp.Status}
	if resp.NodeID != "" {
		v := resp.NodeID
		out.NodeId = &v
	}
	if resp.ExpiresAt != "" {
		v := resp.ExpiresAt
		out.ExpiresAt = &v
	}
	if resp.RunnerID != 0 {
		v := resp.RunnerID
		out.RunnerId = &v
	}
	if resp.Certificate != "" {
		v := resp.Certificate
		out.Certificate = &v
	}
	if resp.PrivateKey != "" {
		v := resp.PrivateKey
		out.PrivateKey = &v
	}
	if resp.CACertificate != "" {
		v := resp.CACertificate
		out.CaCertificate = &v
	}
	if resp.OrgSlug != "" {
		v := resp.OrgSlug
		out.OrgSlug = &v
	}
	// Inject configured gRPC endpoint on authorized responses (parity with
	// REST handler runners_grpc_auth.go:72).
	if resp.Status == "authorized" && s.grpcEndpoint != "" {
		out.GrpcEndpoint = &s.grpcEndpoint
	}
	return connect.NewResponse(out), nil
}

func mapAuthorizeError(err error) error {
	switch {
	case errors.Is(err, runner.ErrRunnerAlreadyExists):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, runner.ErrRunnerQuotaExceeded):
		return connect.NewError(connect.CodeResourceExhausted, err)
	case errors.Is(err, runner.ErrAuthRequestNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, runner.ErrAuthRequestExpired):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, runner.ErrAuthRequestAlreadyAuthorized):
		return connect.NewError(connect.CodeAlreadyExists, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}

// Used only via mapAuthorizeError; satisfy import for the time package
// when the surrounding handlers grow time-based logic.
var _ = time.Now
