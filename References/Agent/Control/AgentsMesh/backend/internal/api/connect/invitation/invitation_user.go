package invitationconnect

import (
	"context"
	"log/slog"

	"connectrpc.com/connect"

	invitationv1 "github.com/anthropics/agentsmesh/proto/gen/go/invitation/v1"
)

// AcceptInvitation accepts an invitation by token. User-scoped — auth
// interceptor supplies the caller's UserID; no org_slug is needed because
// the invitee may not yet be a member of any org (conventions §3.5 #1).
// Mirrors REST POST /api/v1/invitations/:token/accept
// (invitations_user.go:29-54).
func (s *Server) AcceptInvitation(
	ctx context.Context, req *connect.Request[invitationv1.AcceptInvitationRequest],
) (*connect.Response[invitationv1.AcceptInvitationResponse], error) {
	userID, err := userIDFromCtx(ctx)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetToken() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errInvitationEmptyToken)
	}
	result, err := s.invitationSvc.Accept(ctx, req.Msg.GetToken(), userID)
	if err != nil {
		return nil, mapInvitationError(err)
	}
	return connect.NewResponse(&invitationv1.AcceptInvitationResponse{
		Message:      "Successfully joined the organization",
		Organization: toProtoAcceptedOrg(result.Organization),
	}), nil
}

// ListPendingInvitations lists invitations addressed to the caller's email.
// User-scoped — no org_slug. Mirrors REST GET /api/v1/invitations/pending
// (invitations_user.go:58-92).
//
// REST enriches each invitation with org info — replicate that here. Per-
// invitation org lookups that fail silently skip the row (matching REST's
// continue-on-error semantics — a deleted org shouldn't break the list).
func (s *Server) ListPendingInvitations(
	ctx context.Context, _ *connect.Request[invitationv1.ListPendingInvitationsRequest],
) (*connect.Response[invitationv1.ListPendingInvitationsResponse], error) {
	userID, err := userIDFromCtx(ctx)
	if err != nil {
		return nil, err
	}
	user, err := s.userSvc.GetByID(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	invitations, err := s.invitationSvc.ListPendingByEmail(ctx, user.Email)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	items := make([]*invitationv1.PendingInvitation, 0, len(invitations))
	for _, inv := range invitations {
		org, oerr := s.orgInternal.GetByID(ctx, inv.OrganizationID)
		if oerr != nil {
			slog.WarnContext(ctx, "skip pending invitation: org lookup failed",
				"invitation_id", inv.ID, "org_id", inv.OrganizationID, "error", oerr)
			continue
		}
		items = append(items, &invitationv1.PendingInvitation{
			Id:               inv.ID,
			OrganizationId:   inv.OrganizationID,
			OrganizationName: org.Name,
			OrganizationSlug: org.Slug,
			Role:             inv.Role,
			ExpiresAt:        inv.ExpiresAt.Format("2006-01-02T15:04:05Z"),
			Token:            inv.Token,
		})
	}
	return connect.NewResponse(&invitationv1.ListPendingInvitationsResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  0,
		Offset: 0,
	}), nil
}
