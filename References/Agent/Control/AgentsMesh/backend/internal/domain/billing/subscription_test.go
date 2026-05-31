package billing

import (
	"testing"
	"time"
)

// ===========================================
// Test CustomQuotas (subscription.go)
// ===========================================

func TestCustomQuotasScanNil(t *testing.T) {
	var cq CustomQuotas
	err := cq.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if cq != nil {
		t.Error("expected nil CustomQuotas")
	}
}

func TestCustomQuotasScanValid(t *testing.T) {
	var cq CustomQuotas
	err := cq.Scan([]byte(`{"max_runners":20,"extra_minutes":5000}`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if cq["max_runners"] != float64(20) {
		t.Errorf("expected max_runners 20, got %v", cq["max_runners"])
	}
}

func TestCustomQuotasScanInvalidType(t *testing.T) {
	var cq CustomQuotas
	err := cq.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestCustomQuotasScanInvalidJSON(t *testing.T) {
	var cq CustomQuotas
	err := cq.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestCustomQuotasValueNil(t *testing.T) {
	var cq CustomQuotas
	val, err := cq.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestCustomQuotasValueValid(t *testing.T) {
	cq := CustomQuotas{"max_runners": 20}
	val, err := cq.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}

// ===========================================
// Test Subscription (subscription.go)
// ===========================================

func TestSubscriptionTableName(t *testing.T) {
	s := Subscription{}
	if s.TableName() != "subscriptions" {
		t.Errorf("expected 'subscriptions', got %s", s.TableName())
	}
}

func TestSubscriptionIsFrozen(t *testing.T) {
	now := time.Now()
	tests := []struct {
		name     string
		sub      Subscription
		expected bool
	}{
		{
			name:     "active subscription",
			sub:      Subscription{Status: SubscriptionStatusActive},
			expected: false,
		},
		{
			name:     "frozen status",
			sub:      Subscription{Status: SubscriptionStatusFrozen},
			expected: true,
		},
		{
			name:     "frozen_at set",
			sub:      Subscription{Status: SubscriptionStatusActive, FrozenAt: &now},
			expected: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.sub.IsFrozen(); got != tt.expected {
				t.Errorf("IsFrozen() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestSubscriptionIsActive(t *testing.T) {
	now := time.Now()
	tests := []struct {
		name     string
		sub      Subscription
		expected bool
	}{
		{
			name:     "active subscription",
			sub:      Subscription{Status: SubscriptionStatusActive},
			expected: true,
		},
		{
			name:     "canceled subscription",
			sub:      Subscription{Status: SubscriptionStatusCanceled},
			expected: false,
		},
		{
			name:     "active but frozen",
			sub:      Subscription{Status: SubscriptionStatusActive, FrozenAt: &now},
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.sub.IsActive(); got != tt.expected {
				t.Errorf("IsActive() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestSubscriptionCanAddSeats(t *testing.T) {
	basedPlan := &SubscriptionPlan{Name: PlanBased}
	proPlan := &SubscriptionPlan{Name: PlanPro}

	tests := []struct {
		name     string
		sub      Subscription
		plan     *SubscriptionPlan
		expected bool
	}{
		{
			name:     "based plan cannot add seats",
			sub:      Subscription{Plan: basedPlan},
			plan:     nil,
			expected: false,
		},
		{
			name:     "pro plan can add seats",
			sub:      Subscription{Plan: proPlan},
			plan:     nil,
			expected: true,
		},
		{
			name:     "explicit plan overrides subscription plan",
			sub:      Subscription{Plan: basedPlan},
			plan:     proPlan,
			expected: true,
		},
		{
			name:     "nil plan",
			sub:      Subscription{},
			plan:     nil,
			expected: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.sub.CanAddSeats(tt.plan); got != tt.expected {
				t.Errorf("CanAddSeats() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestSubscriptionGetAvailableSeats(t *testing.T) {
	sub := Subscription{SeatCount: 10}

	tests := []struct {
		name      string
		usedSeats int
		expected  int
	}{
		{"no seats used", 0, 10},
		{"half used", 5, 5},
		{"all used", 10, 0},
		{"over used", 12, -2},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := sub.GetAvailableSeats(tt.usedSeats); got != tt.expected {
				t.Errorf("GetAvailableSeats(%d) = %d, want %d", tt.usedSeats, got, tt.expected)
			}
		})
	}
}

func TestSubscriptionStruct(t *testing.T) {
	now := time.Now()
	stripeCustomerID := "cus_123"
	stripeSubID := "sub_456"
	paymentProvider := PaymentProviderStripe
	paymentMethod := PaymentMethodCard

	s := Subscription{
		ID:                   1,
		OrganizationID:       100,
		PlanID:               2,
		Status:               SubscriptionStatusActive,
		BillingCycle:         BillingCycleMonthly,
		CurrentPeriodStart:   now,
		CurrentPeriodEnd:     now.Add(30 * 24 * time.Hour),
		PaymentProvider:      &paymentProvider,
		PaymentMethod:        &paymentMethod,
		AutoRenew:            true,
		SeatCount:            5,
		StripeCustomerID:     &stripeCustomerID,
		StripeSubscriptionID: &stripeSubID,
		CustomQuotas:         CustomQuotas{"extra_minutes": 1000},
		CreatedAt:            now,
		UpdatedAt:            now,
	}

	if s.ID != 1 {
		t.Errorf("expected ID 1, got %d", s.ID)
	}
	if s.SeatCount != 5 {
		t.Errorf("expected SeatCount 5, got %d", s.SeatCount)
	}
	if !s.AutoRenew {
		t.Error("expected AutoRenew true")
	}
}
