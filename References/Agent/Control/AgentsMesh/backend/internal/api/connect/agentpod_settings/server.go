// Package agentpodsettingsconnect hosts Connect-RPC handlers for the
// user-scoped AgentPod settings + AI provider domain.
//
// Mirrors backend/internal/api/rest/v1/agentpod.go. Per conventions §3.5,
// user-scoped services skip the org_slug requirement — the tenant is the
// JWT-claim user, not a payload-derived organization.
//
// AI provider credentials never leave the server in plaintext — the convert
// helpers explicitly scrub encrypted_credentials before responding, mirroring
// agentpod.go:91-93.
package agentpodsettingsconnect

import (
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/service/agentpod"
)

// ServiceName mirrors proto.pod.v1.AgentPodSettingsService exactly. Connect
// derives the URL from `<package>.<Service>` (conventions §1, §12).
const ServiceName = "proto.pod.v1.AgentPodSettingsService"

const (
	GetSettingsProcedure        = "/" + ServiceName + "/GetSettings"
	UpdateSettingsProcedure     = "/" + ServiceName + "/UpdateSettings"
	ListProvidersProcedure      = "/" + ServiceName + "/ListProviders"
	CreateProviderProcedure     = "/" + ServiceName + "/CreateProvider"
	UpdateProviderProcedure     = "/" + ServiceName + "/UpdateProvider"
	DeleteProviderProcedure     = "/" + ServiceName + "/DeleteProvider"
	SetDefaultProviderProcedure = "/" + ServiceName + "/SetDefaultProvider"
)

// Server implements AgentPodSettingsService. Mirrors AgentPodHandler in
// v1/agentpod.go — same service deps threaded through cmd/server wiring.
type Server struct {
	settings   *agentpod.SettingsService
	aiProvider *agentpod.AIProviderService
}

// NewServer constructs a Server.
func NewServer(settings *agentpod.SettingsService, aiProvider *agentpod.AIProviderService) *Server {
	return &Server{settings: settings, aiProvider: aiProvider}
}

// Mount registers all AgentPodSettingsService procedures on mux behind the
// auth interceptor supplied via opts (see cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetSettingsProcedure, connect.NewUnaryHandler(
		GetSettingsProcedure, srv.GetSettings, opts...,
	))
	mux.Handle(UpdateSettingsProcedure, connect.NewUnaryHandler(
		UpdateSettingsProcedure, srv.UpdateSettings, opts...,
	))
	mux.Handle(ListProvidersProcedure, connect.NewUnaryHandler(
		ListProvidersProcedure, srv.ListProviders, opts...,
	))
	mux.Handle(CreateProviderProcedure, connect.NewUnaryHandler(
		CreateProviderProcedure, srv.CreateProvider, opts...,
	))
	mux.Handle(UpdateProviderProcedure, connect.NewUnaryHandler(
		UpdateProviderProcedure, srv.UpdateProvider, opts...,
	))
	mux.Handle(DeleteProviderProcedure, connect.NewUnaryHandler(
		DeleteProviderProcedure, srv.DeleteProvider, opts...,
	))
	mux.Handle(SetDefaultProviderProcedure, connect.NewUnaryHandler(
		SetDefaultProviderProcedure, srv.SetDefaultProvider, opts...,
	))
}
