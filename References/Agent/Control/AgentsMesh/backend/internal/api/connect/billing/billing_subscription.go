package billingconnect

import (
	"context"
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

func (s *Server) GetSubscription(
	ctx context.Context, req *connect.Request[billingv1.GetSubscriptionRequest],
) (*connect.Response[billingv1.Subscription], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.GetSubscription(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSubscription(sub)), nil
}

func (s *Server) CreateSubscription(
	ctx context.Context, req *connect.Request[billingv1.CreateSubscriptionRequest],
) (*connect.Response[billingv1.Subscription], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.CreateSubscription(ctx, tenant.OrganizationID, req.Msg.GetPlanName())
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSubscription(sub)), nil
}

func (s *Server) UpdateSubscription(
	ctx context.Context, req *connect.Request[billingv1.UpdateSubscriptionRequest],
) (*connect.Response[billingv1.Subscription], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.UpdateSubscription(ctx, tenant.OrganizationID, req.Msg.GetPlanName())
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSubscription(sub)), nil
}

func (s *Server) CancelSubscription(
	ctx context.Context, req *connect.Request[billingv1.CancelSubscriptionRequest],
) (*connect.Response[billingv1.CancelSubscriptionResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if err := s.billingSvc.CancelSubscription(ctx, tenant.OrganizationID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&billingv1.CancelSubscriptionResponse{}), nil
}

func (s *Server) RequestCancelSubscription(
	ctx context.Context, req *connect.Request[billingv1.RequestCancelSubscriptionRequest],
) (*connect.Response[billingv1.RequestCancelSubscriptionResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.GetSubscription(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	if err := cancelViaProvider(ctx, s.billingSvc, sub, req.Msg.GetImmediate()); err != nil {
		return nil, err
	}

	if req.Msg.GetImmediate() {
		if err := s.billingSvc.CancelSubscription(ctx, tenant.OrganizationID); err != nil {
			return nil, mapServiceError(err)
		}
		return connect.NewResponse(&billingv1.RequestCancelSubscriptionResponse{Immediate: true}), nil
	}
	if err := s.billingSvc.SetCancelAtPeriodEnd(ctx, tenant.OrganizationID, true); err != nil {
		return nil, mapServiceError(err)
	}
	end := sub.CurrentPeriodEnd.UTC().Format("2006-01-02T15:04:05Z")
	return connect.NewResponse(&billingv1.RequestCancelSubscriptionResponse{
		CurrentPeriodEnd: &end,
	}), nil
}

func (s *Server) ReactivateSubscription(
	ctx context.Context, req *connect.Request[billingv1.ReactivateSubscriptionRequest],
) (*connect.Response[billingv1.Subscription], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.GetSubscription(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	if !sub.CancelAtPeriodEnd {
		return nil, connect.NewError(connect.CodeFailedPrecondition,
			errors.New("subscription is not pending cancellation"))
	}
	if err := reactivateViaProvider(ctx, s.billingSvc, sub); err != nil {
		return nil, err
	}
	if err := s.billingSvc.SetCancelAtPeriodEnd(ctx, tenant.OrganizationID, false); err != nil {
		return nil, mapServiceError(err)
	}
	updated, err := s.billingSvc.GetSubscription(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSubscription(updated)), nil
}

func (s *Server) UpgradeSubscription(
	ctx context.Context, req *connect.Request[billingv1.UpgradeSubscriptionRequest],
) (*connect.Response[billingv1.Subscription], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.UpgradePlan(ctx, tenant.OrganizationID, req.Msg.GetPlanName())
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoSubscription(sub)), nil
}

func (s *Server) ChangeBillingCycle(
	ctx context.Context, req *connect.Request[billingv1.ChangeBillingCycleRequest],
) (*connect.Response[billingv1.ChangeBillingCycleResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.GetSubscription(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	if sub.BillingCycle == req.Msg.GetBillingCycle() {
		return nil, connect.NewError(connect.CodeFailedPrecondition,
			errors.New("already on this billing cycle"))
	}
	if err := s.billingSvc.SetNextBillingCycle(ctx, tenant.OrganizationID, req.Msg.GetBillingCycle()); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&billingv1.ChangeBillingCycleResponse{
		CurrentCycle:  sub.BillingCycle,
		NextCycle:     req.Msg.GetBillingCycle(),
		EffectiveDate: sub.CurrentPeriodEnd.UTC().Format("2006-01-02T15:04:05Z"),
	}), nil
}

func (s *Server) UpdateAutoRenew(
	ctx context.Context, req *connect.Request[billingv1.UpdateAutoRenewRequest],
) (*connect.Response[billingv1.Subscription], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	sub, err := s.billingSvc.GetSubscription(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	if err := s.billingSvc.SetAutoRenew(ctx, tenant.OrganizationID, req.Msg.GetAutoRenew()); err != nil {
		return nil, mapServiceError(err)
	}
	sub.AutoRenew = req.Msg.GetAutoRenew()
	return connect.NewResponse(toProtoSubscription(sub)), nil
}

func mountSubscription(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetSubscriptionProcedure, connect.NewUnaryHandler(GetSubscriptionProcedure, srv.GetSubscription, opts...))
	mux.Handle(CreateSubscriptionProcedure, connect.NewUnaryHandler(CreateSubscriptionProcedure, srv.CreateSubscription, opts...))
	mux.Handle(UpdateSubscriptionProcedure, connect.NewUnaryHandler(UpdateSubscriptionProcedure, srv.UpdateSubscription, opts...))
	mux.Handle(CancelSubscriptionProcedure, connect.NewUnaryHandler(CancelSubscriptionProcedure, srv.CancelSubscription, opts...))
	mux.Handle(RequestCancelSubscriptionProcedure, connect.NewUnaryHandler(RequestCancelSubscriptionProcedure, srv.RequestCancelSubscription, opts...))
	mux.Handle(ReactivateSubscriptionProcedure, connect.NewUnaryHandler(ReactivateSubscriptionProcedure, srv.ReactivateSubscription, opts...))
	mux.Handle(UpgradeSubscriptionProcedure, connect.NewUnaryHandler(UpgradeSubscriptionProcedure, srv.UpgradeSubscription, opts...))
	mux.Handle(ChangeBillingCycleProcedure, connect.NewUnaryHandler(ChangeBillingCycleProcedure, srv.ChangeBillingCycle, opts...))
	mux.Handle(UpdateAutoRenewProcedure, connect.NewUnaryHandler(UpdateAutoRenewProcedure, srv.UpdateAutoRenew, opts...))
}
