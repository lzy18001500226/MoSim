package promocodeconnect

import (
	promocodedomain "github.com/anthropics/agentsmesh/backend/internal/domain/promocode"
	promocodesvc "github.com/anthropics/agentsmesh/backend/internal/service/promocode"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	promocodev1 "github.com/anthropics/agentsmesh/proto/gen/go/promocode/v1"
)

// toProtoValidateResponse maps the service-layer ValidateResponse to wire.
// REST returns ValidateResponse JSON directly; Connect ships the same fields
// in proto shape. Empty plan_name etc. collapse to absent (proto3 optional)
// so the wire footprint matches the REST `omitempty` behavior.
func toProtoValidateResponse(r *promocodesvc.ValidateResponse) *promocodev1.ValidatePromoCodeResponse {
	out := &promocodev1.ValidatePromoCodeResponse{
		Valid: r.Valid,
		Code:  r.Code,
	}
	if r.PlanName != "" {
		v := r.PlanName
		out.PlanName = &v
	}
	if r.PlanDisplayName != "" {
		v := r.PlanDisplayName
		out.PlanDisplayName = &v
	}
	if r.DurationMonths != 0 {
		v := int32(r.DurationMonths)
		out.DurationMonths = &v
	}
	if r.ExpiresAt != nil {
		out.ExpiresAt = protoconv.RFC3339Ptr(r.ExpiresAt)
	}
	if r.MessageCode != "" {
		v := r.MessageCode
		out.MessageCode = &v
	}
	return out
}

// toProtoRedeemResponse maps the service-layer RedeemResponse to wire.
// The REST handler's 400 + apierr.RespondWithExtra trick collapses to a
// typed `success=false` here — connect.Code* is reserved for genuine
// errors (DB / billing / etc.); validation/business misses ride
// `success=false` + `message_code`.
func toProtoRedeemResponse(r *promocodesvc.RedeemResponse) *promocodev1.RedeemPromoCodeResponse {
	out := &promocodev1.RedeemPromoCodeResponse{
		Success: r.Success,
	}
	if r.PlanName != "" {
		v := r.PlanName
		out.PlanName = &v
	}
	if r.DurationMonths != 0 {
		v := int32(r.DurationMonths)
		out.DurationMonths = &v
	}
	if !r.NewPeriodEnd.IsZero() {
		v := protoconv.RFC3339(r.NewPeriodEnd)
		out.NewPeriodEnd = &v
	}
	if r.MessageCode != "" {
		v := r.MessageCode
		out.MessageCode = &v
	}
	return out
}

// toProtoRedemption maps a domain Redemption to wire. PromoCode association
// is intentionally absent — REST ships an empty struct (GORM lazy load), so
// callers never read it. Proto schema omits the field entirely.
func toProtoRedemption(r *promocodedomain.Redemption) *promocodev1.Redemption {
	if r == nil {
		return nil
	}
	out := &promocodev1.Redemption{
		Id:             r.ID,
		PromoCodeId:    r.PromoCodeID,
		OrganizationId: r.OrganizationID,
		UserId:         r.UserID,
		PlanName:       r.PlanName,
		DurationMonths: int32(r.DurationMonths),
		NewPeriodEnd:   protoconv.RFC3339(r.NewPeriodEnd),
		CreatedAt:      protoconv.RFC3339(r.CreatedAt),
	}
	if r.PreviousPlanName != nil {
		v := *r.PreviousPlanName
		out.PreviousPlanName = &v
	}
	if r.PreviousPeriodEnd != nil {
		out.PreviousPeriodEnd = protoconv.RFC3339Ptr(r.PreviousPeriodEnd)
	}
	if r.IPAddress != nil {
		v := *r.IPAddress
		out.IpAddress = &v
	}
	if r.UserAgent != nil {
		v := *r.UserAgent
		out.UserAgent = &v
	}
	return out
}
