package extensionconnect

import (
	"context"
	"errors"
	"testing"
	"time"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	extdom "github.com/anthropics/agentsmesh/backend/internal/domain/extension"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	extensionservice "github.com/anthropics/agentsmesh/backend/internal/service/extension"
	extensionv1 "github.com/anthropics/agentsmesh/proto/gen/go/extension/v1"
)

type fakeOrg struct{ id int64; slug string }

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

// ctxAsUser populates the auth-interceptor stand-in: UserID matters because
// ResolveOrgScope rejects empty TenantContext as Unauthenticated.
func ctxAsUser(userID int64) context.Context {
	return middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: userID})
}

// connectCodeOf is the canonical accessor for the Connect error code,
// independent of the test framework's error helpers.
func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

// --- requireOrgAdmin / Resolve guards ---

func TestListSkillRegistries_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListSkillRegistries(ctxAsUser(42), connect.NewRequest(&extensionv1.ListSkillRegistriesRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListSkillRegistries_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListSkillRegistries(context.Background(), connect.NewRequest(&extensionv1.ListSkillRegistriesRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestListSkillRegistries_NonAdmin_PermissionDenied(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"})
	_, err := srv.ListSkillRegistries(ctxAsUser(42), connect.NewRequest(&extensionv1.ListSkillRegistriesRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodePermissionDenied, connectCodeOf(t, err))
}

// --- mapServiceError table ---

func TestMapServiceError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"not_found", extensionservice.ErrNotFound, connect.CodeNotFound},
		{"wrapped_not_found", errors.New("wrap: " + extensionservice.ErrNotFound.Error()), connect.CodeInternal},
		{"forbidden", extensionservice.ErrForbidden, connect.CodePermissionDenied},
		{"invalid_input", extensionservice.ErrInvalidInput, connect.CodeInvalidArgument},
		{"invalid_scope", extensionservice.ErrInvalidScope, connect.CodeInvalidArgument},
		{"already_installed", extensionservice.ErrAlreadyInstalled, connect.CodeAlreadyExists},
		{"generic_error", errors.New("oops"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := connectCodeOf(t, mapServiceError(tc.in))
			assert.Equal(t, tc.want, got)
		})
	}
}

// --- toProtoSkillRegistry: every field round-trips into the proto message ---

func TestToProtoSkillRegistry_AllFieldsPopulated(t *testing.T) {
	orgID := int64(42)
	syncTime := mustParseTime(t, "2026-05-12T13:16:10Z")
	createdAt := mustParseTime(t, "2026-05-01T00:00:00Z")
	updatedAt := mustParseTime(t, "2026-05-10T00:00:00Z")

	r := &extdom.SkillRegistry{
		ID:               7,
		OrganizationID:   &orgID,
		RepositoryURL:    "https://github.com/example/skills",
		Branch:           "main",
		SourceType:       "auto",
		DetectedType:     "collection",
		CompatibleAgents: []byte(`["claude-code","codex"]`),
		AuthType:         "github_pat",
		LastSyncedAt:     &syncTime,
		LastCommitSha:    "abc123",
		SyncStatus:       "success",
		SyncError:        "",
		SkillCount:       12,
		IsActive:         true,
		CreatedAt:        createdAt,
		UpdatedAt:        updatedAt,
	}

	got := toProtoSkillRegistry(r)
	require.NotNil(t, got)
	assert.Equal(t, int64(7), got.GetId())
	assert.Equal(t, int64(42), got.GetOrganizationId())
	assert.Equal(t, "https://github.com/example/skills", got.GetRepositoryUrl())
	assert.Equal(t, "main", got.GetBranch())
	assert.Equal(t, "auto", got.GetSourceType())
	assert.Equal(t, "collection", got.GetDetectedType())
	assert.Equal(t, []string{"claude-code", "codex"}, got.GetCompatibleAgents())
	assert.Equal(t, "github_pat", got.GetAuthType())
	assert.Equal(t, "2026-05-12T13:16:10Z", got.GetLastSyncedAt())
	assert.Equal(t, "abc123", got.GetLastCommitSha())
	assert.Equal(t, "success", got.GetSyncStatus())
	assert.Equal(t, "", got.GetSyncError(), "empty optional should round-trip to empty string via Get accessor")
	assert.Equal(t, int32(12), got.GetSkillCount())
	assert.True(t, got.GetIsActive())
	assert.Equal(t, "2026-05-01T00:00:00Z", got.GetCreatedAt())
	assert.Equal(t, "2026-05-10T00:00:00Z", got.GetUpdatedAt())
}

func TestToProtoSkillRegistry_PlatformLevel_NoOrganizationID(t *testing.T) {
	r := &extdom.SkillRegistry{
		ID:            1,
		// OrganizationID is nil → platform-level
		RepositoryURL: "https://github.com/agentsmesh/skills-platform",
		Branch:        "main",
		SourceType:    "auto",
		AuthType:      "none",
		SyncStatus:    "pending",
		IsActive:      true,
		CreatedAt:     mustParseTime(t, "2026-05-01T00:00:00Z"),
		UpdatedAt:     mustParseTime(t, "2026-05-01T00:00:00Z"),
	}
	got := toProtoSkillRegistry(r)
	require.NotNil(t, got)
	assert.Nil(t, got.OrganizationId,
		"organization_id must remain nil/absent for platform-level registries")
	assert.Nil(t, got.LastSyncedAt, "absent last_synced_at must remain nil")
}

func TestToProtoSkillRegistry_NilInput_ReturnsNil(t *testing.T) {
	assert.Nil(t, toProtoSkillRegistry(nil))
}

func mustParseTime(t *testing.T, s string) time.Time {
	t.Helper()
	tt, err := time.Parse(time.RFC3339, s)
	require.NoError(t, err)
	return tt
}
