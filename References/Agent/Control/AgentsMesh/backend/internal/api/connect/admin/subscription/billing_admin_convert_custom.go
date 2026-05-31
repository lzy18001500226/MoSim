package subscriptionadminconnect

import (
	"encoding/json"

	"github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	billingservice "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

// toProtoAdminSubscription assembles the admin-facing composite response:
// codegen-generated entity + seat usage + provider flags + JSON-serialized
// custom_quotas. AdminSubscription itself is intentionally not annotated
// (composite of multiple domain types) — only the children are codegen'd.
func toProtoAdminSubscription(sub *billing.Subscription, seatUsage *billingservice.SeatUsage) *billingv1.AdminSubscription {
	if sub == nil {
		return nil
	}
	out := &billingv1.AdminSubscription{
		Subscription:    ToProtoAdminSubscriptionEntity(sub),
		HasStripe:       sub.StripeSubscriptionID != nil,
		HasAlipay:       sub.AlipayAgreementNo != nil,
		HasWechat:       sub.WeChatContractID != nil,
		HasLemonsqueezy: sub.LemonSqueezySubscriptionID != nil,
	}
	if seatUsage != nil {
		out.SeatUsage = ToProtoAdminSeatUsage(seatUsage)
	}
	if sub.CustomQuotas != nil {
		if data, err := json.Marshal(sub.CustomQuotas); err == nil {
			s := string(data)
			out.CustomQuotasJson = &s
		}
	}
	return out
}

// planToProto is the field_custom helper for AdminSubscriptionEntity.plan —
// codegen passes `d.Plan` (typed *billing.SubscriptionPlan) and expects a
// proto pointer back. Mirrors the wire-pointer round-trip.
func planToProto(p *billing.SubscriptionPlan) *billingv1.AdminSubscriptionPlan {
	return ToProtoAdminSubscriptionPlan(p)
}

// planFromProto is the inverse for FromProto.
func planFromProto(p *billingv1.AdminSubscriptionPlan) *billing.SubscriptionPlan {
	return FromProtoAdminSubscriptionPlan(p)
}
