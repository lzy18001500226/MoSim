package billing

import (
	"testing"

	"github.com/stripe/stripe-go/v76"
)

// ===========================================
// MockStripeClient Unit Tests
// ===========================================

// TestMockStripeClient_Reset tests the Reset functionality
func TestMockStripeClient_Reset(t *testing.T) {
	mockClient := NewMockStripeClient()

	// Make some calls
	mockClient.CreateCustomer(&stripe.CustomerParams{
		Email: stripe.String("test@example.com"),
	})
	mockClient.CancelSubscription("sub_123", nil)

	// Verify calls were recorded
	if len(mockClient.CreateCustomerCalls) == 0 {
		t.Error("expected CreateCustomer call to be recorded")
	}
	if len(mockClient.CancelSubscriptionCalls) == 0 {
		t.Error("expected CancelSubscription call to be recorded")
	}

	// Reset
	mockClient.Reset()

	// Verify everything is cleared
	if len(mockClient.CreateCustomerCalls) != 0 {
		t.Error("expected CreateCustomer calls to be cleared")
	}
	if len(mockClient.CancelSubscriptionCalls) != 0 {
		t.Error("expected CancelSubscription calls to be cleared")
	}
	if len(mockClient.customers) != 0 {
		t.Error("expected customers to be cleared")
	}
	if len(mockClient.subscriptions) != 0 {
		t.Error("expected subscriptions to be cleared")
	}
}

// TestMockStripeClient_AddSubscription tests adding a pre-existing subscription
func TestMockStripeClient_AddSubscription(t *testing.T) {
	mockClient := NewMockStripeClient()

	// Add a pre-existing subscription
	mockClient.AddSubscription(&stripe.Subscription{
		ID:     "sub_existing",
		Status: stripe.SubscriptionStatusActive,
	})

	// Verify it exists
	sub, ok := mockClient.GetSubscription("sub_existing")
	if !ok {
		t.Error("expected subscription to exist")
	}
	if sub.Status != stripe.SubscriptionStatusActive {
		t.Errorf("expected active status, got %s", sub.Status)
	}

	// Cancel it
	result, err := mockClient.CancelSubscription("sub_existing", nil)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result.Status != stripe.SubscriptionStatusCanceled {
		t.Errorf("expected canceled status, got %s", result.Status)
	}
}
