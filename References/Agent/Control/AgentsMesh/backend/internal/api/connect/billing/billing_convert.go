package billingconnect

import (
	billingdomain "github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	"github.com/anthropics/agentsmesh/backend/pkg/protoconv"
	billingv1 "github.com/anthropics/agentsmesh/proto/gen/go/billing/v1"
)

// toProtoPlan mirrors backend/internal/domain/billing/plan.go onto the wire.
// `features` and Stripe price IDs are intentionally NOT exposed — UI never
// reads them and proto field set was reconciled in PR for migration (proto §65).
func toProtoPlan(p *billingdomain.SubscriptionPlan) *billingv1.SubscriptionPlan {
	if p == nil {
		return nil
	}
	return &billingv1.SubscriptionPlan{
		Id:                  p.ID,
		Name:                p.Name,
		DisplayName:         p.DisplayName,
		PricePerSeatMonthly: p.PricePerSeatMonthly,
		PricePerSeatYearly:  p.PricePerSeatYearly,
		IncludedPodMinutes:  int32(p.IncludedPodMinutes),
		PricePerExtraMinute: p.PricePerExtraMinute,
		MaxUsers:            int32(p.MaxUsers),
		MaxRunners:          int32(p.MaxRunners),
		MaxConcurrentPods:   int32(p.MaxConcurrentPods),
		MaxRepositories:     int32(p.MaxRepositories),
		IsActive:            p.IsActive,
		CreatedAt:           protoconv.RFC3339(p.CreatedAt),
	}
}

// toProtoSubscription converts the GORM-backed Subscription to wire shape.
// Provider IDs (Stripe / LemonSqueezy) reach the UI so it can route the
// "Manage payment method" link to the correct portal.
func toProtoSubscription(s *billingdomain.Subscription) *billingv1.Subscription {
	if s == nil {
		return nil
	}
	out := &billingv1.Subscription{
		Id:                 s.ID,
		OrganizationId:     s.OrganizationID,
		PlanId:             s.PlanID,
		Status:             s.Status,
		BillingCycle:       s.BillingCycle,
		CurrentPeriodStart: protoconv.RFC3339(s.CurrentPeriodStart),
		CurrentPeriodEnd:   protoconv.RFC3339(s.CurrentPeriodEnd),
		AutoRenew:          s.AutoRenew,
		SeatCount:          int32(s.SeatCount),
		CancelAtPeriodEnd:  s.CancelAtPeriodEnd,
		CreatedAt:          protoconv.RFC3339(s.CreatedAt),
		UpdatedAt:          protoconv.RFC3339(s.UpdatedAt),
	}
	if s.Plan != nil {
		out.Plan = toProtoPlan(s.Plan)
	}
	out.PaymentProvider = copyStringPtr(s.PaymentProvider)
	out.PaymentMethod = copyStringPtr(s.PaymentMethod)
	out.StripeCustomerId = copyStringPtr(s.StripeCustomerID)
	out.StripeSubscriptionId = copyStringPtr(s.StripeSubscriptionID)
	out.LemonsqueezyCustomerId = copyStringPtr(s.LemonSqueezyCustomerID)
	out.LemonsqueezySubscriptionId = copyStringPtr(s.LemonSqueezySubscriptionID)
	out.DowngradeToPlan = copyStringPtr(s.DowngradeToPlan)
	out.NextBillingCycle = copyStringPtr(s.NextBillingCycle)
	if s.CanceledAt != nil {
		out.CanceledAt = protoconv.RFC3339Ptr(s.CanceledAt)
	}
	if s.FrozenAt != nil {
		out.FrozenAt = protoconv.RFC3339Ptr(s.FrozenAt)
	}
	return out
}

func toProtoOverview(o *billingsvc.BillingOverview) *billingv1.BillingOverview {
	if o == nil {
		return nil
	}
	out := &billingv1.BillingOverview{
		Plan:               toProtoPlan(o.Plan),
		Status:             o.Status,
		BillingCycle:       o.BillingCycle,
		CurrentPeriodStart: protoconv.RFC3339(o.CurrentPeriodStart),
		CurrentPeriodEnd:   protoconv.RFC3339(o.CurrentPeriodEnd),
		CancelAtPeriodEnd:  o.CancelAtPeriodEnd,
		Usage:              toProtoUsage(&o.Usage),
	}
	return out
}

