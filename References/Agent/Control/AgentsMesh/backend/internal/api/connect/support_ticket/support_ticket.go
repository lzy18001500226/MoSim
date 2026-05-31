// Package supportticketconnect hosts Connect-RPC handlers for the
// user-facing support ticket domain. All wire is Connect-binary
// (conventions §2.5). The legacy multipart REST endpoints are gone — file
// attachments flow through a 3-step presigned-URL handshake (see
// support_ticket_attachments.go).
//
// User-scoped service (conventions §3.5 exception #1): the caller is
// identified by the auth interceptor's UserID; there is no `org_slug`
// in any request. The handler delegates ownership checks to the
// service layer (`service.supportticket`).
//
// Split rationale (CLAUDE.md 200-line rule):
//   - support_ticket.go              — service scaffolding + Mount
//   - support_ticket_handlers.go     — list / get / attachment-url
//   - support_ticket_attachments.go  — create / message / presign / associate
//   - support_ticket_convert.go      — domain ↔ proto field translation
//   - support_ticket_errors.go       — error mapping + auth guard
package supportticketconnect

import (
	"net/http"

	"connectrpc.com/connect"

	supportticketsvc "github.com/anthropics/agentsmesh/backend/internal/service/supportticket"
)

const (
	ServiceName = "proto.support_ticket.v1.SupportTicketService"

	ListSupportTicketsProcedure      = "/" + ServiceName + "/ListSupportTickets"
	GetSupportTicketProcedure        = "/" + ServiceName + "/GetSupportTicket"
	GetAttachmentURLProcedure        = "/" + ServiceName + "/GetAttachmentUrl"
	CreateSupportTicketProcedure     = "/" + ServiceName + "/CreateSupportTicket"
	AddSupportTicketMessageProcedure = "/" + ServiceName + "/AddSupportTicketMessage"
	PresignAttachmentUploadProcedure = "/" + ServiceName + "/PresignAttachmentUpload"
	AssociateAttachmentsProcedure    = "/" + ServiceName + "/AssociateAttachments"
)

// Server implements SupportTicketService. Single dependency (the service
// layer); ownership / access checks live there, not here.
type Server struct {
	svc *supportticketsvc.Service
}

func NewServer(svc *supportticketsvc.Service) *Server {
	return &Server{svc: svc}
}

// Mount registers procedures behind the auth interceptor supplied via opts
// (cmd/server/connect_init.go). User-scoped only — no public variant.
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListSupportTicketsProcedure, connect.NewUnaryHandler(
		ListSupportTicketsProcedure, srv.ListSupportTickets, opts...,
	))
	mux.Handle(GetSupportTicketProcedure, connect.NewUnaryHandler(
		GetSupportTicketProcedure, srv.GetSupportTicket, opts...,
	))
	mux.Handle(GetAttachmentURLProcedure, connect.NewUnaryHandler(
		GetAttachmentURLProcedure, srv.GetAttachmentURL, opts...,
	))
	mux.Handle(CreateSupportTicketProcedure, connect.NewUnaryHandler(
		CreateSupportTicketProcedure, srv.CreateSupportTicket, opts...,
	))
	mux.Handle(AddSupportTicketMessageProcedure, connect.NewUnaryHandler(
		AddSupportTicketMessageProcedure, srv.AddSupportTicketMessage, opts...,
	))
	mux.Handle(PresignAttachmentUploadProcedure, connect.NewUnaryHandler(
		PresignAttachmentUploadProcedure, srv.PresignAttachmentUpload, opts...,
	))
	mux.Handle(AssociateAttachmentsProcedure, connect.NewUnaryHandler(
		AssociateAttachmentsProcedure, srv.AssociateAttachments, opts...,
	))
}
