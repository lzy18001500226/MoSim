package tokenusageconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	tuv1 "github.com/anthropics/agentsmesh/proto/gen/go/token_usage/v1"
)

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

func TestGetDashboard_NoOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil)
	_, err := srv.GetDashboard(context.Background(),
		connect.NewRequest(&tuv1.GetDashboardRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestIsAdminOrOwner(t *testing.T) {
	assert.True(t, isAdminOrOwner(&middleware.TenantContext{UserRole: "owner"}))
	assert.True(t, isAdminOrOwner(&middleware.TenantContext{UserRole: "admin"}))
	assert.False(t, isAdminOrOwner(&middleware.TenantContext{UserRole: "member"}))
	assert.False(t, isAdminOrOwner(&middleware.TenantContext{UserRole: ""}))
}

func TestBuildFilter_Defaults(t *testing.T) {
	f, err := buildFilter(&tuv1.GetDashboardRequest{})
	require.NoError(t, err)
	assert.Equal(t, "day", f.Granularity)
	assert.Nil(t, f.AgentSlug)
	assert.Nil(t, f.UserID)
	assert.Nil(t, f.Model)
	// Default window is last 30 days
	assert.True(t, f.EndTime.Sub(f.StartTime).Hours() > 24*29)
}

func TestBuildFilter_InvalidGranularity(t *testing.T) {
	_, err := buildFilter(&tuv1.GetDashboardRequest{Granularity: "hour"})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "invalid granularity")
}

func TestBuildFilter_InvalidTimeRange(t *testing.T) {
	_, err := buildFilter(&tuv1.GetDashboardRequest{
		StartTime: "2026-05-01T00:00:00Z",
		EndTime:   "2026-04-01T00:00:00Z",
	})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "start_time must be before end_time")
}

func TestBuildFilter_DateRangeTooLong(t *testing.T) {
	_, err := buildFilter(&tuv1.GetDashboardRequest{
		StartTime: "2024-01-01T00:00:00Z",
		EndTime:   "2026-01-01T00:00:00Z",
	})
	require.Error(t, err)
	assert.Contains(t, err.Error(), "cannot exceed 366 days")
}

func TestProcedureConstants(t *testing.T) {
	assert.Equal(t, "/proto.token_usage.v1.TokenUsageService/GetDashboard", GetDashboardProcedure)
}
