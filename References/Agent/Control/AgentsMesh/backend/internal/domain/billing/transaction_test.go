package billing

import (
	"testing"
	"time"
)

// ===========================================
// Test RawPayload (transaction.go)
// ===========================================

func TestRawPayloadScanNil(t *testing.T) {
	var rp RawPayload
	err := rp.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if rp != nil {
		t.Error("expected nil RawPayload")
	}
}

func TestRawPayloadScanValid(t *testing.T) {
	var rp RawPayload
	err := rp.Scan([]byte(`{"event_id":"evt_123","type":"payment"}`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if rp["event_id"] != "evt_123" {
		t.Errorf("expected event_id 'evt_123', got %v", rp["event_id"])
	}
}

func TestRawPayloadScanInvalidType(t *testing.T) {
	var rp RawPayload
	err := rp.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestRawPayloadScanInvalidJSON(t *testing.T) {
	var rp RawPayload
	err := rp.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestRawPayloadValueNil(t *testing.T) {
	var rp RawPayload
	val, err := rp.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestRawPayloadValueValid(t *testing.T) {
	rp := RawPayload{"event_id": "evt_123"}
	val, err := rp.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}

// ===========================================
// Test PaymentTransaction (transaction.go)
// ===========================================

func TestPaymentTransactionTableName(t *testing.T) {
	pt := PaymentTransaction{}
	if pt.TableName() != "payment_transactions" {
		t.Errorf("expected 'payment_transactions', got %s", pt.TableName())
	}
}

func TestPaymentTransactionStruct(t *testing.T) {
	now := time.Now()
	extTxnID := "txn_123"
	webhookEventID := "evt_456"
	webhookEventType := "payment_intent.succeeded"

	pt := PaymentTransaction{
		ID:                    1,
		PaymentOrderID:        10,
		TransactionType:       TransactionTypePayment,
		ExternalTransactionID: &extTxnID,
		Amount:                99.95,
		Currency:              "USD",
		Status:                TransactionStatusSucceeded,
		WebhookEventID:        &webhookEventID,
		WebhookEventType:      &webhookEventType,
		RawPayload:            RawPayload{"data": "value"},
		CreatedAt:             now,
	}

	if pt.ID != 1 {
		t.Errorf("expected ID 1, got %d", pt.ID)
	}
	if pt.TransactionType != "payment" {
		t.Errorf("expected TransactionType 'payment', got %s", pt.TransactionType)
	}
}
