package invitationconnect

import (
	invitationdomain "github.com/anthropics/agentsmesh/backend/internal/domain/invitation"
	invitationsvc "github.com/anthropics/agentsmesh/backend/internal/service/invitation"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	invitationv1 "github.com/anthropics/agentsmesh/proto/gen/go/invitation/v1"
)

// toProtoInvitation converts the GORM-backed domain model into the wire
// shape used by the org-scoped list. Token is intentionally absent — only
// the invitee receives it via email, never via list APIs.
func toProtoInvitation(inv *invitationdomain.Invitation) *invitationv1.Invitation {
	if inv == nil {
		return nil
	}
	out := &invitationv1.Invitation{
		Id:             inv.ID,
		OrganizationId: inv.OrganizationID,
		Email:          inv.Email,
		Role:           inv.Role,
		InvitedBy:      inv.InvitedBy,
		ExpiresAt:      protoconv.RFC3339(inv.ExpiresAt),
		CreatedAt:      protoconv.RFC3339(inv.CreatedAt),
		UpdatedAt:      protoconv.RFC3339(inv.UpdatedAt),
	}
	if inv.AcceptedAt != nil {
		out.AcceptedAt = protoconv.RFC3339Ptr(inv.AcceptedAt)
	}
	return out
}

// toProtoInvitationInfo converts the service-layer InvitationInfo (which
// already joined org + inviter + computed is_expired) to wire shape.
func toProtoInvitationInfo(info *invitationsvc.InvitationInfo) *invitationv1.InvitationInfo {
	if info == nil {
		return nil
	}
	return &invitationv1.InvitationInfo{
		Id:                info.ID,
		Email:             info.Email,
		Role:              info.Role,
		OrganizationId:    info.OrgID,
		OrganizationName:  info.OrgName,
		OrganizationSlug:  info.OrgSlug,
		InviterName:       info.InviterName,
		ExpiresAt:         protoconv.RFC3339(info.ExpiresAt),
		IsExpired:         info.IsExpired,
	}
}

// toProtoAcceptedOrg mirrors service.AcceptOrgInfo onto the wire.
func toProtoAcceptedOrg(o *invitationsvc.AcceptOrgInfo) *invitationv1.AcceptedOrgInfo {
	if o == nil {
		return nil
	}
	return &invitationv1.AcceptedOrgInfo{
		Id:   o.ID,
		Name: o.Name,
		Slug: o.Slug,
	}
}
