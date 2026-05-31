package channelconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	channeldomain "github.com/anthropics/agentsmesh/backend/internal/domain/channel"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	channelv1 "github.com/anthropics/agentsmesh/proto/gen/go/channel/v1"
)

const (
	defaultMessagesLimit = 50
	maxMessagesLimit     = 100
	defaultSearchLimit   = 20
	maxSearchLimit       = 100
)

func (s *Server) ListChannelMessages(
	ctx context.Context, req *connect.Request[channelv1.ListChannelMessagesRequest],
) (*connect.Response[channelv1.ListChannelMessagesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	ch, err := s.requireChannelAccess(ctx, req.Msg.GetChannelId())
	if err != nil {
		return nil, err
	}
	limit := clampLimit(req.Msg.Limit, defaultMessagesLimit, maxMessagesLimit)

	var messages []*channeldomain.Message
	var hasMore bool
	if before := req.Msg.GetBeforeId(); before > 0 {
		messages, hasMore, err = s.channelSvc.GetMessagesByCursor(ctx, ch.ID, before, int(limit))
	} else {
		messages, hasMore, err = s.channelSvc.GetMessages(ctx, ch.ID, nil, nil, int(limit))
	}
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*channelv1.ChannelMessage, 0, len(messages))
	for _, m := range messages {
		items = append(items, ToProtoChannelMessage(m))
	}
	return connect.NewResponse(&channelv1.ListChannelMessagesResponse{
		Items:   items,
		Total:   int64(len(items)),
		Limit:   limit,
		Offset:  0,
		HasMore: hasMore,
	}), nil
}

func (s *Server) SearchChannelMessages(
	ctx context.Context, req *connect.Request[channelv1.SearchChannelMessagesRequest],
) (*connect.Response[channelv1.SearchChannelMessagesResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	ch, err := s.requireChannelAccess(ctx, req.Msg.GetChannelId())
	if err != nil {
		return nil, err
	}
	query := req.Msg.GetQuery()
	if query == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument, errors.New("query is required"))
	}
	limit := clampLimit(req.Msg.Limit, defaultSearchLimit, maxSearchLimit)
	messages, err := s.channelSvc.SearchMessages(ctx, ch.ID, query, int(limit))
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*channelv1.ChannelMessage, 0, len(messages))
	for _, m := range messages {
		items = append(items, ToProtoChannelMessage(m))
	}
	return connect.NewResponse(&channelv1.SearchChannelMessagesResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  limit,
		Offset: 0,
	}), nil
}

func (s *Server) SendChannelMessage(
	ctx context.Context, req *connect.Request[channelv1.SendChannelMessageRequest],
) (*connect.Response[channelv1.ChannelMessage], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	ch, err := s.requireChannelAccess(ctx, req.Msg.GetChannelId())
	if err != nil {
		return nil, err
	}
	if ch.IsArchived {
		return nil, connect.NewError(connect.CodeFailedPrecondition, errors.New("cannot send messages to archived channel"))
	}
	content, err := resolveSendContent(req.Msg)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}

	tenant := middleware.GetTenant(ctx)
	var podKey *string
	if k := req.Msg.GetPodKey(); k != "" {
		podKey = &k
	}
	var replyTo *int64
	if r := req.Msg.GetReplyTo(); r != 0 {
		replyTo = &r
	}
	msg, err := s.channelSvc.SendMessage(ctx, ch.ID, podKey, &tenant.UserID, content, replyTo)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(ToProtoChannelMessage(msg)), nil
}

func (s *Server) EditChannelMessage(
	ctx context.Context, req *connect.Request[channelv1.EditChannelMessageRequest],
) (*connect.Response[channelv1.ChannelMessage], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	ch, err := s.requireChannelAccess(ctx, req.Msg.GetChannelId())
	if err != nil {
		return nil, err
	}
	content, err := resolveEditContent(req.Msg)
	if err != nil {
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	tenant := middleware.GetTenant(ctx)
	msg, err := s.channelSvc.EditMessage(ctx, ch.ID, req.Msg.GetMessageId(), tenant.UserID, content)
	if err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(ToProtoChannelMessage(msg)), nil
}

func (s *Server) DeleteChannelMessage(
	ctx context.Context, req *connect.Request[channelv1.DeleteChannelMessageRequest],
) (*connect.Response[channelv1.DeleteChannelMessageResponse], error) {
	ctx, _, err := interceptors.ResolveOrgScope(ctx, req.Msg, s.orgSvc)
	if err != nil {
		return nil, err
	}
	ch, err := s.requireChannelAccess(ctx, req.Msg.GetChannelId())
	if err != nil {
		return nil, err
	}
	tenant := middleware.GetTenant(ctx)
	if err := s.channelSvc.DeleteMessage(ctx, ch.ID, req.Msg.GetMessageId(), tenant.UserID); err != nil {
		return nil, mapServiceError(err)
	}
	return connect.NewResponse(&channelv1.DeleteChannelMessageResponse{Status: "deleted"}), nil
}
