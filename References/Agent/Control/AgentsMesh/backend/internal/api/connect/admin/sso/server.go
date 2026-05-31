// Package ssoadminconnect hosts Connect-RPC handlers for the
// platform-admin SSO configuration surface. Mirrors REST handlers in
// backend/internal/api/rest/v1/admin/sso.go (CRUD + list) and
// backend/internal/api/rest/v1/admin/sso_actions.go (test/enable/disable).
//
// Auth model: every RPC calls interceptors.ResolveSystemAdmin to mirror
// REST's AdminMiddleware (is_system_admin + is_active checks). The
// public SSOService (sso.proto: Discover + LdapAuth) lives in
// backend/internal/api/connect/sso/ — separate auth surface (no
// interceptor), so keep the packages split to prevent transport-level
// drift.
//
// Split rationale (CLAUDE.md 200-line rule):
//   - server.go              — service scaffolding + Mount (this file)
//   - convert.go             — domain ↔ proto field translation
//   - audit.go               — Connect-context audit log helper
//   - handlers_query.go      — ListSSOConfigs / GetSSOConfig
//   - handlers_mutations.go  — Create / Update / Delete / Enable / Disable
//   - handlers_test.go       — TestSSOConnection
package ssoadminconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/infra/database"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	ssoservice "github.com/anthropics/agentsmesh/backend/internal/service/sso"
)

const ServiceName = "proto.sso.v1.SSOAdminService"

const (
	ListSSOConfigsProcedure    = "/" + ServiceName + "/ListSSOConfigs"
	GetSSOConfigProcedure      = "/" + ServiceName + "/GetSSOConfig"
	CreateSSOConfigProcedure   = "/" + ServiceName + "/CreateSSOConfig"
	UpdateSSOConfigProcedure   = "/" + ServiceName + "/UpdateSSOConfig"
	DeleteSSOConfigProcedure   = "/" + ServiceName + "/DeleteSSOConfig"
	TestSSOConnectionProcedure = "/" + ServiceName + "/TestSSOConnection"
	EnableSSOConfigProcedure   = "/" + ServiceName + "/EnableSSOConfig"
	DisableSSOConfigProcedure  = "/" + ServiceName + "/DisableSSOConfig"
)

// Server implements SSOAdminService. `db` is threaded through for
// ResolveSystemAdmin's user lookup — same source as the REST
// AdminMiddleware so the two paths can't diverge on the is_system_admin
// check. `adminSvc` is used for audit logging; `ssoSvc` performs CRUD.
type Server struct {
	ssoSvc   *ssoservice.Service
	adminSvc *adminservice.Service
	db       database.DB
}

func NewServer(ssoSvc *ssoservice.Service, adminSvc *adminservice.Service, db database.DB) *Server {
	return &Server{ssoSvc: ssoSvc, adminSvc: adminSvc, db: db}
}

// Mount wires every SSOAdminService procedure onto mux. The auth
// interceptor in opts validates the JWT; per-handler ResolveSystemAdmin
// enforces is_system_admin.
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListSSOConfigsProcedure, connect.NewUnaryHandler(
		ListSSOConfigsProcedure, srv.ListSSOConfigs, opts...,
	))
	mux.Handle(GetSSOConfigProcedure, connect.NewUnaryHandler(
		GetSSOConfigProcedure, srv.GetSSOConfig, opts...,
	))
	mux.Handle(CreateSSOConfigProcedure, connect.NewUnaryHandler(
		CreateSSOConfigProcedure, srv.CreateSSOConfig, opts...,
	))
	mux.Handle(UpdateSSOConfigProcedure, connect.NewUnaryHandler(
		UpdateSSOConfigProcedure, srv.UpdateSSOConfig, opts...,
	))
	mux.Handle(DeleteSSOConfigProcedure, connect.NewUnaryHandler(
		DeleteSSOConfigProcedure, srv.DeleteSSOConfig, opts...,
	))
	mux.Handle(TestSSOConnectionProcedure, connect.NewUnaryHandler(
		TestSSOConnectionProcedure, srv.TestSSOConnection, opts...,
	))
	mux.Handle(EnableSSOConfigProcedure, connect.NewUnaryHandler(
		EnableSSOConfigProcedure, srv.EnableSSOConfig, opts...,
	))
	mux.Handle(DisableSSOConfigProcedure, connect.NewUnaryHandler(
		DisableSSOConfigProcedure, srv.DisableSSOConfig, opts...,
	))
}

// mapServiceError translates sso-service sentinels to Connect codes,
// mirroring apierr translation in REST handlers (sso.go:110-119, 138).
func mapServiceError(err error) error {
	switch {
	case errors.Is(err, ssoservice.ErrConfigNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, ssoservice.ErrDuplicateConfig):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, ssoservice.ErrInvalidProtocol):
		return connect.NewError(connect.CodeInvalidArgument, err)
	}
	var validationErr *ssoservice.ValidationError
	if errors.As(err, &validationErr) {
		return connect.NewError(connect.CodeInvalidArgument, validationErr)
	}
	return connect.NewError(connect.CodeInternal, err)
}

// boolPtr is a local helper for Enable/Disable handlers that build an
// UpdateConfigRequest with a single pointer field.
func boolPtr(b bool) *bool { return &b }
