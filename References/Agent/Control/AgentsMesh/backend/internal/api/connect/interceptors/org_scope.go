package interceptors

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
)

// OrgScopedRequest is implemented by every Connect-RPC request message whose
// service is scoped to an organization. The protobuf compiler emits the
// `GetOrgSlug` accessor automatically for any message with a top-level
// `string org_slug = 1;` field — see proto-naming-conventions.md §3.5.
//
// We rely on the accessor (not field reflection) so the resolver stays
// generic across all 26 services without runtime proto descriptor walks.
type OrgScopedRequest interface {
	GetOrgSlug() string
}

// ResolveOrgScope reads org_slug from a Connect request, validates the
// caller's membership in that organization, and returns a context carrying a
// fully-populated middleware.TenantContext.
//
// Replaces the REST gin.TenantMiddleware: REST URLs have a `/orgs/:slug/`
// path param, Connect URLs do not (Connect routes are
// `/<package>.<Service>/<Method>`). The org slug must come from the request
// body, and this helper is the single point at which 26 service handlers
// resolve it — drift in resolution semantics would be a 26x compounding bug.
//
// Errors map to Connect codes per conventions §10:
//   * empty slug                  → CodeInvalidArgument
//   * unauthenticated caller       → CodeUnauthenticated
//   * org not found                → CodeNotFound
//   * caller not a member          → CodePermissionDenied
//   * internal membership lookup   → CodeInternal
//
// All returned errors are pre-wrapped with `connect.NewError` — callers MUST
// pass them through with `return nil, err` (no further mapping). This is why
// handler call sites look identical across all 30+ services and why
// `// err already wrapped` comments would be redundant noise.
//
// Callers pass `req.Msg` (which is `*T` for protoc-gen-go-emitted message
// types) directly. We avoid `*connect.Request[T]` in the signature because
// Go generics can't reach through that pointer-of-T to constrain `*T`.
func ResolveOrgScope(
	ctx context.Context,
	req OrgScopedRequest,
	orgSvc middleware.OrganizationService,
) (context.Context, middleware.OrganizationGetter, error) {
	slug := req.GetOrgSlug()
	if slug == "" {
		return ctx, nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("org_slug is required"),
		)
	}

	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return ctx, nil, connect.NewError(
			connect.CodeUnauthenticated,
			errors.New("authentication required"),
		)
	}

	org, err := orgSvc.GetBySlug(ctx, slug)
	if err != nil {
		return ctx, nil, connect.NewError(
			connect.CodeNotFound,
			errors.New("organization not found"),
		)
	}

	role, err := orgSvc.GetMemberRole(ctx, org.GetID(), tenant.UserID)
	if err != nil {
		// GetMemberRole returns ErrNotMember for non-members; the service
		// layer wraps it but we cannot match-types here without coupling to
		// org-service internals. Treat any role-lookup failure as forbidden;
		// the membership check below filters infra errors at the IsMember
		// level (genuine 500s reach the caller as CodeInternal).
		isMember, mErr := orgSvc.IsMember(ctx, org.GetID(), tenant.UserID)
		if mErr != nil {
			return ctx, nil, connect.NewError(connect.CodeInternal, mErr)
		}
		if !isMember {
			return ctx, nil, connect.NewError(
				connect.CodePermissionDenied,
				errors.New("not a member of this organization"),
			)
		}
		// Member but role lookup failed — default to "member" to match the
		// gin TenantMiddleware behavior at tenant.go:111.
		role = "member"
	}

	scoped := &middleware.TenantContext{
		OrganizationID:   org.GetID(),
		OrganizationSlug: org.GetSlug(),
		UserID:           tenant.UserID,
		UserRole:         role,
	}
	return middleware.SetTenant(ctx, scoped), org, nil
}
