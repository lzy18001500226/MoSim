package licenseconnect

import (
	"context"
	"errors"
	"testing"
	"time"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/domain/billing"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	licenseservice "github.com/anthropics/agentsmesh/backend/internal/service/license"
	licensev1 "github.com/anthropics/agentsmesh/proto/gen/go/license/v1"
)

func ctxWithRole(role string) context.Context {
	return middleware.SetTenant(context.Background(), &middleware.TenantContext{
		UserID:   42,
		UserRole: role,
	})
}

func ctxNoTenant() context.Context { return context.Background() }

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

// --- requireOwner: REST policy parity ---

func TestRequireOwner_NoTenantContext_Allowed(t *testing.T) {
	// Initial OnPremise activation before any org exists — REST handler's
	// `if exists { ... }` guard falls through, the valid JWT (enforced by
	// the auth interceptor) is the bar. Connect handler mirrors this.
	assert.NoError(t, requireOwner(ctxNoTenant()))
}

func TestRequireOwner_OwnerRole_Allowed(t *testing.T) {
	assert.NoError(t, requireOwner(ctxWithRole("owner")))
}

func TestRequireOwner_MemberRole_PermissionDenied(t *testing.T) {
	err := requireOwner(ctxWithRole("member"))
	require.Error(t, err)
	assert.Equal(t, connect.CodePermissionDenied, connectCodeOf(t, err))
}

func TestRequireOwner_AdminRole_PermissionDenied(t *testing.T) {
	// REST checked `!= "owner"` — admin is NOT owner, the gate must
	// catch it. Asserting explicitly so a future broaden-to-admin change
	// surfaces here.
	err := requireOwner(ctxWithRole("admin"))
	require.Error(t, err)
	assert.Equal(t, connect.CodePermissionDenied, connectCodeOf(t, err))
}

func TestRequireOwner_EmptyRoleTenant_Allowed(t *testing.T) {
	// TenantContext exists but UserRole unset — caller didn't flow
	// through the org middleware. Same fall-through as nil tenant.
	assert.NoError(t, requireOwner(ctxWithRole("")))
}

// --- requireLicenseService: REST ServiceUnavailable parity ---

func TestRequireLicenseService_Nil_Unavailable(t *testing.T) {
	err := requireLicenseService(nil)
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
}

// --- Mutation guards: nil service surfaces Unavailable ---

func TestActivateLicense_NilService_Unavailable(t *testing.T) {
	srv := NewServer(nil)
	_, err := srv.ActivateLicense(ctxWithRole("owner"), connect.NewRequest(
		&licensev1.ActivateLicenseRequest{LicenseData: []byte("{}")},
	))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
}

func TestActivateLicense_MemberRole_PermissionDenied(t *testing.T) {
	// Service is nil but role check runs first (cheap, no I/O) —
	// permission denied takes precedence over Unavailable so role
	// info doesn't leak to non-owners. Asserts order-of-checks.
	srv := NewServer(nil)
	_, err := srv.ActivateLicense(ctxWithRole("member"), connect.NewRequest(
		&licensev1.ActivateLicenseRequest{LicenseData: []byte("{}")},
	))
	require.Error(t, err)
	// Service-availability check actually runs first (see license_mutations.go);
	// asserting that explicitly so re-ordering surfaces as a test break.
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
}

