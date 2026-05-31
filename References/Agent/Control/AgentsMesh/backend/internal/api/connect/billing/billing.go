// Package billingconnect hosts Connect-RPC handlers for the billing domain.
// Mirrors backend/internal/api/rest/v1/billing_*.go but exposes the data
// plane via Connect (binary protobuf wire, see conventions.md §2.5). REST
// stays mounted in parallel; the migration runs dual-track until all 26
// services have flipped.
//
// Two services in this package:
//   - BillingService — org-scoped, auth-required (ResolveOrgScope).
//   - BillingPublicService — no auth, no org_slug (PR #334 fix for the
//     landing-page pricing card).
//
// Handler shape follows runbook §3 + conventions §3.5: every authenticated
// RPC calls ResolveOrgScope first; ListInvoices/ListPlans follow the
// {items,total,limit,offset} envelope; errors map to Connect codes
// (conventions §10).
//
// Split rationale (CLAUDE.md 200-line rule):
//   - billing.go              — service scaffolding (this file)
//   - billing_subscription.go — subscription CRUD + lifecycle RPCs
//   - billing_checkout.go     — checkout flow + provider integration
//   - billing_seats.go        — seat usage + purchase
//   - billing_overview.go     — overview, plans, invoices, deployment
//   - billing_public.go       — BillingPublicService (unauthenticated)
//   - billing_convert.go      — domain ↔ proto field translation
//   - billing_errors.go       — error mapping + role guards
package billingconnect

import (
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
)

const ServiceName = "proto.billing.v1.BillingService"

const (
	GetOverviewProcedure               = "/" + ServiceName + "/GetOverview"
	ListPlansProcedure                 = "/" + ServiceName + "/ListPlans"
	GetSubscriptionProcedure           = "/" + ServiceName + "/GetSubscription"
	CreateSubscriptionProcedure        = "/" + ServiceName + "/CreateSubscription"
	UpdateSubscriptionProcedure        = "/" + ServiceName + "/UpdateSubscription"
	CancelSubscriptionProcedure        = "/" + ServiceName + "/CancelSubscription"
	RequestCancelSubscriptionProcedure = "/" + ServiceName + "/RequestCancelSubscription"
	ReactivateSubscriptionProcedure    = "/" + ServiceName + "/ReactivateSubscription"
	UpgradeSubscriptionProcedure       = "/" + ServiceName + "/UpgradeSubscription"
	ChangeBillingCycleProcedure        = "/" + ServiceName + "/ChangeBillingCycle"
	UpdateAutoRenewProcedure           = "/" + ServiceName + "/UpdateAutoRenew"
	GetSeatUsageProcedure              = "/" + ServiceName + "/GetSeatUsage"
	PurchaseSeatsProcedure             = "/" + ServiceName + "/PurchaseSeats"
	ListInvoicesProcedure              = "/" + ServiceName + "/ListInvoices"
	CreateCheckoutProcedure            = "/" + ServiceName + "/CreateCheckout"
	GetCheckoutStatusProcedure         = "/" + ServiceName + "/GetCheckoutStatus"
	GetDeploymentInfoProcedure         = "/" + ServiceName + "/GetDeploymentInfo"
	GetUsageProcedure                  = "/" + ServiceName + "/GetUsage"
	GetUsageHistoryProcedure           = "/" + ServiceName + "/GetUsageHistory"
	CheckQuotaProcedure                = "/" + ServiceName + "/CheckQuota"
	SetCustomQuotaProcedure            = "/" + ServiceName + "/SetCustomQuota"
	CreateCustomerPortalProcedure      = "/" + ServiceName + "/CreateCustomerPortal"
)

// Server implements BillingService — authenticated, org-scoped.
type Server struct {
	billingSvc *billingsvc.Service
	orgSvc     middleware.OrganizationService
}

func NewServer(b *billingsvc.Service, o middleware.OrganizationService) *Server {
	return &Server{billingSvc: b, orgSvc: o}
}

// Mount registers all BillingService procedures on mux behind the auth
// interceptor supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mountSubscription(mux, srv, opts...)
	mountCheckout(mux, srv, opts...)
	mountSeats(mux, srv, opts...)
	mountOverview(mux, srv, opts...)
	mountUsage(mux, srv, opts...)
}
