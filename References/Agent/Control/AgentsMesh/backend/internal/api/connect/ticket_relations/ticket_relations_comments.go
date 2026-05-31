package ticketrelationsconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	ticketrelationsv1 "github.com/anthropics/agentsmesh/proto/gen/go/ticket_relations/v1"
)

// ListComments mirrors REST `ListComments` (ticket_comments.go:38). REST
// defaults limit=50, offset=0 when query parameters are absent — preserved
// here so callers omitting the optional fields land on the same page size.
func (s *Server) ListComments(
	ctx context.Context, req *connect.Request[ticketrelationsv1.ListCommentsRequest],
) (*connect.Response[ticketrelationsv1.ListCommentsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	limit := int(req.Msg.GetLimit())
	if limit == 0 {
		limit = 50
	}
	offset := int(req.Msg.GetOffset())

	comments, total, err := s.ticketSvc.ListComments(ctx, t.ID, limit, offset)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*ticketrelationsv1.Comment, 0, len(comments))
	for _, c := range comments {
		items = append(items, toProtoComment(c))
	}
	return connect.NewResponse(&ticketrelationsv1.ListCommentsResponse{
		Items:  items,
		Total:  total,
		Limit:  int32(limit),
		Offset: int32(offset),
	}), nil
}

// CreateComment mirrors REST `CreateComment` (ticket_comments.go:67).
func (s *Server) CreateComment(
	ctx context.Context, req *connect.Request[ticketrelationsv1.CreateCommentRequest],
) (*connect.Response[ticketrelationsv1.Comment], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	comment, err := s.ticketSvc.CreateComment(
		ctx, t.ID, tenant.UserID,
		req.Msg.GetContent(),
		req.Msg.ParentId,
		fromProtoMentions(req.Msg.GetMentions()),
	)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoComment(comment)), nil
}

// UpdateComment mirrors REST `UpdateComment` (ticket_comments.go:115).
func (s *Server) UpdateComment(
	ctx context.Context, req *connect.Request[ticketrelationsv1.UpdateCommentRequest],
) (*connect.Response[ticketrelationsv1.Comment], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	comment, err := s.ticketSvc.UpdateComment(
		ctx, t.ID, req.Msg.GetCommentId(), tenant.UserID,
		req.Msg.GetContent(),
		fromProtoMentions(req.Msg.GetMentions()),
	)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoComment(comment)), nil
}

// DeleteComment mirrors REST `DeleteComment` (ticket_comments.go:173).
func (s *Server) DeleteComment(
	ctx context.Context, req *connect.Request[ticketrelationsv1.DeleteCommentRequest],
) (*connect.Response[ticketrelationsv1.DeleteCommentResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	if err := s.ticketSvc.DeleteComment(ctx, t.ID, req.Msg.GetCommentId(), tenant.UserID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&ticketrelationsv1.DeleteCommentResponse{}), nil
}
