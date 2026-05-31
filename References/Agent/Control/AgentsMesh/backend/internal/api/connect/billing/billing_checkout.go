package billingconnect

import (
	"context"
	"errors"
	"fmt"
	"log/slog"
	"net/http"

	"connectrpc.com/connect"
	"github.com/google/uuid"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	billingdomain "github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	"github.com/anthropics/agentsmesh/backend/internal/service/payment"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

func (s *Server) CreateCheckout(
	ctx context.Context, req *connect.Request[billingv1.CreateCheckoutRequest],
) (*connect.Response[billingv1.CreateCheckoutResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	if err := validateCheckoutRequest(req.Msg); err != nil {
		return nil, err
	}

	factory := s.billingSvc.GetPaymentFactory()
	if factory == nil {
		return nil, connect.NewError(connect.CodeUnavailable,
			errors.New("payment service not configured"))
	}

	provider, providerName, err := pickCheckoutProvider(factory, req.Msg.GetProvider())
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}

	priceCalc, err := calculateCheckoutPrice(ctx, s.billingSvc, tenant.OrganizationID, req.Msg)
	if err != nil {
		return nil, err
	}

	return s.createCheckoutSession(ctx, tenant, req.Msg, priceCalc, providerName, provider)
}

func validateCheckoutRequest(req *billingv1.CreateCheckoutRequest) error {
	switch req.GetOrderType() {
	case billingdomain.OrderTypeSubscription,
		billingdomain.OrderTypePlanUpgrade,
		billingdomain.OrderTypeSeatPurchase,
		billingdomain.OrderTypeRenewal:
		// ok
	default:
		return connect.NewError(connect.CodeInvalidArgument,
			fmt.Errorf("invalid order_type: %s", req.GetOrderType()))
	}
	if (req.GetOrderType() == billingdomain.OrderTypeSubscription ||
		req.GetOrderType() == billingdomain.OrderTypePlanUpgrade) && req.GetPlanName() == "" {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("plan_name is required for subscription/plan_upgrade"))
	}
	if req.GetOrderType() == billingdomain.OrderTypeSeatPurchase && req.GetSeats() <= 0 {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("seats must be positive for seat_purchase"))
	}
	if req.GetSuccessUrl() == "" || req.GetCancelUrl() == "" {
		return connect.NewError(connect.CodeInvalidArgument,
			errors.New("success_url and cancel_url are required"))
	}
	return nil
}

func pickCheckoutProvider(factory *payment.Factory, requested string) (payment.Provider, string, error) {
	if requested != "" {
		p, err := factory.GetProvider(requested)
		if err != nil {
			return nil, "", err
		}
		return p, requested, nil
	}
	p, err := factory.GetDefaultProvider()
	if err != nil {
		return nil, "", err
	}
	return p, p.GetProviderName(), nil
}

func calculateCheckoutPrice(
	ctx context.Context, svc *billingsvc.Service, orgID int64, req *billingv1.CreateCheckoutRequest,
) (*billingsvc.PriceCalculation, error) {
	billingCycle := req.GetBillingCycle()
	if billingCycle == "" {
		billingCycle = billingdomain.BillingCycleMonthly
	}

	switch req.GetOrderType() {
	case billingdomain.OrderTypeSubscription:
		seats := int(req.GetSeats())
		if seats <= 0 {
			seats = 1
		}
		p, err := svc.CalculateSubscriptionPrice(ctx, req.GetPlanName(), billingCycle, seats)
		if err != nil {
			return nil, connect.NewError(connect.CodeInvalidArgument, err)
		}
		return p, nil
	case billingdomain.OrderTypePlanUpgrade:
		p, err := svc.CalculateUpgradePrice(ctx, orgID, req.GetPlanName())
		if err != nil {
			return nil, connect.NewError(connect.CodeFailedPrecondition,
				fmt.Errorf("upgrade calculation failed: %w", err))
		}
		return p, nil
	case billingdomain.OrderTypeSeatPurchase:
		p, err := svc.CalculateSeatPurchasePrice(ctx, orgID, int(req.GetSeats()))
		if err != nil {
			return nil, mapServiceError(err)
		}
		return p, nil
	case billingdomain.OrderTypeRenewal:
		p, err := svc.CalculateRenewalPrice(ctx, orgID, billingCycle)
		if err != nil {
			return nil, connect.NewError(connect.CodeFailedPrecondition,
				errors.New("no subscription to renew"))
		}
		return p, nil
	default:
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("invalid order type"))
	}
}

