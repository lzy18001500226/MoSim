// Package promocodeconnect hosts Connect-RPC handlers for the promo code
// domain. Mirrors backend/internal/api/rest/v1/promocode.go but exposes
// the data plane via Connect (binary protobuf wire, conventions §2.5). REST
// stays mounted in parallel; the migration runs dual-track until all 26
// services have flipped.
//
// Scope: Web's `getPromoCodeService()` org-scoped surface
// (Validate / Redeem / GetRedemptionHistory). The platform-admin CRUD over
// promo codes (admin/promo_codes*.go) stays on REST during this migration —
// those endpoints are gated by ADMIN middleware, not org middleware, so
// they migrate as part of the admin/ surface sweep.
//
// Handler shape follows runbook §3 + conventions §3.5: each RPC calls
// ResolveOrgScope first; the list response follows {items, total, limit,
// offset}; errors map to Connect codes (conventions §10).
//
// Split rationale (CLAUDE.md 200-line rule):
//   - promocode.go         — service scaffolding + Mount (this file)
//   - promocode_handlers.go — Validate / Redeem / GetRedemptionHistory
//   - promocode_convert.go — domain ↔ proto field translation
package promocodeconnect

import (
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	promocodesvc "github.com/anthropics/agentsmesh/backend/internal/service/promocode"
)

const ServiceName = "proto.promocode.v1.PromoCodeService"

const (
	ValidateProcedure             = "/" + ServiceName + "/Validate"
	RedeemProcedure               = "/" + ServiceName + "/Redeem"
	GetRedemptionHistoryProcedure = "/" + ServiceName + "/GetRedemptionHistory"
)

// Server implements PromoCodeService — the org-scoped surface used by the
// web client (`getPromoCodeService()`). Constructor mirrors REST's
// NewPromoCodeHandler at promocode.go:22 but threads orgSvc so
// ResolveOrgScope can lookup tenants from the request body's `org_slug`
// (Connect URLs have no path params; conventions §3.5).
type Server struct {
	svc    *promocodesvc.Service
	orgSvc middleware.OrganizationService
}

func NewServer(svc *promocodesvc.Service, orgSvc middleware.OrganizationService) *Server {
	return &Server{svc: svc, orgSvc: orgSvc}
}

// Mount registers all PromoCodeService procedures behind the auth interceptor
// supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ValidateProcedure, connect.NewUnaryHandler(
		ValidateProcedure, srv.Validate, opts...,
	))
	mux.Handle(RedeemProcedure, connect.NewUnaryHandler(
		RedeemProcedure, srv.Redeem, opts...,
	))
	mux.Handle(GetRedemptionHistoryProcedure, connect.NewUnaryHandler(
		GetRedemptionHistoryProcedure, srv.GetRedemptionHistory, opts...,
	))
}
