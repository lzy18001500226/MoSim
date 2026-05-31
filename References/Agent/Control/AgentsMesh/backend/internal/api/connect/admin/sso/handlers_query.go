package ssoadminconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	ssodomain "github.com/anthropics/agentsmesh/backend/internal/domain/sso"
	ssov1 "github.com/anthropics/agentsmesh/proto/gen/go/sso/v1"
)

// ListSSOConfigs mirrors REST's ListConfigs (sso.go:52). Pagination defaults
// (page=1, page_size=20) come from the service layer when zero values land.
func (s *Server) ListSSOConfigs(
	ctx context.Context, req *connect.Request[ssov1.ListSSOConfigsRequest],
) (*connect.Response[ssov1.ListSSOConfigsResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	page := int(req.Msg.GetPage())
	if page < 1 {
		page = 1
	}
	pageSize := int(req.Msg.GetPageSize())
	if pageSize < 1 {
		pageSize = 20
	}

	var query *ssodomain.ListQuery
	search := req.Msg.GetSearch()
	protocol := req.Msg.GetProtocol()
	if search != "" || protocol != "" {
		query = &ssodomain.ListQuery{
			Search:   search,
			Protocol: ssodomain.Protocol(protocol),
		}
	}

	configs, total, err := s.ssoSvc.ListConfigs(ctx, query, page, pageSize)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*ssov1.AdminSSOConfig, 0, len(configs))
	for _, cfg := range configs {
		items = append(items, toProtoAdminSSOConfig(s.ssoSvc.ToConfigResponse(cfg)))
	}

	totalPages := int64(0)
	if total > 0 {
		totalPages = (total + int64(pageSize) - 1) / int64(pageSize)
	}

	return connect.NewResponse(&ssov1.ListSSOConfigsResponse{
		Data:       items,
		Total:      total,
		Page:       int32(page),
		PageSize:   int32(pageSize),
		TotalPages: totalPages,
	}), nil
}

// GetSSOConfig mirrors REST's GetConfig (sso.go:128).
func (s *Server) GetSSOConfig(
	ctx context.Context, req *connect.Request[ssov1.GetSSOConfigRequest],
) (*connect.Response[ssov1.AdminSSOConfig], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	cfg, err := s.ssoSvc.GetConfig(ctx, req.Msg.GetId())
	if err != nil {
		return nil, mapServiceError(err)
	}

	return connect.NewResponse(toProtoAdminSSOConfig(s.ssoSvc.ToConfigResponse(cfg))), nil
}
