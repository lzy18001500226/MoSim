package billingconnect

import (
	"context"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

// PublicServiceName is the unauthenticated pricing surface (proto §54). The
// landing page hits this without an org_slug — see conventions §3.5
// "User-scoped / Platform-admin scoped" exception.
const PublicServiceName = "proto.billing.v1.BillingPublicService"

const (
	GetPublicPricingProcedure        = "/" + PublicServiceName + "/GetPublicPricing"
	GetPublicDeploymentInfoProcedure = "/" + PublicServiceName + "/GetPublicDeploymentInfo"
)

// PublicServer hosts BillingPublicService — pricing card + deployment info.
// Auth interceptor is bypassed for these procedures (no org scope, no JWT).
type PublicServer struct {
	billingSvc *billingsvc.Service
}

func NewPublicServer(b *billingsvc.Service) *PublicServer {
	return &PublicServer{billingSvc: b}
}

func (p *PublicServer) GetPublicPricing(
	ctx context.Context, req *connect.Request[billingv1.GetPublicPricingRequest],
) (*connect.Response[billingv1.PublicPricingResponse], error) {
	info := p.billingSvc.GetDeploymentInfo()
	currency := billing.CurrencyUSD
	if info.DeploymentType == "cn" {
		currency = billing.CurrencyCNY
	}
	if req.Msg.Currency != nil && *req.Msg.Currency != "" {
		currency = *req.Msg.Currency
	}

	plansWithPrices, err := p.billingSvc.ListPlansWithPrices(ctx, currency)
	if err != nil {
		return nil, mapServiceError(err)
	}

	plans := make([]*billingv1.PublicPlanPricing, 0, len(plansWithPrices))
	for _, pwp := range plansWithPrices {
		plans = append(plans, toProtoPublicPlanPricing(pwp.Plan, pwp.Price))
	}
	return connect.NewResponse(&billingv1.PublicPricingResponse{
		DeploymentType: info.DeploymentType,
		Currency:       currency,
		Plans:          plans,
	}), nil
}

func (p *PublicServer) GetPublicDeploymentInfo(
	_ context.Context, _ *connect.Request[billingv1.GetPublicDeploymentInfoRequest],
) (*connect.Response[billingv1.DeploymentInfo], error) {
	return connect.NewResponse(toProtoDeploymentInfo(p.billingSvc.GetDeploymentInfo())), nil
}

// MountPublic registers public RPCs WITHOUT the auth interceptor. Caller
// passes `nil` for opts or only interceptors that don't require auth.
func MountPublic(mux *http.ServeMux, srv *PublicServer, opts ...connect.HandlerOption) {
	mux.Handle(GetPublicPricingProcedure, connect.NewUnaryHandler(GetPublicPricingProcedure, srv.GetPublicPricing, opts...))
	mux.Handle(GetPublicDeploymentInfoProcedure, connect.NewUnaryHandler(GetPublicDeploymentInfoProcedure, srv.GetPublicDeploymentInfo, opts...))
}
