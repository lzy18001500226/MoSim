package billing

import (
	"testing"
	"time"
)

// ===========================================
// Test Features (plan.go)
// ===========================================

func TestFeaturesScanNil(t *testing.T) {
	var f Features
	err := f.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if f != nil {
		t.Error("expected nil Features")
	}
}

func TestFeaturesScanValid(t *testing.T) {
	var f Features
	err := f.Scan([]byte(`{"unlimited_seats":true,"max_runners":10}`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if f["unlimited_seats"] != true {
		t.Errorf("expected unlimited_seats true, got %v", f["unlimited_seats"])
	}
}

func TestFeaturesScanInvalidType(t *testing.T) {
	var f Features
	err := f.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestFeaturesScanInvalidJSON(t *testing.T) {
	var f Features
	err := f.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestFeaturesValueNil(t *testing.T) {
	var f Features
	val, err := f.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestFeaturesValueValid(t *testing.T) {
	f := Features{"feature_x": true}
	val, err := f.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}

// ===========================================
// Test SubscriptionPlan (plan.go)
// ===========================================

func TestSubscriptionPlanTableName(t *testing.T) {
	sp := SubscriptionPlan{}
	if sp.TableName() != "subscription_plans" {
		t.Errorf("expected 'subscription_plans', got %s", sp.TableName())
	}
}

func TestSubscriptionPlanGetPrice(t *testing.T) {
	sp := SubscriptionPlan{
		PricePerSeatMonthly: 19.99,
		PricePerSeatYearly:  199.90,
	}

	if price := sp.GetPrice(BillingCycleMonthly); price != 19.99 {
		t.Errorf("expected monthly price 19.99, got %f", price)
	}
	if price := sp.GetPrice(BillingCycleYearly); price != 199.90 {
		t.Errorf("expected yearly price 199.90, got %f", price)
	}
	// Default to monthly for unknown cycle
	if price := sp.GetPrice("unknown"); price != 19.99 {
		t.Errorf("expected default monthly price 19.99, got %f", price)
	}
}

func TestSubscriptionPlanStruct(t *testing.T) {
	now := time.Now()
	monthlyPriceID := "price_monthly_123"
	yearlyPriceID := "price_yearly_456"

	sp := SubscriptionPlan{
		ID:                   1,
		Name:                 PlanPro,
		DisplayName:          "Pro Plan",
		PricePerSeatMonthly:  19.99,
		PricePerSeatYearly:   199.90,
		IncludedPodMinutes:   1000,
		PricePerExtraMinute:  0.05,
		MaxUsers:             50,
		MaxRunners:           10,
		MaxConcurrentPods:    5,
		MaxRepositories:      100,
		Features:             Features{"priority_support": true},
		StripePriceIDMonthly: &monthlyPriceID,
		StripePriceIDYearly:  &yearlyPriceID,
		IsActive:             true,
		CreatedAt:            now,
	}

	if sp.ID != 1 {
		t.Errorf("expected ID 1, got %d", sp.ID)
	}
	if sp.Name != "pro" {
		t.Errorf("expected Name 'pro', got %s", sp.Name)
	}
	if sp.MaxConcurrentPods != 5 {
		t.Errorf("expected MaxConcurrentPods 5, got %d", sp.MaxConcurrentPods)
	}
	if *sp.StripePriceIDMonthly != "price_monthly_123" {
		t.Errorf("expected StripePriceIDMonthly, got %s", *sp.StripePriceIDMonthly)
	}
}
