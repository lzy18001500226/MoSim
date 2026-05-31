package billing

import (
	"testing"
	"time"
)

// ===========================================
// Test BillingAddress (invoice.go)
// ===========================================

func TestBillingAddressScanNil(t *testing.T) {
	var ba BillingAddress
	err := ba.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if ba != nil {
		t.Error("expected nil BillingAddress")
	}
}

func TestBillingAddressScanValid(t *testing.T) {
	var ba BillingAddress
	err := ba.Scan([]byte(`{"line1":"123 Main St","city":"NYC"}`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if ba["city"] != "NYC" {
		t.Errorf("expected city 'NYC', got %v", ba["city"])
	}
}

func TestBillingAddressScanInvalidType(t *testing.T) {
	var ba BillingAddress
	err := ba.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestBillingAddressScanInvalidJSON(t *testing.T) {
	var ba BillingAddress
	err := ba.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestBillingAddressValueNil(t *testing.T) {
	var ba BillingAddress
	val, err := ba.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestBillingAddressValueValid(t *testing.T) {
	ba := BillingAddress{"line1": "123 Main St"}
	val, err := ba.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}

// ===========================================
// Test LineItems (invoice.go)
// ===========================================

func TestLineItemsScanNil(t *testing.T) {
	var li LineItems
	err := li.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if li != nil {
		t.Error("expected nil LineItems")
	}
}

func TestLineItemsScanValid(t *testing.T) {
	var li LineItems
	err := li.Scan([]byte(`[{"description":"Pro Plan","quantity":1,"unit_price":19.99,"amount":19.99}]`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if len(li) != 1 {
		t.Errorf("expected 1 line item, got %d", len(li))
	}
	if li[0].Description != "Pro Plan" {
		t.Errorf("expected description 'Pro Plan', got %s", li[0].Description)
	}
}

func TestLineItemsScanInvalidType(t *testing.T) {
	var li LineItems
	err := li.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestLineItemsScanInvalidJSON(t *testing.T) {
	var li LineItems
	err := li.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestLineItemsValueNil(t *testing.T) {
	var li LineItems
	val, err := li.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestLineItemsValueValid(t *testing.T) {
	li := LineItems{{Description: "Pro Plan", Quantity: 1, UnitPrice: 19.99, Amount: 19.99}}
	val, err := li.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}

func TestLineItemStruct(t *testing.T) {
	li := LineItem{
		Description: "Pro Plan Subscription",
		Quantity:    5,
		UnitPrice:   19.99,
		Amount:      99.95,
	}

	if li.Description != "Pro Plan Subscription" {
		t.Errorf("expected Description, got %s", li.Description)
	}
	if li.Quantity != 5 {
		t.Errorf("expected Quantity 5, got %d", li.Quantity)
	}
}

// ===========================================
// Test Invoice (invoice.go)
// ===========================================

func TestInvoiceTableName(t *testing.T) {
	inv := Invoice{}
	if inv.TableName() != "invoices" {
		t.Errorf("expected 'invoices', got %s", inv.TableName())
	}
}

func TestInvoiceIsPaid(t *testing.T) {
	tests := []struct {
		name     string
		status   string
		expected bool
	}{
		{"paid", InvoiceStatusPaid, true},
		{"draft", InvoiceStatusDraft, false},
		{"issued", InvoiceStatusIssued, false},
		{"void", InvoiceStatusVoid, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			inv := Invoice{Status: tt.status}
			if got := inv.IsPaid(); got != tt.expected {
				t.Errorf("IsPaid() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestInvoiceStruct(t *testing.T) {
	now := time.Now()
	orderID := int64(10)
	billingName := "Acme Corp"
	billingEmail := "billing@acme.com"
	pdfURL := "https://example.com/invoice.pdf"

	inv := Invoice{
		ID:             1,
		OrganizationID: 100,
		PaymentOrderID: &orderID,
		InvoiceNo:      "INV-2024-001",
		Status:         InvoiceStatusIssued,
		Currency:       "USD",
		Subtotal:       99.95,
		TaxAmount:      8.00,
		Total:          107.95,
		BillingName:    &billingName,
		BillingEmail:   &billingEmail,
		BillingAddress: BillingAddress{"city": "NYC"},
		PeriodStart:    now,
		PeriodEnd:      now.Add(30 * 24 * time.Hour),
		LineItems:      LineItems{{Description: "Pro Plan", Amount: 99.95}},
		PDFURL:         &pdfURL,
		IssuedAt:       &now,
		CreatedAt:      now,
		UpdatedAt:      now,
	}

	if inv.InvoiceNo != "INV-2024-001" {
		t.Errorf("expected InvoiceNo, got %s", inv.InvoiceNo)
	}
	if inv.Total != 107.95 {
		t.Errorf("expected Total 107.95, got %f", inv.Total)
	}
}
