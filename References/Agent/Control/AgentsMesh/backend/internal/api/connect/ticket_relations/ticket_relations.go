// Package ticketrelationsconnect hosts Connect-RPC handlers for the
// ticket-relations sub-domains (relations / merge-requests / commits /
// comments). Mirrors the four REST files:
//   backend/internal/api/rest/v1/ticket_relations.go
//   backend/internal/api/rest/v1/ticket_comments.go
//   backend/internal/api/rest/v1/ticket_commits.go
// (merge-request list lives in ticket_relations.go REST handler).
//
// Handler shape follows runbook §3:
//   * ResolveOrgScope reads org_slug + injects TenantContext.
//   * GetTicketBySlug resolves the ticket_slug → *ticket.Ticket.
//   * Single-entity get/create returns the entity directly.
//   * List responses follow {items, total, limit, offset}.
//   * Errors map to Connect codes (conventions §10).
package ticketrelationsconnect

import (
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	ticketservice "github.com/anthropics/agentsmesh/backend/internal/service/ticket"
)

// ServiceName mirrors proto.ticket_relations.v1.TicketRelationsService exactly
// — Connect derives the URL from `<package>.<Service>` (conventions §1, §12).
const ServiceName = "proto.ticket_relations.v1.TicketRelationsService"

// Procedure paths — every per-RPC mux key is derived from this constant.
const (
	ListRelationsProcedure     = "/" + ServiceName + "/ListRelations"
	CreateRelationProcedure    = "/" + ServiceName + "/CreateRelation"
	DeleteRelationProcedure    = "/" + ServiceName + "/DeleteRelation"
	ListMergeRequestsProcedure = "/" + ServiceName + "/ListMergeRequests"
	ListCommitsProcedure       = "/" + ServiceName + "/ListCommits"
	LinkCommitProcedure        = "/" + ServiceName + "/LinkCommit"
	UnlinkCommitProcedure      = "/" + ServiceName + "/UnlinkCommit"
	ListCommentsProcedure      = "/" + ServiceName + "/ListComments"
	CreateCommentProcedure     = "/" + ServiceName + "/CreateComment"
	UpdateCommentProcedure     = "/" + ServiceName + "/UpdateComment"
	DeleteCommentProcedure     = "/" + ServiceName + "/DeleteComment"
)

// Server implements TicketRelationsService. Threads the same ticket service
// instance that REST uses (services_init.go), so both routes see the same
// repo / event publisher / blockstore wiring.
type Server struct {
	ticketSvc *ticketservice.Service
	orgSvc    middleware.OrganizationService
}

func NewServer(ticketSvc *ticketservice.Service, orgSvc middleware.OrganizationService) *Server {
	return &Server{ticketSvc: ticketSvc, orgSvc: orgSvc}
}
