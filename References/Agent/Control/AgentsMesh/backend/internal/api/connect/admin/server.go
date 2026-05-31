// Package adminconnect hosts Connect-RPC handlers for the platform-admin
// management plane (system administrators with `is_system_admin = true`).
//
// Migrated from REST handlers in backend/internal/api/rest/v1/admin/*. The
// REST surface gets deleted as call sites flip to Connect; the per-resource
// org-scoped Connect surfaces (org/runner/etc.) stay parallel.
//
// Auth model: every RPC calls interceptors.ResolveSystemAdmin to mirror
// REST's AdminMiddleware (is_system_admin + is_active checks). Per
// conventions §3.5 exception #2, admin requests do NOT carry `org_slug` —
// tenant is the whole platform.
//
// Split rationale (CLAUDE.md 200-line rule):
//   - server.go               — service scaffolding + Mount (this file)
//   - convert.go              — domain ↔ proto field translation
//   - convert_relay.go        — relay.RelayInfo → proto translation
//   - convert_runner.go       — runner.Runner + org → proto translation
//   - audit.go                — Connect-context audit log helper
//   - handlers_dashboard.go   — GetDashboardStats
//   - handlers_audit.go       — ListAuditLogs
//   - handlers_users_query.go — ListUsers / GetUser / UpdateUser
//   - handlers_users_actions.go — Disable / Enable / GrantAdmin / RevokeAdmin /
//                                 VerifyUserEmail / UnverifyUserEmail
//   - handlers_orgs.go        — ListOrganizations / GetOrganization /
//                               GetOrganizationMembers / DeleteOrganization
//   - handlers_runners_query.go — ListRunners / GetRunner
//   - handlers_runners_actions.go — DisableRunner / EnableRunner / DeleteRunner
//   - handlers_relays.go      — ListRelays / GetRelay / GetRelayStats /
//                               ForceUnregisterRelay (gated on WithRelayManager)
package adminconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/infra/database"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	agentservice "github.com/anthropics/agentsmesh/backend/internal/service/agent"
	"github.com/anthropics/agentsmesh/backend/internal/service/relay"
)

const ServiceName = "proto.admin.v1.AdminService"

const (
	GetDashboardStatsProcedure = "/" + ServiceName + "/GetDashboardStats"

	ListUsersProcedure         = "/" + ServiceName + "/ListUsers"
	GetUserProcedure           = "/" + ServiceName + "/GetUser"
	UpdateUserProcedure        = "/" + ServiceName + "/UpdateUser"
	DisableUserProcedure       = "/" + ServiceName + "/DisableUser"
	EnableUserProcedure        = "/" + ServiceName + "/EnableUser"
	GrantAdminProcedure        = "/" + ServiceName + "/GrantAdmin"
	RevokeAdminProcedure       = "/" + ServiceName + "/RevokeAdmin"
	VerifyUserEmailProcedure   = "/" + ServiceName + "/VerifyUserEmail"
	UnverifyUserEmailProcedure = "/" + ServiceName + "/UnverifyUserEmail"

	ListOrganizationsProcedure      = "/" + ServiceName + "/ListOrganizations"
	GetOrganizationProcedure        = "/" + ServiceName + "/GetOrganization"
	GetOrganizationMembersProcedure = "/" + ServiceName + "/GetOrganizationMembers"
	DeleteOrganizationProcedure     = "/" + ServiceName + "/DeleteOrganization"

	ListAuditLogsProcedure = "/" + ServiceName + "/ListAuditLogs"

	ListRunnersProcedure   = "/" + ServiceName + "/ListRunners"
	GetRunnerProcedure     = "/" + ServiceName + "/GetRunner"
	DisableRunnerProcedure = "/" + ServiceName + "/DisableRunner"
	EnableRunnerProcedure  = "/" + ServiceName + "/EnableRunner"
	DeleteRunnerProcedure  = "/" + ServiceName + "/DeleteRunner"

	ListRelaysProcedure           = "/" + ServiceName + "/ListRelays"
	GetRelayProcedure             = "/" + ServiceName + "/GetRelay"
	GetRelayStatsProcedure        = "/" + ServiceName + "/GetRelayStats"
	ForceUnregisterRelayProcedure = "/" + ServiceName + "/ForceUnregisterRelay"

	ListDeadLettersProcedure  = "/" + ServiceName + "/ListDeadLetters"
	ReplayDeadLetterProcedure = "/" + ServiceName + "/ReplayDeadLetter"
)

