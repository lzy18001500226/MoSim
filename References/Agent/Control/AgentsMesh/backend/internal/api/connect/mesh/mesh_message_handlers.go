package meshconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	meshv1 "github.com/anthropics/agentsmesh/proto/gen/go/mesh/v1"
)

const (
	defaultMessagesLimit = 50
	maxMessagesLimit     = 200
	defaultDLQLimit      = 50
	maxDLQLimit          = 200
)

func (s *MessageServer) ListMeshMessages(
	ctx context.Context, req *connect.Request[meshv1.ListMeshMessagesRequest],
) (*connect.Response[meshv1.ListMeshMessagesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	podKey := req.Msg.GetPodKey()
	if podKey == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("pod_key is required"))
	}
	limit := clampInt32(req.Msg.Limit, defaultMessagesLimit, maxMessagesLimit)
	offset := clampOffset(req.Msg.Offset)
	unreadOnly := req.Msg.GetUnreadOnly()

	messages, err := s.msgSvc.GetMessages(ctx, podKey, unreadOnly, nil, int(limit), int(offset))
	if err != nil {
		return nil, mapMessageError(err)
	}
	unread, err := s.msgSvc.GetUnreadCount(ctx, podKey)
	if err != nil {
		return nil, mapMessageError(err)
	}
	items := toProtoMeshMessages(messages)
	return connect.NewResponse(&meshv1.ListMeshMessagesResponse{
		Items:       items,
		Total:       int64(len(items)),
		Limit:       limit,
		Offset:      offset,
		UnreadCount: unread,
	}), nil
}

func (s *MessageServer) GetMeshUnreadCount(
	ctx context.Context, req *connect.Request[meshv1.GetMeshUnreadCountRequest],
) (*connect.Response[meshv1.GetMeshUnreadCountResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	if req.Msg.GetPodKey() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("pod_key is required"))
	}
	count, err := s.msgSvc.GetUnreadCount(ctx, req.Msg.GetPodKey())
	if err != nil {
		return nil, mapMessageError(err)
	}
	return connect.NewResponse(&meshv1.GetMeshUnreadCountResponse{Count: count}), nil
}

func (s *MessageServer) GetMeshMessage(
	ctx context.Context, req *connect.Request[meshv1.GetMeshMessageRequest],
) (*connect.Response[meshv1.MeshMessage], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	id := req.Msg.GetId()
	if id <= 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("id is required"))
	}
	msg, err := s.msgSvc.GetMessage(ctx, id)
	if err != nil {
		return nil, mapMessageError(err)
	}
	return connect.NewResponse(toProtoMeshMessage(msg)), nil
}

func (s *MessageServer) MarkAllMeshMessagesRead(
	ctx context.Context, req *connect.Request[meshv1.MarkAllReadRequest],
) (*connect.Response[meshv1.MarkAllReadResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	podKey := req.Msg.GetPodKey()
	if podKey == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("pod_key is required"))
	}
	count, err := s.msgSvc.MarkAllRead(ctx, podKey)
	if err != nil {
		return nil, mapMessageError(err)
	}
	return connect.NewResponse(&meshv1.MarkAllReadResponse{MarkedCount: count}), nil
}

func (s *MessageServer) GetMeshConversation(
	ctx context.Context, req *connect.Request[meshv1.GetConversationRequest],
) (*connect.Response[meshv1.GetConversationResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	cid := req.Msg.GetCorrelationId()
	if cid == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("correlation_id is required"))
	}
	limit := clampInt32(req.Msg.Limit, defaultMessagesLimit, maxMessagesLimit)
	messages, err := s.msgSvc.GetConversation(ctx, cid, int(limit))
	if err != nil {
		return nil, mapMessageError(err)
	}
	items := toProtoMeshMessages(messages)
	return connect.NewResponse(&meshv1.GetConversationResponse{
		Items: items,
		Total: int64(len(items)),
		Limit: limit,
	}), nil
}

func (s *MessageServer) GetMeshSentMessages(
	ctx context.Context, req *connect.Request[meshv1.GetSentMessagesRequest],
) (*connect.Response[meshv1.GetSentMessagesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	podKey := req.Msg.GetPodKey()
	if podKey == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("pod_key is required"))
	}
	limit := clampInt32(req.Msg.Limit, defaultMessagesLimit, maxMessagesLimit)
	offset := clampOffset(req.Msg.Offset)
	messages, err := s.msgSvc.GetSentMessages(ctx, podKey, int(limit), int(offset))
	if err != nil {
		return nil, mapMessageError(err)
	}
	items := toProtoMeshMessages(messages)
	return connect.NewResponse(&meshv1.GetSentMessagesResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  limit,
		Offset: offset,
	}), nil
}

func (s *MessageServer) GetMeshDeadLetters(
	ctx context.Context, req *connect.Request[meshv1.GetDeadLettersRequest],
) (*connect.Response[meshv1.GetDeadLettersResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	limit := clampInt32(req.Msg.Limit, defaultDLQLimit, maxDLQLimit)
	offset := clampOffset(req.Msg.Offset)
	entries, err := s.msgSvc.GetDeadLetters(ctx, int(limit), int(offset))
	if err != nil {
		return nil, mapMessageError(err)
	}
	items := toProtoDeadLetters(entries)
	return connect.NewResponse(&meshv1.GetDeadLettersResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  limit,
		Offset: offset,
	}), nil
}

func (s *MessageServer) ReplayMeshDeadLetter(
	ctx context.Context, req *connect.Request[meshv1.ReplayDeadLetterRequest],
) (*connect.Response[meshv1.ReplayDeadLetterResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	entryID := req.Msg.GetEntryId()
	if entryID <= 0 {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("entry_id is required"))
	}
	msg, err := s.msgSvc.ReplayDeadLetter(ctx, entryID)
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound, err)
	}
	statusText := "Replayed successfully"
	return connect.NewResponse(&meshv1.ReplayDeadLetterResponse{
		Message:         &statusText,
		ReplayedMessage: toProtoMeshMessage(msg),
	}), nil
}

// clampInt32 keeps the proto-optional pagination param within sane bounds —
// defaults to `def`, caps at `max`, treats 0 / nil / negative as "use default".
func clampInt32(v *int32, def, max int32) int32 {
	if v == nil {
		return def
	}
	n := *v
	if n <= 0 {
		return def
	}
	if n > max {
		return max
	}
	return n
}

// clampOffset returns 0 for nil / negative inputs. proto3 `optional int32`
// + REST parity: REST allowed `?offset=0` explicitly, and so do we.
func clampOffset(v *int32) int32 {
	if v == nil || *v < 0 {
		return 0
	}
	return *v
}
