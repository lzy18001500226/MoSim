package userconnect

import (
	"context"
	"testing"
	"time"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	domainuser "github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	userv1 "github.com/anthropics/agentsmesh/proto/gen/go/user/v1"
)

// Auth-guard tests — each RPC short-circuits on missing TenantContext.
// Business-logic coverage lives alongside userservice.Service; the
// connect handlers add only proto<->domain translation + auth gating.

func TestGetMe_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.GetMe(context.Background(), connect.NewRequest(&userv1.GetMeRequest{}))
	requireConnectCode(t, err, connect.CodeUnauthenticated)
}

func TestUpdateMe_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.UpdateMe(context.Background(), connect.NewRequest(&userv1.UpdateMeRequest{}))
	requireConnectCode(t, err, connect.CodeUnauthenticated)
}

func TestChangePassword_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.ChangePassword(context.Background(), connect.NewRequest(&userv1.ChangePasswordRequest{}))
	requireConnectCode(t, err, connect.CodeUnauthenticated)
}

func TestListIdentities_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.ListIdentities(context.Background(), connect.NewRequest(&userv1.ListIdentitiesRequest{}))
	requireConnectCode(t, err, connect.CodeUnauthenticated)
}

func TestDeleteIdentity_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.DeleteIdentity(context.Background(), connect.NewRequest(&userv1.DeleteIdentityRequest{Provider: "github"}))
	requireConnectCode(t, err, connect.CodeUnauthenticated)
}

func TestSearchUsers_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.SearchUsers(context.Background(), connect.NewRequest(&userv1.SearchUsersRequest{Q: "ab"}))
	requireConnectCode(t, err, connect.CodeUnauthenticated)
}

func TestSearchUsers_QueryTooShort_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.SearchUsers(authedCtx(42), connect.NewRequest(&userv1.SearchUsersRequest{Q: "a"}))
	requireConnectCode(t, err, connect.CodeInvalidArgument)
}

func TestChangePassword_TooShortNewPassword_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.ChangePassword(authedCtx(42), connect.NewRequest(&userv1.ChangePasswordRequest{
		CurrentPassword: "current",
		NewPassword:     "short",
	}))
	requireConnectCode(t, err, connect.CodeInvalidArgument)
}

func TestChangePassword_EmptyFields_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.ChangePassword(authedCtx(42), connect.NewRequest(&userv1.ChangePasswordRequest{}))
	requireConnectCode(t, err, connect.CodeInvalidArgument)
}

func TestDeleteIdentity_EmptyProvider_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.DeleteIdentity(authedCtx(42), connect.NewRequest(&userv1.DeleteIdentityRequest{Provider: ""}))
	requireConnectCode(t, err, connect.CodeInvalidArgument)
}

func TestRequireUserID_HasUserID(t *testing.T) {
	uid, err := requireUserID(authedCtx(42))
	require.NoError(t, err)
	assert.Equal(t, int64(42), uid)
}

func TestRequireUserID_ZeroUserID_Unauthenticated(t *testing.T) {
	ctx := middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: 0})
	_, err := requireUserID(ctx)
	requireConnectCode(t, err, connect.CodeUnauthenticated)
}

