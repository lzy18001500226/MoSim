package promocodeadminconnect

import (
	"strings"
	"time"

	"github.com/anthropics/agentsmesh/backend/internal/domain/promocode"
	adminservice "github.com/anthropics/agentsmesh/backend/internal/service/admin"
	promocodev1 "github.com/anthropics/agentsmesh/proto/gen/go/promocode/v1"
)

// toProtoRedemptionDetail enriches the codegen output with derived flat
// user/organization fields that come from eager-loaded associations. The
// domain struct has no flat *_email / *_username / *_name / *_slug fields,
// so codegen marks them field_skip and we populate them here.
func toProtoRedemptionDetail(d *adminservice.RedemptionWithDetails) *promocodev1.RedemptionDetail {
	out := ToProtoRedemptionDetail(d)
	if out == nil || d == nil {
		return out
	}
	if u := d.User; u != nil {
		email := u.Email
		out.UserEmail = &email
		username := u.Username
		out.UserUsername = &username
	}
	if o := d.Organization; o != nil {
		name := o.Name
		out.OrganizationName = &name
		slug := o.Slug
		out.OrganizationSlug = &slug
	}
	return out
}

// promoTypeToProto bridges the promocode.PromoCodeType string newtype to
// a plain string on the wire (proto string field can't carry the newtype).
func promoTypeToProto(t promocode.PromoCodeType) string { return string(t) }

func promoTypeFromProto(s string) promocode.PromoCodeType { return promocode.PromoCodeType(s) }

// parseTime parses an RFC3339 string, returning zero time + nil err for empty
// input so callers can opt into "use server-now" semantics by omitting the
// field.
func parseTime(s string) (time.Time, error) {
	if s == "" {
		return time.Time{}, nil
	}
	return time.Parse(time.RFC3339, s)
}

// normalizeCode mirrors REST's strings.ToUpper(req.Code) at promo_codes.go:131.
func normalizeCode(s string) string { return strings.ToUpper(s) }
