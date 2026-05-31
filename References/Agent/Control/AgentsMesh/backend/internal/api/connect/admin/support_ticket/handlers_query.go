package supportticketadminconnect

import (
	"context"
	"log/slog"
	"math"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	supportticketsvc "github.com/anthropics/agentsmesh/backend/internal/service/supportticket"
	supportticketv1 "github.com/anthropics/agentsmesh/proto/gen/go/support_ticket/v1"
)

// ListSupportTickets mirrors REST's List (support_tickets.go:52).
// Pagination defaults match the REST query parser (page=1, page_size=20).
func (s *Server) ListSupportTickets(
	ctx context.Context, req *connect.Request[supportticketv1.AdminListSupportTicketsRequest],
) (*connect.Response[supportticketv1.AdminListSupportTicketsResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	page := int(req.Msg.GetPage())
	if page < 1 {
		page = 1
	}
	pageSize := int(req.Msg.GetPageSize())
	if pageSize < 1 {
		pageSize = 20
	}

	result, err := s.svc.AdminList(ctx, &supportticketsvc.AdminListQuery{
		Search:   req.Msg.GetSearch(),
		Status:   req.Msg.GetStatus(),
		Category: req.Msg.GetCategory(),
		Priority: req.Msg.GetPriority(),
		Page:     page,
		PageSize: pageSize,
	})
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*supportticketv1.AdminSupportTicket, 0, len(result.Data))
	for i := range result.Data {
		items = append(items, ToProtoAdminSupportTicket(&result.Data[i]))
	}

	totalPages := int32(0)
	if result.PageSize > 0 {
		totalPages = int32(math.Ceil(float64(result.Total) / float64(result.PageSize)))
	}

	return connect.NewResponse(&supportticketv1.AdminListSupportTicketsResponse{
		Data:       items,
		Total:      result.Total,
		Page:       int32(result.Page),
		PageSize:   int32(result.PageSize),
		TotalPages: totalPages,
	}), nil
}

// GetSupportTicketStats mirrors REST's GetStats (support_tickets.go:80).
func (s *Server) GetSupportTicketStats(
	ctx context.Context, _ *connect.Request[supportticketv1.GetSupportTicketStatsRequest],
) (*connect.Response[supportticketv1.SupportTicketStats], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	stats, err := s.svc.AdminGetStats(ctx)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	return connect.NewResponse(&supportticketv1.SupportTicketStats{
		Total:      stats.Total,
		Open:       stats.Open,
		InProgress: stats.InProgress,
		Resolved:   stats.Resolved,
		Closed:     stats.Closed,
	}), nil
}

// GetSupportTicket mirrors REST's GetByID (support_tickets.go:92). Best-effort
// message load — failures log+swallow, matching REST behavior.
func (s *Server) GetSupportTicket(
	ctx context.Context, req *connect.Request[supportticketv1.AdminGetSupportTicketRequest],
) (*connect.Response[supportticketv1.AdminSupportTicketDetail], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	id := req.Msg.GetId()
	ticket, err := s.svc.AdminGetByID(ctx, id)
	if err != nil {
		return nil, mapServiceError(err)
	}

	messages, err := s.svc.AdminListMessages(ctx, id)
	if err != nil {
		slog.WarnContext(ctx, "failed to load messages for ticket",
			"ticket_id", id, "error", err)
		messages = nil
	}

	protoMsgs := make([]*supportticketv1.AdminSupportTicketMessage, 0, len(messages))
	for i := range messages {
		protoMsgs = append(protoMsgs, ToProtoAdminSupportTicketMessage(&messages[i]))
	}

	return connect.NewResponse(&supportticketv1.AdminSupportTicketDetail{
		Ticket:   ToProtoAdminSupportTicket(ticket),
		Messages: protoMsgs,
	}), nil
}

// ListSupportTicketMessages mirrors REST's ListMessages (support_tickets.go:122).
func (s *Server) ListSupportTicketMessages(
	ctx context.Context, req *connect.Request[supportticketv1.AdminListSupportTicketMessagesRequest],
) (*connect.Response[supportticketv1.AdminListSupportTicketMessagesResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	messages, err := s.svc.AdminListMessages(ctx, req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	out := make([]*supportticketv1.AdminSupportTicketMessage, 0, len(messages))
	for i := range messages {
		out = append(out, ToProtoAdminSupportTicketMessage(&messages[i]))
	}

	return connect.NewResponse(&supportticketv1.AdminListSupportTicketMessagesResponse{
		Data: out,
	}), nil
}

// GetSupportTicketAttachmentUrl mirrors REST's GetAttachmentURL
// (support_ticket_actions.go:178).
func (s *Server) GetSupportTicketAttachmentUrl(
	ctx context.Context, req *connect.Request[supportticketv1.AdminGetSupportTicketAttachmentUrlRequest],
) (*connect.Response[supportticketv1.AdminGetSupportTicketAttachmentUrlResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	url, err := s.svc.AdminGetAttachmentURL(ctx, req.Msg.GetAttachmentId())
	if err != nil {
		return nil, mapServiceError(err)
	}

	return connect.NewResponse(&supportticketv1.AdminGetSupportTicketAttachmentUrlResponse{
		Url: url,
	}), nil
}
