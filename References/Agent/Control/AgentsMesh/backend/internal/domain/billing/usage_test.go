package billing

import (
	"testing"
	"time"
)

// ===========================================
// Test UsageMetadata (usage.go)
// ===========================================

func TestUsageMetadataScanNil(t *testing.T) {
	var um UsageMetadata
	err := um.Scan(nil)
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if um != nil {
		t.Error("expected nil UsageMetadata")
	}
}

func TestUsageMetadataScanValid(t *testing.T) {
	var um UsageMetadata
	err := um.Scan([]byte(`{"pod_id":"pod-123","user_id":50}`))
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if um["pod_id"] != "pod-123" {
		t.Errorf("expected pod_id 'pod-123', got %v", um["pod_id"])
	}
}

func TestUsageMetadataScanInvalidType(t *testing.T) {
	var um UsageMetadata
	err := um.Scan("not bytes")
	if err == nil {
		t.Error("expected error for invalid type")
	}
}

func TestUsageMetadataScanInvalidJSON(t *testing.T) {
	var um UsageMetadata
	err := um.Scan([]byte(`invalid json`))
	if err == nil {
		t.Error("expected error for invalid JSON")
	}
}

func TestUsageMetadataValueNil(t *testing.T) {
	var um UsageMetadata
	val, err := um.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val != nil {
		t.Error("expected nil value")
	}
}

func TestUsageMetadataValueValid(t *testing.T) {
	um := UsageMetadata{"pod_id": "pod-123"}
	val, err := um.Value()
	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}
	if val == nil {
		t.Error("expected non-nil value")
	}
}

// ===========================================
// Test UsageRecord (usage.go)
// ===========================================

func TestUsageRecordTableName(t *testing.T) {
	ur := UsageRecord{}
	if ur.TableName() != "usage_records" {
		t.Errorf("expected 'usage_records', got %s", ur.TableName())
	}
}

func TestUsageRecordStruct(t *testing.T) {
	now := time.Now()

	ur := UsageRecord{
		ID:             1,
		OrganizationID: 100,
		UsageType:      UsageTypePodMinutes,
		Quantity:       120.5,
		PeriodStart:    now,
		PeriodEnd:      now.Add(24 * time.Hour),
		Metadata:       UsageMetadata{"pod_id": "pod-123"},
		CreatedAt:      now,
	}

	if ur.ID != 1 {
		t.Errorf("expected ID 1, got %d", ur.ID)
	}
	if ur.OrganizationID != 100 {
		t.Errorf("expected OrganizationID 100, got %d", ur.OrganizationID)
	}
	if ur.UsageType != "pod_minutes" {
		t.Errorf("expected UsageType 'pod_minutes', got %s", ur.UsageType)
	}
	if ur.Quantity != 120.5 {
		t.Errorf("expected Quantity 120.5, got %f", ur.Quantity)
	}
}
