package blockstoreconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/domain/blockstore"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	blockstorev1 "github.com/anthropics/agentsmesh/proto/gen/go/blockstore/v1"
)

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

// TestApplyOps_MissingOrgSlug — auth interceptor + org_scope helper reject
// requests that don't carry org_slug at tag 1 (conventions §3.5). Without
// org_slug the call must never reach the service layer.
func TestApplyOps_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ApplyOps(ctxAsUser(42), connect.NewRequest(&blockstorev1.ApplyOpsRequest{
		WorkspaceId: "00000000-0000-0000-0000-000000000001",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestApplyOps_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.ApplyOps(context.Background(), connect.NewRequest(&blockstorev1.ApplyOpsRequest{
		OrgSlug:     "acme",
		WorkspaceId: "00000000-0000-0000-0000-000000000001",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestDeleteWorkspace_BadUUID_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.DeleteWorkspace(ctxAsUser(42), connect.NewRequest(&blockstorev1.DeleteWorkspaceRequest{
		OrgSlug:     "acme",
		WorkspaceId: "not-a-uuid",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestGetBlock_BadUUID_InvalidArgument(t *testing.T) {
	srv := NewServer(nil, &fakeOrgService{role: "admin"})
	_, err := srv.GetBlock(ctxAsUser(42), connect.NewRequest(&blockstorev1.GetBlockRequest{
		OrgSlug: "acme",
		Id:      "not-a-uuid",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// TestTranslateErr — every domain sentinel maps to the expected Connect code
// per conventions §10. Mirror of REST's translateErr table (handler.go:75).
func TestTranslateErr(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"nil", nil, connect.Code(0)},
		{"workspace_not_found", blockstore.ErrWorkspaceNotFound, connect.CodeNotFound},
		{"block_not_found", blockstore.ErrBlockNotFound, connect.CodeNotFound},
		{"org_mismatch", blockstore.ErrOrgMismatch, connect.CodePermissionDenied},
		{"forbidden", blockstore.ErrBlockForbidden, connect.CodePermissionDenied},
		{"unknown_block_type", blockstore.ErrUnknownBlockType, connect.CodeInvalidArgument},
		{"unknown_op_kind", blockstore.ErrUnknownOpKind, connect.CodeInvalidArgument},
		{"apply_ops_empty", blockstore.ErrApplyOpsEmpty, connect.CodeInvalidArgument},
		{"single_nest_parent", blockstore.ErrSingleNestParent, connect.CodeAlreadyExists},
		{"nest_cycle", blockstore.ErrNestCycle, connect.CodeAlreadyExists},
		{"stale_update", blockstore.ErrStaleUpdate, connect.CodeAlreadyExists},
		{"workspace_already_exists", blockstore.ErrWorkspaceAlreadyExists, connect.CodeAlreadyExists},
		{"generic", errors.New("oops"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := translateErr(tc.in)
			if tc.in == nil {
				assert.NoError(t, got)
				return
			}
			require.Error(t, got)
			assert.Equal(t, tc.want, connectCodeOf(t, got))
		})
	}
}

// TestApplyOpsInputFromProto_PayloadJSON — every OpEnvelope.payload_json round-
// trips through the connect→service translation; bad JSON surfaces as
// InvalidArgument with the offending index.
func TestApplyOpsInputFromProto_GoodPayload(t *testing.T) {
	req := &blockstorev1.ApplyOpsRequest{
		OrgSlug:     "acme",
		WorkspaceId: "ws",
		Ops: []*blockstorev1.OpEnvelope{
			{Op: "createBlock", PayloadJson: `{"id":"abc","type":"page"}`},
		},
	}
	in, err := applyOpsInputFromProto(req)
	require.NoError(t, err)
	assert.Equal(t, "ws", in.WorkspaceID)
	require.Len(t, in.Ops, 1)
	assert.Equal(t, "createBlock", in.Ops[0].Op)
	assert.Equal(t, "abc", in.Ops[0].Payload["id"])
}

func TestApplyOpsInputFromProto_BadJSON(t *testing.T) {
	req := &blockstorev1.ApplyOpsRequest{
		OrgSlug:     "acme",
		WorkspaceId: "ws",
		Ops: []*blockstorev1.OpEnvelope{
			{Op: "createBlock", PayloadJson: `{not json}`},
		},
	}
	_, err := applyOpsInputFromProto(req)
	require.Error(t, err)
	assert.Contains(t, err.Error(), "index 0")
}

// TestServiceURLs_MatchPackageContract pins every procedure constant to its
// `/<package>.<Service>/<Method>` shape (conventions §12). A drift in the
// proto package or service name surfaces here before it can break routing.
func TestServiceURLs_MatchPackageContract(t *testing.T) {
	assert.Equal(t, "proto.blockstore.v1.BlockstoreService", ServiceName)
	cases := []struct {
		name, want string
	}{
		{ApplyOpsProcedure, "/proto.blockstore.v1.BlockstoreService/ApplyOps"},
		{ListWorkspacesProcedure, "/proto.blockstore.v1.BlockstoreService/ListWorkspaces"},
		{SemanticSearchProcedure, "/proto.blockstore.v1.BlockstoreService/SemanticSearch"},
		{MemoryRetrieveProcedure, "/proto.blockstore.v1.BlockstoreService/MemoryRetrieve"},
		{ExportWorkspaceProcedure, "/proto.blockstore.v1.BlockstoreService/ExportWorkspace"},
	}
	for _, tc := range cases {
		assert.Equal(t, tc.want, tc.name)
	}
}
