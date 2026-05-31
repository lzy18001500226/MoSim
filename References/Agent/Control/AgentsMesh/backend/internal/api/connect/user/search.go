package userconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	userv1 "github.com/anthropics/agentsmesh/proto/gen/go/user/v1"
)

// Limit constants mirror REST's binding rules (users.go:188:
// `binding:"omitempty,min=1,max=50"` and default 10).
const (
	defaultSearchLimit = 10
	maxSearchLimit     = 50
	minSearchQueryLen  = 2
)

// SearchUsers — REST analogue: GET /api/v1/users/search.
//
// Mirrors REST's binding rules (min query 2 chars, limit 1..50, default
// 10) and emits the §8 envelope. total == len(items) because the
// service has no separate count call today.
func (s *Server) SearchUsers(
	ctx context.Context, req *connect.Request[userv1.SearchUsersRequest],
) (*connect.Response[userv1.SearchUsersResponse], error) {
	if _, err := requireUserID(ctx); err != nil {
		return nil, err
	}
	query := req.Msg.GetQ()
	if len(query) < minSearchQueryLen {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("query must be at least 2 characters"))
	}
	limit := int(req.Msg.GetLimit())
	if limit <= 0 {
		limit = defaultSearchLimit
	}
	if limit > maxSearchLimit {
		limit = maxSearchLimit
	}
	users, err := s.userSvc.Search(ctx, query, limit)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*userv1.UserSummary, 0, len(users))
	for _, u := range users {
		items = append(items, toProtoUserSummary(u))
	}
	return connect.NewResponse(&userv1.SearchUsersResponse{
		Items:  items,
		Total:  int64(len(items)),
		Limit:  int32(limit),
		Offset: 0,
	}), nil
}
