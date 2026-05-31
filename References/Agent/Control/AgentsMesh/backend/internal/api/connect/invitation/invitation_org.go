package invitationconnect

import (
	"context"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	invitationsvc "github.com/anthropics/agentsmesh/backend/internal/service/invitation"
	invitationv1 "github.com/anthropics/agentsmesh/proto/gen/go/invitation/v1"
)

// ListInvitations returns pending + accepted invitations for the org.
// Membership-only — admin role not required for read (mirrors REST GET
// /api/v1/orgs/:slug/invitations at invitations_org.go:104).
func (s *Server) ListInvitations(
	ctx context.Context, req *connect.Request[invitationv1.ListInvitationsRequest],
) (*connect.Response[invitationv1.ListInvitationsResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	invitations, err := s.invitationSvc.ListByOrganization(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*invitationv1.Invitation, 0, len(invitations))
	for _, inv := range invitations {
		items = append(items, toProtoInvitation(inv))
	}
	return connect.NewResponse(&invitationv1.ListInvitationsResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  req.Msg.GetLimit(),
		Offset: req.Msg.GetOffset(),
	}), nil
}

// CreateInvitation sends a new invitation. Admin-gated. Checks seat
// availability through the optional billing service before issuing the
// invitation. Mirrors REST POST /api/v1/orgs/:slug/invitations
// (invitations_org.go:18-100).
func (s *Server) CreateInvitation(
	ctx context.Context, req *connect.Request[invitationv1.CreateInvitationRequest],
) (*connect.Response[invitationv1.Invitation], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireAdmin(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	if s.billingSvc != nil {
		if err := s.billingSvc.CheckSeatAvailability(ctx, tenant.OrganizationID, 1); err != nil {
			return nil, mapBillingError(err)
		}
	}

	inviter, err := s.userSvc.GetByID(ctx, tenant.UserID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	org, err := s.orgInternal.GetByID(ctx, tenant.OrganizationID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}

	inviterName := inviter.Username
	if inviter.Name != nil && *inviter.Name != "" {
		inviterName = *inviter.Name
	}

	inv, err := s.invitationSvc.Create(ctx, &invitationsvc.CreateRequest{
		OrganizationID: tenant.OrganizationID,
		Email:          req.Msg.GetEmail(),
		Role:           req.Msg.GetRole(),
		InviterID:      tenant.UserID,
		InviterName:    inviterName,
		OrgName:        org.Name,
	})
	if err != nil {
		return nil, mapInvitationError(err)
	}
	return connect.NewResponse(toProtoInvitation(inv)), nil
}

// RevokeInvitation deletes a pending invitation. Admin-gated. Mirrors REST
// DELETE /api/v1/orgs/:slug/invitations/:id (invitations_org.go:122-165).
func (s *Server) RevokeInvitation(
	ctx context.Context, req *connect.Request[invitationv1.RevokeInvitationRequest],
) (*connect.Response[invitationv1.RevokeInvitationResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireAdmin(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	// REST cross-checks invitation.OrganizationID before deletion to defeat
	// IDOR-style probing across orgs — mirror that here.
	inv, err := s.invitationSvc.GetByID(ctx, req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound, err)
	}
	if inv.OrganizationID != tenant.OrganizationID {
		return nil, connect.NewError(connect.CodeNotFound,
			invitationsvc.ErrInvitationNotFound)
	}

	if err := s.invitationSvc.Revoke(ctx, req.Msg.GetId()); err != nil {
		return nil, mapInvitationError(err)
	}
	return connect.NewResponse(&invitationv1.RevokeInvitationResponse{
		Message: "Invitation revoked successfully",
	}), nil
}

// ResendInvitation re-sends an invitation email and (re)extends expiration.
// Admin-gated. Mirrors REST POST /api/v1/orgs/:slug/invitations/:id/resend
// (invitations_org.go:169-229).
func (s *Server) ResendInvitation(
	ctx context.Context, req *connect.Request[invitationv1.ResendInvitationRequest],
) (*connect.Response[invitationv1.ResendInvitationResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if err := requireAdmin(ctx); err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)

	inv, err := s.invitationSvc.GetByID(ctx, req.Msg.GetId())
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound, err)
	}
	if inv.OrganizationID != tenant.OrganizationID {
		return nil, connect.NewError(connect.CodeNotFound,
			invitationsvc.ErrInvitationNotFound)
	}

	// REST best-effort populates inviter/org names; failures fall back to
	// stub strings — mirror that here so a missing user doesn't 500.
	inviterName := "Someone"
	if inviter, ierr := s.userSvc.GetByID(ctx, tenant.UserID); ierr == nil && inviter != nil {
		inviterName = inviter.Username
		if inviter.Name != nil && *inviter.Name != "" {
			inviterName = *inviter.Name
		}
	}
	orgName := "the organization"
	if org, oerr := s.orgInternal.GetByID(ctx, tenant.OrganizationID); oerr == nil && org != nil {
		orgName = org.Name
	}

	if err := s.invitationSvc.Resend(ctx, req.Msg.GetId(), inviterName, orgName); err != nil {
		return nil, mapInvitationError(err)
	}
	return connect.NewResponse(&invitationv1.ResendInvitationResponse{
		Message: "Invitation resent successfully",
	}), nil
}
