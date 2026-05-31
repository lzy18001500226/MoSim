// Package meshconnect hosts Connect-RPC handlers for the mesh domain.
// Mirrors backend/internal/api/rest/v1/mesh.go but exposes the data plane
// via Connect (binary protobuf wire, see conventions §2.5).
//
// Two services share this package because they share the same proto package
// (proto.mesh.v1):
//
//   - MeshService: topology + ticket→pod lookup + pod-for-ticket creation.
//     Stayed on REST throughout the ticket migration because they belong
//     to MeshService, not TicketService.
//   - MeshMessageService: pod-to-pod direct messaging — Send/Get/Mark-read
//     + DLQ. Migrated from /api/v1/orgs/:slug/messages/*. REST authenticated
//     via X-Pod-Key; Connect names the caller pod in `pod_key` on every
//     per-pod request (binding-style auth, parity-preserving).
//
// REST handler stays mounted in parallel until consumers flip lanes.
package meshconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	agentservice "github.com/anthropics/agentsmesh/backend/internal/service/agent"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	meshservice "github.com/anthropics/agentsmesh/backend/internal/service/mesh"
	ticketservice "github.com/anthropics/agentsmesh/backend/internal/service/ticket"
)

const ServiceName = "proto.mesh.v1.MeshService"

const (
	GetMeshTopologyProcedure    = "/" + ServiceName + "/GetMeshTopology"
	GetTicketPodsProcedure      = "/" + ServiceName + "/GetTicketPods"
	BatchGetTicketPodsProcedure = "/" + ServiceName + "/BatchGetTicketPods"
	CreatePodForTicketProcedure = "/" + ServiceName + "/CreatePodForTicket"
)

const MessageServiceName = "proto.mesh.v1.MeshMessageService"

const (
	ListMeshMessagesProcedure        = "/" + MessageServiceName + "/ListMeshMessages"
	GetMeshUnreadCountProcedure      = "/" + MessageServiceName + "/GetMeshUnreadCount"
	GetMeshMessageProcedure          = "/" + MessageServiceName + "/GetMeshMessage"
	MarkAllMeshMessagesReadProcedure = "/" + MessageServiceName + "/MarkAllMeshMessagesRead"
	GetMeshConversationProcedure     = "/" + MessageServiceName + "/GetMeshConversation"
	GetMeshSentMessagesProcedure     = "/" + MessageServiceName + "/GetMeshSentMessages"
	GetMeshDeadLettersProcedure      = "/" + MessageServiceName + "/GetMeshDeadLetters"
	ReplayMeshDeadLetterProcedure    = "/" + MessageServiceName + "/ReplayMeshDeadLetter"
)

// Server implements the MeshService contract. Mirrors REST's MeshHandler
// dependencies (mesh.go:17) — the mesh + ticket services in tandem because
// the ticket→pod lookups resolve the ticket by slug before delegating to
// the mesh service.
type Server struct {
	meshSvc   *meshservice.Service
	ticketSvc *ticketservice.Service
	orgSvc    middleware.OrganizationService
}

func NewServer(
	meshSvc *meshservice.Service,
	ticketSvc *ticketservice.Service,
	orgSvc middleware.OrganizationService,
) *Server {
	return &Server{meshSvc: meshSvc, ticketSvc: ticketSvc, orgSvc: orgSvc}
}

// MessageServer implements the MeshMessageService contract. Mirrors REST's
// MessageHandler — the agent message service is the underlying repository
// the REST DLQ handler also calls (messages_dlq.go).
type MessageServer struct {
	msgSvc *agentservice.MessageService
	orgSvc middleware.OrganizationService
}

func NewMessageServer(
	msgSvc *agentservice.MessageService, orgSvc middleware.OrganizationService,
) *MessageServer {
	return &MessageServer{msgSvc: msgSvc, orgSvc: orgSvc}
}

// mapServiceError mirrors REST's apierr translations (mesh.go). Translates
// mesh-domain sentinels to Connect codes per conventions §10. The mesh
// service mostly delegates to repo / pod / channel / binding services, so
// sentinels are imported from the package level (ErrTicketNotFound /
// ErrRunnerNotFound) rather than re-exported per-RPC.
func mapServiceError(err error) error {
	switch {
	case errors.Is(err, meshservice.ErrTicketNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, meshservice.ErrRunnerNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}

// mapMessageError translates agent.MessageService sentinels (message_types.go)
// to Connect codes per conventions §10.
func mapMessageError(err error) error {
	switch {
	case errors.Is(err, agentservice.ErrMessageNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, agentservice.ErrNotAuthorized):
		return connect.NewError(connect.CodePermissionDenied, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}

// Mount registers all MeshService procedures on mux behind the auth
// interceptor supplied via opts (cmd/server/connect_init.go).
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(GetMeshTopologyProcedure, connect.NewUnaryHandler(
		GetMeshTopologyProcedure, srv.GetMeshTopology, opts...,
	))
	mux.Handle(GetTicketPodsProcedure, connect.NewUnaryHandler(
		GetTicketPodsProcedure, srv.GetTicketPods, opts...,
	))
	mux.Handle(BatchGetTicketPodsProcedure, connect.NewUnaryHandler(
		BatchGetTicketPodsProcedure, srv.BatchGetTicketPods, opts...,
	))
	mux.Handle(CreatePodForTicketProcedure, connect.NewUnaryHandler(
		CreatePodForTicketProcedure, srv.CreatePodForTicket, opts...,
	))
}

// MountMessages registers all MeshMessageService procedures on mux behind
// the auth interceptor supplied via opts. Wires the same auth surface as
// MeshService — REST's per-pod X-Pod-Key model collapses to Bearer +
// pod_key-in-payload on Connect.
func MountMessages(mux *http.ServeMux, srv *MessageServer, opts ...connect.HandlerOption) {
	mux.Handle(ListMeshMessagesProcedure, connect.NewUnaryHandler(
		ListMeshMessagesProcedure, srv.ListMeshMessages, opts...,
	))
	mux.Handle(GetMeshUnreadCountProcedure, connect.NewUnaryHandler(
		GetMeshUnreadCountProcedure, srv.GetMeshUnreadCount, opts...,
	))
	mux.Handle(GetMeshMessageProcedure, connect.NewUnaryHandler(
		GetMeshMessageProcedure, srv.GetMeshMessage, opts...,
	))
	mux.Handle(MarkAllMeshMessagesReadProcedure, connect.NewUnaryHandler(
		MarkAllMeshMessagesReadProcedure, srv.MarkAllMeshMessagesRead, opts...,
	))
	mux.Handle(GetMeshConversationProcedure, connect.NewUnaryHandler(
		GetMeshConversationProcedure, srv.GetMeshConversation, opts...,
	))
	mux.Handle(GetMeshSentMessagesProcedure, connect.NewUnaryHandler(
		GetMeshSentMessagesProcedure, srv.GetMeshSentMessages, opts...,
	))
	mux.Handle(GetMeshDeadLettersProcedure, connect.NewUnaryHandler(
		GetMeshDeadLettersProcedure, srv.GetMeshDeadLetters, opts...,
	))
	mux.Handle(ReplayMeshDeadLetterProcedure, connect.NewUnaryHandler(
		ReplayMeshDeadLetterProcedure, srv.ReplayMeshDeadLetter, opts...,
	))
}
