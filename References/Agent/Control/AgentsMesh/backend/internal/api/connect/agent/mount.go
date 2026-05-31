package agentconnect

import (
	"net/http"

	"connectrpc.com/connect"
)

// Mount registers all AgentService + UserAgentConfigService procedures on
// mux behind the auth interceptor supplied via opts (see
// cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mountAgentService(mux, srv, opts...)
	mountUserAgentConfigService(mux, srv, opts...)
}

func mountAgentService(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListAgentsProcedure, connect.NewUnaryHandler(
		ListAgentsProcedure, srv.ListAgents, opts...,
	))
	mux.Handle(GetAgentProcedure, connect.NewUnaryHandler(
		GetAgentProcedure, srv.GetAgent, opts...,
	))
	mux.Handle(GetAgentConfigSchemaProcedure, connect.NewUnaryHandler(
		GetAgentConfigSchemaProcedure, srv.GetAgentConfigSchema, opts...,
	))
	mux.Handle(CreateCustomAgentProcedure, connect.NewUnaryHandler(
		CreateCustomAgentProcedure, srv.CreateCustomAgent, opts...,
	))
	mux.Handle(UpdateCustomAgentProcedure, connect.NewUnaryHandler(
		UpdateCustomAgentProcedure, srv.UpdateCustomAgent, opts...,
	))
	mux.Handle(DeleteCustomAgentProcedure, connect.NewUnaryHandler(
		DeleteCustomAgentProcedure, srv.DeleteCustomAgent, opts...,
	))
}

func mountUserAgentConfigService(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListUserAgentConfigsProcedure, connect.NewUnaryHandler(
		ListUserAgentConfigsProcedure, srv.ListUserAgentConfigs, opts...,
	))
	mux.Handle(GetUserAgentConfigProcedure, connect.NewUnaryHandler(
		GetUserAgentConfigProcedure, srv.GetUserAgentConfig, opts...,
	))
	mux.Handle(SetUserAgentConfigProcedure, connect.NewUnaryHandler(
		SetUserAgentConfigProcedure, srv.SetUserAgentConfig, opts...,
	))
	mux.Handle(DeleteUserAgentConfigProcedure, connect.NewUnaryHandler(
		DeleteUserAgentConfigProcedure, srv.DeleteUserAgentConfig, opts...,
	))
}
