// Package usercredentialconnect hosts Connect-RPC handlers for user-scoped
// services that share the proto.user_credential.v1 package: Git credentials
// and Repository providers. They're grouped because they're tightly coupled
// at the data layer (GitCredential references RepositoryProvider) and share
// the same user-scope auth boundary.
//
// Per conventions §3.5 these are user-scoped — the auth interceptor populates
// TenantContext.UserID and that's the only scope each RPC enforces, no
// org_slug = 1 (would have been a no-op).
//
// SENSITIVE DATA: PAT / SSH private key / OAuth client_secret / bot_token
// never appear on response messages. The convert helpers omit them by
// construction (REST-side has `json:"-"` on the same fields).
package usercredentialconnect

import (
	"net/http"

	"connectrpc.com/connect"

	userservice "github.com/anthropics/agentsmesh/backend/internal/service/user"
)

const (
	GitServiceName      = "proto.user_credential.v1.UserGitCredentialService"
	ProviderServiceName = "proto.user_credential.v1.UserRepositoryProviderService"
)

const (
	ListGitCredentialsProcedure        = "/" + GitServiceName + "/ListGitCredentials"
	GetGitCredentialProcedure          = "/" + GitServiceName + "/GetGitCredential"
	CreateGitCredentialProcedure       = "/" + GitServiceName + "/CreateGitCredential"
	UpdateGitCredentialProcedure       = "/" + GitServiceName + "/UpdateGitCredential"
	DeleteGitCredentialProcedure       = "/" + GitServiceName + "/DeleteGitCredential"
	GetDefaultGitCredentialProcedure   = "/" + GitServiceName + "/GetDefaultGitCredential"
	SetDefaultGitCredentialProcedure   = "/" + GitServiceName + "/SetDefaultGitCredential"
	ClearDefaultGitCredentialProcedure = "/" + GitServiceName + "/ClearDefaultGitCredential"
)

const (
	ListRepositoryProvidersProcedure          = "/" + ProviderServiceName + "/ListRepositoryProviders"
	GetRepositoryProviderProcedure            = "/" + ProviderServiceName + "/GetRepositoryProvider"
	CreateRepositoryProviderProcedure         = "/" + ProviderServiceName + "/CreateRepositoryProvider"
	UpdateRepositoryProviderProcedure         = "/" + ProviderServiceName + "/UpdateRepositoryProvider"
	DeleteRepositoryProviderProcedure         = "/" + ProviderServiceName + "/DeleteRepositoryProvider"
	SetDefaultRepositoryProviderProcedure     = "/" + ProviderServiceName + "/SetDefaultRepositoryProvider"
	TestRepositoryProviderConnectionProcedure = "/" + ProviderServiceName + "/TestRepositoryProviderConnection"
	ListProviderRepositoriesProcedure         = "/" + ProviderServiceName + "/ListProviderRepositories"
)

// Server implements the two credential services. They share the user service
// as their data home (both Git credentials and Repository providers).
type Server struct {
	userSvc *userservice.Service
}

func NewServer(userSvc *userservice.Service) *Server {
	return &Server{userSvc: userSvc}
}

// Mount registers all procedures across the two services on mux behind
// the auth interceptor supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mountGitCredential(mux, srv, opts...)
	mountRepositoryProvider(mux, srv, opts...)
}

func mountGitCredential(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListGitCredentialsProcedure, connect.NewUnaryHandler(
		ListGitCredentialsProcedure, srv.ListGitCredentials, opts...,
	))
	mux.Handle(GetGitCredentialProcedure, connect.NewUnaryHandler(
		GetGitCredentialProcedure, srv.GetGitCredential, opts...,
	))
	mux.Handle(CreateGitCredentialProcedure, connect.NewUnaryHandler(
		CreateGitCredentialProcedure, srv.CreateGitCredential, opts...,
	))
	mux.Handle(UpdateGitCredentialProcedure, connect.NewUnaryHandler(
		UpdateGitCredentialProcedure, srv.UpdateGitCredential, opts...,
	))
	mux.Handle(DeleteGitCredentialProcedure, connect.NewUnaryHandler(
		DeleteGitCredentialProcedure, srv.DeleteGitCredential, opts...,
	))
	mux.Handle(GetDefaultGitCredentialProcedure, connect.NewUnaryHandler(
		GetDefaultGitCredentialProcedure, srv.GetDefaultGitCredential, opts...,
	))
	mux.Handle(SetDefaultGitCredentialProcedure, connect.NewUnaryHandler(
		SetDefaultGitCredentialProcedure, srv.SetDefaultGitCredential, opts...,
	))
	mux.Handle(ClearDefaultGitCredentialProcedure, connect.NewUnaryHandler(
		ClearDefaultGitCredentialProcedure, srv.ClearDefaultGitCredential, opts...,
	))
}

func mountRepositoryProvider(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListRepositoryProvidersProcedure, connect.NewUnaryHandler(
		ListRepositoryProvidersProcedure, srv.ListRepositoryProviders, opts...,
	))
	mux.Handle(GetRepositoryProviderProcedure, connect.NewUnaryHandler(
		GetRepositoryProviderProcedure, srv.GetRepositoryProvider, opts...,
	))
	mux.Handle(CreateRepositoryProviderProcedure, connect.NewUnaryHandler(
		CreateRepositoryProviderProcedure, srv.CreateRepositoryProvider, opts...,
	))
	mux.Handle(UpdateRepositoryProviderProcedure, connect.NewUnaryHandler(
		UpdateRepositoryProviderProcedure, srv.UpdateRepositoryProvider, opts...,
	))
	mux.Handle(DeleteRepositoryProviderProcedure, connect.NewUnaryHandler(
		DeleteRepositoryProviderProcedure, srv.DeleteRepositoryProvider, opts...,
	))
	mux.Handle(SetDefaultRepositoryProviderProcedure, connect.NewUnaryHandler(
		SetDefaultRepositoryProviderProcedure, srv.SetDefaultRepositoryProvider, opts...,
	))
	mux.Handle(TestRepositoryProviderConnectionProcedure, connect.NewUnaryHandler(
		TestRepositoryProviderConnectionProcedure, srv.TestRepositoryProviderConnection, opts...,
	))
	mux.Handle(ListProviderRepositoriesProcedure, connect.NewUnaryHandler(
		ListProviderRepositoriesProcedure, srv.ListProviderRepositories, opts...,
	))
}
