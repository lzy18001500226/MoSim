package billing

import (
	"testing"
	"time"
)

// ===========================================
// Test OrderMetadata (order.go)
// ===========================================

func TestOrderMetadataScanNil(t *testing.T) {
	var om OrderMetadata
	err := om.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if om != nil {
		t.Error("expected nil OrderMetadata")
	}
}

func TestOrderMetadataScanValid(t *testing.T) {
	var om OrderMetadata
	err := om.Scan([]byte(`{"plan_name":"pro","seats":5}`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if om["plan_name"] != "pro" {
		t.Errorf("expected plan_name 'pro', got %v", om["plan_name"])
	}
}

func TestOrderMetadataScanInvalidType(t *testing.T) {
	var om OrderMetadata
	err := om.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestOrderMetadataScanInvalidJSON(t *testing.T) {
	var om OrderMetadata
	err := om.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestOrderMetadataValueNil(t *testing.T) {
	var om OrderMetadata
	val, err := om.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestOrderMetadataValueValid(t *testing.T) {
	om := OrderMetadata{"plan_name": "pro"}
	val, err := om.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}

// ===========================================
// Test PaymentOrder (order.go)
// ===========================================

func TestPaymentOrderTableName(t *testing.T) {
	po := PaymentOrder{}
	if po.TableName() != "payment_orders" {
		t.Errorf("expected 'payment_orders', got %s", po.TableName())
	}
}

func TestPaymentOrderIsPending(t *testing.T) {
	tests := []struct {
		name     string
		status   string
		expected bool
	}{
		{"pending", OrderStatusPending, true},
		{"succeeded", OrderStatusSucceeded, false},
		{"failed", OrderStatusFailed, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po := PaymentOrder{Status: tt.status}
			if got := po.IsPending(); got != tt.expected {
				t.Errorf("IsPending() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestPaymentOrderIsSucceeded(t *testing.T) {
	tests := []struct {
		name     string
		status   string
		expected bool
	}{
		{"succeeded", OrderStatusSucceeded, true},
		{"pending", OrderStatusPending, false},
		{"failed", OrderStatusFailed, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po := PaymentOrder{Status: tt.status}
			if got := po.IsSucceeded(); got != tt.expected {
				t.Errorf("IsSucceeded() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestPaymentOrderIsExpired(t *testing.T) {
	past := time.Now().Add(-1 * time.Hour)
	future := time.Now().Add(1 * time.Hour)

	tests := []struct {
		name      string
		expiresAt *time.Time
		expected  bool
	}{
		{"no expiry", nil, false},
		{"expired", &past, true},
		{"not expired", &future, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			po := PaymentOrder{ExpiresAt: tt.expiresAt}
			if got := po.IsExpired(); got != tt.expected {
				t.Errorf("IsExpired() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestPaymentOrderStruct(t *testing.T) {
	now := time.Now()
	externalOrderNo := "ext_123"
	planID := int64(2)
	paymentMethod := PaymentMethodCard
	idempotencyKey := "idem_456"

	po := PaymentOrder{
		ID:              1,
		OrganizationID:  100,
		OrderNo:         "ORD-20240101-001",
		ExternalOrderNo: &externalOrderNo,
		OrderType:       OrderTypeSubscription,
		PlanID:          &planID,
		BillingCycle:    BillingCycleMonthly,
		Seats:           5,
		Currency:        "USD",
		Amount:          99.95,
		DiscountAmount:  10.00,
		ActualAmount:    89.95,
		PaymentProvider: PaymentProviderStripe,
		PaymentMethod:   &paymentMethod,
		Status:          OrderStatusPending,
		Metadata:        OrderMetadata{"source": "web"},
		IdempotencyKey:  &idempotencyKey,
		CreatedAt:       now,
		UpdatedAt:       now,
		CreatedByID:     1,
	}

	if po.OrderNo != "ORD-20240101-001" {
		t.Errorf("expected OrderNo, got %s", po.OrderNo)
	}
	if po.ActualAmount != 89.95 {
		t.Errorf("expected ActualAmount 89.95, got %f", po.ActualAmount)
	}
}
