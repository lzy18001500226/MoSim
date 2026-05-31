package interceptors_test

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
)

// fakeOrgScopedReq satisfies interceptors.OrgScopedRequest. Mirrors what
// `protoc-gen-go` emits for `string org_slug = 1;` — `Get*` accessors that
// return zero values for absent fields. The other request fields aren't
// material to the resolver, so the stub is intentionally minimal.
type fakeOrgScopedReq struct{ OrgSlug string }

func (f *fakeOrgScopedReq) GetOrgSlug() string { return f.OrgSlug }

type fakeOrg struct {
	id   int64
	slug string
}

func (f fakeOrg) GetID() int64    { return f.id }
func (f fakeOrg) GetSlug() string { return f.slug }
func (f fakeOrg) GetName() string { return f.slug }

type fakeOrgService struct {
	bySlug    map[string]fakeOrg
	roles     map[int64]string
	roleErr   error
	memberErr error
	isMember  bool
}

func (f *fakeOrgService) GetBySlug(_ context.Context, slug string) (middleware.OrganizationGetter, error) {
	org, ok := f.bySlug[slug]
	if !ok {
		return nil, errors.New("org not found")
	}
	return org, nil
}

func (f *fakeOrgService) IsMember(_ context.Context, _, _ int64) (bool, error) {
	return f.isMember, f.memberErr
}

func (f *fakeOrgService) GetMemberRole(_ context.Context, _, userID int64) (string, error) {
	if f.roleErr != nil {
		return "", f.roleErr
	}
	return f.roles[userID], nil
}

func ctxWithUser(userID int64) context.Context {
	return middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: userID})
}

func TestResolveOrgScope_Valid_SetsTenantContext(t *testing.T) {
	svc := &fakeOrgService{
		bySlug: map[string]fakeOrg{"acme": {id: 7, slug: "acme"}},
		roles:  map[int64]string{42: "admin"},
	}
	ctx := ctxWithUser(42)
	req := connect.NewRequest(&fakeOrgScopedReq{OrgSlug: "acme"})

	resolved, org, err := interceptors.ResolveOrgScope(ctx, req.Msg, svc)
	require.NoError(t, err)
	require.NotNil(t, org)
	assert.Equal(t, int64(7), org.GetID())

	tenant := middleware.GetTenant(resolved)
	require.NotNil(t, tenant)
	assert.Equal(t, int64(7), tenant.OrganizationID)
	assert.Equal(t, "acme", tenant.OrganizationSlug)
	assert.Equal(t, int64(42), tenant.UserID)
	assert.Equal(t, "admin", tenant.UserRole)
}

func TestResolveOrgScope_MissingSlug_ReturnsInvalidArgument(t *testing.T) {
	svc := &fakeOrgService{bySlug: map[string]fakeOrg{}}
	ctx := ctxWithUser(42)
	req := connect.NewRequest(&fakeOrgScopedReq{OrgSlug: ""})

	_, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, svc)
	require.Error(t, err)
	var ce *connect.Error
	require.True(t, errors.As(err, &ce))
	assert.Equal(t, connect.CodeInvalidArgument, ce.Code())
}

func TestResolveOrgScope_NoAuthCtx_ReturnsUnauthenticated(t *testing.T) {
	svc := &fakeOrgService{
		bySlug: map[string]fakeOrg{"acme": {id: 7, slug: "acme"}},
	}
	req := connect.NewRequest(&fakeOrgScopedReq{OrgSlug: "acme"})

	_, _, err := interceptors.ResolveOrgScope(context.Background(), req.Msg, svc)
	require.Error(t, err)
	var ce *connect.Error
	require.True(t, errors.As(err, &ce))
	assert.Equal(t, connect.CodeUnauthenticated, ce.Code())
}

func TestResolveOrgScope_UnknownSlug_ReturnsNotFound(t *testing.T) {
	svc := &fakeOrgService{bySlug: map[string]fakeOrg{}}
	ctx := ctxWithUser(42)
	req := connect.NewRequest(&fakeOrgScopedReq{OrgSlug: "ghost"})

	_, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, svc)
	require.Error(t, err)
	var ce *connect.Error
	require.True(t, errors.As(err, &ce))
	assert.Equal(t, connect.CodeNotFound, ce.Code())
}

func TestResolveOrgScope_NotMember_ReturnsPermissionDenied(t *testing.T) {
	svc := &fakeOrgService{
		bySlug:   map[string]fakeOrg{"acme": {id: 7, slug: "acme"}},
		roleErr:  errors.New("not a member"),
		isMember: false,
	}
	ctx := ctxWithUser(42)
	req := connect.NewRequest(&fakeOrgScopedReq{OrgSlug: "acme"})

	_, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, svc)
	require.Error(t, err)
	var ce *connect.Error
	require.True(t, errors.As(err, &ce))
	assert.Equal(t, connect.CodePermissionDenied, ce.Code())
}

func TestResolveOrgScope_RoleLookupFails_MembershipOK_DefaultsToMember(t *testing.T) {
	svc := &fakeOrgService{
		bySlug:   map[string]fakeOrg{"acme": {id: 7, slug: "acme"}},
		roleErr:  errors.New("role lookup failed"),
		isMember: true,
	}
	ctx := ctxWithUser(42)
	req := connect.NewRequest(&fakeOrgScopedReq{OrgSlug: "acme"})

	resolved, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, svc)
	require.NoError(t, err, "must not fail when caller is a member but role lookup glitched")
	tenant := middleware.GetTenant(resolved)
	require.NotNil(t, tenant)
	assert.Equal(t, "member", tenant.UserRole, "must default to 'member' role")
}

func TestResolveOrgScope_MembershipLookupFails_ReturnsInternal(t *testing.T) {
	svc := &fakeOrgService{
		bySlug:    map[string]fakeOrg{"acme": {id: 7, slug: "acme"}},
		roleErr:   errors.New("role lookup failed"),
		memberErr: errors.New("db down"),
	}
	ctx := ctxWithUser(42)
	req := connect.NewRequest(&fakeOrgScopedReq{OrgSlug: "acme"})

	_, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, svc)
	require.Error(t, err)
	var ce *connect.Error
	require.True(t, errors.As(err, &ce))
	assert.Equal(t, connect.CodeInternal, ce.Code())
}