// Server implements proto.admin.v1.AdminService (dashboard + user +
// organization + audit + runner + relay + DLQ slices). Per-resource
// org-scoped surfaces stay parallel.
//
// relayMgr is optional — only deployments that wire the relay subsystem
// surface the 4 relay RPCs. msgSvc is optional — DLQ RPCs return
// CodeUnavailable when omitted. When nil, the handlers return
// CodeUnavailable to mirror REST's apierr.ServiceUnavailable behavior in
// relays.go.
type Server struct {
	svc      *adminservice.Service
	db       database.DB
	relayMgr *relay.Manager
	msgSvc   *agentservice.MessageService
}

// Option configures optional dependencies on Server. Mirrors the option
// pattern in podconnect / runnerconnect — required deps stay positional in
// NewServer, optional deps come through With* funcs so callers can skip
// when a subsystem is disabled.
type Option func(*Server)

// WithRelayManager wires the relay manager so the 4 relay RPCs (List /
// Get / Stats / ForceUnregister) can serve. Without it those RPCs return
// CodeUnavailable.
func WithRelayManager(mgr *relay.Manager) Option {
	return func(s *Server) { s.relayMgr = mgr }
}

// WithMessageService wires the agent message service so the DLQ RPCs
// (ListDeadLetters / ReplayDeadLetter) can serve. Without it those RPCs
// return CodeUnavailable.
func WithMessageService(msgSvc *agentservice.MessageService) Option {
	return func(s *Server) { s.msgSvc = msgSvc }
}

