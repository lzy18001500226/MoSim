package supportticketconnect

import (
	supportticketdomain "github.com/anthropics/agentsmesh/backend/internal/domain/supportticket"
	domainuser "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	supportticketv1 "github.com/anthropics/agentsmesh/proto/gen/go/support_ticket/v1"
)

// messageUserToProto trims the *user.User association into the wire-only
// SupportTicketUser shape (id/email/name/avatar). nil-safe.
func messageUserToProto(u *domainuser.User) *supportticketv1.SupportTicketUser {
	if u == nil {
		return nil
	}
	return &supportticketv1.SupportTicketUser{
		Id:        u.ID,
		Email:     u.Email,
		Name:      protoconv.StringPtr(u.Name),
		AvatarUrl: protoconv.StringPtr(u.AvatarURL),
	}
}

// messageUserFromProto — inverse of messageUserToProto.
func messageUserFromProto(p *supportticketv1.SupportTicketUser) *domainuser.User {
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
func messageAttachmentsToProto(in []supportticketdomain.SupportTicketAttachment) []*supportticketv1.SupportTicketAttachment {
	out := make([]*supportticketv1.SupportTicketAttachment, 0, len(in))
	for i := range in {
		out = append(out, ToProtoSupportTicketAttachment(&in[i]))
	}
	return out
}

// messageAttachmentsFromProto — inverse of messageAttachmentsToProto.
func messageAttachmentsFromProto(in []*supportticketv1.SupportTicketAttachment) []supportticketdomain.SupportTicketAttachment {
	out := make([]supportticketdomain.SupportTicketAttachment, 0, len(in))
	for _, p := range in {
		a := FromProtoSupportTicketAttachment(p)
		if a != nil {
			out = append(out, *a)
		}
	}
	return out
}

// normalizeListArgs picks defaults that match the REST handler's
// `normalizePagination(page=1, page_size=20)` — server-side default
// PageSize is 20 with a 100-row ceiling. Connect's `{offset, limit}`
// envelope (conventions §8) translates: offset=0 means page 1.
func normalizeListArgs(offset, limit int32) (int32, int32) {
	if limit < 1 || limit > 100 {
		limit = 20
	}
	if offset < 0 {
		offset = 0
	}
	return offset, limit
}
