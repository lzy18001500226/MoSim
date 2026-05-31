package ticketrelationsconnect

import (
	"context"
	"errors"
	"time"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	ticketrelationsv1 "github.com/anthropics/agentsmesh/proto/gen/go/ticket_relations/v1"
)

// ListCommits mirrors REST `ListCommits` (ticket_commits.go:25).
func (s *Server) ListCommits(
	ctx context.Context, req *connect.Request[ticketrelationsv1.ListCommitsRequest],
) (*connect.Response[ticketrelationsv1.ListCommitsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}

	commits, err := s.ticketSvc.ListCommits(ctx, t.ID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*ticketrelationsv1.Commit, 0, len(commits))
	for _, c := range commits {
		items = append(items, toProtoCommit(c))
	}
	return connect.NewResponse(&ticketrelationsv1.ListCommitsResponse{
		Items: items,
		Total: int64(len(items)),
	}), nil
}

// LinkCommit mirrors REST `LinkCommit` (ticket_commits.go:46). The REST
// handler rejects when ticket.RepositoryID is nil — preserved as
// FailedPrecondition (Connect mapping for the 400 BadRequest).
func (s *Server) LinkCommit(
	ctx context.Context, req *connect.Request[ticketrelationsv1.LinkCommitRequest],
) (*connect.Response[ticketrelationsv1.Commit], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	t, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug())
	if err != nil {
		return nil, mapServiceError(err)
	}
	if t.RepositoryID == nil {
		return nil, connect.NewError(connect.CodeFailedPrecondition, errors.New("ticket has no repository"))
	}

	committedAt, err := parseOptionalRFC3339(req.Msg.CommittedAt)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}

	commit, err := s.ticketSvc.LinkCommit(
		ctx,
		tenant.OrganizationID,
		t.ID,
		*t.RepositoryID,
		nil, // podID — REST handler always passes nil; no proto field yet
		req.Msg.GetCommitSha(),
		req.Msg.GetCommitMessage(),
		req.Msg.CommitUrl,
		req.Msg.AuthorName,
		req.Msg.AuthorEmail,
		committedAt,
	)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(toProtoCommit(commit)), nil
}

// UnlinkCommit mirrors REST `UnlinkCommit` (ticket_commits.go:102).
func (s *Server) UnlinkCommit(
	ctx context.Context, req *connect.Request[ticketrelationsv1.UnlinkCommitRequest],
) (*connect.Response[ticketrelationsv1.UnlinkCommitResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	if _, err := s.ticketSvc.GetTicketBySlug(ctx, tenant.OrganizationID, req.Msg.GetTicketSlug()); err != nil {
		return nil, mapServiceError(err)
	}
	if err := s.ticketSvc.UnlinkCommit(ctx, req.Msg.GetCommitId()); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&ticketrelationsv1.UnlinkCommitResponse{}), nil
}

// parseOptionalRFC3339 maps an optional ISO-8601 string to *time.Time. Empty
// string treated as absent (REST handler also accepted "" as nil).
func parseOptionalRFC3339(s *string) (*time.Time, error) {
	if s == nil || *s == "" {
		return nil, nil
	}
	t, err := time.Parse(time.RFC3339, *s)
	if err != nil {
		return nil, err
	}
	return &t, nil
}
