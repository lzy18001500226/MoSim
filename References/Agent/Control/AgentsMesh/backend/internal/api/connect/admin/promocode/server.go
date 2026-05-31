// Package promocodeadminconnect hosts Connect-RPC handlers for the
// platform-admin promo-code surface. Mirrors
// backend/internal/api/rest/v1/admin/promo_codes*.go.
//
// Auth model: every RPC calls interceptors.ResolveSystemAdmin to mirror
// REST's AdminMiddleware (is_system_admin + is_active checks). The
// org-scoped PromoCodeService lives next door in
// backend/internal/api/connect/promocode/ — separate auth surface, so
// keep the packages split to prevent transport-level drift.
//
// Split rationale (CLAUDE.md 200-line rule):
//   - server.go         — service scaffolding + Mount (this file)
//   - handlers_query.go — List / Get / ListRedemptions
//   - handlers_write.go — Create / Update / Delete / Activate / Deactivate
//   - convert.go        — domain ↔ proto field translation
package promocodeadminconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/infra/database"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
)

const ServiceName = "proto.promocode.v1.PromoCodeAdminService"

const (
	ListPromoCodesProcedure            = "/" + ServiceName + "/ListPromoCodes"
	GetPromoCodeProcedure              = "/" + ServiceName + "/GetPromoCode"
	CreatePromoCodeProcedure           = "/" + ServiceName + "/CreatePromoCode"
	UpdatePromoCodeProcedure           = "/" + ServiceName + "/UpdatePromoCode"
	ActivatePromoCodeProcedure         = "/" + ServiceName + "/ActivatePromoCode"
	DeactivatePromoCodeProcedure       = "/" + ServiceName + "/DeactivatePromoCode"
	DeletePromoCodeProcedure           = "/" + ServiceName + "/DeletePromoCode"
	ListPromoCodeRedemptionsProcedure  = "/" + ServiceName + "/ListPromoCodeRedemptions"
)

// Server implements PromoCodeAdminService. `db` is threaded through for
// ResolveSystemAdmin's user lookup — same source as the REST
// AdminMiddleware so the two paths can't diverge on the is_system_admin
// check.
type Server struct {
	svc *adminservice.Service
	db  database.DB
}

func NewServer(svc *adminservice.Service, db database.DB) *Server {
	return &Server{svc: svc, db: db}
}

// Mount wires every PromoCodeAdminService procedure onto mux. The auth
// interceptor in opts validates the JWT; per-handler ResolveSystemAdmin
// then enforces the is_system_admin flag (handler-level so the interceptor
// stays generic across user-scoped + admin-scoped services).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListPromoCodesProcedure, connect.NewUnaryHandler(
		ListPromoCodesProcedure, srv.ListPromoCodes, opts...,
	))
	mux.Handle(GetPromoCodeProcedure, connect.NewUnaryHandler(
		GetPromoCodeProcedure, srv.GetPromoCode, opts...,
	))
	mux.Handle(CreatePromoCodeProcedure, connect.NewUnaryHandler(
		CreatePromoCodeProcedure, srv.CreatePromoCode, opts...,
	))
	mux.Handle(UpdatePromoCodeProcedure, connect.NewUnaryHandler(
		UpdatePromoCodeProcedure, srv.UpdatePromoCode, opts...,
	))
	mux.Handle(ActivatePromoCodeProcedure, connect.NewUnaryHandler(
		ActivatePromoCodeProcedure, srv.ActivatePromoCode, opts...,
	))
	mux.Handle(DeactivatePromoCodeProcedure, connect.NewUnaryHandler(
		DeactivatePromoCodeProcedure, srv.DeactivatePromoCode, opts...,
	))
	mux.Handle(DeletePromoCodeProcedure, connect.NewUnaryHandler(
		DeletePromoCodeProcedure, srv.DeletePromoCode, opts...,
	))
	mux.Handle(ListPromoCodeRedemptionsProcedure, connect.NewUnaryHandler(
		ListPromoCodeRedemptionsProcedure, srv.ListPromoCodeRedemptions, opts...,
	))
}

// mapServiceError translates admin-service sentinels to Connect codes.
// Mirrors apierr translation in REST handlers — keeping the mapping in
// one place prevents drift between the two transports.
func mapServiceError(err error) error {
	switch {
	case errors.Is(err, adminservice.ErrPromoCodeNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, adminservice.ErrPromoCodeAlreadyExists),
		errors.Is(err, adminservice.ErrPromoCodeHasRedemptions):
		return connect.NewError(connect.CodeAlreadyExists, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
