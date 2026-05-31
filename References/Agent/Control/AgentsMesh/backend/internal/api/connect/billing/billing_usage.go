package billingconnect

import (
	"context"
	"errors"
	"fmt"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	"github.com/anthropics/agentsmesh/backend/internal/service/payment"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

// GetUsage mirrors REST `GET /api/v1/orgs/{slug}/billing/usage`. When
// `usage_type` is set returns a single metric; otherwise the full usage
// overview piggy-backs on `GetBillingOverview`.
func (s *Server) GetUsage(
	ctx context.Context, req *connect.Request[billingv1.GetUsageRequest],
) (*connect.Response[billingv1.GetUsageResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if t := req.Msg.GetUsageType(); t != "" {
		value, err := s.billingSvc.GetUsage(ctx, tenant.OrganizationID, t)
		if err != nil {
			return nil, mapServiceError(err)
		}
		mt := t
		return connect.NewResponse(&billingv1.GetUsageResponse{
			MetricValue: &value,
			MetricType:  &mt,
		}), nil
	}
	overview, err := s.billingSvc.GetBillingOverview(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&billingv1.GetUsageResponse{
		Overview: toProtoUsage(&overview.Usage),
	}), nil
}

// GetUsageHistory mirrors REST `GET /api/v1/orgs/{slug}/billing/usage/history`.
// `months` is clamped to [1, 12] (REST defaulted to 3 on out-of-range input).
func (s *Server) GetUsageHistory(
	ctx context.Context, req *connect.Request[billingv1.GetUsageHistoryRequest],
) (*connect.Response[billingv1.GetUsageHistoryResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	months := int(req.Msg.GetMonths())
	if months < 1 || months > 12 {
		months = 3
	}
	records, err := s.billingSvc.GetUsageHistory(ctx, tenant.OrganizationID, req.Msg.GetUsageType(), months)
	if err != nil {
		return nil, mapServiceError(err)
	}
	out := make([]*billingv1.UsageRecord, 0, len(records))
	for _, r := range records {
		out = append(out, &billingv1.UsageRecord{
			Id:             r.ID,
			OrganizationId: r.OrganizationID,
			UsageType:      r.UsageType,
			Quantity:       r.Quantity,
			PeriodStart:    r.PeriodStart.Format("2006-01-02T15:04:05Z07:00"),
			PeriodEnd:      r.PeriodEnd.Format("2006-01-02T15:04:05Z07:00"),
			CreatedAt:      r.CreatedAt.Format("2006-01-02T15:04:05Z07:00"),
		})
	}
	return connect.NewResponse(&billingv1.GetUsageHistoryResponse{Records: out}), nil
}

// CheckQuota mirrors REST `GET /api/v1/orgs/{slug}/billing/quota/check`.
// Resource is required; amount < 1 clamps to 1 (REST behavior).
func (s *Server) CheckQuota(
	ctx context.Context, req *connect.Request[billingv1.CheckQuotaRequest],
) (*connect.Response[billingv1.CheckQuotaResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetResource() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("resource is required"))
	}
	amount := int(req.Msg.GetAmount())
	if amount < 1 {
		amount = 1
	}
	tenant := middleware.GetTenant(ctx)
	if err := s.billingSvc.CheckQuota(ctx, tenant.OrganizationID, req.Msg.GetResource(), amount); err != nil {
		// mapServiceError already routes ErrQuotaExceeded /
		// ErrSubscriptionFrozen / ErrSubscriptionNotFound — same surface as
		// the REST `handleQuotaError` helper, just on Connect codes.
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&billingv1.CheckQuotaResponse{Available: true}), nil
}

// SetCustomQuota mirrors REST `POST /api/v1/orgs/{slug}/billing/quota`. Owner /
// admin only — matches REST role guard.
func (s *Server) SetCustomQuota(
	ctx context.Context, req *connect.Request[billingv1.SetCustomQuotaRequest],
) (*connect.Response[billingv1.SetCustomQuotaResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if tenant.UserRole != "owner" && tenant.UserRole != "admin" {
		return nil, connect.NewError(connect.CodePermissionDenied,
			errors.New("owner or admin role required"))
	}
	if err := s.billingSvc.SetCustomQuota(ctx, tenant.OrganizationID, req.Msg.GetResource(), int(req.Msg.GetLimit())); err != nil {
		if errors.Is(err, billingsvc.ErrSubscriptionNotFound) {
			return nil, connect.NewError(connect.CodeNotFound,
				errors.New("no active subscription"))
		}
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&billingv1.SetCustomQuotaResponse{Message: "custom quota updated"}), nil
}

// CreateCustomerPortal mirrors REST `POST /api/v1/orgs/{slug}/billing/customer-portal`.
// Owner only — payment provider redirect URL flow.
func (s *Server) CreateCustomerPortal(
	ctx context.Context, req *connect.Request[billingv1.CreateCustomerPortalRequest],
) (*connect.Response[billingv1.CreateCustomerPortalResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if tenant.UserRole != "owner" {
		return nil, connect.NewError(connect.CodePermissionDenied,
			errors.New("owner role required"))
	}
	sub, err := s.billingSvc.GetSubscription(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound,
			errors.New("no active subscription"))
	}
	factory := s.billingSvc.GetPaymentFactory()
	if factory == nil {
		return nil, connect.NewError(connect.CodeUnavailable,
			errors.New("payment service not configured"))
	}
	provider, customerID, subscriptionID, err := pickPortalProvider(factory, sub)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	if provider == nil {
		return nil, connect.NewError(connect.CodeFailedPrecondition,
			errors.New("no payment provider associated with this subscription"))
	}
	subProvider, ok := provider.(payment.SubscriptionProvider)
	if !ok {
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("provider does not support customer portal"))
	}
	resp, err := subProvider.GetCustomerPortalURL(ctx, &payment.CustomerPortalRequest{
		CustomerID:     customerID,
		SubscriptionID: subscriptionID,
		ReturnURL:      req.Msg.GetReturnUrl(),
	})
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			fmt.Errorf("failed to create portal session: %w", err))
	}
	return connect.NewResponse(&billingv1.CreateCustomerPortalResponse{Url: resp.URL}), nil
}

