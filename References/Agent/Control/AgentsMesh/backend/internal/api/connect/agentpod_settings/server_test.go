package agentpodsettingsconnect

import (
	"context"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	podv1 "github.com/anthropics/agentsmesh/proto/gen/go/pod/v1"
)

// Test the auth-guard. Heavy integration tests live alongside
// SettingsService / AIProviderService — Connect handlers add no
// business logic beyond proto<->domain translation + auth gating.
func TestGetSettings_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.GetSettings(context.Background(), connect.NewRequest(&podv1.GetSettingsRequest{}))
	require.Error(t, err)
	var ce *connect.Error
	require.ErrorAs(t, err, &ce)
	assert.Equal(t, connect.CodeUnauthenticated, ce.Code())
}

func TestListProviders_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.ListProviders(context.Background(), connect.NewRequest(&podv1.ListProvidersRequest{}))
	require.Error(t, err)
	var ce *connect.Error
	require.ErrorAs(t, err, &ce)
	assert.Equal(t, connect.CodeUnauthenticated, ce.Code())
}

func TestUpdateSettings_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.UpdateSettings(context.Background(), connect.NewRequest(&podv1.UpdateSettingsRequest{}))
	require.Error(t, err)
	var ce *connect.Error
	require.ErrorAs(t, err, &ce)
	assert.Equal(t, connect.CodeUnauthenticated, ce.Code())
}

func TestCreateProvider_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.CreateProvider(context.Background(), connect.NewRequest(&podv1.CreateProviderRequest{}))
	require.Error(t, err)
	var ce *connect.Error
	require.ErrorAs(t, err, &ce)
	assert.Equal(t, connect.CodeUnauthenticated, ce.Code())
}

func TestRequireUserID_HasUserID(t *testing.T) {
	ctx := middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: 42})
	uid, err := requireUserID(ctx)
	require.NoError(t, err)
	assert.Equal(t, int64(42), uid)
}

func TestRequireUserID_ZeroUserID_Unauthenticated(t *testing.T) {
	ctx := middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: 0})
	_, err := requireUserID(ctx)
	require.Error(t, err)
	var ce *connect.Error
	require.ErrorAs(t, err, &ce)
	assert.Equal(t, connect.CodeUnauthenticated, ce.Code())
}
