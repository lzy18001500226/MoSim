package ticketrelationsconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	ticketrelationsv1 "github.com/anthropics/agentsmesh/proto/gen/go/ticket_relations/v1"
)

// ListRelations mirrors REST `ListRelations` (ticket_relations.go:22).
func (s *Server) ListRelations(
	ctx context.Context, req *connect.Request[ticketrelationsv1.ListRelationsRequest],
) (*connect.Response[ticketrelationsv1.ListRelationsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	relations, err := s.ticketSvc.ListRelations(ctx, t.ID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*ticketrelationsv1.Relation, 0, len(relations))
	for _, r := range relations {
		items = append(items, toProtoRelation(r))
	}
	return connect.NewResponse(&ticketrelationsv1.ListRelationsResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}

// CreateRelation mirrors REST `CreateRelation` (ticket_relations.go:43).
// Re-uses the REST handler's two-ticket lookup pattern — source + target are
// both org-scoped GetTicketBySlug calls before delegating to the service.
func (s *Server) CreateRelation(
	ctx context.Context, req *connect.Request[ticketrelationsv1.CreateRelationRequest],
) (*connect.Response[ticketrelationsv1.Relation], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	source, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}
	target, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTargetSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	relation, err := s.ticketSvc.CreateRelation(
		ctx, tenant.OrganizationID, source.ID, target.ID, req.Msg.GetRelationType(),
	)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoRelation(relation)), nil
}

// DeleteRelation mirrors REST `DeleteRelation` (ticket_relations.go:85). The
// REST handler does a ticket existence check before deleting — preserved here
// so a misrouted relation_id can't punch through to a different org's row.
func (s *Server) DeleteRelation(
	ctx context.Context, req *connect.Request[ticketrelationsv1.DeleteRelationRequest],
) (*connect.Response[ticketrelationsv1.DeleteRelationResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	if _, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug()); err != nil {
		return nil, mapServiceError(err)
	}
	if err := s.ticketSvc.DeleteRelation(ctx, req.Msg.GetRelationId()); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&ticketrelationsv1.DeleteRelationResponse{}), nil
}

// ListMergeRequests mirrors REST `ListMergeRequests` (ticket_relations.go:112).
func (s *Server) ListMergeRequests(
	ctx context.Context, req *connect.Request[ticketrelationsv1.ListMergeRequestsRequest],
) (*connect.Response[ticketrelationsv1.ListMergeRequestsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	mrs, err := s.ticketSvc.ListMergeRequests(ctx, t.ID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*ticketrelationsv1.MergeRequest, 0, len(mrs))
	for _, mr := range mrs {
		items = append(items, toProtoMergeRequest(mr))
	}
	return connect.NewResponse(&ticketrelationsv1.ListMergeRequestsResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}
