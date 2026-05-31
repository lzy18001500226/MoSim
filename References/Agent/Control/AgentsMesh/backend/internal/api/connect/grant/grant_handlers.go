package grantconnect

import (
	"context"
	"errors"
	"strconv"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/grant"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/pkg/policy"
	grantv1 "github.com/anthropics/agentsmesh/proto/gen/go/grant/v1"
)

// ListGrants — REST analogues:
//   GET /api/v1/orgs/:slug/pods/:key/grants
//   GET /api/v1/orgs/:slug/runners/:id/grants
//   GET /api/v1/orgs/:slug/repositories/:id/grants
//
// Per-resource policy:
//   pod        — PodPolicy.AllowWrite (creator/admin/owner)
//   runner     — AllowAdmin (org admin only)
//   repository — AllowAdmin (org admin only)
func (s *Server) ListGrants(
	ctx context.Context, req *connect.Request[grantv1.ListGrantsRequest],
) (*connect.Response[grantv1.ListGrantsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}

	resourceType := req.Msg.GetResourceType()
	resourceID := req.Msg.GetResourceId()
	if !isValidResourceType(resourceType) {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("resource_type must be pod / runner / repository"))
	}
	if resourceID == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("resource_id is required"))
	}

	if err := s.authorizeAccess(ctx, resourceType, resourceID, policyActionRead); err != nil {
		return nil, err
	}

	grants, err := s.grantSvc.ListGrants(ctx, resourceType, resourceID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*grantv1.ResourceGrant, 0, len(grants))
	for _, g := range grants {
		items = append(items, toProtoGrant(g))
	}
	return connect.NewResponse(&grantv1.ListGrantsResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  int32(len(items)),
		Offset: 0,
	}), nil
}

// CreateGrant — REST analogues:
//   POST /api/v1/orgs/:slug/pods/:key/grants
//   POST /api/v1/orgs/:slug/runners/:id/grants
//   POST /api/v1/orgs/:slug/repositories/:id/grants
func (s *Server) CreateGrant(
	ctx context.Context, req *connect.Request[grantv1.CreateGrantRequest],
) (*connect.Response[grantv1.ResourceGrant], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	resourceType := req.Msg.GetResourceType()
	resourceID := req.Msg.GetResourceId()
	if !isValidResourceType(resourceType) {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("resource_type must be pod / runner / repository"))
	}
	if resourceID == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("resource_id is required"))
	}
	if req.Msg.GetUserId() == 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("user_id is required"))
	}

	if err := s.authorizeAccess(ctx, resourceType, resourceID, policyActionWrite); err != nil {
		return nil, err
	}

	g, err := s.grantSvc.GrantAccess(
		ctx, tenant.OrganizationID, resourceType, resourceID,
		req.Msg.GetUserId(), tenant.UserID,
	)
	if err != nil {
		return nil, mapGrantError(err)
	}
	return connect.NewResponse(toProtoGrant(g)), nil
}

// DeleteGrant — REST analogues:
//   DELETE /api/v1/orgs/:slug/pods/:key/grants/:grant_id
//   DELETE /api/v1/orgs/:slug/runners/:id/grants/:grant_id
//   DELETE /api/v1/orgs/:slug/repositories/:id/grants/:grant_id
func (s *Server) DeleteGrant(
	ctx context.Context, req *connect.Request[grantv1.DeleteGrantRequest],
) (*connect.Response[grantv1.DeleteGrantResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}

	resourceType := req.Msg.GetResourceType()
	resourceID := req.Msg.GetResourceId()
	if !isValidResourceType(resourceType) {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("resource_type must be pod / runner / repository"))
	}
	if resourceID == "" || req.Msg.GetGrantId() == 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("resource_id and grant_id are required"))
	}

	if err := s.authorizeAccess(ctx, resourceType, resourceID, policyActionWrite); err != nil {
		return nil, err
	}

	if err := s.grantSvc.RevokeAccess(ctx, resourceType, resourceID, req.Msg.GetGrantId()); err != nil {
		return nil, connect.NewError(connect.CodeNotFound, errors.New("grant not found"))
	}
	return connect.NewResponse(&grantv1.DeleteGrantResponse{Message: "Grant revoked"}), nil
}

// authorizeAccess loads the underlying resource and runs the per-resource
// policy check. action == read|write.
func (s *Server) authorizeAccess(
	ctx context.Context, resourceType, resourceID string, action policyAction,
) error {
	tenant := middleware.GetTenant(ctx)
	sub := policy.NewSubject(tenant.OrganizationID, tenant.UserID, tenant.UserRole)

	switch resourceType {
	case grant.TypePod:
		pod, err := s.podSvc.GetPod(ctx, resourceID)
		if err != nil {
			return connect.NewError(connect.CodeNotFound, errors.New("pod not found"))
		}
		rc := policy.PodResource(pod.OrganizationID, pod.CreatedByID)
		if !policy.PodPolicy.AllowWrite(sub, rc) {
			return connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
		}
	case grant.TypeRunner:
		runnerID, err := strconv.ParseInt(resourceID, 10, 64)
		if err != nil {
			return connect.NewError(connect.CodeInvalidArgument, errors.New("invalid runner id"))
		}
		r, err := s.runnerSvc.GetRunner(ctx, runnerID)
		if err != nil {
			return connect.NewError(connect.CodeNotFound, errors.New("runner not found"))
		}
		if !policy.AllowAdmin(sub, tenant.OrganizationID) {
			return connect.NewError(connect.CodePermissionDenied, errors.New("organization admin role required"))
		}
		check := policy.RunnerPolicy.AllowRead
		if action == policyActionWrite {
			check = policy.RunnerPolicy.AllowWrite
		}
		if !check(sub, policy.VisibleResource(r.OrganizationID, r.RegisteredByUserID, r.Visibility)) {
			return connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
		}
	case grant.TypeRepository:
		repoID, err := strconv.ParseInt(resourceID, 10, 64)
		if err != nil {
			return connect.NewError(connect.CodeInvalidArgument, errors.New("invalid repository id"))
		}
		repo, err := s.repoSvc.GetByID(ctx, repoID)
		if err != nil {
			return connect.NewError(connect.CodeNotFound, errors.New("repository not found"))
		}
		if !policy.AllowAdmin(sub, tenant.OrganizationID) {
			return connect.NewError(connect.CodePermissionDenied, errors.New("organization admin role required"))
		}
		check := policy.RepositoryPolicy.AllowRead
		if action == policyActionWrite {
			check = policy.RepositoryPolicy.AllowWrite
		}
		if !check(sub, policy.VisibleResource(repo.OrganizationID, repo.ImportedByUserID, repo.Visibility)) {
			return connect.NewError(connect.CodePermissionDenied, errors.New("forbidden"))
		}
	}
	return nil
}

type policyAction int

const (
	policyActionRead  policyAction = 0
	policyActionWrite policyAction = 1
)

func isValidResourceType(t string) bool {
	return t == grant.TypePod || t == grant.TypeRunner || t == grant.TypeRepository
}
