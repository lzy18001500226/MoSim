package grantconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	grantsvc "github.com/anthropics/agentsmesh/backend/internal/service/grant"
	grantv1 "github.com/anthropics/agentsmesh/proto/gen/go/grant/v1"
)

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

// --- Validation guards (org_slug missing) ---

func TestListGrants_NoOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.ListGrants(context.Background(),
		connect.NewRequest(&grantv1.ListGrantsRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestCreateGrant_NoOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.CreateGrant(context.Background(),
		connect.NewRequest(&grantv1.CreateGrantRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestDeleteGrant_NoOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.DeleteGrant(context.Background(),
		connect.NewRequest(&grantv1.DeleteGrantRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// --- mapGrantError table ---

func TestMapGrantError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"self_grant", grantsvc.ErrSelfGrant, connect.CodeInvalidArgument},
		{"invalid_type", grantsvc.ErrInvalidType, connect.CodeInvalidArgument},
		{"grant_not_found", grantsvc.ErrGrantNotFound, connect.CodeNotFound},
		{"generic", errors.New("boom"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			assert.Equal(t, tc.want, connectCodeOf(t, mapGrantError(tc.in)))
		})
	}
}

// --- isValidResourceType ---

func TestIsValidResourceType(t *testing.T) {
	assert.True(t, isValidResourceType("pod"))
	assert.True(t, isValidResourceType("runner"))
	assert.True(t, isValidResourceType("repository"))
	assert.False(t, isValidResourceType(""))
	assert.False(t, isValidResourceType("file"))
	assert.False(t, isValidResourceType("POD"))
}

// --- procedure constant identity (conventions §12) ---

func TestProcedureConstants(t *testing.T) {
	assert.Equal(t, "/proto.grant.v1.GrantService/ListGrants", ListGrantsProcedure)
	assert.Equal(t, "/proto.grant.v1.GrantService/CreateGrant", CreateGrantProcedure)
	assert.Equal(t, "/proto.grant.v1.GrantService/DeleteGrant", DeleteGrantProcedure)
}
