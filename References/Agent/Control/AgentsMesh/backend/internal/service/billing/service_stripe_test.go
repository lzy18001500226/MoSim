package billing

import (
	"context"
	"testing"
)

// TestCreateStripeCustomer_NotEnabled tests CreateStripeCustomer when Stripe is not enabled
func TestCreateStripeCustomer_NotEnabled(t *testing.T) {
	svc, _ := setupTestService(t)

	// Stripe is not enabled by default in test setup
	customerID, err := svc.CreateStripeCustomer(context.Background(), 1, "test@example.com", "Test User")
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if customerID != "" {
		t.Errorf("expected empty customer ID when Stripe is not enabled, got %s", customerID)
	}
}

// TestListPlans_Error tests ListPlans error handling
func TestListPlans_Error(t *testing.T) {
	svc, db := setupTestService(t)

	// Drop the subscription_plans table to cause an error
	db.Exec("DROP TABLE subscription_plans")

	_, err := svc.ListPlans(context.Background())
	if err == nil {
		t.Error("expected error when table doesn't exist")
	}
}

// TestGetPlanPrices_Error tests GetPlanPrices error handling
func TestGetPlanPrices_Error(t *testing.T) {
	svc, db := setupTestService(t)

	// Drop the plan_prices table to cause an error
	db.Exec("DROP TABLE plan_prices")

	_, err := svc.GetPlanPrices(context.Background(), "pro")
	if err == nil {
		t.Error("expected error when table doesn't exist")
	}
}

// TestGetUsage_NoSubscription tests GetUsage when no subscription exists
func TestGetUsage_NoSubscription(t *testing.T) {
	svc, _ := setupTestService(t)

	// Try to get usage for organization without subscription
	// GetUsage requires subscription, should return error
	_, err := svc.GetUsage(context.Background(), 999, "pod_minutes")
	if err == nil {
		t.Error("expected error when no subscription exists")
	}
}

// TestGetUsageHistory_NotFound tests GetUsageHistory when no records exist
func TestGetUsageHistory_NotFound(t *testing.T) {
	svc, _ := setupTestService(t)

	// Try to get usage history for non-existent organization
	history, err := svc.GetUsageHistory(context.Background(), 999, "pod_minutes", 10)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if len(history) != 0 {
		t.Errorf("expected empty history for non-existent org, got %d records", len(history))
	}
}

// TestGetInvoicesByOrg_NotFound tests GetInvoicesByOrg when no invoices exist
func TestGetInvoicesByOrg_NotFound(t *testing.T) {
	svc, _ := setupTestService(t)

	// Try to get invoices for non-existent organization
	invoices, err := svc.GetInvoicesByOrg(context.Background(), 999, 10, 0)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if len(invoices) != 0 {
		t.Errorf("expected empty invoices for non-existent org, got %d", len(invoices))
	}
}

// TestGetPaymentOrderByExternalNo_NotFound tests GetPaymentOrderByExternalNo when not found
func TestGetPaymentOrderByExternalNo_NotFound(t *testing.T) {
	svc, _ := setupTestService(t)

	// Try to get order by non-existent external order number
	order, err := svc.GetPaymentOrderByExternalNo(context.Background(), "nonexistent")
	if err == nil {
		t.Error("expected error for non-existent external order no")
	}
	if order != nil {
		t.Error("expected nil order for non-existent external order no")
	}
}

// TestCheckQuota_NoSubscription_FallsBackToBasedPlan tests CheckQuota falls back to Based plan
func TestCheckQuota_NoSubscription_FallsBackToBasedPlan(t *testing.T) {
	svc, _ := setupTestService(t)

	// CheckQuota should fall back to Based plan when no subscription exists
	// Based plan has max_users = 1, so requesting 1 user should succeed
	err := svc.CheckQuota(context.Background(), 999, "users", 1)
	if err != nil {
		t.Errorf("expected no error when falling back to Based plan, got %v", err)
	}

	// But requesting more than max should fail
	err = svc.CheckQuota(context.Background(), 999, "users", 2)
	if err != ErrQuotaExceeded {
		t.Errorf("expected ErrQuotaExceeded, got %v", err)
	}
}

// TestGetSeatUsage_NoSubscription tests GetSeatUsage when no subscription exists
func TestGetSeatUsage_NoSubscription(t *testing.T) {
	svc, _ := setupTestService(t)

	// Try to get seat usage for organization without subscription
	usage, err := svc.GetSeatUsage(context.Background(), 999)
	if err == nil {
		t.Error("expected error when no subscription exists")
	}
	if usage != nil {
		t.Error("expected nil usage when no subscription exists")
	}
}
