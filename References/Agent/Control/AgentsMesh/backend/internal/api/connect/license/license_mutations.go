package licenseconnect

import (
	"context"
	"errors"

	"connectrpc.com/connect"

	licensev1 "github.com/anthropics/agentsmesh/proto/gen/go/license/v1"
)

// LicenseService — auth-required mutations + validation. Every RPC checks
// (1) service availability, (2) owner-role gate when a tenant context is
// present. The combination mirrors the REST handler chain
// (apierr.ServiceUnavailable + apierr.ForbiddenOwner).

func (s *Server) ActivateLicense(
	ctx context.Context, req *connect.Request[licensev1.ActivateLicenseRequest],
) (*connect.Response[licensev1.LicenseStatus], error) {
	if err := requireLicenseService(s.licenseSvc); err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	if len(req.Msg.GetLicenseData()) == 0 {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("license_data is required"),
		)
	}
	if err := s.licenseSvc.ActivateLicense(ctx, req.Msg.GetLicenseData()); err != nil {
		// REST returned apierr.ValidationError (400) for parse / verify
		// failures; CodeInvalidArgument is the Connect equivalent
		// (conventions §10).
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	return connect.NewResponse(toProtoStatus(s.licenseSvc.GetLicenseStatus())), nil
}

func (s *Server) RefreshLicense(
	ctx context.Context, _ *connect.Request[licensev1.RefreshLicenseRequest],
) (*connect.Response[licensev1.LicenseStatus], error) {
	if err := requireLicenseService(s.licenseSvc); err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	if err := s.licenseSvc.RefreshLicense(); err != nil {
		// "no license file path configured" → FailedPrecondition;
		// downstream parse failures → InvalidArgument. Distinguish by
		// substring so we don't introduce a new sentinel just for one
		// boundary check (the service layer doesn't export the sentinel
		// today, and adding one would broaden the SOLID surface).
		if err.Error() == "no license file path configured" {
			return nil, connect.NewError(connect.CodeFailedPrecondition, err)
		}
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	return connect.NewResponse(toProtoStatus(s.licenseSvc.GetLicenseStatus())), nil
}

func (s *Server) ValidateLicense(
	ctx context.Context, req *connect.Request[licensev1.ValidateLicenseRequest],
) (*connect.Response[licensev1.ValidatedLicense], error) {
	if err := requireLicenseService(s.licenseSvc); err != nil {
		return nil, err
	}
	if err := requireOwner(ctx); err != nil {
		return nil, err
	}
	if len(req.Msg.GetLicenseData()) == 0 {
		return nil, connect.NewError(
			connect.CodeInvalidArgument,
			errors.New("license_data is required"),
		)
	}
	licenseData, err := s.licenseSvc.ParseAndVerify(req.Msg.GetLicenseData())
	if err != nil {
		// REST returned a 400 + {valid: false} envelope. Proto preserves
		// the failure shape by encoding `valid: false` on a typed message
		// — the call still surfaces as a Connect error so middleware /
		// telemetry treat it as failure, and Connect's typed-error body
		// carries the diagnostic. UI that needs the preview shape can
		// distinguish via the error code.
		return nil, connect.NewError(connect.CodeInvalidArgument, err)
	}
	return connect.NewResponse(toProtoValidated(licenseData)), nil
}
