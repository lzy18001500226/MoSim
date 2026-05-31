package billingconnect

import (
	"context"
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

func (s *Server) GetSeatUsage(
	ctx context.Context, req *connect.Request[billingv1.GetSeatUsageRequest],
) (*connect.Response[billingv1.SeatUsage], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	usage, err := s.billingSvc.GetSeatUsage(ctx, tenant.OrganizationID)
	if err != nil {
		if errors.Is(err, billingsvc.ErrSubscriptionNotFound) {
			// Mirror REST default for free plan (billing_seats.go:18).
			return connect.NewResponse(&billingv1.SeatUsage{
				TotalSeats: 1, UsedSeats: 1, AvailableSeats: 0, MaxSeats: 1, CanAddSeats: false,
			}), nil
		}
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSeatUsage(usage)), nil
}

func (s *Server) PurchaseSeats(
	ctx context.Context, req *connect.Request[billingv1.PurchaseSeatsRequest],
) (*connect.Response[billingv1.PurchaseSeatsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if err := s.billingSvc.UpdateSeats(ctx, tenant.OrganizationID, int(req.Msg.GetSeats())); err != nil {
		return nil, mapServiceError(err)
	}
	out := &billingv1.PurchaseSeatsResponse{}
	if usage, e := s.billingSvc.GetSeatUsage(ctx, tenant.OrganizationID); e == nil {
		out.Seats = toProtoSeatUsage(usage)
	}
	return connect.NewResponse(out), nil
}

func mountSeats(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetSeatUsageProcedure, connect.NewUnaryHandler(GetSeatUsageProcedure, srv.GetSeatUsage, opts...))
	mux.Handle(PurchaseSeatsProcedure, connect.NewUnaryHandler(PurchaseSeatsProcedure, srv.PurchaseSeats, opts...))
}
