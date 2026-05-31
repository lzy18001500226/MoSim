// Package skillregistryadminconnect hosts Connect-RPC handlers for the
// platform-admin skill registry surface. Mirrors
// backend/internal/api/rest/v1/admin/skill_registries.go.
//
// Auth model: every RPC calls interceptors.ResolveSystemAdmin to mirror
// REST's AdminMiddleware (is_system_admin + is_active checks). The
// org-scoped SkillRegistryService lives next door in
// backend/internal/api/connect/extension/ — separate auth surface, so
// keep the packages split to prevent transport-level drift.
//
// Platform scope: every entry is OrganizationID = nil. The handlers
// pass `nil` to repo.ListSkillRegistries / FindSkillRegistryByURL so
// only platform-level rows surface. Sync + Delete additionally re-read
// the row and refuse to operate when IsPlatformLevel() returns false —
// belt-and-braces against an admin URL pointing at an org-scoped ID.
package skillregistryadminconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/domain/extension"
	"github.com/anthropics/agentsmesh/backend/internal/infra/database"
	extensionservice "github.com/anthropics/agentsmesh/backend/internal/service/extension"
)

const ServiceName = "proto.extension.v1.SkillRegistryAdminService"

const (
	ListSkillRegistriesProcedure   = "/" + ServiceName + "/ListSkillRegistries"
	CreateSkillRegistryProcedure   = "/" + ServiceName + "/CreateSkillRegistry"
	SyncSkillRegistryProcedure     = "/" + ServiceName + "/SyncSkillRegistry"
	DeleteSkillRegistryProcedure   = "/" + ServiceName + "/DeleteSkillRegistry"
)

// Server implements SkillRegistryAdminService. `db` is threaded through
// for ResolveSystemAdmin's user lookup — same source as the REST
// AdminMiddleware so the two paths can't diverge on the is_system_admin
// check. `repo` + `worker` mirror NewSkillRegistryHandler's deps in REST.
type Server struct {
	repo   extension.Repository
	worker *extensionservice.MarketplaceWorker
	db     database.DB
}

func NewServer(repo extension.Repository, worker *extensionservice.MarketplaceWorker, db database.DB) *Server {
	return &Server{repo: repo, worker: worker, db: db}
}

// Mount wires every SkillRegistryAdminService procedure onto mux. The
// auth interceptor in opts validates the JWT; per-handler
// ResolveSystemAdmin then enforces the is_system_admin flag.
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListSkillRegistriesProcedure, connect.NewUnaryHandler(
		ListSkillRegistriesProcedure, srv.ListSkillRegistries, opts...,
	))
	mux.Handle(CreateSkillRegistryProcedure, connect.NewUnaryHandler(
		CreateSkillRegistryProcedure, srv.CreateSkillRegistry, opts...,
	))
	mux.Handle(SyncSkillRegistryProcedure, connect.NewUnaryHandler(
		SyncSkillRegistryProcedure, srv.SyncSkillRegistry, opts...,
	))
	mux.Handle(DeleteSkillRegistryProcedure, connect.NewUnaryHandler(
		DeleteSkillRegistryProcedure, srv.DeleteSkillRegistry, opts...,
	))
}

// errPlatformLevelOnly fires when a caller tries to sync/delete an
// org-scoped registry through the admin surface — same guard as REST's
// IsPlatformLevel() check in skill_registries.go.
var errPlatformLevelOnly = errors.New("not a platform-level skill registry")

// errMarketplaceWorkerUnavailable mirrors REST's "marketplace worker not
// available" 500 — only fires on Sync since Create's async trigger is
// best-effort.
var errMarketplaceWorkerUnavailable = errors.New("marketplace worker not available")
