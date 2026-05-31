package invitationconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	invitationsvc "github.com/anthropics/agentsmesh/backend/internal/service/invitation"
	invitationv1 "github.com/anthropics/agentsmesh/proto/gen/go/invitation/v1"
)

// fakeOrg satisfies middleware.OrganizationGetter for ResolveOrgScope tests.
type fakeOrg struct {
	id   int64
	slug string
}

func (f fakeOrg) GetID() int64    { return f.id }
func (f fakeOrg) GetSlug() string { return f.slug }
func (f fakeOrg) GetName() string { return f.slug }

// fakeOrgService satisfies middleware.OrganizationService — used by
// ResolveOrgScope. The role field controls the UserRole the interceptor
// would set; "" means no role override.
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
	return middleware.SetTenant(context.Background(),
		&middleware.TenantContext{UserID: userID})
}

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

// --- Auth / org scope guards ---

func TestListInvitations_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"}, nil, nil)
	_, err := srv.ListInvitations(ctxAsUser(42),
		connect.NewRequest(&invitationv1.ListInvitationsRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListInvitations_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"}, nil, nil)
	_, err := srv.ListInvitations(context.Background(),
		connect.NewRequest(&invitationv1.ListInvitationsRequest{OrgSlug: "acme"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestCreateInvitation_NonAdmin_PermissionDenied(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"}, nil, nil)
	_, err := srv.CreateInvitation(ctxAsUser(42),
		connect.NewRequest(&invitationv1.CreateInvitationRequest{
			OrgSlug: "acme", Email: "bob@example.com", Role: "member",
		}))
	require.Error(t, err)
	assert.Equal(t, connect.CodePermissionDenied, connectCodeOf(t, err))
}

func TestRevokeInvitation_NonAdmin_PermissionDenied(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"}, nil, nil)
	_, err := srv.RevokeInvitation(ctxAsUser(42),
		connect.NewRequest(&invitationv1.RevokeInvitationRequest{OrgSlug: "acme", Id: 1}))
	require.Error(t, err)
	assert.Equal(t, connect.CodePermissionDenied, connectCodeOf(t, err))
}

func TestResendInvitation_NonAdmin_PermissionDenied(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "member"}, nil, nil)
	_, err := srv.ResendInvitation(ctxAsUser(42),
		connect.NewRequest(&invitationv1.ResendInvitationRequest{OrgSlug: "acme", Id: 1}))
	require.Error(t, err)
	assert.Equal(t, connect.CodePermissionDenied, connectCodeOf(t, err))
}

// --- User-scoped guards ---

func TestAcceptInvitation_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil)
	_, err := srv.AcceptInvitation(context.Background(),
		connect.NewRequest(&invitationv1.AcceptInvitationRequest{Token: "abc"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestAcceptInvitation_EmptyToken_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil)
	_, err := srv.AcceptInvitation(ctxAsUser(42),
		connect.NewRequest(&invitationv1.AcceptInvitationRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListPendingInvitations_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil)
	_, err := srv.ListPendingInvitations(context.Background(),
		connect.NewRequest(&invitationv1.ListPendingInvitationsRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

// --- Public service guards ---

func TestGetInvitationByToken_EmptyToken_InvalidArgument(t *testing.T) {
	pub := NewPublicServer(nil)
	_, err := pub.GetInvitationByToken(context.Background(),
		connect.NewRequest(&invitationv1.GetInvitationByTokenRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// --- mapInvitationError + mapBillingError tables ---

func TestMapInvitationError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"not_found", invitationsvc.ErrInvitationNotFound, connect.CodeNotFound},
		{"expired", invitationsvc.ErrInvitationExpired, connect.CodeFailedPrecondition},
		{"already_accepted", invitationsvc.ErrInvitationAccepted, connect.CodeFailedPrecondition},
		{"already_member", invitationsvc.ErrAlreadyMember, connect.CodeAlreadyExists},
		{"pending_invitation", invitationsvc.ErrPendingInvitation, connect.CodeAlreadyExists},
		{"invalid_role", invitationsvc.ErrInvalidRole, connect.CodeInvalidArgument},
		{"not_authorized", invitationsvc.ErrNotAuthorized, connect.CodePermissionDenied},
		{"generic", errors.New("boom"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, connectCodeOf(t, mapInvitationError(tc.in)))
		})
	}
}

func TestMapBillingError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"quota_exceeded", billingsvc.ErrQuotaExceeded, connect.CodeFailedPrecondition},
		{"subscription_frozen", billingsvc.ErrSubscriptionFrozen, connect.CodeFailedPrecondition},
		{"generic", errors.New("boom"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, connectCodeOf(t, mapBillingError(tc.in)))
		})
	}
}

// --- requireAdmin guard ---

func TestRequireAdmin_NoTenant_Unauthenticated(t *testing.T) {
	err := requireAdmin(context.Background())
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestRequireAdmin_Member_PermissionDenied(t *testing.T) {
	ctx := middleware.SetTenant(context.Background(),
		&middleware.TenantContext{UserID: 42, UserRole: "member"})
	err := requireAdmin(ctx)
	require.Error(t, err)
	assert.Equal(t, connect.CodePermissionDenied, connectCodeOf(t, err))
}

func TestRequireAdmin_AdminOrOwner_Ok(t *testing.T) {
	for _, role := range []string{"admin", "owner"} {
		t.Run(role, func(t *testing.T) {
			ctx := middleware.SetTenant(context.Background(),
				&middleware.TenantContext{UserID: 42, UserRole: role})
			assert.NoError(t, requireAdmin(ctx))
		})
	}
}

func TestUserIDFromCtx_NoTenant_Unauthenticated(t *testing.T) {
	_, err := userIDFromCtx(context.Background())
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestUserIDFromCtx_ZeroUserID_Unauthenticated(t *testing.T) {
	ctx := middleware.SetTenant(context.Background(), &middleware.TenantContext{UserID: 0})
	_, err := userIDFromCtx(ctx)
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestUserIDFromCtx_Ok(t *testing.T) {
	uid, err := userIDFromCtx(ctxAsUser(42))
	require.NoError(t, err)
	assert.Equal(t, int64(42), uid)
}
