package promocodeconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	promocodesvc "github.com/anthropics/agentsmesh/backend/internal/service/promocode"
	promocodev1 "github.com/anthropics/agentsmesh/proto/gen/go/promocode/v1"
)

// Validate validates a promo code. Any org member can call. Returns
// valid=false + message_code (i18n key) on validation miss; genuine server
// errors surface as connect.CodeInternal. Mirrors REST POST
// /api/v1/orgs/:slug/billing/promo-codes/validate (promocode.go:35).
func (s *Server) Validate(
	ctx context.Context, req *connect.Request[promocodev1.ValidatePromoCodeRequest],
) (*connect.Response[promocodev1.ValidatePromoCodeResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	code := req.Msg.GetCode()
	if code == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("code is required"))
	}

	resp, err := s.svc.Validate(ctx, &promocodesvc.ValidateRequest{
		Code:           code,
		OrganizationID: tenant.OrganizationID,
	})
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoValidateResponse(resp)), nil
}

// Redeem redeems a promo code. Only the org owner can call (the service
// layer enforces this via UserRole). Returns success=false + message_code
// when the caller is not owner / code already used / quota hit; the REST
// handler's 400 + apierr.RespondWithExtra trick collapses to a typed
// response here. Mirrors REST POST
// /api/v1/orgs/:slug/billing/promo-codes/redeem (promocode.go:63).
func (s *Server) Redeem(
	ctx context.Context, req *connect.Request[promocodev1.RedeemPromoCodeRequest],
) (*connect.Response[promocodev1.RedeemPromoCodeResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	code := req.Msg.GetCode()
	if code == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("code is required"))
	}

	// Audit trail: REST handler captures c.ClientIP() and
	// c.Request.UserAgent() — Connect's Peer struct exposes the same TCP
	// peer + Forwarded-For header proxy chain; User-Agent lives in the
	// request header.
	ipAddr := req.Peer().Addr
	userAgent := req.Header().Get("User-Agent")

	resp, err := s.svc.Redeem(ctx, &promocodesvc.RedeemRequest{
		Code:           code,
		OrganizationID: tenant.OrganizationID,
		UserID:         tenant.UserID,
		UserRole:       tenant.UserRole,
		IPAddress:      ipAddr,
		UserAgent:      userAgent,
	})
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	return connect.NewResponse(toProtoRedeemResponse(resp)), nil
}

// GetRedemptionHistory returns redemptions for the caller's org. Any org
// member can read. Mirrors REST GET
// /api/v1/orgs/:slug/billing/promo-codes/history (promocode.go:95).
//
// Pagination: the service layer currently returns the full list (no
// paging at the repo layer). The proto envelope still ships limit/offset
// per conventions §8 so we can paginate later without a wire break.
func (s *Server) GetRedemptionHistory(
	ctx context.Context, req *connect.Request[promocodev1.GetRedemptionHistoryRequest],
) (*connect.Response[promocodev1.GetRedemptionHistoryResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	redemptions, err := s.svc.GetRedemptionHistory(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*promocodev1.Redemption, 0, len(redemptions))
	for _, r := range redemptions {
		items = append(items, toProtoRedemption(r))
	}
	return connect.NewResponse(&promocodev1.GetRedemptionHistoryResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  req.Msg.GetLimit(),
		Offset: req.Msg.GetOffset(),
	}), nil
}