func toProtoUsage(u *billingsvc.UsageOverview) *billingv1.UsageOverview {
	if u == nil {
		return nil
	}
	return &billingv1.UsageOverview{
		PodMinutes:         u.PodMinutes,
		IncludedPodMinutes: u.IncludedPodMinutes,
		Users:              int32(u.Users),
		MaxUsers:           int32(u.MaxUsers),
		Runners:            int32(u.Runners),
		MaxRunners:         int32(u.MaxRunners),
		ConcurrentPods:     int32(u.ConcurrentPods),
		MaxConcurrentPods:  int32(u.MaxConcurrentPods),
		Repositories:       int32(u.Repositories),
		MaxRepositories:    int32(u.MaxRepositories),
	}
}

func toProtoSeatUsage(u *billingsvc.SeatUsage) *billingv1.SeatUsage {
	if u == nil {
		return nil
	}
	return &billingv1.SeatUsage{
		TotalSeats:     int32(u.TotalSeats),
		UsedSeats:      int32(u.UsedSeats),
		AvailableSeats: int32(u.AvailableSeats),
		MaxSeats:       int32(u.MaxSeats),
		CanAddSeats:    u.CanAddSeats,
	}
}

func toProtoDeploymentInfo(d *billingsvc.DeploymentInfo) *billingv1.DeploymentInfo {
	if d == nil {
		return &billingv1.DeploymentInfo{}
	}
	return &billingv1.DeploymentInfo{
		DeploymentType:     d.DeploymentType,
		AvailableProviders: append([]string(nil), d.AvailableProviders...),
	}
}

func toProtoInvoice(i *billingdomain.Invoice) *billingv1.Invoice {
	if i == nil {
		return nil
	}
	out := &billingv1.Invoice{
		Id:             i.ID,
		OrganizationId: i.OrganizationID,
		PaymentOrderId: i.PaymentOrderID,
		InvoiceNo:      i.InvoiceNo,
		Status:         i.Status,
		Currency:       i.Currency,
		Subtotal:       i.Subtotal,
		TaxAmount:      i.TaxAmount,
		Total:          i.Total,
		PeriodStart:    protoconv.RFC3339(i.PeriodStart),
		PeriodEnd:      protoconv.RFC3339(i.PeriodEnd),
		PdfUrl:         copyStringPtr(i.PDFURL),
		CreatedAt:      protoconv.RFC3339(i.CreatedAt),
		UpdatedAt:      protoconv.RFC3339(i.UpdatedAt),
	}
	if i.IssuedAt != nil {
		out.IssuedAt = protoconv.RFC3339Ptr(i.IssuedAt)
	}
	if i.DueAt != nil {
		out.DueAt = protoconv.RFC3339Ptr(i.DueAt)
	}
	if i.PaidAt != nil {
		out.PaidAt = protoconv.RFC3339Ptr(i.PaidAt)
	}
	return out
}

func toProtoCheckoutStatus(o *billingdomain.PaymentOrder) *billingv1.CheckoutStatus {
	if o == nil {
		return nil
	}
	out := &billingv1.CheckoutStatus{
		OrderNo:   o.OrderNo,
		Status:    o.Status,
		OrderType: o.OrderType,
		Amount:    o.ActualAmount,
		Currency:  o.Currency,
		CreatedAt: protoconv.RFC3339(o.CreatedAt),
	}
	if o.PaidAt != nil {
		out.PaidAt = protoconv.RFC3339Ptr(o.PaidAt)
	}
	return out
}

func toProtoPublicPlanPricing(plan *billingdomain.SubscriptionPlan, price *billingdomain.PlanPrice) *billingv1.PublicPlanPricing {
	out := &billingv1.PublicPlanPricing{
		Name:              plan.Name,
		DisplayName:       plan.DisplayName,
		MaxUsers:          int32(plan.MaxUsers),
		MaxRunners:        int32(plan.MaxRunners),
		MaxRepositories:   int32(plan.MaxRepositories),
		MaxConcurrentPods: int32(plan.MaxConcurrentPods),
	}
	if price != nil {
		out.PriceMonthly = price.PriceMonthly
		out.PriceYearly = price.PriceYearly
	}
	return out
}

func copyStringPtr(p *string) *string {
	if p == nil {
		return nil
	}
	v := *p
	return &v
}
