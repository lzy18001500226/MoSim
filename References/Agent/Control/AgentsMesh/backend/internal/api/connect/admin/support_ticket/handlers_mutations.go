package supportticketadminconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/domain/admin"
	supportticketsvc "github.com/anthropics/agentsmesh/backend/internal/service/supportticket"
	supportticketv1 "github.com/anthropics/agentsmesh/proto/gen/go/support_ticket/v1"
)

// ReplySupportTicket mirrors REST's Reply (support_ticket_actions.go:18) for
// the JSON-only path. Multipart attachment uploads stay on REST; the Connect
// RPC accepts only content. Empty content is rejected with InvalidArgument to
// match REST's validation behavior.
func (s *Server) ReplySupportTicket(
	ctx context.Context, req *connect.Request[supportticketv1.AdminReplySupportTicketRequest],
) (*connect.Response[supportticketv1.AdminSupportTicketMessage], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	ticketID := req.Msg.GetId()
	content := req.Msg.GetContent()
	if content == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("content is required"))
	}

	msg, err := s.svc.AdminAddReply(ctx, ticketID, adminUser.ID, &supportticketsvc.AddMessageRequest{
		Content: content,
	})
	if err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.adminSvc, adminUser.ID,
		admin.AuditActionSupportTicketReply, admin.TargetTypeSupportTicket, ticketID,
		nil, map[string]any{"content": content},
		req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(ToProtoAdminSupportTicketMessage(msg)), nil
}

// UpdateSupportTicketStatus mirrors REST's UpdateStatus
// (support_ticket_actions.go:90). Pre-fetches the ticket to capture the
// old status for the audit log, mirroring REST behavior at line 103.
func (s *Server) UpdateSupportTicketStatus(
	ctx context.Context, req *connect.Request[supportticketv1.AdminUpdateSupportTicketStatusRequest],
) (*connect.Response[supportticketv1.AdminUpdateSupportTicketStatusResponse], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	ticketID := req.Msg.GetId()
	newStatus := req.Msg.GetStatus()

	oldTicket, err := s.svc.AdminGetByID(ctx, ticketID)
	if err != nil {
		return nil, mapServiceError(err)
	}

	if err := s.svc.AdminUpdateStatus(ctx, ticketID, newStatus); err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.adminSvc, adminUser.ID,
		admin.AuditActionSupportTicketStatus, admin.TargetTypeSupportTicket, ticketID,
		map[string]any{"status": oldTicket.Status},
		map[string]any{"status": newStatus},
		req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(&supportticketv1.AdminUpdateSupportTicketStatusResponse{
		Message: "Status updated",
	}), nil
}

// AssignSupportTicket mirrors REST's Assign (support_ticket_actions.go:144).
// If admin_id is nil, the caller is assigned (REST default at line 155).
func (s *Server) AssignSupportTicket(
	ctx context.Context, req *connect.Request[supportticketv1.AdminAssignSupportTicketRequest],
) (*connect.Response[supportticketv1.AdminAssignSupportTicketResponse], error) {
	ctx, adminUser, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	ticketID := req.Msg.GetId()
	assignedAdminID := adminUser.ID
	if req.Msg.AdminId != nil {
		assignedAdminID = *req.Msg.AdminId
	}

	if err := s.svc.AdminAssign(ctx, ticketID, assignedAdminID); err != nil {
		return nil, mapServiceError(err)
	}

	logAdminAction(ctx, s.adminSvc, adminUser.ID,
		admin.AuditActionSupportTicketAssign, admin.TargetTypeSupportTicket, ticketID,
		nil,
		map[string]any{"assigned_admin_id": assignedAdminID},
		req.Peer().Addr, req.Header().Get("User-Agent"))

	return connect.NewResponse(&supportticketv1.AdminAssignSupportTicketResponse{
		Message: "Ticket assigned",
	}), nil
}
