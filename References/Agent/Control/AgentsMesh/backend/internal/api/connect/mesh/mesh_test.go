package meshconnect

import (
	"context"
	"errors"
	"testing"
	"time"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/domain/agentpod"
	domainmesh "github.com/anthropics/agentsmesh/backend/internal/domain/mesh"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	meshservice "github.com/anthropics/agentsmesh/backend/internal/service/mesh"
	meshv1 "github.com/anthropics/agentsmesh/proto/gen/go/mesh/v1"
)

// --- test fakes ---

type fakeOrg struct {
	id   int64
	slug string
}

func (f fakeOrg) GetID() int64    { return f.id }
func (f fakeOrg) GetSlug() string { return f.slug }
func (f fakeOrg) GetName() string { return f.slug }

type fakeOrgService struct{}

func (f *fakeOrgService) GetBySlug(_ context.Context, slug string) (middleware.OrganizationGetter, error) {
	if slug == "missing" {
		return nil, errors.New("org not found")
	}
	return fakeOrg{id: 7, slug: slug}, nil
}
func (f *fakeOrgService) IsMember(context.Context, int64, int64) (bool, error) { return true, nil }
func (f *fakeOrgService) GetMemberRole(context.Context, int64, int64) (string, error) {
	return "member", nil
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

// --- guard rails: org_slug + auth on every RPC ---

func TestGetMeshTopology_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, &fakeOrgService{})
	_, err := srv.GetMeshTopology(ctxAsUser(1), connect.NewRequest(&meshv1.GetMeshTopologyRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestGetMeshTopology_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil, &fakeOrgService{})
	_, err := srv.GetMeshTopology(context.Background(), connect.NewRequest(&meshv1.GetMeshTopologyRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestGetTicketPods_MissingTicketSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, &fakeOrgService{})
	_, err := srv.GetTicketPods(ctxAsUser(1), connect.NewRequest(&meshv1.GetTicketPodsRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestBatchGetTicketPods_EmptyIDs_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, &fakeOrgService{})
	_, err := srv.BatchGetTicketPods(ctxAsUser(1), connect.NewRequest(&meshv1.BatchGetTicketPodsRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestBatchGetTicketPods_OverLimit_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, &fakeOrgService{})
	ids := make([]int64, 101)
	for i := range ids {
		ids[i] = int64(i + 1)
	}
	_, err := srv.BatchGetTicketPods(ctxAsUser(1), connect.NewRequest(&meshv1.BatchGetTicketPodsRequest{
		OrgSlug:   "acme",
		TicketIds: ids,
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestCreatePodForTicket_MissingRunnerID_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, &fakeOrgService{})
	_, err := srv.CreatePodForTicket(ctxAsUser(1), connect.NewRequest(&meshv1.CreatePodForTicketRequest{
		OrgSlug:    "acme",
		TicketSlug: "T-1",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// --- mapServiceError table ---

func TestMapServiceError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"ticket_not_found", meshservice.ErrTicketNotFound, connect.CodeNotFound},
		{"runner_not_found", meshservice.ErrRunnerNotFound, connect.CodeNotFound},
		{"generic_error", errors.New("oops"), connect.CodeInternal},
		{"wrapped_unrelated_not_found", errors.New("not found: foo"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := connectCodeOf(t, mapServiceError(tc.in))
			assert.Equal(t, tc.want, got)
		})
	}
}

// --- toProtoMeshNode: every field round-trips into the proto message ---

func mustParseTime(t *testing.T, s string) time.Time {
	t.Helper()
	tt, err := time.Parse(time.RFC3339, s)
	require.NoError(t, err)
	return tt
}

func TestToProtoMeshNode_AllFieldsPopulated(t *testing.T) {
	model := "claude-3-7-sonnet"
	title := "Build a chatbot"
	alias := "worker"
	ticketID := int64(42)
	ticketSlug := "AGM-123"
	ticketTitle := "Fix the bug"
	repoID := int64(7)
	startedAt := mustParseTime(t, "2026-05-10T00:00:00Z")

	n := domainmesh.MeshNode{
		PodKey:       "pod-001",
		Status:       "running",
		AgentStatus:  "active",
		Model:        &model,
		Title:        &title,
		Alias:        &alias,
		TicketID:     &ticketID,
		TicketSlug:   &ticketSlug,
		TicketTitle:  &ticketTitle,
		RepositoryID: &repoID,
		CreatedByID:  99,
		RunnerID:     11,
		RunnerNodeID: "node-abc",
		RunnerStatus: "online",
		StartedAt:    &startedAt,
	}

	got := toProtoMeshNode(n)
	require.NotNil(t, got)
	assert.Equal(t, "pod-001", got.GetPodKey())
	assert.Equal(t, "running", got.GetStatus())
	assert.Equal(t, "active", got.GetAgentStatus())
	assert.Equal(t, "claude-3-7-sonnet", got.GetModel())
	assert.Equal(t, "Build a chatbot", got.GetTitle())
	assert.Equal(t, "worker", got.GetAlias())
	assert.Equal(t, int64(42), got.GetTicketId())
	assert.Equal(t, "AGM-123", got.GetTicketSlug())
	assert.Equal(t, "Fix the bug", got.GetTicketTitle())
	assert.Equal(t, int64(7), got.GetRepositoryId())
	assert.Equal(t, int64(99), got.GetCreatedById())
	assert.Equal(t, int64(11), got.GetRunnerId())
	assert.Equal(t, "node-abc", got.GetRunnerNodeId())
	assert.Equal(t, "online", got.GetRunnerStatus())
	assert.Equal(t, "2026-05-10T00:00:00Z", got.GetStartedAt())
}

func TestToProtoMeshNode_NilOptionalsAbsent(t *testing.T) {
	n := domainmesh.MeshNode{
		PodKey:       "p",
		Status:       "creating",
		AgentStatus:  "idle",
		CreatedByID:  1,
		RunnerID:     2,
		RunnerNodeID: "n",
		RunnerStatus: "online",
	}
	got := toProtoMeshNode(n)
	require.NotNil(t, got)
	assert.Nil(t, got.Model)
	assert.Nil(t, got.Title)
	assert.Nil(t, got.Alias)
	assert.Nil(t, got.TicketId)
	assert.Nil(t, got.TicketSlug)
	assert.Nil(t, got.TicketTitle)
	assert.Nil(t, got.RepositoryId)
	assert.Nil(t, got.StartedAt)
}

func TestToProtoTopology_NilInput_ReturnsEmpty(t *testing.T) {
	got := toProtoTopology(nil)
	require.NotNil(t, got)
	assert.Empty(t, got.GetNodes())
	assert.Empty(t, got.GetEdges())
	assert.Empty(t, got.GetChannels())
	assert.Empty(t, got.GetRunners())
}

func TestToProtoMeshEdge_PreservesScopes(t *testing.T) {
	e := domainmesh.MeshEdge{
		ID:            17,
		Source:        "pod-a",
		Target:        "pod-b",
		GrantedScopes: []string{"pod:read", "pod:write"},
		PendingScopes: []string{"pod:admin"},
		Status:        "active",
	}
	got := toProtoMeshEdge(e)
	require.NotNil(t, got)
	assert.Equal(t, int64(17), got.GetId())
	assert.Equal(t, []string{"pod:read", "pod:write"}, got.GetGrantedScopes())
	assert.Equal(t, []string{"pod:admin"}, got.GetPendingScopes())
}

func TestPodToProtoMeshNode_NilReturnsNil(t *testing.T) {
	assert.Nil(t, podToProtoMeshNode(nil))
}

func TestPodToProtoMeshNode_PullsRunnerAndTicketFromAssociations(t *testing.T) {
	model := "opus"
	title := "Worker"
	startedAt := mustParseTime(t, "2026-05-09T00:00:00Z")
	p := &agentpod.Pod{
		PodKey:      "pod-xyz",
		Status:      "running",
		AgentStatus: "active",
		AgentSlug:   "claude-code",
		CreatedByID: 5,
		RunnerID:    3,
		Model:       &model,
		Title:       &title,
		StartedAt:   &startedAt,
	}
	got := podToProtoMeshNode(p)
	require.NotNil(t, got)
	assert.Equal(t, "pod-xyz", got.GetPodKey())
	assert.Equal(t, "claude-code", got.GetAgentSlug())
	assert.Equal(t, "opus", got.GetModel())
	assert.Equal(t, "2026-05-09T00:00:00Z", got.GetStartedAt())
	// Runner and Ticket associations omitted — nil pointers leave the fields
	// at proto zero values (empty string), parity with the REST projection.
	assert.Empty(t, got.GetRunnerNodeId())
	assert.Empty(t, got.GetRunnerStatus())
	assert.Nil(t, got.TicketSlug)
}
