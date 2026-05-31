package billing

import (
	"testing"
	"time"
)

// ===========================================
// Test License (license.go)
// ===========================================

func TestLicenseTableName(t *testing.T) {
	lic := License{}
	if lic.TableName() != "licenses" {
		t.Errorf("expected 'licenses', got %s", lic.TableName())
	}
}

func TestLicenseIsValid(t *testing.T) {
	past := time.Now().Add(-24 * time.Hour)
	future := time.Now().Add(24 * time.Hour)

	tests := []struct {
		name     string
		license  License
		expected bool
	}{
		{
			name:     "active valid license",
			license:  License{IsActive: true},
			expected: true,
		},
		{
			name:     "inactive license",
			license:  License{IsActive: false},
			expected: false,
		},
		{
			name:     "revoked license",
			license:  License{IsActive: true, RevokedAt: &past},
			expected: false,
		},
		{
			name:     "expired license",
			license:  License{IsActive: true, ExpiresAt: &past},
			expected: false,
		},
		{
			name:     "not expired license",
			license:  License{IsActive: true, ExpiresAt: &future},
			expected: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.license.IsValid(); got != tt.expected {
				t.Errorf("IsValid() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestLicenseIsActivated(t *testing.T) {
	now := time.Now()
	orgID := int64(100)

	tests := []struct {
		name     string
		license  License
		expected bool
	}{
		{
			name:     "not activated",
			license:  License{},
			expected: false,
		},
		{
			name:     "only activated_at set",
			license:  License{ActivatedAt: &now},
			expected: false,
		},
		{
			name:     "only org_id set",
			license:  License{ActivatedOrgID: &orgID},
			expected: false,
		},
		{
			name:     "fully activated",
			license:  License{ActivatedAt: &now, ActivatedOrgID: &orgID},
			expected: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.license.IsActivated(); got != tt.expected {
				t.Errorf("IsActivated() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func TestLicenseDaysUntilExpiry(t *testing.T) {
	tests := []struct {
		name     string
		license  License
		expected int
	}{
		{
			name:     "no expiry",
			license:  License{},
			expected: -1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.license.DaysUntilExpiry(); got != tt.expected {
				t.Errorf("DaysUntilExpiry() = %v, want %v", got, tt.expected)
			}
		})
	}

	// Test with future expiry (approximately)
	future := time.Now().Add(10 * 24 * time.Hour)
	lic := License{ExpiresAt: &future}
	days := lic.DaysUntilExpiry()
	if days < 9 || days > 11 {
		t.Errorf("DaysUntilExpiry() = %d, want approximately 10", days)
	}
}

func TestLicenseStruct(t *testing.T) {
	now := time.Now()
	future := now.Add(365 * 24 * time.Hour)
	fingerprint := "abc123"

	lic := License{
		ID:                   1,
		LicenseKey:           "AM-ENT-2024-XXXXX",
		OrganizationName:     "Acme Corp",
		ContactEmail:         "admin@acme.com",
		PlanName:             PlanEnterprise,
		MaxUsers:             -1,
		MaxRunners:           -1,
		MaxRepositories:      -1,
		MaxConcurrentPods:    -1,
		Features:             Features{"unlimited": true},
		IssuedAt:             now,
		ExpiresAt:            &future,
		Signature:            "BASE64SIGNATURE",
		PublicKeyFingerprint: &fingerprint,
		IsActive:             true,
		CreatedAt:            now,
		UpdatedAt:            now,
	}

	if lic.LicenseKey != "AM-ENT-2024-XXXXX" {
		t.Errorf("expected LicenseKey, got %s", lic.LicenseKey)
	}
	if lic.MaxUsers != -1 {
		t.Errorf("expected MaxUsers -1, got %d", lic.MaxUsers)
	}
}

func TestLicenseStatusStruct(t *testing.T) {
	future := time.Now().Add(365 * 24 * time.Hour)

	ls := LicenseStatus{
		IsActive:         true,
		LicenseKey:       "AM-ENT-2024-XXXXX",
		OrganizationName: "Acme Corp",
		Plan:             PlanEnterprise,
		ExpiresAt:        &future,
		MaxUsers:         -1,
		MaxRunners:       -1,
		MaxRepositories:  -1,
		MaxPodMinutes:    -1,
		Features:         []string{"unlimited_pods", "priority_support"},
		Message:          "License is valid",
	}

	if !ls.IsActive {
		t.Error("expected IsActive true")
	}
	if len(ls.Features) != 2 {
		t.Errorf("expected 2 features, got %d", len(ls.Features))
	}
}
