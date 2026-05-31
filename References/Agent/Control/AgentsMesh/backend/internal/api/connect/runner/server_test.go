package runnerconnect

import (
	"context"
	"errors"
	"testing"
	"time"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	rundom "github.com/anthropics/agentsmesh/backend/internal/domain/runner"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
	runnerapiv1 "github.com/anthropics/agentsmesh/proto/gen/go/runner_api/v1"
)

// =====================================================================
// Helpers
// =====================================================================

type fakeOrg struct {
	id   int64
	slug string
}

func (f fakeOrg) GetID() int64    { return f.id }
func (f fakeOrg) GetSlug() string { return f.slug }
func (f fakeOrg) GetName() string { return f.slug }

type fakeOrgService struct {
	role string
}

func (f *fakeOrgService) GetBySlug(_ context.Context, slug string) (middleware.OrganizationGetter, error) {
	if slug == "missing" {
		return nil, errors.New("org not found")
	}
	return fakeOrg{id: 7, slug: slug}, nil
}
func (f *fakeOrgService) IsMember(context.Context, int64, int64) (bool, error) { return true, nil }
func (f *fakeOrgService) GetMemberRole(context.Context, int64, int64) (string, error) {
	return f.role, nil
}

func ctxAsUser(userID int64) context.Context {
	return middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: userID})
}

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

// =====================================================================
// Resolve / auth guards
// =====================================================================

