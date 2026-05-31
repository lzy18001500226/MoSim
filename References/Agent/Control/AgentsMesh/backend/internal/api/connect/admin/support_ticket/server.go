// Package supportticketadminconnect hosts Connect-RPC handlers for the
// platform-admin support ticket surface. Mirrors REST handlers in
// backend/internal/api/rest/v1/admin/support_tickets.go (list/stats/get/
// messages) and support_ticket_actions.go (reply/status/assign/attachment).
//
// Auth model: every RPC calls interceptors.ResolveSystemAdmin to mirror
// REST's AdminMiddleware (is_system_admin + is_active checks). The
// user-facing SupportTicketService lives next door at
// backend/internal/api/connect/support_ticket/ — separate auth surface,
// so keep the packages split to prevent transport-level drift.
//
// File-upload note: the Reply RPC handles JSON-only replies. Multipart
// attachment uploads stay on the REST /reply endpoint during the dual-track
// window — Connect-RPC has no multipart story. The web-admin renderer is
// expected to fall back to REST when files are attached.
package supportticketadminconnect

import (
	"errors"
	"net/http"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/infra/database"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	"github.com/anthropics/agentsmesh/backend/internal/service/supportticket"
)

const ServiceName = "proto.support_ticket.v1.SupportTicketAdminService"

const (
	ListSupportTicketsProcedure              = "/" + ServiceName + "/ListSupportTickets"
	GetSupportTicketStatsProcedure           = "/" + ServiceName + "/GetSupportTicketStats"
	GetSupportTicketProcedure                = "/" + ServiceName + "/GetSupportTicket"
	ListSupportTicketMessagesProcedure       = "/" + ServiceName + "/ListSupportTicketMessages"
	ReplySupportTicketProcedure              = "/" + ServiceName + "/ReplySupportTicket"
	UpdateSupportTicketStatusProcedure       = "/" + ServiceName + "/UpdateSupportTicketStatus"
	AssignSupportTicketProcedure             = "/" + ServiceName + "/AssignSupportTicket"
	GetSupportTicketAttachmentUrlProcedure   = "/" + ServiceName + "/GetSupportTicketAttachmentUrl"
)

// Server implements SupportTicketAdminService. `db` threads through to
// ResolveSystemAdmin's user lookup — same source as REST's
// AdminMiddleware so the two paths can't diverge on is_system_admin.
// `adminSvc` powers audit logging; `svc` performs CRUD.
type Server struct {
	svc      *supportticket.Service
	adminSvc *adminservice.Service
	db       database.DB
}

func NewServer(svc *supportticket.Service, adminSvc *adminservice.Service, db database.DB) *Server {
	return &Server{svc: svc, adminSvc: adminSvc, db: db}
}

// Mount wires every SupportTicketAdminService procedure onto mux. The auth
// interceptor in opts validates the JWT; per-handler ResolveSystemAdmin
// enforces is_system_admin.
func Mount(mux *http.ServeMux, srv *Server, opts ...connect.HandlerOption) {
	mux.Handle(ListSupportTicketsProcedure, connect.NewUnaryHandler(
		ListSupportTicketsProcedure, srv.ListSupportTickets, opts...,
	))
	mux.Handle(GetSupportTicketStatsProcedure, connect.NewUnaryHandler(
		GetSupportTicketStatsProcedure, srv.GetSupportTicketStats, opts...,
	))
	mux.Handle(GetSupportTicketProcedure, connect.NewUnaryHandler(
		GetSupportTicketProcedure, srv.GetSupportTicket, opts...,
	))
	mux.Handle(ListSupportTicketMessagesProcedure, connect.NewUnaryHandler(
		ListSupportTicketMessagesProcedure, srv.ListSupportTicketMessages, opts...,
	))
	mux.Handle(ReplySupportTicketProcedure, connect.NewUnaryHandler(
		ReplySupportTicketProcedure, srv.ReplySupportTicket, opts...,
	))
	mux.Handle(UpdateSupportTicketStatusProcedure, connect.NewUnaryHandler(
		UpdateSupportTicketStatusProcedure, srv.UpdateSupportTicketStatus, opts...,
	))
	mux.Handle(AssignSupportTicketProcedure, connect.NewUnaryHandler(
		AssignSupportTicketProcedure, srv.AssignSupportTicket, opts...,
	))
	mux.Handle(GetSupportTicketAttachmentUrlProcedure, connect.NewUnaryHandler(
		GetSupportTicketAttachmentUrlProcedure, srv.GetSupportTicketAttachmentUrl, opts...,
	))
}

// mapServiceError translates supportticket sentinels to Connect codes,
// mirroring apierr translation in REST handlers (support_tickets.go:101,
// support_ticket_actions.go:37/126).
func mapServiceError(err error) error {
	switch {
	case errors.Is(err, supportticket.ErrTicketNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, supportticket.ErrAttachmentNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, supportticket.ErrInvalidStatus):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, supportticket.ErrInvalidTransition):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, supportticket.ErrInvalidCategory):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, supportticket.ErrInvalidPriority):
		return connect.NewError(connect.CodeInvalidArgument, err)
	}
	return connect.NewError(connect.CodeInternal, err)
}
