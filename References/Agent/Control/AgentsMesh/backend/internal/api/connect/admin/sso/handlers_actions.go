package ssoadminconnect

import (
	"context"
	"log/slog"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/api/connect/interceptors"
	ssov1 "github.com/anthropics/agentsmesh/proto/gen/go/sso/v1"
)

// TestSSOConnection mirrors REST's TestConnection (sso_actions.go:16). The
// REST handler returns HTTP 200 even on failure with `success=false` so the
// frontend can switch between toast.success / toast.error without dealing
// with non-2xx envelopes. Mirror that behavior: we never return a Connect
// error code on connection failure — we surface it as success=false on the
// response.
//
// The connection-attempt error message is intentionally sanitized
// ("Connection test failed. Check server logs for details.") to avoid
// leaking IdP-side internals via the API response. Full error stays in
// slog.
func (s *Server) TestSSOConnection(
	ctx context.Context, req *connect.Request[ssov1.TestSSOConnectionRequest],
) (*connect.Response[ssov1.TestSSOConnectionResponse], error) {
	ctx, _, err := interceptors.ResolveSystemAdmin(ctx, s.db)
	if err != nil {
		return nil, err
	}

	id := req.Msg.GetId()
	if err := s.ssoSvc.TestConnection(ctx, id); err != nil {
		slog.WarnContext(ctx, "SSO test connection failed", "id", id, "error", err)
		errMsg := "Connection test failed. Check server logs for details."
		return connect.NewResponse(&ssov1.TestSSOConnectionResponse{
			Success: false,
			Error:   &errMsg,
		}), nil
	}

	msg := "Connection successful"
	return connect.NewResponse(&ssov1.TestSSOConnectionResponse{
		Success: true,
		Message: &msg,
	}), nil
}