func TestListRunners_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListRunners(ctxAsUser(42), connect.NewRequest(&runnerapiv1.ListRunnersRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListRunners_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListRunners(context.Background(), connect.NewRequest(&runnerapiv1.ListRunnersRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

// =====================================================================
// mapServiceError table
// =====================================================================

func TestMapServiceError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"not_found", runner.ErrRunnerNotFound, connect.CodeNotFound},
		{"token_not_found", runner.ErrGRPCTokenNotFound, connect.CodeNotFound},
		{"has_loop_refs", runner.ErrRunnerHasLoopRefs, connect.CodeFailedPrecondition},
		{"not_connected", runner.ErrRunnerNotConnected, connect.CodeUnavailable},
		{"offline", runner.ErrRunnerOffline, connect.CodeUnavailable},
		{"quota_exceeded", runner.ErrRunnerQuotaExceeded, connect.CodeResourceExhausted},
		{"invalid_token", runner.ErrInvalidToken, connect.CodeUnauthenticated},
		{"token_expired", runner.ErrTokenExpired, connect.CodeUnauthenticated},
		{"wrapped_not_found", errors.New("wrap: " + runner.ErrRunnerNotFound.Error()), connect.CodeInternal},
		{"generic", errors.New("oops"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := connectCodeOf(t, mapServiceError(tc.in))
			assert.Equal(t, tc.want, got)
		})
	}
}

// =====================================================================
// toProtoRunner — every field round-trips
// =====================================================================

func TestToProtoRunner_AllFieldsPopulated(t *testing.T) {
	heartbeat := mustParseTime(t, "2026-05-12T13:16:10Z")
	createdAt := mustParseTime(t, "2026-05-01T00:00:00Z")
	updatedAt := mustParseTime(t, "2026-05-10T00:00:00Z")
	version := "0.29.0"
	registeredBy := int64(42)

	r := &rundom.Runner{
		ID:                 7,
		OrganizationID:     99,
		NodeID:             "node-abc",
		Description:        "dev runner",
		Status:             "online",
		LastHeartbeat:      &heartbeat,
		CurrentPods:        2,
		MaxConcurrentPods:  5,
		RunnerVersion:      &version,
		IsEnabled:          true,
		AvailableAgents:    rundom.StringSlice{"claude-code", "codex"},
		AgentVersions: rundom.AgentVersionSlice{
			{Slug: "claude-code", Version: "1.2.3", Path: "/usr/local/bin/claude"},
		},
		HostInfo:           rundom.HostInfo{"os": "linux", "arch": "arm64"},
		Tags:               rundom.StringSlice{"prod", "edge"},
		Visibility:         "organization",
		RegisteredByUserID: &registeredBy,
		CreatedAt:          createdAt,
		UpdatedAt:          updatedAt,
	}

	got := ToProtoRunner(r)
	require.NotNil(t, got)
	assert.Equal(t, int64(7), got.GetId())
	assert.Equal(t, int64(99), got.GetOrganizationId())
	assert.Equal(t, "node-abc", got.GetNodeId())
	assert.Equal(t, "dev runner", got.GetDescription())
	assert.Equal(t, "online", got.GetStatus())
	assert.Equal(t, "2026-05-12T13:16:10Z", got.GetLastHeartbeat())
	assert.Equal(t, int32(2), got.GetCurrentPods())
	assert.Equal(t, int32(5), got.GetMaxConcurrentPods())
	assert.Equal(t, "0.29.0", got.GetRunnerVersion())
	assert.True(t, got.GetIsEnabled())
	assert.Equal(t, []string{"claude-code", "codex"}, got.GetAvailableAgents())
	assert.Len(t, got.GetAgentVersions(), 1)
	assert.Equal(t, "claude-code", got.GetAgentVersions()[0].GetSlug())
	assert.Equal(t, []string{"prod", "edge"}, got.GetTags())
	assert.Equal(t, "organization", got.GetVisibility())
	assert.Equal(t, int64(42), got.GetRegisteredByUserId())
	assert.Equal(t, "2026-05-01T00:00:00Z", got.GetCreatedAt())
	assert.Equal(t, "2026-05-10T00:00:00Z", got.GetUpdatedAt())
	// host_info JSON contains both keys, regardless of map iteration order.
	hostJSON := got.GetHostInfoJson()
	assert.Contains(t, hostJSON, `"os":"linux"`)
	assert.Contains(t, hostJSON, `"arch":"arm64"`)
}

func TestToProtoRunner_NilInput_ReturnsNil(t *testing.T) {
	assert.Nil(t, ToProtoRunner(nil))
}

func TestToProtoRunner_MinimalFields_OmitsAbsentOptionals(t *testing.T) {
	r := &rundom.Runner{
		ID:                1,
		NodeID:            "node-1",
		Status:            "offline",
		MaxConcurrentPods: 1,
		Visibility:        "private",
		CreatedAt:         mustParseTime(t, "2026-05-01T00:00:00Z"),
		UpdatedAt:         mustParseTime(t, "2026-05-01T00:00:00Z"),
	}
	got := ToProtoRunner(r)
	require.NotNil(t, got)
	assert.Nil(t, got.LastHeartbeat, "absent heartbeat must remain nil")
	assert.Nil(t, got.RunnerVersion, "absent runner_version must remain nil")
	assert.Nil(t, got.RegisteredByUserId, "absent registered_by_user_id must remain nil")
	assert.Empty(t, got.GetHostInfoJson(), "nil host_info encodes to empty string")
	assert.Empty(t, got.GetAvailableAgents())
	assert.Empty(t, got.GetTags())
	assert.Empty(t, got.GetAgentVersions())
}

// =====================================================================
// labelsToMap
// =====================================================================

func TestLabelsToMap(t *testing.T) {
	cases := []struct {
		name string
		in   []string
		want map[string]string
	}{
		{"empty", nil, nil},
		{"single", []string{"env=prod"}, map[string]string{"env": "prod"}},
		{"multi", []string{"a=b", "c=d"}, map[string]string{"a": "b", "c": "d"}},
		{"value_with_equals", []string{"k=a=b"}, map[string]string{"k": "a=b"}},
		{"malformed_dropped", []string{"k=v", "nokey"}, map[string]string{"k": "v"}},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, labelsToMap(tc.in))
		})
	}
}

func mustParseTime(t *testing.T, s string) time.Time {
	t.Helper()
	tt, err := time.Parse(time.RFC3339, s)
	require.NoError(t, err)
	return tt
}
