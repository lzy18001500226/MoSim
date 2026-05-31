package adminconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

func (s *Server) ListOrganizations(
	ctx context.Context, req *connect.Request[adminv1.ListOrganizationsRequest],
) (*connect.Response[adminv1.ListOrganizationsResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	query := &adminservice.OrganizationListQuery{
		Search:   req.Msg.GetSearch(),
		Page:     int(req.Msg.GetPage()),
		PageSize: int(req.Msg.GetPageSize()),
	}

	result, err := s.svc.ListOrganizations(ctx, query)
	if err != nil {
		return nil, mapServiceError(err)
	}

	items := make([]*adminv1.AdminOrganization, 0, len(result.Data))
	for i := range result.Data {
		items = append(items, ToProtoAdminOrganization(&result.Data[i]))
	}
	return connect.NewResponse(&adminv1.ListOrganizationsResponse{
		Items:      items,
		Total:      result.Total,
		Page:       int32(result.Page),
		PageSize:   int32(result.PageSize),
		TotalPages: int32(result.TotalPages),
	}), nil
}

func (s *Server) GetOrganization(
	ctx context.Context, req *connect.Request[adminv1.GetOrganizationRequest],
) (*connect.Response[adminv1.AdminOrganization], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	orgID := req.Msg.GetOrgId()
	org, err := s.svc.GetOrganization(ctx, orgID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionOrgView, admin.TargetTypeOrganization, orgID,
		nil, nil, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminOrganization(org)), nil
}

func (s *Server) GetOrganizationMembers(
	ctx context.Context, req *connect.Request[adminv1.GetOrganizationMembersRequest],
) (*connect.Response[adminv1.GetOrganizationMembersResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	orgID := req.Msg.GetOrgId()
	org, members, err := s.svc.GetOrganizationWithMembers(ctx, orgID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	items := make([]*adminv1.AdminOrganizationMember, 0, len(members))
	for i := range members {
		items = append(items, ToProtoAdminOrganizationMember(&members[i]))
	}

	return connect.NewResponse(&adminv1.GetOrganizationMembersResponse{
		Organization: ToProtoAdminOrganization(org),
		Members:      items,
	}), nil
}

func (s *Server) DeleteOrganization(
	ctx context.Context, req *connect.Request[adminv1.DeleteOrganizationRequest],
) (*connect.Response[adminv1.DeleteOrganizationResponse], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	orgID := req.Msg.GetOrgId()
	oldOrg, _ := s.svc.GetOrganization(ctx, orgID)

	if err := s.svc.DeleteOrganization(ctx, orgID); err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionOrgDelete, admin.TargetTypeOrganization, orgID,
		oldOrg, nil, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(&adminv1.DeleteOrganizationResponse{
		Message: "Organization deleted successfully",
	}), nil
}