// pickPortalProvider mirrors REST `resolveCustomerPortalProvider` — LemonSqueezy
// first, then Stripe; matches the historical ordering.
func pickPortalProvider(factory *payment.Factory, sub *billing.Subscription) (payment.Provider, string, string, error) {
	if sub.LemonSqueezyCustomerID != nil {
		p, err := factory.GetProvider(billing.PaymentProviderLemonSqueezy)
		if err != nil {
			return nil, "", "", err
		}
		subID := ""
		if sub.LemonSqueezySubscriptionID != nil {
			subID = *sub.LemonSqueezySubscriptionID
		}
		return p, *sub.LemonSqueezyCustomerID, subID, nil
	}
	if sub.StripeCustomerID != nil {
		p, err := factory.GetProvider(billing.PaymentProviderStripe)
		if err != nil {
			return nil, "", "", err
		}
		subID := ""
		if sub.StripeSubscriptionID != nil {
			subID = *sub.StripeSubscriptionID
		}
		return p, *sub.StripeCustomerID, subID, nil
	}
	return nil, "", "", nil
}

func mountUsage(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetUsageProcedure, connect.NewUnaryHandler(GetUsageProcedure, srv.GetUsage, opts...))
	mux.Handle(GetUsageHistoryProcedure, connect.NewUnaryHandler(GetUsageHistoryProcedure, srv.GetUsageHistory, opts...))
	mux.Handle(CheckQuotaProcedure, connect.NewUnaryHandler(CheckQuotaProcedure, srv.CheckQuota, opts...))
	mux.Handle(SetCustomQuotaProcedure, connect.NewUnaryHandler(SetCustomQuotaProcedure, srv.SetCustomQuota, opts...))
	mux.Handle(CreateCustomerPortalProcedure, connect.NewUnaryHandler(CreateCustomerPortalProcedure, srv.CreateCustomerPortal, opts...))
}
