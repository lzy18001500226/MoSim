package podconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/domain/agentpod"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	agentpodservice "github.com/anthropics/agentsmesh/backend/internal/service/agentpod"
	billingservice "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	runner "github.com/anthropics/agentsmesh/backend/internal/service/runner"
	podv1 "github.com/anthropics/agentsmesh/proto/gen/go/pod/v1"
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

func TestListPods_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListPods(ctxAsUser(42), connect.NewRequest(&podv1.ListPodsRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListPods_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListPods(context.Background(), connect.NewRequest(&podv1.ListPodsRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestCreatePod_OrchestratorNotConfigured_Unavailable(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.CreatePod(ctxAsUser(42), connect.NewRequest(&podv1.CreatePodRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
}

func TestTerminatePod_CoordinatorNotConfigured_Unavailable(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.TerminatePod(ctxAsUser(42), connect.NewRequest(&podv1.TerminatePodRequest{OrgSlug: "acme", PodKey: "p"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
}

func TestSendPodPrompt_CommandSenderNotConfigured_Unavailable(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.SendPodPrompt(ctxAsUser(42), connect.NewRequest(&podv1.SendPodPromptRequest{OrgSlug: "acme", PodKey: "p", Prompt: "hi"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
}

func TestGetPodConnection_NoRelay_Unavailable(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.GetPodConnection(ctxAsUser(42), connect.NewRequest(&podv1.GetPodConnectionRequest{OrgSlug: "acme", PodKey: "p"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnavailable, connectCodeOf(t, err))
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
		{"pod_not_found", agentpodservice.ErrPodNotFound, connect.CodeNotFound},
		{"source_pod_not_found", agentpodservice.ErrSourcePodNotFound, connect.CodeNotFound},
		{"missing_runner_id", agentpodservice.ErrMissingRunnerID, connect.CodeInvalidArgument},
		{"missing_agent_slug", agentpodservice.ErrMissingAgentSlug, connect.CodeInvalidArgument},
		{"source_pod_not_terminated", agentpodservice.ErrSourcePodNotTerminated, connect.CodeInvalidArgument},
		{"resume_runner_mismatch", agentpodservice.ErrResumeRunnerMismatch, connect.CodeInvalidArgument},
		{"unsupported_interaction_mode", agentpodservice.ErrUnsupportedInteractionMode, connect.CodeInvalidArgument},
		{"invalid_agentfile_layer", agentpodservice.ErrInvalidAgentfileLayer, connect.CodeInvalidArgument},
		{"quota_exceeded", billingservice.ErrQuotaExceeded, connect.CodeResourceExhausted},
		{"subscription_frozen", billingservice.ErrSubscriptionFrozen, connect.CodeFailedPrecondition},
		{"source_pod_access_denied", agentpodservice.ErrSourcePodAccessDenied, connect.CodePermissionDenied},
		{"source_pod_already_resumed", agentpodservice.ErrSourcePodAlreadyResumed, connect.CodeAlreadyExists},
		{"sandbox_already_resumed", agentpod.ErrSandboxAlreadyResumed, connect.CodeAlreadyExists},
		{"no_available_runner", agentpodservice.ErrNoAvailableRunner, connect.CodeUnavailable},
		{"runner_dispatch_failed", agentpodservice.ErrRunnerDispatchFailed, connect.CodeUnavailable},
		{"pod_already_terminated", runner.ErrPodAlreadyTerminated, connect.CodeUnavailable},
		{"config_build_failed", agentpodservice.ErrConfigBuildFailed, connect.CodeInternal},
		{"wrapped_not_found", errors.New("wrap: " + agentpodservice.ErrPodNotFound.Error()), connect.CodeInternal},
		{"generic", errors.New("oops"), connect.CodeInternal},
		{"nil", nil, 0},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := mapServiceError(tc.in)
			if tc.want == 0 {
				assert.NoError(t, got)
				return
			}
			assert.Equal(t, tc.want, connectCodeOf(t, got))
		})
	}
}
