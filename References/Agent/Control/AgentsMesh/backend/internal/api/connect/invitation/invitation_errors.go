package invitationconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
	invitationsvc "github.com/anthropics/agentsmesh/backend/internal/service/invitation"
	"github.com/anthropics/agentsmesh/backend/internal/middleware"
)

// errInvitationEmptyToken is the sentinel returned for blank-token requests
// before any service call. Caller side is auth-required (AcceptInvitation),
// so this surfaces as CodeInvalidArgument, not CodeNotFound.
var errInvitationEmptyToken = errors.New("token is required")

// requireAdmin enforces admin/owner role for org-scoped write operations.
// Mirrors REST `if tc.UserRole != organization.RoleOwner && tc.UserRole !=
// organization.RoleAdmin` at invitations_org.go:32, :130, :177.
func requireAdmin(ctx context.Context) error {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil {
		return connect.NewError(connect.CodeUnauthenticated, errors.New("missing tenant context"))
	}
	if tenant.UserRole != "admin" && tenant.UserRole != "owner" {
		return connect.NewError(
			connect.CodePermissionDenied,
			errors.New("organization admin role required"),
		)
	}
	return nil
}

// userIDFromCtx extracts the authenticated user ID for user-scoped RPCs that
// don't go through ResolveOrgScope (Accept, ListPending).
func userIDFromCtx(ctx context.Context) (int64, error) {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil || tenant.UserID == 0 {
		return 0, connect.NewError(connect.CodeUnauthenticated,
			errors.New("authentication required"))
	}
	return tenant.UserID, nil
}

// mapInvitationError translates invitation-service sentinels to Connect codes
// per conventions §10. Mirrors REST error switches in invitations_org.go
// and invitations_user.go.
func mapInvitationError(err error) error {
	switch {
	case errors.Is(err, invitationsvc.ErrInvitationNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, invitationsvc.ErrInvitationExpired):
		return connect.NewError(connect.CodeFailedPrecondition, err)
	case errors.Is(err, invitationsvc.ErrInvitationAccepted):
		return connect.NewError(connect.CodeFailedPrecondition, err)
	case errors.Is(err, invitationsvc.ErrAlreadyMember),
		errors.Is(err, invitationsvc.ErrPendingInvitation):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, invitationsvc.ErrInvalidRole):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, invitationsvc.ErrNotAuthorized):
		return connect.NewError(connect.CodePermissionDenied, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}

// mapBillingError translates billing-service quota errors emitted by
// CheckSeatAvailability. PaymentRequired has no Connect mapping; the closest
// gRPC semantic match is FailedPrecondition (mirrors billingconnect's choice).
//
// The REST handler maps both ErrQuotaExceeded and ErrSubscriptionFrozen to
// PaymentRequired (402) with distinct API error codes. Connect collapses both
// to FailedPrecondition; client distinguishes via the message text — same
// approach billingconnect takes.
func mapBillingError(err error) error {
	switch {
	case errors.Is(err, billingsvc.ErrQuotaExceeded),
		errors.Is(err, billingsvc.ErrSubscriptionFrozen):
		return connect.NewError(connect.CodeFailedPrecondition, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
