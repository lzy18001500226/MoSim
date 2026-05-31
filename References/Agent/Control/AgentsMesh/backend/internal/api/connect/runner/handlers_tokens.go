package runnerconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	runnerapiv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner_api/v1"
)

// Token CRUD — registration tokens minted for gRPC runner enrollment. Only
// org admins/owners can mint, list, or delete. The single-use semantics are
// derived from MaxUses (1 or 0 means one-shot); legacy REST callers passed
// labels as either map[string]string or "k=v" slice — we accept the slice
// shape here and translate via labelsToMap (kept tolerant on purpose).

func (s *Server) CreateRunnerToken(
	ctx context.Context, req *connect.Request[runnerapiv1.CreateRunnerTokenRequest],
) (*connect.Response[runnerapiv1.RunnerToken], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if tenant.UserRole != "owner" && tenant.UserRole != "admin" {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("organization admin role required"))
	}

	// Convert labels from []string ("k=v") → map[string]string. The legacy
	// REST handler accepted both shapes (map JSON) so the wasm callers send
	// a slice; both are translated identically here.
	labels := labelsToMap(req.Msg.GetLabels())
	expiresInSeconds := 0
	if req.Msg.ExpiresInDays != nil {
		expiresInSeconds = int(req.Msg.GetExpiresInDays() * 86400)
	}
	maxUses := int(req.Msg.GetMaxUses())

	gen, err := s.runnerSvc.GenerateGRPCRegistrationToken(
		ctx,
		tenant.OrganizationID,
		tenant.UserID,
		&runner.GenerateGRPCRegistrationTokenRequest{
			Name:      req.Msg.GetName(),
			Labels:    labels,
			SingleUse: maxUses == 0 || maxUses == 1,
			MaxUses:   maxUses,
			ExpiresIn: expiresInSeconds,
		},
		s.baseURL,
	)
	if err != nil {
		return nil, mapServiceError(err)
	}

	token := gen.Token
	expiresAt := protoconv.RFC3339(gen.ExpiresAt)
	out := &runnerapiv1.RunnerToken{
		Id:        gen.ID,
		Token:     &token,
		ExpiresAt: &expiresAt,
	}
	return connect.NewResponse(out), nil
}

func (s *Server) ListRunnerTokens(
	ctx context.Context, req *connect.Request[runnerapiv1.ListRunnerTokensRequest],
) (*connect.Response[runnerapiv1.ListRunnerTokensResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if tenant.UserRole != "owner" && tenant.UserRole != "admin" {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("organization admin role required"))
	}
	tokens, err := s.runnerSvc.ListGRPCRegistrationTokens(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*runnerapiv1.RunnerToken, 0, len(tokens))
	for _, t := range tokens {
		items = append(items, toProtoToken(t))
	}
	return connect.NewResponse(&runnerapiv1.ListRunnerTokensResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}

func (s *Server) DeleteRunnerToken(
	ctx context.Context, req *connect.Request[runnerapiv1.DeleteRunnerTokenRequest],
) (*connect.Response[runnerapiv1.DeleteRunnerTokenResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if tenant.UserRole != "owner" && tenant.UserRole != "admin" {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("organization admin role required"))
	}
	if err := s.runnerSvc.DeleteGRPCRegistrationToken(ctx, req.Msg.GetId(), tenant.OrganizationID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&runnerapiv1.DeleteRunnerTokenResponse{}), nil
}

// labelsToMap converts a "k=v" slice into a map. Empty / malformed entries
// are silently dropped to match the REST handler's tolerant binding.
func labelsToMap(labels []string) map[string]string {
	if len(labels) == 0 {
		return nil
	}
	out := make(map[string]string, len(labels))
	for _, l := range labels {
		for i := 0; i < len(l); i++ {
			if l[i] == '=' {
				out[l[:i]] = l[i+1:]
				break
			}
		}
	}
	return out
}
