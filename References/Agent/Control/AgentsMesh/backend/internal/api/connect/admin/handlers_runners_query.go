package adminconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	adminv1 "github.com/anthropics/agentsmesh/proto/gen/go/admin/v1"
)

func (s *Server) ListRunners(
	ctx context.Context, req *connect.Request[adminv1.ListRunnersRequest],
) (*connect.Response[adminv1.ListRunnersResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	query := &adminservice.RunnerListQuery{
		Search:   req.Msg.GetSearch(),
		Status:   req.Msg.GetStatus(),
		Page:     int(req.Msg.GetPage()),
		PageSize: int(req.Msg.GetPageSize()),
	}
	if req.Msg.OrgId != nil {
		v := req.Msg.GetOrgId()
		query.OrgID = &v
	}

	result, err := s.svc.ListRunners(ctx, query)
	if err != nil {
		return nil, mapServiceError(err)
	}

	items := make([]*adminv1.AdminRunner, 0, len(result.Data))
	for i := range result.Data {
		rwo := &result.Data[i]
		items = append(items, toProtoAdminRunner(&rwo.Runner, rwo.Organization))
	}
	return connect.NewResponse(&adminv1.ListRunnersResponse{
		Items:      items,
		Total:      result.Total,
		Page:       int32(result.Page),
		PageSize:   int32(result.PageSize),
		TotalPages: int32(result.TotalPages),
	}), nil
}

func (s *Server) GetRunner(
	ctx context.Context, req *connect.Request[adminv1.GetRunnerRequest],
) (*connect.Response[adminv1.AdminRunner], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	runnerID := req.Msg.GetRunnerId()
	rwo, err := s.svc.GetRunnerWithOrg(ctx, runnerID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.svc, adminUser.ID,
		admin.AuditActionRunnerView, admin.TargetTypeRunner, runnerID,
		nil, nil, req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(toProtoAdminRunner(&rwo.Runner, rwo.Organization)), nil
}