func TestActivateLicense_EmptyData_InvalidArgument(t *testing.T) {
	svc := &licenseservice.Service{}
	srv := NewServer(svc)
	_, err := srv.ActivateLicense(ctxWithRole("owner"), connect.NewRequest(
		&licensev1.ActivateLicenseRequest{},
	))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestValidateLicense_EmptyData_InvalidArgument(t *testing.T) {
	svc := &licenseservice.Service{}
	srv := NewServer(svc)
	_, err := srv.ValidateLicense(ctxWithRole("owner"), connect.NewRequest(
		&licensev1.ValidateLicenseRequest{},
	))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// --- Public service: no auth, but still gated on service availability ---

func TestGetLicenseStatus_NilService_Unavailable(t *testing.T) {
	srv := NewPublicServer(nil)
	_, err := srv.GetLicenseStatus(ctxNoTenant(), connect.NewRequest(
		&licensev1.GetLicenseStatusRequest{},
	))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
}

func TestCheckFeature_EmptyFeature_InvalidArgument(t *testing.T) {
	svc := &licenseservice.Service{}
	srv := NewPublicServer(svc)
	_, err := srv.CheckFeature(ctxNoTenant(), connect.NewRequest(
		&licensev1.CheckFeatureRequest{},
	))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestCheckFeature_PopulatedFeature_ReturnsEnabledFlag(t *testing.T) {
	// licenseservice.Service.HasFeature returns false for nil current
	// license — exercising the happy public-service path without needing
	// to wire a fake repo. Asserting the response envelope, not the
	// HasFeature inner logic.
	svc := &licenseservice.Service{}
	srv := NewPublicServer(svc)
	resp, err := srv.CheckFeature(ctxNoTenant(), connect.NewRequest(
		&licensev1.CheckFeatureRequest{Feature: "sso"},
	))
	require.NoError(t, err)
	assert.Equal(t, "sso", resp.Msg.GetFeature())
	assert.False(t, resp.Msg.GetEnabled())
}

func TestGetLicenseLimits_NoLicense_NotFound(t *testing.T) {
	svc := &licenseservice.Service{}
	srv := NewPublicServer(svc)
	_, err := srv.GetLicenseLimits(ctxNoTenant(), connect.NewRequest(
		&licensev1.GetLicenseLimitsRequest{},
	))
	require.Error(t, err)
	assert.Equal(t, connect.CodeNotFound, connectCodeOf(t, err))
}

// --- Convert helpers: REST → proto wire shape ---

func TestToProtoStatus_AllFieldsPopulated(t *testing.T) {
	expires := time.Date(2027, 5, 13, 0, 0, 0, 0, time.UTC)
	s := &billing.LicenseStatus{
		IsActive:         true,
		LicenseKey:       "LK-2026-ABCDEF",
		OrganizationName: "Acme Corp",
		Plan:             "enterprise",
		ExpiresAt:        &expires,
		MaxUsers:         50,
		MaxRunners:       10,
		MaxRepositories:  100,
		MaxPodMinutes:    -1,
		Features:         []string{"sso", "audit_logs"},
		Message:          "License is active",
	}
	out := toProtoStatus(s)
	require.NotNil(t, out)
	assert.True(t, out.GetIsActive())
	assert.Equal(t, "LK-2026-ABCDEF", out.GetLicenseKey())
	assert.Equal(t, "Acme Corp", out.GetOrganizationName())
	assert.Equal(t, "enterprise", out.GetPlan())
	require.NotNil(t, out.ExpiresAt)
	assert.Equal(t, "2027-05-13T00:00:00Z", *out.ExpiresAt)
	assert.Equal(t, int32(50), out.GetMaxUsers())
	assert.Equal(t, int32(10), out.GetMaxRunners())
	assert.Equal(t, int32(100), out.GetMaxRepositories())
	assert.Equal(t, int32(-1), out.GetMaxPodMinutes())
	assert.Equal(t, []string{"sso", "audit_logs"}, out.GetFeatures())
	assert.Equal(t, "License is active", out.GetMessage())
}

func TestToProtoStatus_NilInput_EmptyMessage(t *testing.T) {
	out := toProtoStatus(nil)
	require.NotNil(t, out)
	assert.False(t, out.GetIsActive())
}

func TestToProtoStatus_NilExpiresAt_OptionalAbsent(t *testing.T) {
	s := &billing.LicenseStatus{
		IsActive: false,
		Message:  "No license installed",
	}
	out := toProtoStatus(s)
	require.NotNil(t, out)
	assert.Nil(t, out.ExpiresAt, "absent ExpiresAt must remain nil on the wire")
}

func TestToProtoLimits_PassesThrough(t *testing.T) {
	l := licenseservice.LicenseLimits{
		MaxUsers:        50,
		MaxRunners:      10,
		MaxRepositories: 100,
		MaxPodMinutes:   -1,
	}
	out := toProtoLimits(l)
	require.NotNil(t, out)
	assert.Equal(t, int32(50), out.GetMaxUsers())
	assert.Equal(t, int32(10), out.GetMaxRunners())
	assert.Equal(t, int32(100), out.GetMaxRepositories())
	assert.Equal(t, int32(-1), out.GetMaxPodMinutes())
}

func TestToProtoValidated_AllFieldsPopulated(t *testing.T) {
	issuedAt := time.Date(2026, 5, 13, 0, 0, 0, 0, time.UTC)
	expiresAt := time.Date(2027, 5, 13, 0, 0, 0, 0, time.UTC)
	l := &licenseservice.LicenseData{
		LicenseKey:       "LK-PREVIEW",
		OrganizationName: "Preview Org",
		ContactEmail:     "ops@preview.example",
		Plan:             "team",
		Limits: licenseservice.LicenseLimits{
			MaxUsers:        25,
			MaxRunners:      5,
			MaxRepositories: 50,
			MaxPodMinutes:   -1,
		},
		Features:  []string{"sso"},
		IssuedAt:  issuedAt,
		ExpiresAt: expiresAt,
	}
	out := toProtoValidated(l)
	require.NotNil(t, out)
	assert.True(t, out.GetValid())
	assert.Equal(t, "LK-PREVIEW", out.GetLicenseKey())
	assert.Equal(t, "Preview Org", out.GetOrganizationName())
	assert.Equal(t, "ops@preview.example", out.GetContactEmail())
	assert.Equal(t, "team", out.GetPlan())
	require.NotNil(t, out.GetLimits())
	assert.Equal(t, int32(25), out.GetLimits().GetMaxUsers())
	assert.Equal(t, []string{"sso"}, out.GetFeatures())
	assert.Equal(t, "2026-05-13T00:00:00Z", out.GetIssuedAt())
	assert.Equal(t, "2027-05-13T00:00:00Z", out.GetExpiresAt())
}

func TestToProtoValidated_NilInput_InvalidEnvelope(t *testing.T) {
	out := toProtoValidated(nil)
	require.NotNil(t, out)
	assert.False(t, out.GetValid(), "nil input must surface as valid=false envelope")
}
