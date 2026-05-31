package infra

import (
	"context"
	"testing"

	"github.com/anthropics/agentsmesh/backend/internal/domain/envbundle"
	"github.com/anthropics/agentsmesh/backend/internal/testkit"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func envStrPtr(s string) *string { return &s }

func newTestEnvBundleRepo(t *testing.T) envbundle.Repository {
	t.Helper()
	return NewEnvBundleRepository(testkit.SetupTestDB(t))
}

// CreateWithPrimary inserts the bundle as the sole primary within its group.
func TestEnvBundleRepo_CreateWithPrimary_FreshGroup(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	b := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser,
		OwnerID:    1,
		AgentSlug:  envStrPtr("claude-code"),
		Name:       "work",
		Kind:       envbundle.KindCredential,
		IsActive:   true,
		Data:       envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, b))
	assert.True(t, b.KindPrimary)
}

// CreateWithPrimary atomically demotes any prior primary in the same group.
func TestEnvBundleRepo_CreateWithPrimary_DemotesExisting(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	first := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("claude-code"), Name: "first",
		Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, first))

	second := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("claude-code"), Name: "second",
		Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, second))

	got1, _ := repo.GetByID(ctx, first.ID)
	got2, _ := repo.GetByID(ctx, second.ID)
	assert.False(t, got1.KindPrimary, "first primary must be demoted by the second insert")
	assert.True(t, got2.KindPrimary)
}

// Two primaries in different agent_slug groups coexist.
func TestEnvBundleRepo_CreateWithPrimary_DifferentAgentsCoexist(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	cc := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("claude-code"), Name: "cc",
		Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, cc))

	codex := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("codex-cli"), Name: "codex",
		Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, codex))

	got1, _ := repo.GetByID(ctx, cc.ID)
	got2, _ := repo.GetByID(ctx, codex.ID)
	assert.True(t, got1.KindPrimary, "different agent_slug groups don't compete")
	assert.True(t, got2.KindPrimary)
}

// NULL agent_slug forms its own group, distinct from any concrete slug.
func TestEnvBundleRepo_CreateWithPrimary_NullAgentSlugIsOwnGroup(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	universal := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: nil, Name: "universal",
		Kind: envbundle.KindRuntime, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, universal))

	scoped := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("claude-code"), Name: "scoped",
		Kind: envbundle.KindRuntime, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, scoped))

	gotUniversal, _ := repo.GetByID(ctx, universal.ID)
	gotScoped, _ := repo.GetByID(ctx, scoped.ID)
	assert.True(t, gotUniversal.KindPrimary, "universal primary survives")
	assert.True(t, gotScoped.KindPrimary, "agent-scoped primary also survives")
}

// SetPrimary on an existing row demotes others in the same group.
func TestEnvBundleRepo_SetPrimary_DemotesOthers(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	first := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("claude-code"), Name: "first",
		Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.CreateWithPrimary(ctx, first))

	// Insert a second non-primary, then SetPrimary on it.
	second := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("claude-code"), Name: "second",
		Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.Create(ctx, second))
	assert.False(t, second.KindPrimary)

	require.NoError(t, repo.SetPrimary(ctx, second))

	got1, _ := repo.GetByID(ctx, first.ID)
	got2, _ := repo.GetByID(ctx, second.ID)
	assert.False(t, got1.KindPrimary, "first must be demoted by SetPrimary on second")
	assert.True(t, got2.KindPrimary)
}

// ListEffectiveForUser returns user-owned + org-owned bundles when orgID > 0.
func TestEnvBundleRepo_ListEffectiveForUser_IncludesUserAndOrg(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	userBundle := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 7,
		Name: "user-x", Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.Create(ctx, userBundle))

	orgBundle := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeOrg, OwnerID: 42,
		Name: "org-y", Kind: envbundle.KindShared, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.Create(ctx, orgBundle))

	// Bundle owned by a different org — should NOT appear
	otherOrg := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeOrg, OwnerID: 999,
		Name: "other-org", Kind: envbundle.KindShared, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.Create(ctx, otherOrg))

	out, err := repo.ListEffectiveForUser(ctx, 7, 42, "")
	require.NoError(t, err)
	names := map[string]bool{}
	for _, b := range out {
		names[b.Name] = true
	}
	assert.True(t, names["user-x"])
	assert.True(t, names["org-y"])
	assert.False(t, names["other-org"], "bundles from a different org leak into the user view")
}

// OwnerFilter.AgentSlug tri-state: nil / &"" / &"x".
func TestEnvBundleRepo_List_AgentSlugTriState(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	universal := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: nil, Name: "universal", Kind: envbundle.KindRuntime, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.Create(ctx, universal))

	cc := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		AgentSlug: envStrPtr("claude-code"), Name: "cc",
		Kind: envbundle.KindRuntime, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.Create(ctx, cc))

	// nil → no agent filter (both rows)
	all, _ := repo.List(ctx, envbundle.OwnerFilter{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1, AgentSlug: nil,
	})
	assert.Len(t, all, 2)

	// &"" → NULL only
	empty := ""
	nullOnly, _ := repo.List(ctx, envbundle.OwnerFilter{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1, AgentSlug: &empty,
	})
	require.Len(t, nullOnly, 1)
	assert.Equal(t, "universal", nullOnly[0].Name)

	// &"claude-code" → that slug only
	scoped, _ := repo.List(ctx, envbundle.OwnerFilter{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1, AgentSlug: envStrPtr("claude-code"),
	})
	require.Len(t, scoped, 1)
	assert.Equal(t, "cc", scoped[0].Name)
}

// NameExists discrimination with excludeID for the rename path.
func TestEnvBundleRepo_NameExists_ExcludeID(t *testing.T) {
	repo := newTestEnvBundleRepo(t)
	ctx := context.Background()

	b := &envbundle.EnvBundle{
		OwnerScope: envbundle.OwnerScopeUser, OwnerID: 1,
		Name: "taken", Kind: envbundle.KindCredential, IsActive: true,
		Data: envbundle.BundleData{},
	}
	require.NoError(t, repo.Create(ctx, b))

	exists, err := repo.NameExists(ctx, envbundle.OwnerScopeUser, 1, "taken", nil)
	require.NoError(t, err)
	assert.True(t, exists)

	exists, err = repo.NameExists(ctx, envbundle.OwnerScopeUser, 1, "taken", &b.ID)
	require.NoError(t, err)
	assert.False(t, exists, "excluding the row itself reveals the name as free")
}
