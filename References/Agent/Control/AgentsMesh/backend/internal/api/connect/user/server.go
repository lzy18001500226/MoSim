// Package userconnect hosts Connect-RPC handlers for the user domain.
// Mirrors backend/internal/api/rest/v1/users.go but exposes the data
// plane via Connect (binary protobuf wire, conventions §2.5). REST stays
// mounted in parallel; the migration runs dual-track until the wasm /
// TS clients have flipped.
//
// All RPCs are USER-SCOPED — they address the caller (auth interceptor
// supplies the user ID via TenantContext.UserID, no org_slug payload —
// conventions §3.5 exception #1). User search is also user-scoped (a
// user looking up another user by query).
//
// SENSITIVE DATA: password_hash, OAuth tokens, verification/reset tokens
// never appear on response messages. The convert helper omits them by
// construction (REST-side has `json:"-"` on the same fields).
package userconnect

import (
	"net/http"

	"connectrpc.com/connect"

	orgservice "github.com/anthropics/agentsmesh/backend/internal/service/organization"
	userservice "github.com/anthropics/agentsmesh/backend/internal/service/user"
)

const ServiceName = "proto.user.v1.UserService"

const (
	GetMeProcedure          = "/" + ServiceName + "/GetMe"
	UpdateMeProcedure       = "/" + ServiceName + "/UpdateMe"
	ChangePasswordProcedure = "/" + ServiceName + "/ChangePassword"
	ListIdentitiesProcedure = "/" + ServiceName + "/ListIdentities"
	DeleteIdentityProcedure = "/" + ServiceName + "/DeleteIdentity"
	SearchUsersProcedure    = "/" + ServiceName + "/SearchUsers"
)

// Server implements UserService. orgSvc is currently unused but kept
// matching REST's NewUserHandler signature so dependency wiring in
// connect_init.go is symmetric with REST's RegisterUserRoutes.
type Server struct {
	userSvc *userservice.Service
	orgSvc  *orgservice.Service
}

// NewServer constructs a Server with the required service deps.
func NewServer(userSvc *userservice.Service, orgSvc *orgservice.Service) *Server {
	return &Server{userSvc: userSvc, orgSvc: orgSvc}
}

// Mount registers all UserService procedures on mux behind the auth
// interceptor supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetMeProcedure, connect.NewUnaryHandler(
		GetMeProcedure, srv.GetMe, opts...,
	))
	mux.Handle(UpdateMeProcedure, connect.NewUnaryHandler(
		UpdateMeProcedure, srv.UpdateMe, opts...,
	))
	mux.Handle(ChangePasswordProcedure, connect.NewUnaryHandler(
		ChangePasswordProcedure, srv.ChangePassword, opts...,
	))
	mux.Handle(ListIdentitiesProcedure, connect.NewUnaryHandler(
		ListIdentitiesProcedure, srv.ListIdentities, opts...,
	))
	mux.Handle(DeleteIdentityProcedure, connect.NewUnaryHandler(
		DeleteIdentityProcedure, srv.DeleteIdentity, opts...,
	))
	mux.Handle(SearchUsersProcedure, connect.NewUnaryHandler(
		SearchUsersProcedure, srv.SearchUsers, opts...,
	))
}
