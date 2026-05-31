package interceptors

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/domain/user"
	"github.com/anthropics/agentsmesh/backend/internal/infra/database"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
)

type adminUserCtxKey struct{}

// ResolveSystemAdmin validates that the authenticated user (already
// populated into TenantContext by NewAuthInterceptor) has is_system_admin
// + is_active set on their user record. Mirrors middleware.AdminMiddleware
// for the Connect path: AuthMiddleware → AdminMiddleware in REST collapses
// into NewAuthInterceptor → handler-level ResolveSystemAdmin call here.
//
// Returns a new context carrying the resolved *user.User so audit-logging
// call sites (FromAdminContext) can recover the admin id without hitting
// the DB a second time.
//
// Errors map to Connect codes:
//   - missing tenant / userID 0      → CodeUnauthenticated
//   - user not found                  → CodeUnauthenticated (parity with REST's
//                                        AbortUnauthorized; the JWT was valid
//                                        but the user vanished from the DB)
//   - is_system_admin = false         → CodePermissionDenied
//   - is_active = false               → CodePermissionDenied
//   - DB read error                   → CodeInternal
func ResolveSystemAdmin(ctx context.Context, db database.DB) (context.Context, *user.User, error) {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return ctx, nil, connect.NewError(
			connect.CodeUnauthenticated,
			errors.New("authentication required"),
		)
	}

	var u user.User
	if err := db.First(&u, tenant.UserID); err != nil {
		return ctx, nil, connect.NewError(
			connect.CodeUnauthenticated,
			errors.New("user not found"),
		)
	}
	if !u.IsSystemAdmin {
		return ctx, nil, connect.NewError(
			connect.CodePermissionDenied,
			errors.New("system administrator privileges required"),
		)
	}
	if !u.IsActive {
		return ctx, nil, connect.NewError(
			connect.CodePermissionDenied,
			errors.New("user account is disabled"),
		)
	}

	return context.WithValue(ctx, adminUserCtxKey{}, &u), &u, nil
}

// AdminUserFromContext retrieves the resolved admin user attached by
// ResolveSystemAdmin. Returns nil when the caller skipped admin
// resolution — used by audit-logging helpers that need the admin ID
// without re-loading from the DB.
func AdminUserFromContext(ctx context.Context) *user.User {
	u, _ := ctx.Value(adminUserCtxKey{}).(*user.User)
	return u
}
