package supportticketadminconnect

import (
	supportticketdomain "github.com/anthropics/agentsmesh/backend/internal/domain/supportticket"
	domainuser "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	supportticketv1 "github.com/anthropics/agentsmesh/proto/gen/go/support_ticket/v1"
)

// messageUserToProto trims the *user.User association into the wire-only
// AdminSupportTicketUser shape (id/email/name/avatar). nil-safe.
func messageUserToProto(u *domainuser.User) *supportticketv1.AdminSupportTicketUser {
	if u == nil {
		return nil
	}
	return &supportticketv1.AdminSupportTicketUser{
		Id:        u.ID,
		Email:     u.Email,
		Name:      protoconv.StringPtr(u.Name),
		AvatarUrl: protoconv.StringPtr(u.AvatarURL),
	}
}

// messageUserFromProto — inverse of messageUserToProto. The four wire fields
// roundtrip; other user.User fields stay zero (not part of the wire shape).
func messageUserFromProto(p *supportticketv1.AdminSupportTicketUser) *domainuser.User {
	if p == nil {
		return nil
	}
	return &domainuser.User{
		ID:        p.Id,
		Email:     p.Email,
		Name:      protoconv.StringPtr(p.Name),
		AvatarURL: protoconv.StringPtr(p.AvatarUrl),
	}
}

// messageAttachmentsToProto bridges the value-slice domain shape to the
// pointer-slice wire shape (proto repeated message → []*T).
func messageAttachmentsToProto(in []supportticketdomain.SupportTicketAttachment) []*supportticketv1.AdminSupportTicketAttachment {
	out := make([]*supportticketv1.AdminSupportTicketAttachment, 0, len(in))
	for i := range in {
		out = append(out, ToProtoAdminSupportTicketAttachment(&in[i]))
	}
	return out
}

// messageAttachmentsFromProto — inverse of messageAttachmentsToProto.
func messageAttachmentsFromProto(in []*supportticketv1.AdminSupportTicketAttachment) []supportticketdomain.SupportTicketAttachment {
	out := make([]supportticketdomain.SupportTicketAttachment, 0, len(in))
	for _, p := range in {
		a := FromProtoAdminSupportTicketAttachment(p)
		if a != nil {
			out = append(out, *a)
		}
	}
	return out
}