func (s *Server) createCheckoutSession(
	ctx context.Context, tenant *middleware.TenantContext,
	req *billingv1.CreateCheckoutRequest, priceCalc *billingsvc.PriceCalculation,
	providerName string, provider payment.Provider,
) (*connect.Response[billingv1.CreateCheckoutResponse], error) {
	var planID *int64
	if priceCalc.PlanID > 0 {
		v := priceCalc.PlanID
		planID = &v
	}
	orderNo := fmt.Sprintf("ORD-%d-%s", tenant.OrganizationID, uuid.New().String()[:8])

	metadata := map[string]string{"order_no": orderNo}
	if priceCalc.LemonSqueezyVariantID != "" {
		metadata["variant_id"] = priceCalc.LemonSqueezyVariantID
	}
	if priceCalc.StripePrice != "" {
		metadata["stripe_price_id"] = priceCalc.StripePrice
	}

	checkoutReq := &payment.CheckoutRequest{
		OrganizationID: tenant.OrganizationID,
		UserID:         tenant.UserID,
		OrderType:      req.GetOrderType(),
		BillingCycle:   req.GetBillingCycle(),
		Seats:          priceCalc.Seats,
		Currency:       "usd",
		Amount:         priceCalc.Amount,
		ActualAmount:   priceCalc.ActualAmount,
		SuccessURL:     req.GetSuccessUrl(),
		CancelURL:      req.GetCancelUrl(),
		IdempotencyKey: orderNo,
		Metadata:       metadata,
	}
	if planID != nil {
		checkoutReq.PlanID = *planID
	}
	resp, err := provider.CreateCheckoutSession(ctx, checkoutReq)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal,
			fmt.Errorf("failed to create checkout: %w", err))
	}

	order := &billingdomain.PaymentOrder{
		OrganizationID:  tenant.OrganizationID,
		OrderNo:         orderNo,
		ExternalOrderNo: &resp.ExternalOrderNo,
		OrderType:       req.GetOrderType(),
		PlanID:          planID,
		BillingCycle:    req.GetBillingCycle(),
		Seats:           priceCalc.Seats,
		Amount:          priceCalc.Amount,
		ActualAmount:    priceCalc.ActualAmount,
		Currency:        "usd",
		Status:          billingdomain.OrderStatusPending,
		PaymentProvider: providerName,
		ExpiresAt:       &resp.ExpiresAt,
		CreatedByID:     tenant.UserID,
	}
	if err := s.billingSvc.CreatePaymentOrder(ctx, order); err != nil {
		slog.ErrorContext(ctx, "failed to save payment order",
			"order_no", orderNo, "error", err)
		return nil, connect.NewError(connect.CodeInternal,
			errors.New("failed to create payment order"))
	}

	out := &billingv1.CreateCheckoutResponse{
		OrderNo:    orderNo,
		SessionId:  resp.SessionID,
		SessionUrl: resp.SessionURL,
		ExpiresAt:  protoconv.RFC3339(resp.ExpiresAt),
		Provider:   providerName,
	}
	if resp.QRCodeURL != "" {
		v := resp.QRCodeURL
		out.QrCodeUrl = &v
	}
	return connect.NewResponse(out), nil
}

func mountCheckout(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(CreateCheckoutProcedure, connect.NewUnaryHandler(CreateCheckoutProcedure, srv.CreateCheckout, opts...))
}