func TestToProtoUser_AllFieldsMapped(t *testing.T) {
	hash := "supersecret-bcrypt-hash"
	name := "Alice"
	avatar := "https://example.com/a.png"
	lastLogin := time.Date(2026, 5, 1, 0, 0, 0, 0, time.UTC)
	credID := int64(7)
	in := &domainuser.User{
		ID:                     42,
		Email:                  "alice@example.com",
		Username:               "alice",
		Name:                   &name,
		AvatarURL:              &avatar,
		PasswordHash:           &hash,
		IsActive:               true,
		IsSystemAdmin:          false,
		IsEmailVerified:        true,
		LastLoginAt:            &lastLogin,
		DefaultGitCredentialID: &credID,
		CreatedAt:              time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
		UpdatedAt:              time.Date(2026, 5, 1, 0, 0, 0, 0, time.UTC),
	}
	out := ToProtoUser(in)
	require.NotNil(t, out)
	assert.Equal(t, int64(42), out.GetId())
	assert.Equal(t, "alice@example.com", out.GetEmail())
	assert.Equal(t, "alice", out.GetUsername())
	assert.Equal(t, "Alice", out.GetName())
	assert.Equal(t, "https://example.com/a.png", out.GetAvatarUrl())
	assert.True(t, out.GetIsActive())
	assert.False(t, out.GetIsSystemAdmin())
	assert.True(t, out.GetIsEmailVerified())
	assert.Equal(t, "2026-05-01T00:00:00Z", out.GetLastLoginAt())
	assert.Equal(t, int64(7), out.GetDefaultGitCredentialId())
	assert.Equal(t, "2026-01-01T00:00:00Z", out.GetCreatedAt())
	assert.Equal(t, "2026-05-01T00:00:00Z", out.GetUpdatedAt())
}

func TestToProtoUser_OptionalFieldsAbsent(t *testing.T) {
	// User with only required fields set — optional fields stay unset.
	in := &domainuser.User{
		ID:        1,
		Email:     "bob@example.com",
		Username:  "bob",
		IsActive:  true,
		CreatedAt: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
		UpdatedAt: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
	}
	out := ToProtoUser(in)
	require.NotNil(t, out)
	assert.Nil(t, out.Name)
	assert.Nil(t, out.AvatarUrl)
	assert.Nil(t, out.LastLoginAt)
	assert.Nil(t, out.DefaultGitCredentialId)
}

func TestToProtoUserSummary_OnlyPublicFields(t *testing.T) {
	hash := "supersecret-bcrypt-hash"
	name := "Alice"
	avatar := "https://example.com/a.png"
	in := &domainuser.User{
		ID:           42,
		Email:        "alice@example.com",
		Username:     "alice",
		Name:         &name,
		AvatarURL:    &avatar,
		PasswordHash: &hash,
	}
	out := toProtoUserSummary(in)
	require.NotNil(t, out)
	assert.Equal(t, int64(42), out.GetId())
	assert.Equal(t, "alice@example.com", out.GetEmail())
	assert.Equal(t, "alice", out.GetUsername())
	assert.Equal(t, "Alice", out.GetName())
	assert.Equal(t, "https://example.com/a.png", out.GetAvatarUrl())
}

func TestToProtoIdentity_AllFieldsMapped(t *testing.T) {
	providerUsername := "alice-gh"
	tokenExpires := time.Date(2026, 6, 1, 0, 0, 0, 0, time.UTC)
	in := &domainuser.Identity{
		ID:               101,
		UserID:           42,
		Provider:         "github",
		ProviderUserID:   "1234567",
		ProviderUsername: &providerUsername,
		TokenExpiresAt:   &tokenExpires,
		CreatedAt:        time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC),
		UpdatedAt:        time.Date(2026, 5, 1, 0, 0, 0, 0, time.UTC),
	}
	out := ToProtoIdentity(in)
	require.NotNil(t, out)
	assert.Equal(t, int64(101), out.GetId())
	assert.Equal(t, int64(42), out.GetUserId())
	assert.Equal(t, "github", out.GetProvider())
	assert.Equal(t, "1234567", out.GetProviderUserId())
	assert.Equal(t, "alice-gh", out.GetProviderUsername())
	assert.Equal(t, "2026-06-01T00:00:00Z", out.GetTokenExpiresAt())
	assert.Equal(t, "2026-01-01T00:00:00Z", out.GetCreatedAt())
}

// --- helpers ---

func authedCtx(userID int64) context.Context {
	return middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: userID})
}

func requireConnectCode(t *testing.T, err error, code connect.Code) {
	t.Helper()
	require.Error(t, err)
	var ce *connect.Error
	require.ErrorAs(t, err, &ce)
	assert.Equal(t, code, ce.Code())
}
