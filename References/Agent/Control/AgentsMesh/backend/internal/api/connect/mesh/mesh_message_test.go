package meshconnect

import (
	"context"
	"errors"
	"testing"
	"time"

	"connectrpc.com/connect"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/anthropics/agentsmesh/backend/internal/domain/agent"
	agentservice "github.com/anthropics/agentsmesh/backend/internal/service/agent"
	meshv1 "github.com/anthropics/agentsmesh/proto/gen/go/mesh/v1"
)

// --- guard rails: MessageServer auth + payload validation ---

func TestListMeshMessages_MissingOrgSlug_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.ListMeshMessages(ctxAsUser(1), connect.NewRequest(&meshv1.ListMeshMessagesRequest{
		PodKey: "pod-1",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListMeshMessages_MissingPodKey_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.ListMeshMessages(ctxAsUser(1), connect.NewRequest(&meshv1.ListMeshMessagesRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestListMeshMessages_NoAuth_Unauthenticated(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.ListMeshMessages(context.Background(), connect.NewRequest(&meshv1.ListMeshMessagesRequest{
		OrgSlug: "acme",
		PodKey:  "pod-1",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeUnauthenticated, connectCodeOf(t, err))
}

func TestGetMeshUnreadCount_MissingPodKey_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.GetMeshUnreadCount(ctxAsUser(1), connect.NewRequest(&meshv1.GetMeshUnreadCountRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestGetMeshMessage_MissingId_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.GetMeshMessage(ctxAsUser(1), connect.NewRequest(&meshv1.GetMeshMessageRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestMarkAllMeshMessagesRead_MissingPodKey_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.MarkAllMeshMessagesRead(ctxAsUser(1), connect.NewRequest(&meshv1.MarkAllReadRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestGetMeshConversation_MissingCorrelationId_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.GetMeshConversation(ctxAsUser(1), connect.NewRequest(&meshv1.GetConversationRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestGetMeshSentMessages_MissingPodKey_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.GetMeshSentMessages(ctxAsUser(1), connect.NewRequest(&meshv1.GetSentMessagesRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

func TestReplayMeshDeadLetter_MissingEntryId_InvalidArgument(t *testing.T) {
	srv := NewMessageServer(nil, &fakeOrgService{})
	_, err := srv.ReplayMeshDeadLetter(ctxAsUser(1), connect.NewRequest(&meshv1.ReplayDeadLetterRequest{
		OrgSlug: "acme",
	}))
	require.Error(t, err)
	assert.Equal(t, connect.CodeInvalidArgument, connectCodeOf(t, err))
}

// --- mapMessageError table ---

func TestMapMessageError(t *testing.T) {
	cases := []struct {
		name string
		in   error
		want connect.Code
	}{
		{"message_not_found", agentservice.ErrMessageNotFound, connect.CodeNotFound},
		{"not_authorized", agentservice.ErrNotAuthorized, connect.CodePermissionDenied},
		{"generic_error", errors.New("oops"), connect.CodeInternal},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := connectCodeOf(t, mapMessageError(tc.in))
			assert.Equal(t, tc.want, got)
		})
	}
}// --- toProtoMeshMessage: every field surfaces on the wire ---

func TestToProtoMeshMessage_NilInputReturnsNil(t *testing.T) {
	assert.Nil(t, toProtoMeshMessage(nil))
}

func TestToProtoMeshMessage_AllFieldsPopulated(t *testing.T) {
	correlationID := "corr-1"
	parentID := int64(99)
	createdAt := mustParseTime(t, "2026-05-10T00:00:00Z")
	m := &agent.AgentMessage{
		ID:              42,
		SenderPod:       "pod-a",
		ReceiverPod:     "pod-b",
		MessageType:     "requirement",
		Content:         agent.MessageContent{"text": "hello"},
		Status:          agent.MessageStatusRead,
		CorrelationID:   &correlationID,
		ParentMessageID: &parentID,
		CreatedAt:       createdAt,
	}
	got := toProtoMeshMessage(m)
	require.NotNil(t, got)
	assert.Equal(t, int64(42), got.GetId())
	assert.Equal(t, "pod-a", got.GetSenderPod())
	assert.Equal(t, "pod-b", got.GetReceiverPod())
	assert.Equal(t, "requirement", got.GetMessageType())
	assert.Equal(t, "corr-1", got.GetCorrelationId())
	assert.Equal(t, int64(99), got.GetReplyToId())
	assert.True(t, got.GetIsRead())
	assert.Equal(t, "2026-05-10T00:00:00Z", got.GetCreatedAt())
	// Content travels as a JSON-stringified blob.
	assert.Contains(t, got.GetContent(), `"text":"hello"`)
}

func TestToProtoMeshMessage_IsReadReflectsStatus(t *testing.T) {
	pending := &agent.AgentMessage{ID: 1, Status: agent.MessageStatusPending, CreatedAt: time.Now()}
	read := &agent.AgentMessage{ID: 2, Status: agent.MessageStatusRead, CreatedAt: time.Now()}
	assert.False(t, toProtoMeshMessage(pending).GetIsRead())
	assert.True(t, toProtoMeshMessage(read).GetIsRead())
}

func TestToProtoDeadLetter_NilInputReturnsNil(t *testing.T) {
	assert.Nil(t, toProtoDeadLetter(nil))
}

func TestToProtoDeadLetter_EmbedsOriginalMessage(t *testing.T) {
	e := &agent.DeadLetterEntry{
		ID:        7,
		Reason:    "retry exhausted",
		CreatedAt: mustParseTime(t, "2026-05-10T00:00:00Z"),
		OriginalMessage: &agent.AgentMessage{
			ID:        100,
			SenderPod: "pod-x",
			Status:    agent.MessageStatusDeadLetter,
			CreatedAt: time.Now(),
		},
	}
	got := toProtoDeadLetter(e)
	require.NotNil(t, got)
	assert.Equal(t, int64(7), got.GetId())
	assert.Equal(t, "retry exhausted", got.GetError())
	require.NotNil(t, got.Message)
	assert.Equal(t, int64(100), got.GetMessage().GetId())
	assert.Equal(t, "pod-x", got.GetMessage().GetSenderPod())
}

func TestToProtoDeadLetter_NilOriginalMessageOmitted(t *testing.T) {
	e := &agent.DeadLetterEntry{ID: 3, Reason: "lost", CreatedAt: time.Now()}
	got := toProtoDeadLetter(e)
	require.NotNil(t, got)
	assert.Nil(t, got.Message)
	assert.Equal(t, "lost", got.GetError())
}

// --- clamp helpers ---

func TestClampInt32_NilDefaults(t *testing.T) {
	assert.Equal(t, int32(50), clampInt32(nil, 50, 200))
}

func TestClampInt32_ZeroAndNegativeDefault(t *testing.T) {
	zero, neg := int32(0), int32(-1)
	assert.Equal(t, int32(50), clampInt32(&zero, 50, 200))
	assert.Equal(t, int32(50), clampInt32(&neg, 50, 200))
}

func TestClampInt32_RespectsMax(t *testing.T) {
	v := int32(500)
	assert.Equal(t, int32(200), clampInt32(&v, 50, 200))
}

func TestClampInt32_InRangeKept(t *testing.T) {
	v := int32(75)
	assert.Equal(t, int32(75), clampInt32(&v, 50, 200))
}

func TestClampOffset_NilZero(t *testing.T) {
	assert.Equal(t, int32(0), clampOffset(nil))
}

func TestClampOffset_NegativeZero(t *testing.T) {
	n := int32(-3)
	assert.Equal(t, int32(0), clampOffset(&n))
}

func TestClampOffset_PositiveKept(t *testing.T) {
	n := int32(10)
	assert.Equal(t, int32(10), clampOffset(&n))
}
