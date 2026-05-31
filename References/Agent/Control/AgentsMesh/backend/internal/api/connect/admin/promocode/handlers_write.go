package promocodeadminconnect

import (
	"context"
	"errors"
	"time"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/promocode"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	promocodev1 "github.com/anthropics/agentsmesh/proto/gen/go/promocode/v1"
)

func (s *Server) CreatePromoCode(
	ctx context.Context, req *connect.Request[promocodev1.CreatePromoCodeRequest],
) (*connect.Response[promocodev1.PromoCode], error) {
	ctx, admin, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	startsAt, err := parseTime(req.Msg.GetStartsAt())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid starts_at format, use RFC3339"))
	}
	if startsAt.IsZero() {
		startsAt = time.Now()
	}

	var expiresAt *time.Time
	if v := req.Msg.GetExpiresAt(); v != "" {
		t, err := time.Parse(time.RFC3339, v)
		if err != nil {
			return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid expires_at format, use RFC3339"))
		}
		expiresAt = &t
	}

	maxUsesPerOrg := int(req.Msg.GetMaxUsesPerOrg())
	if maxUsesPerOrg <= 0 {
		maxUsesPerOrg = 1
	}

	adminID := admin.ID
	code := &promocode.PromoCode{
		Code:           normalizeCode(req.Msg.GetCode()),
		Name:           req.Msg.GetName(),
		Description:    req.Msg.GetDescription(),
		Type:           promocode.PromoCodeType(req.Msg.GetType()),
		PlanName:       req.Msg.GetPlanName(),
		DurationMonths: int(req.Msg.GetDurationMonths()),
		MaxUsesPerOrg:  maxUsesPerOrg,
		StartsAt:       startsAt,
		ExpiresAt:      expiresAt,
		IsActive:       true,
		CreatedByID:    &adminID,
	}
	if req.Msg.MaxUses != nil {
		v := int(req.Msg.GetMaxUses())
		code.MaxUses = &v
	}

	if err := s.svc.CreatePromoCode(ctx, code, adminID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(ToProtoPromoCode(code)), nil
}

func (s *Server) UpdatePromoCode(
	ctx context.Context, req *connect.Request[promocodev1.UpdatePromoCodeRequest],
) (*connect.Response[promocodev1.PromoCode], error) {
	ctx, admin, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	updates := &adminservice.PromoCodeUpdateInput{}
	if req.Msg.Name != nil {
		v := req.Msg.GetName()
		updates.Name = &v
	}
	if req.Msg.Description != nil {
		v := req.Msg.GetDescription()
		updates.Description = &v
	}
	if req.Msg.MaxUses != nil {
		v := int(req.Msg.GetMaxUses())
		updates.MaxUses = &v
	}
	if req.Msg.MaxUsesPerOrg != nil {
		v := int(req.Msg.GetMaxUsesPerOrg())
		updates.MaxUsesPerOrg = &v
	}
	if req.Msg.GetClearExpiresAt() {
		updates.ClearExpiresAt = true
	} else if req.Msg.ExpiresAt != nil {
		t, err := time.Parse(time.RFC3339, req.Msg.GetExpiresAt())
		if err != nil {
			return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid expires_at format, use RFC3339"))
		}
		updates.ExpiresAt = &t
	}

	code, err := s.svc.UpdatePromoCode(ctx, req.Msg.GetId(), updates, admin.ID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(ToProtoPromoCode(code)), nil
}

func (s *Server) ActivatePromoCode(
	ctx context.Context, req *connect.Request[promocodev1.ActivatePromoCodeRequest],
) (*connect.Response[promocodev1.ActivatePromoCodeResponse], error) {
	ctx, admin, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}
	if err := s.svc.ActivatePromoCode(ctx, req.Msg.GetId(), admin.ID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&promocodev1.ActivatePromoCodeResponse{Message: "promo code activated"}), nil
}

func (s *Server) DeactivatePromoCode(
	ctx context.Context, req *connect.Request[promocodev1.DeactivatePromoCodeRequest],
) (*connect.Response[promocodev1.DeactivatePromoCodeResponse], error) {
	ctx, admin, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}
	if err := s.svc.DeactivatePromoCode(ctx, req.Msg.GetId(), admin.ID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&promocodev1.DeactivatePromoCodeResponse{Message: "promo code deactivated"}), nil
}

func (s *Server) DeletePromoCode(
	ctx context.Context, req *connect.Request[promocodev1.DeletePromoCodeRequest],
) (*connect.Response[promocodev1.DeletePromoCodeResponse], error) {
	ctx, admin, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}
	if err := s.svc.DeletePromoCode(ctx, req.Msg.GetId(), admin.ID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&promocodev1.DeletePromoCodeResponse{Message: "promo code deleted"}), nil
}
