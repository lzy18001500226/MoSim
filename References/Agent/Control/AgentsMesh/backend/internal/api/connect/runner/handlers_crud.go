package runnerconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
	runnerapiv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner_api/v1"
)

// ListRunners — REST analogue: GET /api/v1/organizations/:slug/runners.
// Filters by RunnerPolicy.ListFilter (private runners exclude non-owners).
// Returns the uniform list envelope plus the optional latest_runner_version
// envelope hint (DEVIATION from §8, kept because the value is global).
func (s *Server) ListRunners(
	ctx context.Context, req *connect.Request[runnerapiv1.ListRunnersRequest],
) (*connect.Response[runnerapiv1.ListRunnersResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	filter := listFilter(tenant)
	runners, err := s.runnerSvc.ListRunners(ctx, tenant.OrganizationID, filter.VisibilityUserID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	resp := &runnerapiv1.ListRunnersResponse{
		Items:  toProtoRunners(runners),
		Total:  int64(len(runners)),
		Limit:  req.Msg.GetLimit(),
		Offset: req.Msg.GetOffset(),
	}
	if s.versionChecker != nil {
		if v := s.versionChecker.GetLatestVersion(ctx); v != "" {
			resp.LatestRunnerVersion = &v
		}
	}
	return connect.NewResponse(resp), nil
}

func (s *Server) ListAvailableRunners(
	ctx context.Context, req *connect.Request[runnerapiv1.ListAvailableRunnersRequest],
) (*connect.Response[runnerapiv1.ListAvailableRunnersResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	filter := listFilter(tenant)
	runners, err := s.runnerSvc.ListAvailableRunners(ctx, tenant.OrganizationID, filter.VisibilityUserID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&runnerapiv1.ListAvailableRunnersResponse{
		Items: toProtoRunners(runners),
		Total: int64(len(runners)),
	}), nil
}

func (s *Server) GetRunner(
	ctx context.Context, req *connect.Request[runnerapiv1.GetRunnerRequest],
) (*connect.Response[runnerapiv1.GetRunnerResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	runnerID := req.Msg.GetId()

	r, err := s.runnerSvc.GetRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.RunnerPolicy.AllowRead(sub, policy.VisibleResource(
		r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}

	resp := &runnerapiv1.GetRunnerResponse{Runner: ToProtoRunner(r)}
	if s.podCoordinator != nil {
		resp.RelayConnections = toProtoRelayConnections(s.podCoordinator.GetRelayConnections(runnerID))
	}
	if s.versionChecker != nil {
		if v := s.versionChecker.GetLatestVersion(ctx); v != "" {
			resp.LatestRunnerVersion = &v
		}
	}
	return connect.NewResponse(resp), nil
}

func (s *Server) UpdateRunner(
	ctx context.Context, req *connect.Request[runnerapiv1.UpdateRunnerRequest],
) (*connect.Response[runnerapiv1.Runner], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.AllowAdmin(sub, tenant.OrganizationID) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("organization admin role required"))
	}

	runnerID := req.Msg.GetId()
	r, err := s.runnerSvc.GetRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	if !policy.RunnerPolicy.AllowWrite(sub, policy.VisibleResource(
		r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}

	input := runner.RunnerUpdateInput{}
	if req.Msg.Description != nil {
		v := req.Msg.GetDescription()
		input.Description = &v
	}
	if req.Msg.MaxConcurrentPods != nil {
		v := int(req.Msg.GetMaxConcurrentPods())
		input.MaxConcurrentPods = &v
	}
	if req.Msg.IsEnabled != nil {
		v := req.Msg.GetIsEnabled()
		input.IsEnabled = &v
	}
	if req.Msg.Visibility != nil {
		v := req.Msg.GetVisibility()
		input.Visibility = &v
	}
	// TagsUpdate semantics: presence of the message means "set to values",
	// absence means "leave unchanged". service-layer treats nil = no-op.
	if req.Msg.GetTags() != nil {
		input.Tags = req.Msg.GetTags().GetValues()
		if input.Tags == nil {
			// Distinguish "explicit empty" from "no update" — service uses
			// len(Tags) == 0 with non-nil slice to mean "clear".
			input.Tags = []string{}
		}
	}

	updated, err := s.runnerSvc.UpdateRunner(ctx, runnerID, input)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(ToProtoRunner(updated)), nil
}

func (s *Server) DeleteRunner(
	ctx context.Context, req *connect.Request[runnerapiv1.DeleteRunnerRequest],
) (*connect.Response[runnerapiv1.DeleteRunnerResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)
	if !policy.AllowAdmin(sub, tenant.OrganizationID) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("organization admin role required"))
	}

	runnerID := req.Msg.GetId()
	r, err := s.runnerSvc.GetRunner(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	if !policy.RunnerPolicy.AllowWrite(sub, policy.VisibleResource(
		r.OrganizationID, r.RegisteredByUserID, r.Visibility,
	)) {
		return nil, connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
	}

	if err := s.runnerSvc.DeleteRunner(ctx, runnerID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&runnerapiv1.DeleteRunnerResponse{}), nil
}
