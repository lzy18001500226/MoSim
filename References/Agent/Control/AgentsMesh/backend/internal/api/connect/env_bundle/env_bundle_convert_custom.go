package envbundleconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
)

// requireUserID mirrors usercredentialconnect.requireUserID — user-scoped
// services don't run ResolveOrgScope, just enforce a valid JWT-supplied UID.
func requireUserID(ctx context.Context) (int64, error) {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return 0, connect.NewError(connect.CodeUnauthenticated, errors.New("authentication required"))
	}
	return tenant.UserID, nil
}
