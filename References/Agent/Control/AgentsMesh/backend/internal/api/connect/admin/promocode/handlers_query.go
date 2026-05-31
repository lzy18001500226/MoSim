package promocodeadminconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/promocode"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	promocodev1 "github.com/anthropics/agentsmesh/proto/gen/go/promocode/v1"
)

func (s *Server) ListPromoCodes(
	ctx context.Context, req *connect.Request[promocodev1.ListPromoCodesRequest],
) (*connect.Response[promocodev1.ListPromoCodesResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	filter := &adminservice.PromoCodeListFilter{
		Page:     int(req.Msg.GetPage()),
		PageSize: int(req.Msg.GetPageSize()),
	}
	if t := req.Msg.GetType(); t != "" {
		pt := promocode.PromoCodeType(t)
		filter.Type = &pt
	}
	if p := req.Msg.GetPlanName(); p != "" {
		filter.PlanName = &p
	}
	if req.Msg.IsActive != nil {
		v := req.Msg.GetIsActive()
		filter.IsActive = &v
	}
	if sQ := req.Msg.GetSearch(); sQ != "" {
		filter.Search = &sQ
	}

	result, err := s.svc.ListPromoCodes(ctx, filter)
	if err != nil {
		return nil, mapServiceError(err)
	}

	items := make([]*promocodev1.PromoCode, 0, len(result.Data))
	for _, p := range result.Data {
		items = append(items, ToProtoPromoCode(p))
	}
	return connect.NewResponse(&promocodev1.ListPromoCodesResponse{
		Data:       items,
		Total:      result.Total,
		Page:       int32(result.Page),
		PageSize:   int32(result.PageSize),
		TotalPages: int32(result.TotalPages),
	}), nil
}

func (s *Server) GetPromoCode(
	ctx context.Context, req *connect.Request[promocodev1.GetPromoCodeRequest],
) (*connect.Response[promocodev1.PromoCode], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	code, err := s.svc.GetPromoCode(ctx, req.Msg.GetId())
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(ToProtoPromoCode(code)), nil
}

func (s *Server) ListPromoCodeRedemptions(
	ctx context.Context, req *connect.Request[promocodev1.ListPromoCodeRedemptionsRequest],
) (*connect.Response[promocodev1.ListPromoCodeRedemptionsResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	result, err := s.svc.ListPromoCodeRedemptions(
		ctx, req.Msg.GetId(), int(req.Msg.GetPage()), int(req.Msg.GetPageSize()),
	)
	if err != nil {
		return nil, mapServiceError(err)
	}

	items := make([]*promocodev1.RedemptionDetail, 0, len(result.Data))
	for _, d := range result.Data {
		items = append(items, toProtoRedemptionDetail(d))
	}
	return connect.NewResponse(&promocodev1.ListPromoCodeRedemptionsResponse{
		Data:       items,
		Total:      result.Total,
		Page:       int32(result.Page),
		PageSize:   int32(result.PageSize),
		TotalPages: int32(result.TotalPages),
	}), nil
}
