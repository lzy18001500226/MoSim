package userconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/service/user"
	userv1 "github.com/anthropics/agentsmesh/proto/gen/go/user/v1"
)

// ListIdentities — REST analogue: GET /api/v1/users/me/identities.
//
// REST returns `gin.H{"identities": [...]}` with no pagination. We adopt
// the §8 envelope; identity count is bounded (max ~4 providers) so
// total == len(items), and limit/offset are filler (no pagination today).
func (s *Server) ListIdentities(
	ctx context.Context, _ *connect.Request[userv1.ListIdentitiesRequest],
) (*connect.Response[userv1.ListIdentitiesResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	identities, err := s.userSvc.ListIdentities(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	items := make([]*userv1.Identity, 0, len(identities))
	for _, identity := range identities {
		items = append(items, ToProtoIdentity(identity))
	}
	total := int64(len(items))
	return connect.NewResponse(&userv1.ListIdentitiesResponse{
		Items:  items,
		Total:  total,
		Limit:  int32(total),
		Offset: 0,
	}), nil
}

// DeleteIdentity — REST analogue: DELETE /api/v1/users/me/identities/:provider.
//
// REST refuses to remove the last login method (no password + only one
// identity). Mirrors that check via CodeInvalidArgument so the wasm
// client can surface it the same way.
func (s *Server) DeleteIdentity(
	ctx context.Context, req *connect.Request[userv1.DeleteIdentityRequest],
) (*connect.Response[userv1.DeleteIdentityResponse], error) {
	userID, err := requireUserID(ctx)
	if err != nil {
		return nil, err
	}
	provider := req.Msg.GetProvider()
	if provider == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("provider is required"))
	}
	u, err := s.userSvc.GetByID(ctx, userID)
	if err != nil {
		return nil, mapUserServiceError(err)
	}
	identities, err := s.userSvc.ListIdentities(ctx, userID)
	if err != nil {
		return nil, connect.NewError(connect.CodeInternal, err)
	}
	if u.PasswordHash == nil && len(identities) <= 1 {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errors.New("cannot remove last login method"))
	}
	if err := s.userSvc.DeleteIdentity(ctx, userID, provider); err != nil {
		return nil, mapIdentityServiceError(err)
	}
	return connect.NewResponse(&userv1.DeleteIdentityResponse{
		Message: "Identity removed",
	}), nil
}

func mapIdentityServiceError(err error) error {
	if errors.Is(err, user.ErrUserNotFound) {
		return connect.NewError(connect.CodeNotFound, err)
	}
	return connect.NewError(connect.CodeInternal, err)
}
