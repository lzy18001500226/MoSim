package grantconnect

import (
	"errors"

	"connectrpc.com/connect"

	grantsvc "github.com/anthropics/agentsmesh/backend/internal/service/grant"
)

// mapGrantError translates grant-service sentinels to Connect codes
// per conventions §10. Mirrors REST handleGrantError in
// resource_grants.go.
func mapGrantError(err error) error {
	switch {
	case errors.Is(err, grantsvc.ErrSelfGrant):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, grantsvc.ErrInvalidType):
		return connect.NewError(connect.CodeInvalidArgument, err)
	case errors.Is(err, grantsvc.ErrGrantNotFound):
		return connect.NewError(connect.CodeNotFound, err)
	default:
		return connect.NewError(connect.CodeInternal, err)
	}
}
