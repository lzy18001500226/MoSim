// Package invitationconnect hosts Connect-RPC handlers for the invitation
// domain. Mirrors backend/internal/api/rest/v1/invitations*.go but exposes
// the data plane via Connect (binary protobuf wire, conventions §2.5). REST
// stays mounted in parallel; the migration runs dual-track until all 26
// services have flipped.
//
// Three services in this package:
//   - InvitationService          — org-scoped (admin/owner). ResolveOrgScope
//                                  + requireAdmin. List/Create/Revoke/Resend.
//   - UserInvitationService      — invitee-scoped. Caller's UserID (from auth
//                                  interceptor) is the only scope, no org_slug
//                                  (conventions §3.5 exception #1). Accept and
//                                  ListPending live here because the invitee
//                                  may not yet be a member of any org — the
//                                  token / email IS the scope.
//   - PublicInvitationService    — unauthenticated. GetByToken renders the
//                                  /invite/[token] card before sign-in. No
//                                  auth, the token IS the credential.
//
// Handler shape follows runbook §3 + conventions §3.5: org-scoped RPCs call
// ResolveOrgScope first; List response follows {items, total, limit, offset};
// errors map to Connect codes (conventions §10).
//
// Split rationale (CLAUDE.md 200-line rule):
//   - invitation.go         — service scaffolding + Mount (this file)
//   - invitation_org.go     — InvitationService (4 RPCs, admin-gated)
//   - invitation_user.go    — UserInvitationService (Accept, ListPending)
//   - invitation_public.go  — PublicInvitationService (GetByToken)
//   - invitation_convert.go — domain ↔ proto field translation
//   - invitation_errors.go  — error mapping + role guards
package invitationconnect

import (
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	invitationsvc "github.com/anthropics/agentsmesh/backend/internal/service/invitation"
	orgservice "github.com/anthropics/agentsmesh/backend/internal/service/organization"
	userservice "github.com/anthropics/agentsmesh/backend/internal/service/user"
)

const (
	OrgServiceName    = "proto.invitation.v1.InvitationService"
	UserServiceName   = "proto.invitation.v1.UserInvitationService"
	PublicServiceName = "proto.invitation.v1.PublicInvitationService"
)

const (
	ListInvitationsProcedure  = "/" + OrgServiceName + "/ListInvitations"
	CreateInvitationProcedure = "/" + OrgServiceName + "/CreateInvitation"
	RevokeInvitationProcedure = "/" + OrgServiceName + "/RevokeInvitation"
	ResendInvitationProcedure = "/" + OrgServiceName + "/ResendInvitation"
)

const (
	AcceptInvitationProcedure       = "/" + UserServiceName + "/AcceptInvitation"
	ListPendingInvitationsProcedure = "/" + UserServiceName + "/ListPendingInvitations"
)

const (
	GetInvitationByTokenProcedure = "/" + PublicServiceName + "/GetInvitationByToken"
)

// Server implements InvitationService + UserInvitationService — the two
// authenticated services. They share dependencies (invitation + org + user +
// billing) so one struct keeps the dep wiring simple.
type Server struct {
	invitationSvc *invitationsvc.Service
	orgSvc        middleware.OrganizationService
	orgInternal   *orgservice.Service
	userSvc       *userservice.Service
	billingSvc    *billingsvc.Service
}

// NewServer constructs a Server. billingSvc is optional — when nil, seat
// availability checks are skipped (mirrors the REST nil-guard at
// invitations_org.go:39).
func NewServer(
	invitationSvc *invitationsvc.Service,
	orgSvc middleware.OrganizationService,
	orgInternal *orgservice.Service,
	userSvc *userservice.Service,
	opts ...Option,
) *Server {
	s := &Server{
		invitationSvc: invitationSvc,
		orgSvc:        orgSvc,
		orgInternal:   orgInternal,
		userSvc:       userSvc,
	}
	for _, opt := range opts {
		opt(s)
	}
	return s
}

// Option — functional options for the optional billing dependency so
// deployments without billing can mount a degraded handler without nil
// panics.
type Option func(*Server)

func WithBillingService(b *billingsvc.Service) Option {
	return func(s *Server) { s.billingSvc = b }
}

// PublicServer hosts PublicInvitationService — token-only invitation lookup,
// no auth, no org_slug. The token IS the credential (single-use, opaque hex).
type PublicServer struct {
	invitationSvc *invitationsvc.Service
}

func NewPublicServer(invitationSvc *invitationsvc.Service) *PublicServer {
	return &PublicServer{invitationSvc: invitationSvc}
}

// Mount registers org-scoped + user-scoped procedures behind the auth
// interceptor supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListInvitationsProcedure, connect.NewUnaryHandler(
		ListInvitationsProcedure, srv.ListInvitations, opts...,
	))
	mux.Handle(CreateInvitationProcedure, connect.NewUnaryHandler(
		CreateInvitationProcedure, srv.CreateInvitation, opts...,
	))
	mux.Handle(RevokeInvitationProcedure, connect.NewUnaryHandler(
		RevokeInvitationProcedure, srv.RevokeInvitation, opts...,
	))
	mux.Handle(ResendInvitationProcedure, connect.NewUnaryHandler(
		ResendInvitationProcedure, srv.ResendInvitation, opts...,
	))
	mux.Handle(AcceptInvitationProcedure, connect.NewUnaryHandler(
		AcceptInvitationProcedure, srv.AcceptInvitation, opts...,
	))
	mux.Handle(ListPendingInvitationsProcedure, connect.NewUnaryHandler(
		ListPendingInvitationsProcedure, srv.ListPendingInvitations, opts...,
	))
}

// MountPublic registers public RPCs WITHOUT the auth interceptor. Mirrors
// billing_public.go:MountPublic — token IS the auth credential, no JWT.
func MountPublic(mux *http.ServeMux, srv *PublicServer, opts ...connect.HandlerOption) {
	mux.Handle(GetInvitationByTokenProcedure, connect.NewUnaryHandler(
		GetInvitationByTokenProcedure, srv.GetInvitationByToken, opts...,
	))
}
