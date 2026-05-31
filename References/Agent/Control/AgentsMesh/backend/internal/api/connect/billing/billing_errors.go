package billingconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	"github.com/anthropics/agentsmesh/backend/internal/middleware"
	billingsvc "github.com/anthropics/agentsmesh/backend/internal/service/billing"
)

// requireOwner gates write operations that REST scopes to org owner only —
// cancel / reactivate / upgrade / change-cycle / auto-renew / purchase-seats
// / create-checkout. Mirrors REST's `if tenant.UserRole != "owner"` check.
func requireOwner(ctx context.Context) error {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil {
		return connect.NewError(connect.CodeUnauthenticated, errors.New("missing tenant context"))
	}
	if tenant.UserRole != "owner" {
		return connect.NewError(connect.CodePermissionDenied, errors.New("organization owner role required"))
	}
	return nil
}

// requireOwnerOrAdmin allows admin too. Used by SetCustomQuota only (not in
// the current Connect surface) — kept here so the table is the SSOT.
func requireOwnerOrAdmin(ctx context.Context) error {
	tenant := middleware.GetTenant(ctx)
	if tenant == nil {
		return connect.NewError(connect.CodeUnauthenticated, errors.New("missing tenant context"))
	}
	if tenant.UserRole != "owner" && tenant.UserRole != "admin" {
		return connect.NewError(connect.CodePermissionDenied, errors.New("organization admin or owner role required"))
	}
	return nil
}

// mapServiceError translates the billing service sentinels to Connect codes
// per conventions §10. Mirrors the REST error switches scattered across
// billing_handler.go / billing_subscription*.go / billing_seats.go.
func mapServiceError(err error) error {
	switch {
	case errors.Is(err, billingsvc.ErrSubscriptionNotFound),
		errors.Is(err, billingsvc.ErrPlanNotFound),
		errors.Is(err, billingsvc.ErrPriceNotFound),
		errors.Is(err, billingsvc.ErrOrderNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	case errors.Is(err, billingsvc.ErrSubscriptionAlreadyExists):
		return connect.NewError(connect.CodeAlreadyExists, err)
	case errors.Is(err, billingsvc.ErrInvalidPlan),
		errors.Is(err, billingsvc.ErrInvalidOrderStatus),
		errors.Is(err, billingsvc.ErrSeatCountExceedsLimit),
		errors.Is(err, billingsvc.ErrSubscriptionNotActive):
		return connect.NewError(connect.CodeFailedPrecondition, err)
	case errors.Is(err, billingsvc.ErrSubscriptionFrozen),
		errors.Is(err, billingsvc.ErrQuotaExceeded):
		// PaymentRequired has no Connect mapping; FailedPrecondition is the
		// closest semantic match per gRPC code table.
		return connect.NewError(connect.CodeFailedPrecondition, err)
	case errors.Is(err, billingsvc.ErrOrderExpired):
		return connect.NewError(connect.CodeDeadlineExceeded, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
