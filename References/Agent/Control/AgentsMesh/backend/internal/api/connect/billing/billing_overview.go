package billingconnect

import (
	"context"
	"errors"
	"fmt"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

func (s *Server) GetOverview(
	ctx context.Context, req *connect.Request[billingv1.GetOverviewRequest],
) (*connect.Response[billingv1.BillingOverview], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	out, err := s.billingSvc.GetBillingOverview(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoOverview(out)), nil
}

func (s *Server) ListPlans(
	ctx context.Context, req *connect.Request[billingv1.ListPlansRequest],
) (*connect.Response[billingv1.ListPlansResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	plans, err := s.billingSvc.ListPlans(ctx)
	if err != nil {
		return nil, mapServiceError(err)
	}
	items := make([]*billingv1.SubscriptionPlan, 0, len(plans))
	for _, p := range plans {
		items = append(items, toProtoPlan(p))
	}
	return connect.NewResponse(&billingv1.ListPlansResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}

func (s *Server) ListInvoices(
	ctx context.Context, req *connect.Request[billingv1.ListInvoicesRequest],
) (*connect.Response[billingv1.ListInvoicesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	limit := int(req.Msg.GetLimit())
	if limit < 1 || limit > 100 {
		limit = 20
	}
	offset := int(req.Msg.GetOffset())
	invoices, err := s.billingSvc.GetInvoicesByOrg(ctx, tenant.OrganizationID, limit, offset)
	if err != nil {
		return nil, mapServiceError(err)
	}
	items := make([]*billingv1.Invoice, 0, len(invoices))
	for _, i := range invoices {
		items = append(items, toProtoInvoice(i))
	}
	return connect.NewResponse(&billingv1.ListInvoicesResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  int32(limit),
		Offset: int32(offset),
	}), nil
}

func (s *Server) GetCheckoutStatus(
	ctx context.Context, req *connect.Request[billingv1.GetCheckoutStatusRequest],
) (*connect.Response[billingv1.CheckoutStatus], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	order, err := s.billingSvc.GetPaymentOrderByNo(ctx, req.Msg.GetOrderNo())
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound, fmt.Errorf("order not found"))
	}
	if order.OrganizationID != tenant.OrganizationID {
		return nil, connect.NewError(connect.CodePermissionDenied,
			errors.New("order belongs to another organization"))
	}
	return connect.NewResponse(toProtoCheckoutStatus(order)), nil
}

func (s *Server) GetDeploymentInfo(
	ctx context.Context, req *connect.Request[billingv1.GetDeploymentInfoRequest],
) (*connect.Response[billingv1.DeploymentInfo], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	_ = ctx
	return connect.NewResponse(toProtoDeploymentInfo(s.billingSvc.GetDeploymentInfo())), nil
}

func mountOverview(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetOverviewProcedure, connect.NewUnaryHandler(GetOverviewProcedure, srv.GetOverview, opts...))
	mux.Handle(ListPlansProcedure, connect.NewUnaryHandler(ListPlansProcedure, srv.ListPlans, opts...))
	mux.Handle(ListInvoicesProcedure, connect.NewUnaryHandler(ListInvoicesProcedure, srv.ListInvoices, opts...))
	mux.Handle(GetCheckoutStatusProcedure, connect.NewUnaryHandler(GetCheckoutStatusProcedure, srv.GetCheckoutStatus, opts...))
	mux.Handle(GetDeploymentInfoProcedure, connect.NewUnaryHandler(GetDeploymentInfoProcedure, srv.GetDeploymentInfo, opts...))
}