func NewServer(svc *adminservice.Service, db database.DB, opts ...Option) *Server {
	s := &Server{svc: svc, db: db}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

// Mount wires each implemented AdminService procedure onto mux. The auth
// interceptor in opts validates the JWT; per-handler ResolveSystemAdmin
// enforces is_system_admin (handler-level so the interceptor stays generic
// across user-scoped + admin-scoped services).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetDashboardStatsProcedure, connect.NewUnaryHandler(
		GetDashboardStatsProcedure, srv.GetDashboardStats, opts...,
	))

	mux.Handle(ListUsersProcedure, connect.NewUnaryHandler(
		ListUsersProcedure, srv.ListUsers, opts...,
	))
	mux.Handle(GetUserProcedure, connect.NewUnaryHandler(
		GetUserProcedure, srv.GetUser, opts...,
	))
	mux.Handle(UpdateUserProcedure, connect.NewUnaryHandler(
		UpdateUserProcedure, srv.UpdateUser, opts...,
	))
	mux.Handle(DisableUserProcedure, connect.NewUnaryHandler(
		DisableUserProcedure, srv.DisableUser, opts...,
	))
	mux.Handle(EnableUserProcedure, connect.NewUnaryHandler(
		EnableUserProcedure, srv.EnableUser, opts...,
	))
	mux.Handle(GrantAdminProcedure, connect.NewUnaryHandler(
		GrantAdminProcedure, srv.GrantAdmin, opts...,
	))
	mux.Handle(RevokeAdminProcedure, connect.NewUnaryHandler(
		RevokeAdminProcedure, srv.RevokeAdmin, opts...,
	))
	mux.Handle(VerifyUserEmailProcedure, connect.NewUnaryHandler(
		VerifyUserEmailProcedure, srv.VerifyUserEmail, opts...,
	))
	mux.Handle(UnverifyUserEmailProcedure, connect.NewUnaryHandler(
		UnverifyUserEmailProcedure, srv.UnverifyUserEmail, opts...,
	))

	mux.Handle(ListOrganizationsProcedure, connect.NewUnaryHandler(
		ListOrganizationsProcedure, srv.ListOrganizations, opts...,
	))
	mux.Handle(GetOrganizationProcedure, connect.NewUnaryHandler(
		GetOrganizationProcedure, srv.GetOrganization, opts...,
	))
	mux.Handle(GetOrganizationMembersProcedure, connect.NewUnaryHandler(
		GetOrganizationMembersProcedure, srv.GetOrganizationMembers, opts...,
	))
	mux.Handle(DeleteOrganizationProcedure, connect.NewUnaryHandler(
		DeleteOrganizationProcedure, srv.DeleteOrganization, opts...,
	))

	mux.Handle(ListAuditLogsProcedure, connect.NewUnaryHandler(
		ListAuditLogsProcedure, srv.ListAuditLogs, opts...,
	))

	mux.Handle(ListRunnersProcedure, connect.NewUnaryHandler(
		ListRunnersProcedure, srv.ListRunners, opts...,
	))
	mux.Handle(GetRunnerProcedure, connect.NewUnaryHandler(
		GetRunnerProcedure, srv.GetRunner, opts...,
	))
	mux.Handle(DisableRunnerProcedure, connect.NewUnaryHandler(
		DisableRunnerProcedure, srv.DisableRunner, opts...,
	))
	mux.Handle(EnableRunnerProcedure, connect.NewUnaryHandler(
		EnableRunnerProcedure, srv.EnableRunner, opts...,
	))
	mux.Handle(DeleteRunnerProcedure, connect.NewUnaryHandler(
		DeleteRunnerProcedure, srv.DeleteRunner, opts...,
	))

	mux.Handle(ListRelaysProcedure, connect.NewUnaryHandler(
		ListRelaysProcedure, srv.ListRelays, opts...,
	))
	mux.Handle(GetRelayProcedure, connect.NewUnaryHandler(
		GetRelayProcedure, srv.GetRelay, opts...,
	))
	mux.Handle(GetRelayStatsProcedure, connect.NewUnaryHandler(
		GetRelayStatsProcedure, srv.GetRelayStats, opts...,
	))
	mux.Handle(ForceUnregisterRelayProcedure, connect.NewUnaryHandler(
		ForceUnregisterRelayProcedure, srv.ForceUnregisterRelay, opts...,
	))

	mux.Handle(ListDeadLettersProcedure, connect.NewUnaryHandler(
		ListDeadLettersProcedure, srv.ListDeadLetters, opts...,
	))
	mux.Handle(ReplayDeadLetterProcedure, connect.NewUnaryHandler(
		ReplayDeadLetterProcedure, srv.ReplayDeadLetter, opts...,
	))
}

// mapServiceError translates admin-service sentinels to Connect codes,
// mirroring apierr translation in REST handlers.
func mapServiceError(err error) error {
	switch {
	case errors.Is(err, adminservice.ErrUserNotFound),
		errors.Is(err, adminservice.ErrOrganizationNotFound),
		errors.Is(err, adminservice.ErrRunnerNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, adminservice.ErrUsernameAlreadyExists),
		errors.Is(err, adminservice.ErrEmailAlreadyExists),
		errors.Is(err, adminservice.ErrOrganizationHasActiveRunner),
		errors.Is(err, adminservice.ErrRunnerHasActivePods),
		errors.Is(err, adminservice.ErrRunnerHasLoopRefs):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, adminservice.ErrCannotRevokeOwnAdmin),
		errors.Is(err, adminservice.ErrCannotDisableSelf):
		return connect.NewError(connect.CodeInvalidArgument, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
