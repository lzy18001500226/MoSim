package ticketrelationsconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	ticketservice "github.com/anthropics/agentsmesh/backend/internal/service/ticket"
	ticketrelationsv1 "github.com/anthropics/agentsmesh/proto/gen/go/ticket_relations/v1"
)

// fakeOrg and fakeOrgService mirror the repository connect test helpers —
// minimal implementations sufficient for ResolveOrgScope to succeed (or
// fail in the documented ways).
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

// --- ResolveOrgScope guards (one per RPC family is enough; same helper) ---

func TestListRelations_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListRelations(ctxAsUser(42), connect.NewRequest(&ticketrelationsv1.ListRelationsRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListComments_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ListComments(context.Background(), connect.NewRequest(&ticketrelationsv1.ListCommentsRequest{
		OrgSlug: "acme", TicketSlug: "T-1",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

// --- mapServiceError table ---

func TestMapServiceError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"ticket_not_found", ticketservice.ErrTicketNotFound, connect.CodeNotFound},
		{"comment_not_found", ticketservice.ErrCommentNotFound, connect.CodeNotFound},
		{"relation_not_found", ticketservice.ErrRelationNotFound, connect.CodeNotFound},
		{"unauthorized_comment", ticketservice.ErrUnauthorizedComment, connect.CodePermissionDenied},
		{"self_relation", ticketservice.ErrSelfRelation, connect.CodeInvalidArgument},
		{"generic_error", errors.New("oops"), connect.CodeInternal},
		{"nil_err", nil, connect.Code(0)},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := mapServiceError(tc.in)
			if tc.in == nil {
				assert.NoError(t, got)
				return
			}
			assert.Equal(t, tc.want, connectCodeOf(t, got))
		})
	}
}

// --- parseOptionalRFC3339 ---

func TestParseOptionalRFC3339(t *testing.T) {
	t.Run("nil returns nil", func(t *testing.T) {
		got, err := parseOptionalRFC3339(nil)
		require.NoError(t, err)
		assert.Nil(t, got)
	})
	t.Run("empty string returns nil", func(t *testing.T) {
		s := ""
		got, err := parseOptionalRFC3339(&s)
		require.NoError(t, err)
		assert.Nil(t, got)
	})
	t.Run("valid RFC3339 parses", func(t *testing.T) {
		s := "2026-05-12T00:00:00Z"
		got, err := parseOptionalRFC3339(&s)
		require.NoError(t, err)
		require.NotNil(t, got)
		assert.Equal(t, 2026, got.Year())
	})
	t.Run("malformed returns error", func(t *testing.T) {
		s := "not a date"
		_, err := parseOptionalRFC3339(&s)
		require.Error(t, err)
	})
}
