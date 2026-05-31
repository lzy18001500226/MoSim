// Package blockstoreconnect hosts Connect-RPC handlers for the blockstore
// domain. Mirrors backend/internal/api/rest/v1/blockstore_*.go but exposes
// the data plane via Connect (binary protobuf wire, see conventions.md
// §2.5). REST stays mounted in parallel; the migration runs dual-track
// until all 26 services have flipped.
//
// Handler shape follows runbook §3:
//   * ResolveOrgScope reads org_slug + injects TenantContext.
//   * Single-entity get/create return the entity directly.
//   * List responses follow {items, total, limit, offset}.
//   * Errors map to Connect codes (conventions §10) via translateErr.
//
// Block.data / .meta / BlockOp.{payload, forward, inverse, context} ride as
// opaque UTF-8 JSON strings on the wire — see proto file header for why
// (200+ blocktype subschemas).
package blockstoreconnect

import (
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	blockstoreservice "github.com/anthropics/agentsmesh/backend/internal/service/blockstore"
)

// ServiceName mirrors proto.blockstore.v1.BlockstoreService exactly —
// Connect derives the URL from `<package>.<Service>` (conventions §1, §12).
const ServiceName = "proto.blockstore.v1.BlockstoreService"

const (
	ApplyOpsProcedure               = "/" + ServiceName + "/ApplyOps"
	ListWorkspacesProcedure         = "/" + ServiceName + "/ListWorkspaces"
	EnsureDefaultWorkspaceProcedure = "/" + ServiceName + "/EnsureDefaultWorkspace"
	CreateWorkspaceProcedure        = "/" + ServiceName + "/CreateWorkspace"
	DeleteWorkspaceProcedure        = "/" + ServiceName + "/DeleteWorkspace"

	GetBlockProcedure      = "/" + ServiceName + "/GetBlock"
	ListChildrenProcedure  = "/" + ServiceName + "/ListChildren"
	ListBacklinksProcedure = "/" + ServiceName + "/ListBacklinks"

	GetSubtreeProcedure       = "/" + ServiceName + "/GetSubtree"
	StreamOpsProcedure        = "/" + ServiceName + "/StreamOps"
	ExportWorkspaceProcedure  = "/" + ServiceName + "/ExportWorkspace"
	ListTypeDefsProcedure     = "/" + ServiceName + "/ListTypeDefs"
	GetBlockAtProcedure       = "/" + ServiceName + "/GetBlockAt"

	SemanticSearchProcedure = "/" + ServiceName + "/SemanticSearch"
	MemoryRetrieveProcedure = "/" + ServiceName + "/MemoryRetrieve"
)

// Server implements the BlockstoreService contract. Mirrors REST's
// BlockstoreHandler dependencies (blockstore_handler.go:19).
type Server struct {
	svc    *blockstoreservice.Service
	orgSvc middleware.OrganizationService
}

func NewServer(svc *blockstoreservice.Service, orgSvc middleware.OrganizationService) *Server {
	return &Server{svc: svc, orgSvc: orgSvc}
}

// Mount registers all BlockstoreService procedures on mux behind the auth
// interceptor supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mountOps(mux, srv, opts...)
	mountWorkspaces(mux, srv, opts...)
	mountBlocks(mux, srv, opts...)
	mountWorkspaceQueries(mux, srv, opts...)
	mountSearch(mux, srv, opts...)
}

func mountOps(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ApplyOpsProcedure, connect.NewUnaryHandler(ApplyOpsProcedure, srv.ApplyOps, opts...))
}

func mountWorkspaces(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListWorkspacesProcedure, connect.NewUnaryHandler(ListWorkspacesProcedure, srv.ListWorkspaces, opts...))
	mux.Handle(EnsureDefaultWorkspaceProcedure, connect.NewUnaryHandler(EnsureDefaultWorkspaceProcedure, srv.EnsureDefaultWorkspace, opts...))
	mux.Handle(CreateWorkspaceProcedure, connect.NewUnaryHandler(CreateWorkspaceProcedure, srv.CreateWorkspace, opts...))
	mux.Handle(DeleteWorkspaceProcedure, connect.NewUnaryHandler(DeleteWorkspaceProcedure, srv.DeleteWorkspace, opts...))
}

func mountBlocks(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetBlockProcedure, connect.NewUnaryHandler(GetBlockProcedure, srv.GetBlock, opts...))
	mux.Handle(ListChildrenProcedure, connect.NewUnaryHandler(ListChildrenProcedure, srv.ListChildren, opts...))
	mux.Handle(ListBacklinksProcedure, connect.NewUnaryHandler(ListBacklinksProcedure, srv.ListBacklinks, opts...))
}

func mountWorkspaceQueries(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetSubtreeProcedure, connect.NewUnaryHandler(GetSubtreeProcedure, srv.GetSubtree, opts...))
	mux.Handle(StreamOpsProcedure, connect.NewUnaryHandler(StreamOpsProcedure, srv.StreamOps, opts...))
	mux.Handle(ExportWorkspaceProcedure, connect.NewUnaryHandler(ExportWorkspaceProcedure, srv.ExportWorkspace, opts...))
	mux.Handle(ListTypeDefsProcedure, connect.NewUnaryHandler(ListTypeDefsProcedure, srv.ListTypeDefs, opts...))
	mux.Handle(GetBlockAtProcedure, connect.NewUnaryHandler(GetBlockAtProcedure, srv.GetBlockAt, opts...))
}

func mountSearch(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(SemanticSearchProcedure, connect.NewUnaryHandler(SemanticSearchProcedure, srv.SemanticSearch, opts...))
	mux.Handle(MemoryRetrieveProcedure, connect.NewUnaryHandler(MemoryRetrieveProcedure, srv.MemoryRetrieve, opts...))
}
