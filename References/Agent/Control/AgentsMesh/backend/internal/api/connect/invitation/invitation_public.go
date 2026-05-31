package invitationconnect

import (
	"context"

	"connectrpc.com/connect"

	invitationv1 "github.com/anthropics/agentsmesh/proto/gen/go/invitation/v1"
)

// GetInvitationByToken returns invitation info by token. Unauthenticated —
// the opaque hex token IS the single-use credential. Mirrors REST GET
// /api/v1/invitations/:token (invitations_user.go:15-25).
//
// The service computes is_expired server-side so the /invite/[token] card
// can route to the "expired" branch without recomputing on the client.
// Returns CodeNotFound on either missing token or token mismatch — REST
// uses 404 in both cases (don't leak existence of unknown tokens).
func (p *PublicServer) GetInvitationByToken(
	ctx context.Context, req *connect.Request[invitationv1.GetInvitationByTokenRequest],
) (*connect.Response[invitationv1.InvitationInfo], error) {
	if req.Msg.GetToken() == "" {
		return nil, connect.NewError(connect.CodeInvalidArgument,
			errInvitationEmptyToken)
	}
	info, err := p.invitationSvc.GetInvitationInfo(ctx, req.Msg.GetToken())
	if err != nil {
		return nil, connect.NewError(connect.CodeNotFound, err)
	}
	return connect.NewResponse(toProtoInvitationInfo(info)), nil
}
