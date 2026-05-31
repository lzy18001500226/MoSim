package loopconnect

import (
	"context"
	"errors"
	"testing"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	loopv1 "github.com/anthropics/agentsmesh/proto/gen/go/loop/v1"
)

func connectCodeOf(t *testing.T, err error) connect.Code {
	t.Helper()
	var ce *connect.Error
	require.True(t, errors.As(err, &ce), "expected *connect.Error, got %v", err)
	return ce.Code()
}

func TestListLoops_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.ListLoops(context.Background(), connect.NewRequest(&loopv1.ListLoopsRequest{}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestGetLoop_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.GetLoop(context.Background(), connect.NewRequest(&loopv1.GetLoopRequest{LoopSlug: "s"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestCreateLoop_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.CreateLoop(context.Background(), connect.NewRequest(&loopv1.CreateLoopRequest{Name: "n"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestUpdateLoop_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.UpdateLoop(context.Background(), connect.NewRequest(&loopv1.UpdateLoopRequest{LoopSlug: "s"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestDeleteLoop_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.DeleteLoop(context.Background(), connect.NewRequest(&loopv1.DeleteLoopRequest{LoopSlug: "s"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestEnableLoop_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.EnableLoop(context.Background(), connect.NewRequest(&loopv1.LoopActionRequest{LoopSlug: "s"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestDisableLoop_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.DisableLoop(context.Background(), connect.NewRequest(&loopv1.LoopActionRequest{LoopSlug: "s"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestTriggerLoop_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.TriggerLoop(context.Background(), connect.NewRequest(&loopv1.TriggerLoopRequest{LoopSlug: "s"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListRuns_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.ListRuns(context.Background(), connect.NewRequest(&loopv1.ListRunsRequest{LoopSlug: "s"}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestCancelRun_NoOrgSlug(t *testing.T) {
	srv := NewServer(nil, nil, nil, nil, nil)
	_, err := srv.CancelRun(context.Background(), connect.NewRequest(&loopv1.CancelRunRequest{LoopSlug: "s", RunId: 1}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestProcedureConstants(t *testing.T) {
	cases := map[string]string{
		"/proto.loop.v1.LoopService/ListLoops":   ListLoopsProcedure,
		"/proto.loop.v1.LoopService/GetLoop":     GetLoopProcedure,
		"/proto.loop.v1.LoopService/CreateLoop":  CreateLoopProcedure,
		"/proto.loop.v1.LoopService/UpdateLoop":  UpdateLoopProcedure,
		"/proto.loop.v1.LoopService/DeleteLoop":  DeleteLoopProcedure,
		"/proto.loop.v1.LoopService/EnableLoop":  EnableLoopProcedure,
		"/proto.loop.v1.LoopService/DisableLoop": DisableLoopProcedure,
		"/proto.loop.v1.LoopService/TriggerLoop": TriggerLoopProcedure,
		"/proto.loop.v1.LoopService/ListRuns":    ListRunsProcedure,
		"/proto.loop.v1.LoopService/CancelRun":   CancelRunProcedure,
	}
	for want, got := range cases {
		assert.Equal(t, want, got)
	}
}
